from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.VendorProductListView.as_view(), name='vendor_index'),
    path('registration/', views.Add_Vendor.as_view(), name='vendor_register'),
    path('add-product/', views.NewProduct.as_view(), name='add_product'),
    # path('vendor-product/', views.VendorProductListView.as_view(), name='vendor_product_list'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)