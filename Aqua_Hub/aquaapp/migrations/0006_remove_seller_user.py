# Generated by Django 5.1 on 2024-09-04 16:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aquaapp', '0005_seller_username'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='seller',
            name='user',
        ),
    ]
