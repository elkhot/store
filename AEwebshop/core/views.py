from django.shortcuts import render, get_object_or_404, redirect, get_list_or_404
from django.views.generic import ListView, DetailView, View
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CheckoutForm, CouponForm, RefundForm, PaymentForm, ArCheckoutForm
from .models import Item, OrderItem, Order, Address, Payment, Coupon, Refund
from django.conf import settings

import random
import string
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))


def ar_products(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request, 'ar-product-page.html', context)


def en_products(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request, 'en-product-page.html', context)


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


class ArCheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = ArCheckoutForm()
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True
            }

            return render(self.request, "ar-checkout-page.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "عفوا, لا يوجد لديك طلب")
            return redirect("core:ar-checkout")

    def post(self, *args, **kwargs):
        form = ArCheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)

        except ObjectDoesNotExist:
            messages.warning(self.request, "عفوا, لا يوجد لديك طلب")

        if form.is_valid():
            print("User is entering a new shipping address")
            full_name = form.cleaned_data.get(
                'full_name')
            phone_number = form.cleaned_data.get(
                'phone_number')
            email_address = form.cleaned_data.get(
                'email_address')
            shipping_address1 = form.cleaned_data.get(
                'shipping_address')
            shipping_address2 = form.cleaned_data.get(
                'shipping_address2')
            ar_shipping_country = form.cleaned_data.get(
                'ar_shipping_country')

            if is_valid_form([full_name, phone_number, shipping_address1, ar_shipping_country]):
                shipping_address = Address(
                    user=self.request.user,
                    customer_name=full_name,
                    phone=phone_number,
                    email=email_address,
                    street_address=shipping_address1,
                    apartment_address=shipping_address2,
                    country=ar_shipping_country,
                    address_type='S'

                )
                shipping_address.save()

                order.shipping_address = shipping_address
                order.save()

        else:
            messages.info(
                self.request, "من فضلك قم بادخال بيانات عنوان الشحن المطلوبة")
            return redirect('core:ar-checkout')

        ar_payment_option = form.cleaned_data.get('ar_payment_option')

        if ar_payment_option == 'S':
            return redirect('core:ar-payment', ar_payment_option='الدفع ببطاقة الائتمان')
        elif ar_payment_option == 'P':
            return redirect('core:ar-delivery', ar_payment_option='الدفع عند الاستلام')
        else:
            messages.warning(
                self.request, "وسيلة دفع غير متوفرة")
            return redirect('core:ar-checkout')


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


class EnCheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True
            }

            return render(self.request, "en-checkout-page.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("core:en-checkout")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)

        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")

        if form.is_valid():
            print("User is entering a new shipping address")
            full_name = form.cleaned_data.get(
                'full_name')
            phone_number = form.cleaned_data.get(
                'phone_number')
            email_address = form.cleaned_data.get(
                'email_address')
            shipping_address1 = form.cleaned_data.get(
                'shipping_address')
            shipping_address2 = form.cleaned_data.get(
                'shipping_address2')
            shipping_country = form.cleaned_data.get(
                'shipping_country')

            if is_valid_form([full_name, phone_number, shipping_address1, shipping_country]):
                shipping_address = Address(
                    user=self.request.user,
                    customer_name=full_name,
                    phone=phone_number,
                    email=email_address,
                    street_address=shipping_address1,
                    apartment_address=shipping_address2,
                    country=shipping_country,
                    address_type='S'

                )
                shipping_address.save()

                order.shipping_address = shipping_address
                order.save()

        else:
            messages.info(
                self.request, "Please fill in the required shipping address fields")
            return redirect('core:en-checkout')

        en_payment_option = form.cleaned_data.get('en_payment_option')

        if en_payment_option == 'S':
            return redirect('core:en-payment', en_payment_option='stripe')
        elif en_payment_option == 'P':
            return redirect('core:en-delivery', en_payment_option='paypal')
        else:
            messages.warning(
                self.request, "Invalid payment option selected")
            return redirect('core:en-checkout')


class ArPaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        context = {
            'order': order
        }
        return render(self.request, 'ar-payment.html', context)

    def post(self, *args, **kwargs):
        token = self.request.POST.get('stripeToken')
        order = Order.objects.get(user=self.request.user, ordered=False)
        amount = int(order.get_total_price() * 100)  # cents
        try:
            charge = stripe.Charge.create(
                amount=amount,
                currency="egp",
                source=token,
            )
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total_price()
            payment.save()

            order.ordered = True
            order.payment = payment
            order.ref_code = create_ref_code()
            order.save()
            messages.success(self.request, 'الطلب تم بنجاح')
            return redirect('/ar/')

        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            body = e.jason_body
            err = body.get('error', {})
            messages.warning(self.request, f"{err.get('message')}")
            return redirect("/ar/")

        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.warning(self.request, ' Rate limit error')
            return redirect('/ar/')

        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            messages.warning(self.request, ' Invalid parameters')
            return redirect('/ar/')
        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.warning(self.request, ' Not authenticated')
            return redirect('/ar/')
        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.warning(self.request, ' Network error')
            #             return redirect('/ar/')
            #         except stripe.error.StripeError as e:
            #             # Display a very generic error to the user, and maybe send
            #             # yourself an email
            messages.warning(self.request, ' Something went wrong. You were not charged. Please try again!')
            return redirect('/ar/')
        except Exception as e:
            # Something else happened, completely unrelated to Stripe
            # send an email to our selves
            messages.warning(self.request, ' Serious error occurred. We have been notified')
            return redirect('/ar/')


class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        context = {
            'order': order
        }
        return render(self.request, 'en-payment.html', context)

    def post(self, *args, **kwargs):
        token = self.request.POST.get('stripeToken')
        order = Order.objects.get(user=self.request.user, ordered=False)
        amount = int(order.get_total_price() * 100)  # cents
        try:
            charge = stripe.Charge.create(
                amount=amount,
                currency="egp",
                source=token,
            )
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total_price()
            payment.save()

            order.ordered = True
            order.payment = payment
            order.ref_code = create_ref_code()
            order.save()
            messages.success(self.request, 'Your order was successful.')
            return redirect('/en/')

        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            body = e.jason_body
            err = body.get('error', {})
            messages.warning(self.request, f"{err.get('message')}")
            return redirect("/en/")

        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.warning(self.request, ' Rate limit error')
            return redirect('/en/')

        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            messages.warning(self.request, ' Invalid parameters')
            return redirect('/en/')
        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.warning(self.request, ' Not authenticated')
            return redirect('/en/')
        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.warning(self.request, ' Network error')
            return redirect('/en/')
        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.warning(self.request, ' Something went wrong. You were not charged. Please try again!')
            return redirect('/en/')
        except Exception as e:
            # Something else happened, completely unrelated to Stripe
            # send an email to our selves
            messages.warning(self.request, ' Serious error occurred. We have been notified')
            return redirect('/en/')


class HomeView(ListView):
    model = Item
    template_name = "home-multilingual.html"


class EnHomeView(ListView):
    model = Item
    paginate_by = 10
    template_name = "en-home-page.html"


class ArHomeView(ListView):
    model = Item
    paginate_by = 10
    template_name = "ar-home-page.html"


class ArOrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'ar-order-summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "عفوا لا يوجد لديك طلب")
            return redirect("/ar")


class EnOrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'en-order-summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/en")


class ArDeliveryView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order,
            }
            return render(self.request, 'ar-delivery.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "عفوا ليس لديك طلب")
            return redirect("/ar")


class EnDeliveryView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order,
            }
            return render(self.request, 'en-delivery.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/en")


class ArItemDetailView(DetailView):
    model = Item
    template_name = "ar-product-page.html"


class EnItemDetailView(DetailView):
    model = Item
    template_name = "en-product-page.html"


@login_required
def ar_add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(item=item, user=request.user, ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, 'تم تحديث كمية االسلعة فى العربة.')
        else:
            order.items.add(order_item)
            messages.info(request, 'تمت اضافه السلعه الى العربه بنجاح.')

    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, 'تم اضافة هذا المنتج الى العربة.')
    return redirect('core:ar-products', slug=slug)


@login_required
def en_add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(item=item, user=request.user, ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, 'This item quantity was updated in your cart.')
        else:
            order.items.add(order_item)
            messages.info(request, 'This item was added to your cart.')

    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, 'This item was added to your cart.')
    return redirect('core:en-products', slug=slug)


@login_required
def ar_remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[0]
            if order_item.quantity > 0:
                order_item.quantity -= 1
                order_item.save()
                messages.info(request, 'تم تحديت كمية هذا المنتج فى العربة.')

            else:
                messages.info(request, 'هذا المنتج غير موجود فى العربة.')
                return redirect('core:ar-products', slug=slug)
        else:
            messages.info(request, 'هذا المنتج غير موجود فى العربة.')
            return redirect('core:ar-products', slug=slug)
    else:
        messages.info(request, 'عفوا لا يوجد لديك طلب.')
        return redirect('core:ar-products', slug=slug)
    return redirect('core:ar-products', slug=slug)


@login_required
def en_remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[0]
            if order_item.quantity > 0:
                order_item.quantity -= 1
                order_item.save()
                messages.info(request, 'This item was removed from your cart.')

            else:
                messages.info(request, 'This item does not exist in your cart.')
                return redirect('core:en-products', slug=slug)
        else:
            messages.info(request, 'This item does not exist in your cart.')
            return redirect('core:en-products', slug=slug)
    else:
        messages.info(request, 'You do not have an active order!')
        return redirect('core:en-products', slug=slug)
    return redirect('core:en-products', slug=slug)


@login_required
def ar_add_item_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(item=item, user=request.user, ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, 'تم تحديث كميه هذا المنتج فى العربه.')
        else:
            messages.info(request, 'تمت اضافة هذا المنتج الى العربة.')
            order.items.add(order_item)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, 'تمت اضافة هذا المنتج الى العربة.')
    return redirect('core:ar-order-summary')


@login_required
def en_add_item_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(item=item, user=request.user, ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, 'This item quantity was updated in your cart.')
        else:
            messages.info(request, 'This item was added to your cart.')
            order.items.add(order_item)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, 'This item was added to your cart.')
    return redirect('core:en-order-summary')


@login_required
def ar_remove_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
                messages.info(request, 'تمت ازالة هذا المنتج من العربة.')

            else:
                order.items.remove(order_item)
                messages.info(request, 'هذا المنتج غير موجود فى العربة')
                return redirect('core:ar-order-summary')
        else:
            messages.info(request, 'هذا المنتج غير موجود فى العرية.')
            return redirect('core:ar-order-summary')
    else:
        messages.info(request, 'عفوا ليس لديك طلب.')
        return redirect('core:ar-order-summary')
    return redirect('core:ar-order-summary')


@login_required
def en_remove_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
                messages.info(request, 'This item was removed from your cart.')

            else:
                order.items.remove(order_item)
                messages.info(request, 'This item does not exist in your cart.')
                return redirect('core:en-order-summary')
        else:
            messages.info(request, 'This item does not exist in your cart.')
            return redirect('core:en-order-summary')
    else:
        messages.info(request, 'You do not have an active order!')
        return redirect('core:en-order-summary')
    return redirect('core:en-order-summary')


@login_required
def ar_remove_all_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[0]
            if order_item.quantity > 0:
                order.items.remove(order_item)
                order_item.save()
                messages.info(request, 'تمت ازالة هذه المنتجات من العربة.')

            else:
                messages.info(request, 'هذا المنتج غير موجود بالعربة.')
                return redirect('core:ar-order-summary')
        else:
            messages.info(request, 'هذا المنتج غير موجود بالعربة.')
            return redirect('core:ar-order-summary')
    else:
        messages.info(request, 'عفوالا يوجد لديك طلب')
        return redirect('core:ar-order-summary')
    return redirect('core:ar-order-summary')


@login_required
def en_remove_all_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[0]
            if order_item.quantity > 0:
                order.items.remove(order_item)
                order_item.save()
                messages.info(request, 'These items were removed from your cart.')

            else:
                messages.info(request, 'This item does not exist in your cart.')
                return redirect('core:en-order-summary')
        else:
            messages.info(request, 'This item does not exist in your cart.')
            return redirect('core:en-order-summary')
    else:
        messages.info(request, 'You do not have an active order!')
        return redirect('core:en-order-summary')
    return redirect('core:en-order-summary')


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon

    except ObjectDoesNotExist:
        messages.info(request, 'This coupon does not exist')
        return redirect('core:checkout')


class ArAddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(user=self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, 'Successfully added coupon.')
                return redirect('core:ar-checkout')

            except ObjectDoesNotExist:
                messages.info(self.request, 'You do not have an active order!')
                return redirect('core:ar-checkout')


class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(user=self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, 'Successfully added coupon.')
                return redirect('core:en-checkout')

            except ObjectDoesNotExist:
                messages.info(self.request, 'You do not have an active order!')
                return redirect('core:en-checkout')


class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, 'request_refund.html', context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            customer_name = form.cleaned_data('customer_name')
            phone = form.cleaned_data('phone')
            email = form.cleaned_data.get('email')

            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.customer_name = customer_name
                refund.phone = phone
                refund.email = email
                refund.save()

                messages.info(self.request, 'Your request was received')
                return redirect('core:request-refund')

            except ObjectDoesNotExist:
                messages.info(self.request, 'This order does not exist')
                return redirect('core:request-refund')


@login_required
def ar_deliver_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[0]

            if order_item.quantity > 0:
                order.being_delivered = True
                order.ordered = True
                order.save()
                messages.info(request, 'سوف تشحن هذه البضائع قريبا')
                return redirect('/ar/')

            else:
                messages.info(request, 'هذا المنتج غير موجود بالعربه')
                return redirect('core:ar-delivery')
        else:
            messages.info(request, 'هذا المنتج غير موجود بالعربه')
            return redirect('core:ar-delivery')
    else:
        messages.info(request, 'عفوا لا يوجد لديك طلب')
        return redirect('core:ar-delivery')
    return redirect('core:ar-delivery')


@login_required
def en_deliver_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[0]

            if order_item.quantity > 0:
                order.being_delivered = True
                order.ordered = True
                order.save()
                messages.info(request, 'These items were delivered.')
                return redirect('/en/')

            else:
                messages.info(request, 'This item does not exist in your cart.')
                return redirect('core:en-delivery')
        else:
            messages.info(request, 'This item does not exist in your cart.')
            return redirect('core:en-delivery')
    else:
        messages.info(request, 'You do not have an active order!')
        return redirect('core:en-delivery')
    return redirect('core:en-delivery')
