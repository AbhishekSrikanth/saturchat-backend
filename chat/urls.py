from rest_framework_nested import routers
from django.urls import path, include
from . import views

router = routers.SimpleRouter()
router.register(r'conversations', views.ConversationViewSet, basename='conversation')

# Nested routes for messages within conversations
conversation_router = routers.NestedSimpleRouter(router, r'conversations', lookup='conversation')
conversation_router.register(r'messages', views.MessageViewSet, basename='conversation-messages')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(conversation_router.urls)),
]