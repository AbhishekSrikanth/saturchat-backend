from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from encrypted_fields.fields import EncryptedCharField


class User(AbstractUser):
    """Custom User model with additional fields for SaturChat."""
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    is_online = models.BooleanField(default=False)
    last_activity = models.DateTimeField(null=True, blank=True)
    is_bot = models.BooleanField(default=False)

    # Store encrypted API keys for external AI services
    openai_api_key = EncryptedCharField(max_length=255, blank=True, null=True)
    anthropic_api_key = EncryptedCharField(max_length=255, blank=True, null=True)
    gemini_api_key = EncryptedCharField(max_length=255, blank=True, null=True)


    def __str__(self):
        return str(self.username)
