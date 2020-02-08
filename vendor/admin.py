from django.contrib import admin
from .models import Vendor_register


def vendor_request_accepted(modeladmin, request, queryset):
    queryset.update(approved=True)


vendor_request_accepted.short_description = 'Accept Vendor request'


class VendorAdmin(admin.ModelAdmin):
    list_display = [
        'vendor_shop_name',
        'vendor_user_id',
        'vendor_email',
        'vendor_city',
        'vendor_shop_category',
        'approved',
    ]
    actions = [vendor_request_accepted]


admin.site.register(Vendor_register, VendorAdmin)
