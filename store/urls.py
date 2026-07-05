from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('store/', views.store, name='store'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.place_order, name='place_order'),
    path('order/complete/<int:order_id>/', views.order_complete, name='order_complete'),
    path('order/failed/<int:order_id>/', views.payment_failed, name='payment_failed'),
    path('search/', views.search_view, name='search'),
    path('signin/', views.signin_view, name='signin'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # Khalti
    path('payment/khalti/<int:order_id>/', views.khalti_pay, name='khalti_pay'),
    path('payment/khalti/callback/', views.khalti_callback, name='khalti_callback'),

    # eSewa
    path('payment/esewa/<int:order_id>/', views.esewa_pay, name='esewa_pay'),
    path('payment/esewa/success/', views.esewa_callback_success, name='esewa_callback_success'),
    path('payment/esewa/failure/<int:order_id>/', views.esewa_callback_failure, name='esewa_callback_failure'),

    # Card
    path('payment/card/<int:order_id>/', views.card_pay, name='card_pay'),

    # Fonepay
    path('payment/fonepay/<int:order_id>/', views.fonepay_pay, name='fonepay_pay'),
    path('payment/fonepay/callback/<int:order_id>/', views.fonepay_callback, name='fonepay_callback'),
]
