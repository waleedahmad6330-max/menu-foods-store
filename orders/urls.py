from django.urls import path
from . import views

urlpatterns = [
    path('cart/', views.cart_page, name='cart_page'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('increase/<int:product_id>/', views.increase_cart, name='increase_cart'),
    path('decrease/<int:product_id>/', views.decrease_cart, name='decrease_cart'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    
    path('payment-success/<int:order_id>/', views.payment_success, name='payment_success'),
    path('my-orders/', views.my_orders, name='my_orders'),
]