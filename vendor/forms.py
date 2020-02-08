from django import forms
from .models import Vendor_register
from shop.models import Product

# VENDOR_SHOP_CATEGORY = (
#     ('Electronic', 'Electronics'),
#     ('Clothing', 'Clothing'),
#     ('Furniture', 'Furniture'),
#     ('Toys', 'Toys'),
#
# )


class VendorRegister(forms.ModelForm):
    class Meta:
        model = Vendor_register
        fields = [
            'vendor_name',
            'vendor_shop_name',
            'vendor_logo',
            'vendor_email',
            'vendor_city',
            'vendor_shop_category',
            'vendor_phone',
            'vendor_address'
        ]


class AddNewProduct(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'product_name',
            'category',
            'subcategory',
            'type',
            'label',
            'slug',
            'price',
            'discount_price',
            'short_desc',
            'desc',
            'min_quantity',
            'availability',
            'image',
        ]