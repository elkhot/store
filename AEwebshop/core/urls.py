from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('ar/', views.ArHomeView.as_view(), name='ar-home'),
    path('en/', views.EnHomeView.as_view(), name='en-home'),
    path('ar/products/<slug>/', views.ArItemDetailView.as_view(), name='ar-products'),
    path('en/products/<slug>/', views.EnItemDetailView.as_view(), name='en-products'),
    path('ar/checkout/', views.ArCheckoutView.as_view(), name='ar-checkout'),
    path('en/checkout/', views.EnCheckoutView.as_view(), name='en-checkout'),
    path('ar/order-summary/', views.ArOrderSummaryView.as_view(), name='ar-order-summary'),
    path('en/order-summary/', views.EnOrderSummaryView.as_view(), name='en-order-summary'),
    path('ar/add-to-cart/<slug>/', views.ar_add_to_cart, name='ar-add-to-cart'),
    path('en/add-to-cart/<slug>/', views.en_add_to_cart, name='en-add-to-cart'),
    path('en/add-coupon/', views.AddCouponView.as_view(), name='add-en-coupon'),
    path('ar/add-coupon/', views.ArAddCouponView.as_view(), name='add-ar-coupon'),
    path('ar/remove-from-cart/<slug>/', views.ar_remove_from_cart, name='ar-remove-from-cart'),
    path('en/remove-from-cart/<slug>/', views.en_remove_from_cart, name='en-remove-from-cart'),
    path('ar/add-item-to-cart/<slug>/', views.ar_add_item_to_cart, name='ar-add-item-to-cart'),
    path('en/add-item-to-cart/<slug>/', views.en_add_item_to_cart, name='en-add-item-to-cart'),
    path('ar/remove-item-from-cart/<slug>/', views.ar_remove_item_from_cart, name='ar-remove-item-from-cart'),
    path('en/remove-item-from-cart/<slug>/', views.en_remove_item_from_cart, name='en-remove-item-from-cart'),
    path('ar/remove-all-from-cart/<slug>/', views.ar_remove_all_from_cart, name='ar-remove-all-from-cart'),
    path('en/remove-all-from-cart/<slug>/', views.en_remove_all_from_cart, name='en-remove-all-from-cart'),
    path('ar/payment/<ar_payment_option>/', views.ArPaymentView.as_view(), name='ar-payment'),
    path('payment/<en_payment_option>/', views.PaymentView.as_view(), name='en-payment'),
    path('request-refund/', views.RequestRefundView.as_view(), name='request-refund'),
    path('ar/delivery/<ar_payment_option>', views.ArDeliveryView.as_view(), name='ar-delivery'),
    path('en/delivery/<en_payment_option>', views.EnDeliveryView.as_view(), name='en-delivery'),
    path('en/deliver-from-cart/<slug>/', views.en_deliver_from_cart, name='en-deliver-from-cart'),
    path('ar/deliver-from-cart/<slug>/', views.ar_deliver_from_cart, name='ar-deliver-from-cart')
]
