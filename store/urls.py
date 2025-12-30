from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('category/<int:category_id>/', views.category_view, name='category_view'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('about/', views.about, name='about'),
]