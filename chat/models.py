from django.db import models
from django.conf import settings


class Conversation(models.Model):
    """Model for both direct and group conversations."""
    name = models.CharField(max_length=255, blank=True, null=True)
    is_group = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # For group chats
    description = models.TextField(blank=True)
    avatar = models.ImageField(
        upload_to='group_avatars/', null=True, blank=True)

    # If a chatbot is added to the conversation
    has_ai = models.BooleanField(default=False)

    AI_PROVIDERS = [
        ('OPEN_AI', 'OpenAI'),
        ('ANTHROPIC', 'Anthropic'),
    ]

    ai_provider = models.CharField(
        max_length=100,
        choices=AI_PROVIDERS,
        blank=True,
        null=True
    )

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.name or f"Conversation {self.id}"


class Participant(models.Model):
    """Users who are part of a conversation."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name='participants')
    is_admin = models.BooleanField(default=False)  # For group chats
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'conversation']

    def __str__(self):
        return f"{self.user.username} in {self.conversation}"


class Message(models.Model):
    """Encrypted messages within a conversation."""
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    encrypted_content = models.TextField()  # Encrypted message content
    is_ai_generated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # These fields are for message metadata and don't contain sensitive content
    has_attachment = models.BooleanField(default=False)
    attachment_type = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Message {self.id} in {self.conversation}"


class Attachment(models.Model):
    """Files attached to messages."""
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE, related_name='attachments')
    encrypted_file = models.FileField(upload_to='attachments/')
    file_type = models.CharField(max_length=100)
    file_name = models.CharField(max_length=255)

    def __str__(self):
        return f"Attachment {self.id} for Message {self.message.id}"


class Reaction(models.Model):
    """Emoji reactions to messages."""
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    reaction = models.CharField(max_length=10)  # Unicode emoji
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['message', 'user', 'reaction']

    def __str__(self):
        return f"{self.reaction} by {self.user.username}"


class EncryptionKey(models.Model):
    """Public keys for end-to-end encryption."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='encryption_key')
    public_key = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Key for {self.user.username}"
