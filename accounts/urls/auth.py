from django.urls import path, include

urlpatterns = [
    # dj-rest-auth endpoints (register + social login)
    path('', include('dj_rest_auth.urls')),
    path('register/', include('dj_rest_auth.registration.urls')),
]