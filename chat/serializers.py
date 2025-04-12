from rest_framework import serializers
from .models import Conversation, Message, Participant, Reaction, Attachment
from django.contrib.auth import get_user_model

from accounts.serializers import UserSerializer

User = get_user_model()



class ParticipantSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Participant
        fields = ['id', 'user', 'is_admin', 'joined_at']

class ReactionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Reaction
        fields = ['id', 'user', 'reaction', 'created_at']

class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['id', 'file_type', 'file_name', 'encrypted_file']

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    reactions = ReactionSerializer(many=True, read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'sender', 'encrypted_content', 'created_at', 
                 'is_ai_generated', 'has_attachment', 'attachment_type',
                 'reactions', 'attachments']

class ConversationSerializer(serializers.ModelSerializer):
    participants = ParticipantSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ['id', 'name', 'is_group', 'created_at', 'updated_at',
                 'description', 'avatar',
                 'participants', 'last_message']
    
    def get_last_message(self, obj):
        message = obj.messages.order_by('-created_at').first()
        if message:
            return MessageSerializer(message).data
        return None