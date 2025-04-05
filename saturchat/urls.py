from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # API routes
    path('api/', include('chat.urls')),
    path('api/auth/', include('accounts.urls')),  # JWT + OAuth routes
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
