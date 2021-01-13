from django.urls import path
from .views import (
    Home,
    Product,
    OrderSummary,
    Checkout,
    add_to_cart,
    remove_from_cart,
    remove_single_item_from_cart,
    PaymentView,
    ApplyDiscCode,
)

app_name = 'core'

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('product/<slug>/', Product.as_view(), name='product'),
    path('order-summary/', OrderSummary.as_view(), name='order-summary'),
    path('add-to-cart/<slug>', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>', remove_from_cart, name='remove-from-cart'),
    path('remove-single-item-from-cart/<slug>', remove_single_item_from_cart, name='remove-single-item-from-cart'),
    path('apply-code/', ApplyDiscCode.as_view(), name='apply-code'),
    path('checkout/', Checkout.as_view(), name='checkout'),
    path('payment/<payment_option>', PaymentView.as_view(), name='payment'),
]
