from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('join-club/', views.membership_signup, name='membership'),
    path('membership-success/', views.membership_success, name='membership_success'),
]