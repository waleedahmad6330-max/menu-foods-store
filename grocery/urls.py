from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --- YEH LINE ZAROORI HAI (Google Auth ke liye) ---
    path('accounts/', include('allauth.urls')), 
    
    # Aapki App ke URLs
    path('', include('grocery_items.urls')), 
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)