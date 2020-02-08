from django.db import models
from django.shortcuts import reverse
from django.contrib.auth.models import User
from vendor.models import Vendor_register
from tinymce.models import HTMLField
from datetime import datetime
from django_countries.fields import CountryField

product_type = (
    ('Hot', 'Hot'),
    ('Feature', 'Feature'),
    ('Special Deal', 'Special Deal'),
)
LABEL_CHOICES = (
    ('P', 'Sale'),
    ('S', 'Hot'),
    ('D', 'New')
)
Availability = (
    ('inStock', 'In Stock'),
    ('OutStock', 'Out of Stock'),
)

ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping')
)


class Category(models.Model):
    category_name = models.CharField(max_length=50)
    fa_icon = models.CharField(max_length=20)

    def __str__(self):
        return self.category_name


class Product(models.Model):
    # product_id = models.AutoField
    product_name = models.CharField(max_length=50)
    category = models.ForeignKey(Category, on_delete=models.SET_DEFAULT, default='Uncategorized')
    subcategory = models.CharField(max_length=30)
    type = models.CharField(choices=product_type, max_length=10)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    slug = models.SlugField()
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    short_desc = models.TextField()
    desc = models.TextField()
    min_quantity = models.IntegerField(default=1)
    availability = models.CharField(choices=Availability, max_length=20, default='In Stock')
    pub_date = models.DateField(default=datetime.now(), blank=True)
    image = models.ImageField(upload_to='shop/images', default="")
    vendor = models.ForeignKey(Vendor_register, on_delete=models.CASCADE)

    def __str__(self):
        return self.product_name

    def get_add_to_cart_url(self):
        return reverse("add_to_cart", kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("remove_from_cart", kwargs={
            'slug': self.slug
        })

    def get_add_to_wishlist_url(self):
        return reverse("add_to_wishlist", kwargs={
            'slug': self.slug
        })

    def get_add_to_product_booked_url(self):
        return reverse("add_to_booked", kwargs={
            'slug': self.slug
        })

    def get_remove_from_wishlist_url(self):
        return reverse("remove_from_wishlist", kwargs={
            'slug': self.slug
        })


class Images(models.Model):
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='shop/images', blank=True,
                              verbose_name='Image')

    def __str__(self):
        return self.product_id


class OrderItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    sharing = models.BooleanField(default=False)
    item = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)


    def __str__(self):
        return f"{self.item.product_name} quantity {self.quantity}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        else:
            self.get_total_item_price()


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    shipping_address = models.ForeignKey('Address', related_name='shipping_address', on_delete=models.SET_NULL,
                                         blank=True, null=True)
    billing_address = models.ForeignKey('Address', related_name='billing_address', on_delete=models.SET_NULL,
                                        blank=True, null=True)
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        return total

    def get_total_after_coupon(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=100)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()

    def __str__(self):
        return self.code


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    email = models.EmailField()
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.pk}"


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return self.item.product_name


class ProBooked(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return self.user.username


class Contact(models.Model):
    msg_id = models.AutoField(primary_key='true')
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)
    desc = models.TextField(max_length=500)

    def __str__(self):
        return self.name
