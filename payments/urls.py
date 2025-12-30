from django.urls import path
from . import views

urlpatterns = [
    path('success/', views.success, name='success'),
    path('cancel/<int:order_id>/', views.cancel, name='cancel'),
]