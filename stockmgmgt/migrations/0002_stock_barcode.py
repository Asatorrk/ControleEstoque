# Generated by Django 5.1.2 on 2024-10-30 17:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stockmgmgt', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='stock',
            name='barcode',
            field=models.CharField(max_length=50, null=True, unique=True),
        ),
    ]
