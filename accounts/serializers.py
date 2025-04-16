from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'avatar', 'bio',
            'openai_api_key', 'anthropic_api_key', 'gemini_api_key',
            'is_online', 'last_activity', 'is_bot',
        ]
        read_only_fields = ['id', 'is_online',
                            'last_activity', 'is_bot', 'username']
        extra_kwargs = {
            'openai_api_key': {'write_only': True},
            'anthropic_api_key': {'write_only': True},
            'gemini_api_key': {'write_only': True},
        }
