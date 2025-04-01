from django.urls import path
from . import views

urlpatterns = [
    # User endpoints
    path('users/', views.UserViewSet.as_view(), name='user-list'),
    path('users/<int:pk>/', views.UserViewSet.as_view(), name='user-detail'),

    # Conversation endpoints
    path('conversations/', views.ConversationViewSet.as_view(),
         name='conversation-list'),
    path('conversations/<int:pk>/', views.ConversationViewSet.as_view(),
         name='conversation-detail'),

    # Message endpoints (nested under conversations)
    path('conversations/<int:conversation_pk>/messages/',
         views.MessageViewSet.as_view(), name='message-list'),
    path('conversations/<int:conversation_pk>/messages/<int:pk>/',
         views.MessageViewSet.as_view(), name='message-detail'),

    # Encryption key endpoints
    path('encryption-keys/', views.EncryptionKeyViewSet.as_view(),
         name='encryption-key-list'),
    path('encryption-keys/<int:pk>/',
         views.EncryptionKeyViewSet.as_view(), name='encryption-key-detail'),
]
