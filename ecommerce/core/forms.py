from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget


PAYMENT_OPTIONS = (
    ('S', 'Stripe'),
    ('P', 'PayPal'),
)


class CheckoutForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        # 'placeholder': 'John Doe',
        'class': 'form-control',
    }))
    address_1 = forms.CharField(max_length=200, widget=forms.TextInput(attrs={
        # 'placeholder': '1234 Main St',
        'class': 'form-control',
    }))
    address_2 = forms.CharField(max_length=200, widget=forms.TextInput(attrs={
        # 'placeholder': 'Apartment or suite',
        'class': 'form-control',
    }))
    country = CountryField(blank_label='Select country').formfield(
        widget=CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100',
        }))
    state = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
    }))
    zip = forms.CharField(max_length=10, widget=forms.TextInput(attrs={
        'class': 'form-control',
    }))
    same_shipping_address = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    save_info = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    payment_option = forms.ChoiceField(widget=forms.RadioSelect, choices=PAYMENT_OPTIONS)


class DiscountCodeForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Promo code',
        'aria-label': 'Recipient\'s username',
        'aria-describedby': 'basic-addon2'
    }))
