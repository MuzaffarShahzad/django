from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='shopIndex'),
    path('about/', views.about, name='aboutUs'),
    path('contact/', views.contact, name='contactUs'),
    path('tracker/', views.track, name='trackingStatus'),
    path('search/', views.search, name='search'),
    path('product/<slug>/', views.prodview, name='product'),
    path('category/<cat>/', views.category, name='product_category'),
    path('vendor-product-list/<int:vendor>', views.vendorProduct.as_view(), name='vendor_product_list'),

    path('add-to-cart/<slug>', views.add_to_cart, name='add_to_cart'),
    path('add-to-wishlist/<slug>', views.add_to_wishlist, name='add_to_wishlist'),
    # path('product-booked/<slug>', views.ProductBooked, name='add_to_booked'),
    path('add-coupon/', views.AddCouponView.as_view(), name='add_coupon'),
    path('order-summary/', views.OrderSummary.as_view(), name='order_summary'),
    path('wishlist/', views.WishlistSummary.as_view(), name='wishlist'),
    path('remove-from-wishlist/<slug>', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('remove-single-item-from-cart/<slug>', views.remove_single_item_from_cart, name='remove_single_item_from_cart'),
    path('remove-from-cart/<slug>', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout.as_view(), name='checkout'),
    path('payment/<payment_option>/', views.PaymentView.as_view(), name='payment'),
    path('request-refund/', views.RequestRefundView.as_view(), name='request_refund')
]