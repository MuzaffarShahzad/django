# Generated by Django 2.2.7 on 2020-01-15 17:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendor', '0004_vendor_register_vendor_logo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendor_register',
            name='vendor_logo',
            field=models.ImageField(default='vendor_logo/default.png', upload_to='vendor_logo'),
        ),
    ]