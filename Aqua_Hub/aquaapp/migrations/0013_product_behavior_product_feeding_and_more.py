# Generated by Django 5.1 on 2024-10-09 06:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aquaapp', '0012_product_care_info'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='behavior',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='feeding',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='health_issues',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='tank_size',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='water_quality',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
