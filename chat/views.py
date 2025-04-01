from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Q
from chat.models import Conversation, Message, Participant, Reaction, EncryptionKey
from chat.serializers import (
    ConversationSerializer, MessageSerializer, UserSerializer,
    ParticipantSerializer, ReactionSerializer
)

User = get_user_model()


class IsParticipant(permissions.BasePermission):
    """Permission to check if user is a participant in a conversation."""

    def has_object_permission(self, request, view, obj):
        return Participant.objects.filter(
            user=request.user,
            conversation=obj
        ).exists()


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '')
        if len(query) < 3:
            return Response({'error': 'Search query must be at least 3 characters'},
                            status=status.HTTP_400_BAD_REQUEST)

        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).exclude(id=request.user.id)

        serializer = self.get_serializer(users, many=True)
        return Response(serializer.data)


class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipant]

    def get_queryset(self):
        return Conversation.objects.filter(
            participants__user=self.request.user
        ).distinct()

    def create(self, request, *args, **kwargs):
        is_group = request.data.get('is_group', False)
        participant_ids = request.data.get('participants', [])

        # For direct messages, ensure we don't create duplicates
        if not is_group and len(participant_ids) == 1:
            other_user_id = participant_ids[0]

            # Check if conversation already exists
            existing_conversation = Conversation.objects.filter(
                is_group=False,
                participants__user_id=request.user.id
            ).filter(
                participants__user_id=other_user_id
            ).first()

            if existing_conversation:
                serializer = self.get_serializer(existing_conversation)
                return Response(serializer.data)

        # Create new conversation
        conversation = Conversation.objects.create(
            name=request.data.get('name'),
            is_group=is_group,
            description=request.data.get('description', ''),
            has_ai=request.data.get('has_ai', False),
            ai_provider=request.data.get('ai_provider')
        )

        # Add participants
        Participant.objects.create(
            conversation=conversation,
            user=request.user,
            is_admin=True
        )

        for user_id in participant_ids:
            try:
                user = User.objects.get(id=user_id)
                Participant.objects.create(
                    conversation=conversation,
                    user=user
                )
            except User.DoesNotExist:
                pass

        serializer = self.get_serializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        conversation = self.get_object()
        user_id = request.data.get('user_id')

        try:
            user = User.objects.get(id=user_id)
            # Check if user is already a participant
            if Participant.objects.filter(conversation=conversation, user=user).exists():
                return Response({'error': 'User is already a participant'},
                                status=status.HTTP_400_BAD_REQUEST)

            Participant.objects.create(
                conversation=conversation,
                user=user
            )

            return Response({'message': 'User added successfully'})
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def remove_participant(self, request, pk=None):
        conversation = self.get_object()
        user_id = request.data.get('user_id')

        # Verify requester is admin
        requester_participant = Participant.objects.get(
            conversation=conversation,
            user=request.user
        )

        if not requester_participant.is_admin:
            return Response({'error': 'Only admins can remove participants'},
                            status=status.HTTP_403_FORBIDDEN)

        try:
            participant = Participant.objects.get(
                conversation=conversation,
                user_id=user_id
            )
            participant.delete()
            return Response({'message': 'User removed successfully'})
        except Participant.DoesNotExist:
            return Response({'error': 'User is not a participant'},
                            status=status.HTTP_404_NOT_FOUND)


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipant]

    def get_queryset(self):
        conversation_id = self.kwargs.get('conversation_pk')
        return Message.objects.filter(conversation_id=conversation_id)

    def create(self, request, conversation_pk=None):
        # Create message
        message = Message.objects.create(
            conversation_id=conversation_pk,
            sender=request.user,
            encrypted_content=request.data.get('encrypted_content'),
            has_attachment=request.data.get('has_attachment', False),
            attachment_type=request.data.get('attachment_type')
        )

        serializer = self.get_serializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def add_reaction(self, request, pk=None, conversation_pk=None):
        message = self.get_object()
        reaction = request.data.get('reaction')

        # Create or update reaction
        Reaction.objects.update_or_create(
            message=message,
            user=request.user,
            reaction=reaction
        )

        return Response({'message': 'Reaction added'})

    @action(detail=True, methods=['post'])
    def remove_reaction(self, request, pk=None, conversation_pk=None):
        message = self.get_object()
        reaction = request.data.get('reaction')

        try:
            reaction_obj = Reaction.objects.get(
                message=message,
                user=request.user,
                reaction=reaction
            )
            reaction_obj.delete()
            return Response({'message': 'Reaction removed'})
        except Reaction.DoesNotExist:
            return Response({'error': 'Reaction not found'}, status=status.HTTP_404_NOT_FOUND)


class EncryptionKeyViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request):
        # Store user's public key
        EncryptionKey.objects.update_or_create(
            user=request.user,
            defaults={'public_key': request.data.get('public_key')}
        )
        return Response({'message': 'Key stored successfully'})

    def retrieve(self, request, pk=None):
        try:
            key = EncryptionKey.objects.get(user_id=pk)
            return Response({'user_id': pk, 'public_key': key.public_key})
        except EncryptionKey.DoesNotExist:
            return Response({'error': 'Key not found'}, status=status.HTTP_404_NOT_FOUND)
