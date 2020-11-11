from django import template
from core.models import Order

register = template.Library()

@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        order_count = Order.objects.filter(user=user, ordered=False)
        if order_count.exists():
            return order_count[0].items.count()
    return 0
