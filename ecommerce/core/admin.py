from django.contrib import admin
from .models import Item, OrderItem, Order, Payment, DiscountCode, Address


def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)


make_refund_accepted.short_description = 'Update orders to refund granted'


class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'ordered',
        'being_delivered',
        'received',
        'refund_requested',
        'refund_granted',
        'billing_address',
        'shipping_address',
        'payment',
        'disc_code'
    ]
    list_display_links = [
        'user',
        'billing_address',
        'shipping_address',
        'payment',
        'disc_code'
    ]
    list_filter = [
        'ordered',
        'being_delivered',
        'received',
        'refund_requested',
        'refund_granted',
    ]
    search_fields = [
        'user__username',
        'ref_code'
    ]
    actions = [make_refund_accepted]


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'name',
        'address_1',
        'address_2',
        'country',
        'state',
        'zip',
        'address_type',
        'default',
    ]
    list_filter = ['default', 'address_type', 'country']
    search_fields = ['user', 'address_1', 'address_2']


admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(DiscountCode)
admin.site.register(Address, AddressAdmin)
