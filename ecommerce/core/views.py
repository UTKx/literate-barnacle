from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from .models import Item, OrderItem, Order
from django.utils import timezone


class Home(ListView):
	model = Item
	template_name = 'home.html'


class Product(DetailView):
	model = Item
	template_name = 'product.html'


def add_to_cart(request, slug):
	item = get_object_or_404(Item, slug=slug)
	order_item, created = OrderItem.objects.get_or_create(
		item = item,
		user = request.user,
		ordered = False
	)
	order_queryset = Order.objects.filter(user = request.user, ordered = False)
	if order_queryset.exists():
		order = order_queryset[0]
		if order.items.filter(item__slug = item.slug).exists():
			order_item.quantity += 1
			order_item.save()
		else:
			order.items.add(order_item)
	else:
		ordered_date = timezone.now()
		order = Order.objects.create(
			user = request.user,
			ordered_date=ordered_date
		)
	return redirect('core:product', slug = slug)


def remove_from_cart(request, slug):
	item = get_object_or_404(Item, slug=slug)
	order_qs = Order.objects.filter(
		user = request.user,
		ordered = False
	)
	if order_qs.exists():
		order = order_qs[0]
		if order.items.filter(item__slug=item.slug).exists():
			order_item = OrderItem.objects.filter(
				item = item,
				user = request.user,
				ordered = False
			)[0]
			order.items.remove(order_item)
		else:
			return redirect('core:product', slug=slug)
	else:
		return redirect('core:product', slug=slug)
	return redirect('core:product', slug=slug)


def checkout(request):
	return render(request, 'checkout.html', )
