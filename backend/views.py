from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from .pagination import DefaultPagination

class ProductCategoryView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = DefaultPagination()

    def get(self, request, category_id=None):
        if category_id:
            product_category = get_object_or_404(ProductCategory, id=category_id)
            serializer = ProductCategorySerializer(product_category)
            return Response(serializer.data, status=status.HTTP_200_OK)

        categories = ProductCategory.objects.all()
        paginator = self.pagination_class
        paginated_categories = paginator.paginate_queryset(categories, request)
        serializer = ProductCategorySerializer(categories, many=True)
        return paginator.get_paginated_response(serializer.data)

class ProductView(APIView):
    pagination_class = DefaultPagination()

    def get(self, request, product_id=None):
        if product_id:
            product = get_object_or_404(Product, id=product_id)
            serializer = ProductSerializer(product)
            return Response(serializer.data, status=status.HTTP_200_OK)

        products = Product.objects.all()
        paginator = self.pagination_class
        paginated_products = paginator.paginate_queryset(products, request)
        serializer = ProductSerializer(products, many=True)
        return paginator.get_paginated_response(serializer.data)

class TransactionView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = DefaultPagination()

    def get(self, request, transaction_id=None):
        if transaction_id:
            transaction = get_object_or_404(Transaction, id=transaction_id)
            serializer = TransactionSerializer(transaction)
            return Response(serializer.data, status=status.HTTP_200_OK)

        transactions = Transaction.objects.all()
        paginator = self.pagination_class
        paginated_products = paginator.paginate_queryset(transactions, request)
        serializer = TransactionSerializer(transactions, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = TransactionSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            transaction = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        errors = serializer.errors
        first_error_message = next(iter(errors.values()))[0]

        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        errors = serializer.errors
        first_error_message = next(iter(errors.values()))[0]

        return Response({"error": first_error_message}, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"error": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"message": "Logout successful."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)


class UserView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)