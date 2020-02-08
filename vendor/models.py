from django.db import models
from django.contrib.auth.models import User


VENDOR_SHOP_CATEGORY = (
    ('Electronic', 'Electronics'),
    ('Clothing', 'Clothing'),
    ('Furniture', 'Furniture'),
    ('Toys', 'Toys'),

)


class Vendor_register(models.Model):
    vendor_user_id = models.OneToOneField(User, on_delete=models.CASCADE)
    vendor_name = models.CharField(max_length=100)
    vendor_shop_name = models.CharField(max_length=100)
    vendor_logo = models.ImageField(default='vendor_logo/default.png', upload_to='vendor_logo')
    vendor_email = models.EmailField(null=False)
    vendor_city = models.CharField(max_length=30)
    vendor_address = models.CharField(max_length=500)
    vendor_shop_category = models.CharField(choices=VENDOR_SHOP_CATEGORY, max_length=50)
    vendor_phone = models.CharField(max_length=50)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return self.vendor_shop_name
