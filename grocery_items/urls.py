from django.urls import path
from . import views

urlpatterns = [
    # General
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('category/<int:category_id>/', views.category_view, name='category_view'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('about/', views.about, name='about'),

    # Cart
    path('cart/', views.cart_page, name='cart_page'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('increase-cart/<int:product_id>/', views.increase_cart, name='increase_cart'),
    path('decrease-cart/<int:product_id>/', views.decrease_cart, name='decrease_cart'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),

    # Checkout
    path('checkout/', views.checkout, name='checkout'),
    path('success/', views.success, name='success'),
    path('cancel/', views.cancel, name='cancel'),

    # Auth
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('membership/', views.membership_signup, name='membership'),
    path('membership-success/', views.membership_success, name='membership_success'),
    path('welcome-member/', views.welcome_member, name='welcome_member'),
    path('my-orders/', views.my_orders, name='my_orders'),

    # Admin Portal
    path('portal/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('portal/users/', views.admin_users, name='admin_users'),
    path('portal/memberships/', views.admin_memberships, name='admin_memberships'),
    path('portal/orders/', views.admin_all_orders, name='admin_all_orders'),
    path('portal/order/<int:order_id>/', views.admin_order_detail, name='admin_order_detail'),
    # Product Management
    path('portal/products/', views.admin_products_list, name='admin_products_list'), # New List
    path('portal/add-product/', views.admin_add_product, name='admin_add_product'),
    path('portal/edit-product/<int:pid>/', views.admin_edit_product, name='admin_edit_product'), # New Edit
    path('portal/delete-product/<int:pid>/', views.admin_delete_product, name='admin_delete_product'), # New Delete

    # Category Management
    path('portal/categories/', views.admin_categories_list, name='admin_categories_list'), # New List
    path('portal/add-category/', views.admin_add_category, name='admin_add_category'),
    path('portal/edit-category/<int:cid>/', views.admin_edit_category, name='admin_edit_category'), # New Edit
    path('portal/delete-category/<int:cid>/', views.admin_delete_category, name='admin_delete_category'), # New Delete
]