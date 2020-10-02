from django.urls import path
from .views import (
	Home,
	Product,
	checkout,
	add_to_cart,
	)

app_name = 'core'

urlpatterns = [
	path('', Home.as_view(), name='home'),
    path('product/<slug>/', Product.as_view(), name='product'),
    path('add-to-cart/<slug>', add_to_cart, name='cart'),  
    path('checkout/', checkout, name='checkout'),

]