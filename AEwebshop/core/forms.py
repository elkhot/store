from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from .models import Address

AR_PAYMENT_CHOICES = (
    ('S', ' دفع ببطاقة الائتمان'),
    ('P', 'الدفع عند الاستلام')
)

EN_PAYMENT_CHOICES = (
    ('S', 'Pay with credit card'),
    ('P', 'Cash on delivery')
)


class CheckoutForm(forms.Form):
    full_name = forms.CharField(required=True)
    phone_number = forms.IntegerField(required=True)
    email_address = forms.EmailField(required=False)
    shipping_address = forms.CharField(required=True)
    shipping_address2 = forms.CharField(required=False)

    shipping_country = CountryField(blank_label='(Choose a country)').formfield(
        required=True,
        widget=CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100',
        }))
    en_payment_option = forms.ChoiceField(
        required=True,
        widget=forms.RadioSelect, choices=EN_PAYMENT_CHOICES)


class ArCheckoutForm(forms.Form):
    full_name = forms.CharField(required=True)
    phone_number = forms.IntegerField(required=True)
    email_address = forms.EmailField(required=False)
    shipping_address = forms.CharField(required=True)
    shipping_address2 = forms.CharField(required=False)
    ar_shipping_country = CountryField(blank_label='(اختار البلد)').formfield(
        required=True,
        widget=CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100',
        }))
    ar_payment_option = forms.ChoiceField(
        required=True,
        widget=forms.RadioSelect, choices=AR_PAYMENT_CHOICES)


class DeliveryForm(forms.Form):
    user = forms.CharField(disabled=True)
    full_name = forms.CharField(max_length=100, initial=True)
    phone_number = forms.IntegerField(initial=True)
    email_address = forms.EmailField(initial=True)
    shipping_address = forms.CharField(initial=True)
    shipping_address2 = forms.CharField(initial=True)
    ar_shipping_country = CountryField(blank_label='(اختار البلد)').formfield(
        required=False,
        widget=CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100',
        }))
    en_shipping_country = CountryField(blank_label='(Choose a country)').formfield(
        required=False,
        widget=CountrySelectWidget(attrs={
            'class': 'custom-select d-block w-100',
        }))
    shipping_zip = forms.CharField(required=False)

    set_default_shipping = forms.BooleanField(required=False)
    use_default_shipping = forms.BooleanField(required=False)


class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Promo code',
        'aria-label': 'Recipient\'s username',
        'aria-describedby': 'basic-addon2'
    }))


class RefundForm(forms.Form):
    ref_code = forms.CharField()
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 4
    }))
    customer_name = forms.CharField(max_length=100)
    phone = forms.IntegerField()
    email = forms.EmailField()


class PaymentForm(forms.Form):
    stripeToken = forms.CharField(required=False)
    save = forms.BooleanField(required=False)
    use_default = forms.BooleanField(required=False)
    cardNumber = forms.CharField(max_length=16)
    cardExpiry = forms.DateField()
    cardCvc = forms.IntegerField()
    zipCode = forms.IntegerField()