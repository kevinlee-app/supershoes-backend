# Generated by Django 5.1.6 on 2025-04-11 15:50

import backend.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0009_alter_productgallery_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productgallery',
            name='image',
            field=models.ImageField(default='images/default_shoes.png', upload_to=backend.models.product_gallery_upload_path),
        ),
    ]
