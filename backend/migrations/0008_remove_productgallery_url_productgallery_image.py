# Generated by Django 5.1.6 on 2025-03-29 05:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0007_transaction_payment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='productgallery',
            name='url',
        ),
        migrations.AddField(
            model_name='productgallery',
            name='image',
            field=models.ImageField(default='bg-masthead.jpg', upload_to='images/'),
        ),
    ]
