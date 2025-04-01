from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate
import re
from django.conf import settings

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['profile_photo_url']

class UserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="first_name")
    profile_photo_url = serializers.CharField(source="profile.profile_photo_url", required=False)

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'profile_photo_url', 'username', 'is_staff']

    def update(self, instance, validated_data):
        request_user = self.context['request'].user
        
        if 'name' in validated_data:
            validated_data['first_name'] = validated_data.pop('name')
        
        if 'is_staff' in validated_data and not request_user.is_staff:
            validated_data.pop('is_staff')

        profile_data = validated_data.pop('profile', {})

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        profile_instance = instance.profile
        for attr, value in profile_data.items():
            setattr(profile_instance, attr, value)
        profile_instance.save()

        return instance

class ProductGallerySerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    class Meta:
        model = ProductGallery
        fields = ['id', 'image_url']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            image_url = obj.image.url
            if request:
                return request.build_absolute_uri(image_url)
            return f"{settings.MEDIA_URL}{image_url}"
        return None

class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    gallery = serializers.SerializerMethodField()
    category = ProductCategorySerializer()

    class Meta:
        model = Product
        fields = '__all__'

    def get_gallery(self, obj):
        gallery_qs = ProductGallery.objects.filter(product=obj)
        request = self.context.get('request')
        return ProductGallerySerializer(gallery_qs, many=True, context={'request': request}).data 

class TransactionDetailSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), write_only=True)

    class Meta:
        model = TransactionDetail
        fields = ['product', 'product_id', 'quantity']

class TransactionSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    details = TransactionDetailSerializer(many=True)
    
    class Meta:
        model = Transaction
        fields = ['user_id', 'address', 'details', 'total_price', 'shipping_price', 'payment', 'status']

    def get_details(self, obj):
        details_qs = TransactionDetail.objects.filter(transaction=obj)
        return TransactionDetailSerializer(details_qs, many=True).data

    def create(self, validated_data):
        details_data = validated_data.pop('details')  # ✅ Extract details
        request = self.context.get('request', None)
        user = request.user if request else None  # ✅ Get authenticated user

        # ✅ Create transaction
        transaction = Transaction.objects.create(user=user, **validated_data)

        # ✅ Create TransactionDetail instances
        transaction_details = []
        for detail in details_data:
            product = detail.pop('product_id')  # ✅ Extract product ID
            if not isinstance(product.id, int):  # ✅ Ensure it's an integer
                raise serializers.ValidationError({"product_id": "Invalid product ID."})

            product = get_object_or_404(Product, id=product.id)  # ✅ Convert ID to Product instance
            transaction_details.append(TransactionDetail(
                transaction=transaction,
                product=product,
                quantity=detail.get('quantity')
            ))

        TransactionDetail.objects.bulk_create(transaction_details)  # ✅ Save all details efficiently

        return transaction  # ✅ Return the created transact

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6, style={'input_type': 'password'})
    name = serializers.CharField(
        source='first_name',
        required=True, 
        min_length=2, 
        max_length=50,
        error_messages={
            "required": "First name is required.",
            "blank": "First name cannot be empty.",
            "min_length": "First name must be at least 2 characters long."
        }
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'email', 'password', 'is_staff']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def to_representation(self, instance):
        data = {}

        profile, created = UserProfile.objects.get_or_create(user=instance)
        refresh = RefreshToken.for_user(instance)
        data['token'] = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        data['user'] = {
            "id": instance.id,
            "username": instance.username,
            "email": instance.email,
            "is_staff": instance.is_staff,
            "name": instance.first_name,
            "profile_photo_url": profile.profile_photo_url,
        }
        
        return data

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        login = attrs.get("username")
        password = attrs.get("password")

        if not login or not password:
            raise AuthenticationFailed("Both login and password are required")
        
        if re.match(r"[^@]+@[^@]+\.[^@]+", login):
            user_query = User.objects.filter(email=login)
        else:
            user_query = User.objects.filter(username=login)

        if not user_query.exists():
            raise AuthenticationFailed("User not found")
        
        user = user_query.first()
        user = authenticate(username=user.username, password=password)

        if user is None:
            raise AuthenticationFailed("Invalid credentials")

        if not user.is_active:
            raise AuthenticationFailed("User account is disabled")

        data = {}
        refresh = RefreshToken.for_user(user)

        profile, created = UserProfile.objects.get_or_create(user=user)
        data['token'] = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        data['user'] = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_staff": user.is_staff,
            "name": user.first_name,
            "profile_photo_url": profile.profile_photo_url,
        }
        
        return data