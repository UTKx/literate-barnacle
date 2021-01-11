from django.conf import settings
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic import ListView, DetailView, View
from .models import Item, OrderItem, Order, BillingAddress, Payment
from .forms import CheckoutForm

import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


class Home(ListView):
    model = Item
    paginate_by = 2
    template_name = 'home.html'


class Product(DetailView):
    model = Item
    template_name = 'product.html'


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_queryset = Order.objects.filter(user=request.user, ordered=False)
    if order_queryset.exists():
        order = order_queryset[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, 'Your cart is updated')
            return redirect('core:order-summary')
        else:
            order.items.add(order_item)
            messages.info(request, 'This item is added to your cart')
            return redirect('core:order-summary')
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user,
            ordered_date=ordered_date
        )
        order.items.add(order_item)
        messages.info(request, 'This item is added to your cart')
        return redirect('core:order-summary')


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            messages.info(request, 'This item was removed to your cart')
            return redirect('core:order-summary')
        else:
            messages.info(request, 'This item was not in cart')
            return redirect('core:order-summary', slug=slug)
    else:
        messages.info(request, 'You do not have an active order')
        return redirect('core:order-summary', slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
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
                order.items.remove(order_item)
            messages.info(request, 'This item quantity is updated')
            return redirect('core:order-summary')
        else:
            messages.info(request, 'This item was not in cart')
            return redirect('core:product', slug=slug)
    else:
        messages.info(request, 'You do not have an active order')
        return redirect('core:product', slug=slug)


class OrderSummary(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, 'You do not have an active order')
            return redirect('/')


class Checkout(View):
    def get(self, *args, **kwargs):
        form = CheckoutForm()
        order = Order.objects.get(user=self.request.user, ordered=False)
        context = {
            'form': form,
            'order': order
        }
        return render(self.request, 'checkout.html', context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                name = form.cleaned_data.get('name')
                address_1 = form.cleaned_data.get('address_1')
                address_2 = form.cleaned_data.get('address_2')
                country = form.cleaned_data.get('country')
                state = form.cleaned_data.get('state')
                zip = form.cleaned_data.get('zip')
                # same_shipping_address = form.cleaned_data.get('same_shipping_address')
                # save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')

                billing_address = BillingAddress(
                    user=self.request.user,
                    name=name,
                    address_1=address_1,
                    address_2=address_2,
                    country=country,
                    state=state,
                    zip=zip
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()

                if payment_option == 'S':
                    return redirect('core:payment', payment_option='stripe')
                elif payment_option == 'P':
                    return redirect('core:payment', payment_option='paypal')
                else:
                    messages.warning(self.request, 'Invalid payment option')
                    return redirect('core:checkout')

            return redirect('core:checkout')

        except ObjectDoesNotExist:
            messages.error(self.request, 'You do not have an active order')
            return redirect('core:summary')


class PaymentView(View):
    def get(self, *args, **kwargs):
        print('in get')
        order = Order.objects.get(user=self.request.user, ordered=False)
        context = {
            'order': order
        }
        return render(self.request, 'payment.html', context)

    def post(self, *args, **kwargs):
        print('in post')
        order = Order.objects.get(user=self.request.user, ordered=False)
        amount = int(order.get_total() * 100)
        token = self.request.POST.get('stripeToken')

        try:
            # Use Stripe's library to make requests...
            charge = stripe.Charge.create(
                amount=amount,
                currency="usd",
                source=token,
                # description="My First Test Charge (created for API docs)",
            )

            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            order.ordered = True
            order.payment = payment
            order.save()

            messages.success(self.request, "Your order was successful.")
            return redirect('/')

        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            body = e.json_body
            err = body.get('error', {})
            messages.error(self.request, f"{err.get('message')}")
            return redirect('/')
        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.error(self.request, "Rate limit error")
            return redirect('/')
        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            messages.error(self.request, "Invalid request")
            return redirect('/')
        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.error(self.request, "Not authenticated")
            return redirect('/')
        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.error(self.request, "Network error")
            return redirect('/')
        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.error(self.request, "Something went wrong. You were not charged.")
            return redirect('/')
        except Exception as e:
            # Something else happened, completely unrelated to Stripe
            messages.error(self.request, "A serious error occured. We have been notified.")
            return redirect('/')
