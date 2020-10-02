from django.urls import path
from .views import (
	Home,
	Product,
	checkout,

	)

app_name = 'core'

urlpatterns = [
	path('', Home.as_view(), name='home'),
    path('product/<slug>/', Product.as_view(), name='product'),
    path('checkout/', checkout, name='checkout'),

]