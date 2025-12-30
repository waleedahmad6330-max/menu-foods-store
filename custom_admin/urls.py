from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('orders/', views.admin_all_orders, name='admin_all_orders'),
    path('order/<int:order_id>/', views.admin_order_detail, name='admin_order_detail'),
    path('products/', views.admin_products_list, name='admin_products_list'),
    path('add-product/', views.admin_add_product, name='admin_add_product'),
    path('edit-product/<int:pid>/', views.admin_edit_product, name='admin_edit_product'),
    path('delete-product/<int:pid>/', views.admin_delete_product, name='admin_delete_product'),
    path('categories/', views.admin_categories_list, name='admin_categories_list'),
    path('add-category/', views.admin_add_category, name='admin_add_category'),
    path('edit-category/<int:cid>/', views.admin_edit_category, name='admin_edit_category'),
    path('delete-category/<int:cid>/', views.admin_delete_category, name='admin_delete_category'),
    path('users/', views.admin_users, name='admin_users'),
    path('memberships/', views.admin_memberships, name='admin_memberships'),
    path('vendors/', views.admin_vendors_list, name='admin_vendors_list'),
    path('add-vendor/', views.admin_add_vendor, name='admin_add_vendor'),
    path('vendor/<int:vid>/', views.admin_vendor_detail, name='admin_vendor_detail'),
]
