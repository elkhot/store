from django.db.models.signals import post_save
from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.shortcuts import reverse
from django_countries.fields import CountryField
from django.forms import ModelForm

CATEGORY_CHOICES = (
    ('S', 'Shirt'),
    ('SW', 'Sport wear'),
    ('OW', 'Outwear'),
    ('NU', 'Numbers')
)
AR_CATEGORY_CHOICES = (
    ('S', 'ملابس شبابيه'),
    ('SW', 'ملابس رياضية'),
    ('OW', 'ملابس للخروج'),
    ('NU', "ارقام")
)
LABEL_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger')
)
AR_LABEL_CHOICES = (
    ('P', 'اولى'),
    ('S', 'ثانوى'),
    ('D', 'خطر')
)

ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping')
)


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    one_click_purchasing = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class Item(models.Model):
    title = models.CharField(max_length=100)
    ar_title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=4)
    ar_category = models.CharField(choices=AR_CATEGORY_CHOICES, max_length=4)
    label = models.CharField(choices=LABEL_CHOICES, max_length=4)
    ar_label = models.CharField(choices=AR_LABEL_CHOICES, max_length=4)
    description = models.TextField()
    ar_description = models.TextField()
    slug = models.SlugField()
    image = models.ImageField()

    def __str__(self):
        return self.title

    def get_ar_absolute_url(self):
        return reverse('core:ar-products', kwargs={
            'slug': self.slug
        })

    def get_en_absolute_url(self):
        return reverse('core:en-products', kwargs={
            'slug': self.slug
        })

    def get_ar_add_to_cart_url(self):
        return reverse('core:ar-add-to-cart', kwargs={
            'slug': self.slug
        })

    def get_en_add_to_cart_url(self):
        return reverse('core:en-add-to-cart', kwargs={
            'slug': self.slug
        })

    def get_ar_remove_from_cart_url(self):
        return reverse('core:ar-remove-from-cart', kwargs={
            'slug': self.slug
        })

    def get_en_remove_from_cart_url(self):
        return reverse('core:en-remove-from-cart', kwargs={
            'slug': self.slug
        })


class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    billing_address = models.ForeignKey('Address', related_name='billing_address', on_delete=models.SET_NULL,
                                        blank=True, null=True)
    shipping_address = models.ForeignKey('Address', related_name='shipping_address', on_delete=models.SET_NULL,
                                         blank=True, null=True)
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    def get_total_price(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=100, null=True)
    phone = models.IntegerField(null=True)
    email = models.EmailField(null=True, blank=True)
    street_address = models.CharField(max_length=250, null=True)
    apartment_address = models.CharField(max_length=250, null=True, blank=True)
    country = CountryField(multiple=False, null=True, blank=True)
    zip = models.CharField(max_length=100, null=True, blank=True)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'


class CheckoutForm(ModelForm):
    class Meta:
        model = Address
        fields = ['customer_name', 'phone', 'street_address', 'country']


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=150)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Coupon(models.Model):
    code = models.CharField(max_length=30)
    amount = models.FloatField()

    def __str__(self):
        return self.code


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    customer_name = models.CharField(max_length=100, null=True)
    phone = models.IntegerField(null=True)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"


def userprofile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        userprofile = UserProfile.objects.create(user=instance)


post_save.connect(userprofile_receiver, sender=settings.AUTH_USER_MODEL)
