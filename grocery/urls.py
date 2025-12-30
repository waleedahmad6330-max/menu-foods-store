from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('auth/', include('accounts.urls')),
    path('shop/', include('orders.urls')),      
    path('payments/', include('payments.urls')), 
    path('user/', include('user_dashboard.urls')), 
    path('portal/', include('custom_admin.urls')), 
    path('', include('store.urls')), 
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)