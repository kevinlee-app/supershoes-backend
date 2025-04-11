from django.contrib import admin
from .models import *
from django.contrib.auth.models import User
from django.utils.html import mark_safe

class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1  # Show an empty form to add new images
    readonly_fields = ('image_preview',)  # Make the image preview read-only
    fields = ('image_preview', 'image')  # Customize fields shown in the inline form

    def image_preview(self, obj):
        if obj.image.url:  # Ensure the URL is not empty
            return mark_safe(f'<img src="{obj.image.url}" width="100" height="100" style="border-radius:5px;"/>')
        return "No Image"

    image_preview.short_description = "Preview"

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'description', 'tags', 'category', 'gallery_images')
    inlines = [ProductGalleryInline]  # Add gallery images inside the product admin page

    def gallery_images(self, obj):
        galleries = obj.gallery.all()  # Use related_name="gallery"
        if galleries:
            return mark_safe(" ".join([f'<img src="{gallery.image.url}" width="50" height="50" style="border-radius:5px; margin-right:5px;"/>' for gallery in galleries]))
        return "No Images"

    gallery_images.allow_tags = True  # Required to render HTML in Django < 3.x
    gallery_images.short_description = "Gallery"  # Column name in admin
    

class ProductGalleryAdmin(admin.ModelAdmin):
    list_display = ('id', 'image', 'gallery_images')

    def gallery_images(self, gallery):
        print("IMAGE URL: " + gallery.image.url)
        return mark_safe('<img src="{0}" width="50" height="50" style="border-radius:5px; margin-right:5px;"/>'.format(gallery.image.url))

    gallery_images.allow_tags = True  # Required to render HTML in Django < 3.x
    gallery_images.short_description = "Gallery"  # Column name in admin

class TransactionDetailAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'transaction_user', 'product', 'quantity', 'created_at')

# ✅ Custom method to display Transaction ID
    def transaction_id(self, obj):
        return obj.transaction.id  
    transaction_id.short_description = "Transaction ID"

    # ✅ Custom method to display Transaction User (Username)
    def transaction_user(self, obj):
        return obj.transaction.user.username  
    transaction_user.short_description = "User"

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_price', 'shipping_price', 'created_at')

    def user(self, obj):
        return obj.user.username  
    user.short_description = "User"

admin.site.register(Product, ProductAdmin)
admin.site.register(ProductCategory)
admin.site.register(ProductGallery, ProductGalleryAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(TransactionDetail, TransactionDetailAdmin)
