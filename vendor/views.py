from django.shortcuts import render
from .forms import VendorRegister, AddNewProduct
from .models import Vendor_register
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.db import IntegrityError
from shop.models import Category, Product
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import View, ListView , UpdateView


class VendorProductListView(ListView):
    model = Product
    template_name = 'vendor/vendor_home.html'  # <app>/<model>_<viewType>.html
    context_object_name = 'v_products'
    paginate_by = 6

    def get_queryset(self):
        vendor = get_object_or_404(Vendor_register, vendor_user_id=self.request.user.id)
        return Product.objects.filter(vendor=vendor)


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


# def add_product(request):
#     product_category = Category.objects.all()
#     product = Product.objects.all()
#
#     context = {
#         'prodCategory': product_category,
#         'Product': product
#     }
#     return render(request, 'vendor/add_product.html', context)


class Add_Vendor(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        v_form = VendorRegister()
        context = {
            'vendor_form': v_form
        }
        return render(self.request, "vendor/vendor_register.html", context)

    def post(self, *args, **kwargs):
        try:
            if self.request.method == 'POST':
                form = VendorRegister(self.request.POST, self.request.FILES)
                if form.is_valid():
                    vendor_name = form.cleaned_data.get('vendor_name')
                    vendor_shop_name = form.cleaned_data.get('vendor_shop_name')
                    vendor_logo = form.cleaned_data.get('vendor_logo')
                    vendor_email = form.cleaned_data.get('vendor_email')
                    vendor_city = form.cleaned_data.get('vendor_city')
                    vendor_shop_category = form.cleaned_data.get('vendor_shop_category')
                    vendor_phone = form.cleaned_data.get('vendor_phone')
                    vendor_address = form.cleaned_data.get('vendor_address')

                    if is_valid_form(
                            [vendor_name, vendor_shop_name, vendor_email, vendor_logo, vendor_city,
                             vendor_shop_category,
                             vendor_phone, vendor_logo, vendor_address]):
                        vendor = Vendor_register(
                            vendor_user_id=self.request.user,
                            vendor_name=vendor_name,
                            vendor_shop_name=vendor_shop_name,
                            vendor_logo=vendor_logo,
                            vendor_email=vendor_email,
                            vendor_city=vendor_city,
                            vendor_shop_category=vendor_shop_category,
                            vendor_phone=vendor_phone,
                            vendor_address=vendor_address
                        )
                        vendor.save()
                        messages.success(self.request, 'Your request has been submitted successfully.')
                        return redirect("/")
                else:
                    messages.warning(self.request, 'Fields should not be empty.')
                    return redirect("vendor_register")
        except IntegrityError as e:
            messages.warning(self.request, 'Already register as vendor.')
            return redirect("vendor_register")


class NewProduct(LoginRequiredMixin, View):

    def get(self, *args, **kwargs):
        p_form = AddNewProduct()
        vendor = Vendor_register.objects.get(vendor_user_id=self.request.user)
        context = {
            'product_form': p_form,
            'vendor': vendor
        }
        return render(self.request, "vendor/add_product.html", context)

    def post(self, *args, **kwargs):
        vendor = Vendor_register.objects.filter(vendor_user_id=self.request.user.id)
        # vendor = AddNewProduct.vendor = self.request.user
        if self.request.method == 'POST':
            form = AddNewProduct(self.request.POST)
            if not form.is_valid():
                product_name = form.cleaned_data.get('product_name')
                category = form.cleaned_data.get('category')
                subcategory = form.cleaned_data.get('subcategory')
                type = form.cleaned_data.get('type')
                label = form.cleaned_data.get('label')
                slug = form.cleaned_data.get('slug')
                price = form.cleaned_data.get('price')
                discount_price = form.cleaned_data.get('discount_price')
                short_desc = form.cleaned_data.get('short_desc')
                desc = form.cleaned_data.get('desc')
                min_quantity = form.cleaned_data.get('min_quantity')
                availability = form.cleaned_data.get('availability')
                image = form.cleaned_data.get('image')
                # vendor = form.cleaned_data.get('vendor')

                if is_valid_form(
                        [product_name, category, subcategory, type, label, slug, price, discount_price, short_desc,
                         desc, min_quantity, availability, image]):
                    product = Product(
                        product_name=product_name,
                        category=category,
                        subcategory=subcategory,
                        type=type,
                        label=label,
                        slug=slug,
                        price=price,
                        discount_price=discount_price,
                        short_desc=short_desc,
                        desc=desc,
                        min_quantity=min_quantity,
                        availability=availability,
                        image=image,
                        vendor=vendor[0]
                    )
                    product.save()
                    messages.success(self.request, 'Your product has been added successfully.')
                    return redirect("vendor_index")
            else:
                messages.warning(self.request, 'Required Fields should not be empty.')
                return redirect("vendor_index")

















