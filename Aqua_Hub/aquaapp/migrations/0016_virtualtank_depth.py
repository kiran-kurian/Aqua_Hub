# Generated by Django 5.1 on 2024-10-15 05:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aquaapp', '0015_virtualtank'),
    ]

    operations = [
        migrations.AddField(
            model_name='virtualtank',
            name='depth',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]