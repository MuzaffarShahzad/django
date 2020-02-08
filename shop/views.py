from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils import timezone
from users.models import profile
from vendor.models import Vendor_register
from django.views.generic import ListView, DetailView, View
from .models import Product, Contact, Order, OrderItem, Address, Payment, Coupon, Refund, Wishlist, ProBooked, Category
from .forms import CheckoutForm, couponForm, RefundForm, PaymentForm
from django.conf import settings
import stripe
import random
import string

stripe.api_key = settings.STRIPE_PUBLISHABLE_KEY


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


# class Index(ListView):
#     model = Product
#     template_name = "shop/index.html"


def index(request):
    products = Product.objects.all()
    category = Category.objects.all()
    context = {
        'object_list': products,
        'categories': category,

    }

    return render(request, 'shop/index.html', context)


class WishlistSummary(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            wishlist = Wishlist.objects.filter(user=self.request.user)
            context = {
                'object': wishlist
            }
            return render(self.request, 'shop/wishlist.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have any items in wishlist")
            return redirect("/")


class OrderSummary(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            # if order.items.quantity < order.items.item.min_quantity:
            #     messages.error(self.request, f'Minimum Quantity is {order.items.item.min_quantity}.You can share this product with other customer')
            context = {
                'object': order,
                'couponform': couponForm(),
                'DISPLAY_COUPON_FORM': True
            }
            return render(self.request, 'shop/order_summary.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect("/")


# def index(request):
#     products = Product.objects.all()
#     # print(products)
#     n = len(products)
#     nSlides = n // 4 + ceil((n / 4) - (n // 4))
#     # params = {'no_of_slides':nSlides, 'range': range(1,nSlides), 'product': products}
#     allProds = [[products, range(1, nSlides), nSlides],
#                 [products, range(1, nSlides), nSlides]]
#     # params = {'allProds': allProds}
#     params = {'product': products}
#     return render(request, 'shop/index.html', params)


def about(request):
    return render(request, 'shop/about.html')


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        desc = request.POST.get('desc', '')
        if is_valid_form([name, email, phone, desc]):
            contact_form = Contact(name=name, email=email, phone=phone, desc=desc)
            contact_form.save()
            messages.success(request, 'Your message is successfully received. We will contact you shortly.')
        else:
            messages.warning(request, 'Fields should not be empty.')

    return render(request, 'shop/contact.html')


def track(request):
    return render(request, 'shop/track.html')


def search(request):
    return render(request, 'shop/search.html')


# def productView(request, slug):
#     product = get_object_or_404(Product, slug=slug)
#     order = Order.objects.filter(ordered=False, items=product)
#     context = {
#         'product': product,
#         'order': order
#     }
#     return render(request, 'shop/prodView.html', context)


# class productView(DetailView):
#     model = Product
#     template_name = 'shop/prodView.html'

# def get(self, *args, **kwargs):
#     product = Product.objects.get(slug=self.slug)
#     context = {
#         'object': product,
#     }
#     return render(self.request, 'shop/prodView.html', context)


def prodview(request, slug):
    product = get_object_or_404(Product, slug=slug)
    item = product
    booked = ProBooked.objects.filter(item=item)
    context = {
        'product': product,
        'product_booked': booked
    }
    return render(request, 'shop/prodView.html', context)


def category(request, cat):
    products = Product.objects.filter(category=cat)
    context = {
        'product': products
    }
    return render(request, 'shop/product_category.html', context)


class vendorProduct(ListView):
    model = Product
    template_name = 'shop/vendor_products.html'  # <app>/<model>_<viewType>.html
    context_object_name = 'v_products'
    # paginate_by = 6

    def get_queryset(self):
        vendor = get_object_or_404(Vendor_register, id=self.kwargs.get('vendor'))
        return Product.objects.filter(vendor=vendor)


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


class checkout(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'couponform': couponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True
            }
            shipping_address_qs = Address.objects.filter(
                user=self.request.user,
                address_type='S',
                default=True
            )
            if shipping_address_qs.exists():
                context.update(
                    {'default_shipping_address': shipping_address_qs[0]}
                )

                billing_address_qs = Address.objects.filter(
                    user=self.request.user,
                    address_type='B',
                    default=True
                )
                if billing_address_qs.exists():
                    context.update(
                        {'default_billing_address': billing_address_qs[0]}
                    )

            return render(self.request, "shop/checkout.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("shop/checkout")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():

                use_default_shipping = form.cleaned_data.get('use_default_shipping')
                if use_default_shipping:
                    print("Using the default shipping address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='S',
                        default=True
                    )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(self.request, "No default shipping address available")
                        return redirect('checkout')
                else:
                    print("User is entering a new shipping address")

                    shipping_address1 = form.cleaned_data.get('shipping_address')
                    shipping_address2 = form.cleaned_data.get('shipping_address2')
                    shipping_country = form.cleaned_data.get('shipping_country')
                    shipping_zip = form.cleaned_data.get('shipping_zip')

                    if is_valid_form([shipping_address1, shipping_country, shipping_zip]):
                        shipping_address = Address(
                            user=self.request.user,
                            street_address=shipping_address1,
                            apartment_address=shipping_address2,
                            country=shipping_country,
                            zip=shipping_zip,
                            address_type='S'
                        )
                        shipping_address.save()
                        order.shipping_address = shipping_address
                        order.save()

                        set_default_shipping = form.cleaned_data.get('set_default_shipping')
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()
                    else:
                        messages.info(self.request, "Please fill in the required shipping address fields")

                use_default_billing = form.cleaned_data.get('use_default_billing')
                same_billing_address = form.cleaned_data.get('use_default_billing')
                if same_billing_address:
                    billing_address = shipping_address
                    billing_address.pk = None
                    billing_address.save()
                    billing_address.address_type = 'B'
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()

                elif use_default_billing:
                    print("Using the default billing address")
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        address_type='B',
                        default=True
                    )
                    if address_qs.exists():
                        billing_address = address_qs[0]
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.info(self.request, "No default billing address available")
                        return redirect('checkout')
                else:
                    print("User is entering a new billing address")

                    billing_address1 = form.cleaned_data.get('billing_address')
                    billing_address2 = form.cleaned_data.get('billing_address2')
                    billing_country = form.cleaned_data.get('billing_country')
                    billing_zip = form.cleaned_data.get('billing_zip')

                    if is_valid_form([billing_address1, billing_country, billing_zip]):
                        billing_address = Address(
                            user=self.request.user,
                            street_address=billing_address1,
                            apartment_address=billing_address2,
                            country=billing_country,
                            zip=billing_zip,
                            address_type='B'
                        )
                        billing_address.save()
                        order.billing_address = billing_address
                        order.save()

                        set_default_billing = form.cleaned_data.get('set_default_billing')
                        if set_default_billing:
                            billing_address.default = True
                            billing_address.save()
                    else:
                        messages.info(self.request, "Please fill in the required billing address fields")

                payment_option = form.cleaned_data.get('payment_option')

                if payment_option == 'S':
                    return redirect('payment', payment_option='stripe')
                elif payment_option == 'P':
                    return redirect('payment', payment_option='PayPal')
                else:
                    messages.warning(self.request, "Invalid payment option selected")
                    return redirect("checkout")

        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect("order_summary")


class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.billing_address:
            context = {
                'order': order,
                'DISPLAY_COUPON_FORM': False
            }
            userprofile = self.request.user.profile
            if userprofile.one_click_purchasing:
                # fetch the users card list
                cards = stripe.Customer.list_sources(
                    userprofile.stripe_customer_id,
                    limit=3,
                    object='card'
                )
                card_list = cards['data']
                if len(card_list) > 0:
                    # update the context with the default card
                    context.update({
                        'card': card_list[0]
                    })
            return render(self.request, "shop/payment.html", context)
        else:
            messages.warning(self.request, "You have not added a billing address")
            return redirect("checkout")

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        form = PaymentForm(self.request.POST)
        userprofile = profile.objects.get(user=self.request.user)
        if form.is_valid():
            token = form.cleaned_data.get('stripeToken')
            save = form.cleaned_data.get('save')
            use_default = form.cleaned_data.get('use_default')

            if save:
                if userprofile.stripe_customer_id != '' and userprofile.stripe_customer_id is not None:
                    customer = stripe.Customer.retrieve(
                        userprofile.stripe_customer_id)
                    customer.sources.create(source=token)

                else:
                    customer = stripe.Customer.create(
                        email=self.request.user.email,
                    )
                    customer.sources.create(source=token)
                    userprofile.stripe_customer_id = customer['id']
                    userprofile.one_click_purchasing = True
                    userprofile.save()

            amount = int(order.get_total() * 100)

            try:

                if use_default or save:
                    # charge the customer because we cannot charge the token more than once
                    charge = stripe.Charge.create(
                        amount=amount,  # cents
                        currency="usd",
                        customer=userprofile.stripe_customer_id
                    )
                else:
                    # charge once off on the token
                    charge = stripe.Charge.create(
                        amount=amount,  # cents
                        currency="usd",
                        source=token
                    )

                # create the payment
                payment = Payment()
                payment.stripe_charge_id = charge['id']
                payment.user = self.request.user
                payment.amount = order.get_total()
                payment.save()

                # assign the payment to the order

                order_items = order.items.all()
                order_items.update(ordered=True)
                for item in order_items:
                    item.save()

                order.ordered = True
                order.payment = payment
                order.ref_code = create_ref_code()
                order.save()

                messages.success(self.request, "Your order was successful!")
                return redirect("/")

            except stripe.error.CardError as e:
                body = e.json_body
                err = body.get('error', {})
                messages.warning(self.request, f"{err.get('message')}")
                return redirect("/")

            except stripe.error.RateLimitError as e:
                # Too many requests made to the API too quickly
                messages.warning(self.request, "Rate limit error")
                return redirect("/")

            except stripe.error.InvalidRequestError as e:
                # Invalid parameters were supplied to Stripe's API
                print(e)
                messages.warning(self.request, "Invalid parameters")
                return redirect("/")

            except stripe.error.AuthenticationError as e:
                # Authentication with Stripe's API failed
                # (maybe you changed API keys recently)
                messages.warning(self.request, "Not authenticated")
                return redirect("/")

            except stripe.error.APIConnectionError as e:
                # Network communication with Stripe failed
                messages.warning(self.request, "Network error")
                return redirect("/")

            except stripe.error.StripeError as e:
                # Display a very generic error to the user, and maybe send
                # yourself an email
                messages.warning(
                    self.request, "Something went wrong. You were not charged. Please try again.")
                return redirect("/")

            except Exception as e:
                # send an email to ourselves
                messages.warning(
                    self.request, "A serious error occurred. We have been notifed.")
                return redirect("/")

        messages.warning(self.request, "Invalid data received")
        return redirect("/payment/stripe/")


@login_required
def add_to_wishlist(request, slug):
    item = get_object_or_404(Product, slug=slug)
    order_qs = Wishlist.objects.filter(user=request.user, item=item)
    if order_qs.exists():
        messages.info(request, "This item is already in your wishlist.")
        return redirect("wishlist")
    else:
        Wishlist.objects.create(user=request.user, item=item)
        messages.success(request, "This item was added to your wishlist.")
        return redirect("wishlist")


@login_required
def remove_from_wishlist(request, slug):
    item = get_object_or_404(Product, slug=slug)
    order_qs = Wishlist.objects.filter(user=request.user, item=item)
    if order_qs.exists():
        order_qs.delete()
        messages.info(request, "This item is deleted from your wishlist.")
        return redirect("wishlist")
    else:
        messages.success(request, "This item was not in your wishlist.")
        return redirect("wishlist")


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Product, slug=slug)
    # quantity = item.min_quantity
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        quantity=item.min_quantity,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            # return redirect('product', slug=slug)
            return redirect("order_summary")
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            # return redirect('product', slug=slug)
            return redirect("order_summary")

    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        # return redirect('product', slug=slug)
        return redirect("order_summary")


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Product, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            messages.info(request, "This item was removed from your cart.")
            return redirect('order_summary')
        else:
            messages.info(request, "This item was not in your cart")
            return redirect('order_summary')
    else:
        messages.info(request, "You do not have an active order")
        return redirect('order_summary')


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Product, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order_item.remove(order_item)
            messages.info(request, "This item quantity was updated")
            return redirect('order_summary')
        else:
            messages.info(request, "This item was not in your cart")
            return redirect('product', slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect('product', slug=slug)


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This coupon does not exist")
        return redirect('checkout')


class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = couponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(user=self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "Successfully added coupon")
                return redirect("checkout")
            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have an active order")
                return redirect("checkout")


class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, "shop/request_refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                # store the refund in refund table in database
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.success(self.request, "Your request was received")
                return redirect('request_refund')

            except ObjectDoesNotExist:
                messages.info(self.request, "This order does not exist")
                return redirect('request_refund')
