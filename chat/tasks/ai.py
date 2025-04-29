import logging

from celery import shared_task
from django.contrib.auth import get_user_model
from chat.models import Conversation, Message
from chat.utils import send_fallback_message
from chat.llms import AI_PROVIDERS

logger = logging.getLogger(__name__)

User = get_user_model()

@shared_task
def process_ai_message_task(conversation_id, message_content, user_id, ai_provider, api_key):
    """
    Processes an LLM response and sends it as a bot user into the conversation.
    """
    logger.info("[AI] Starting AI task with %s for conversation %d for user %d", ai_provider, conversation_id, user_id)

    try:
        bot_user = User.objects.get(id=user_id, is_bot=True)
    except User.DoesNotExist:
        return f"Bot user with ID {user_id} not found"

    try:
        conversation = Conversation.objects.get(id=conversation_id)
    except Conversation.DoesNotExist:
        return f"Conversation {conversation_id} not found"

    if not api_key:
        return send_fallback_message(bot_user, conversation, "Sorry, I could not find an API Key.")

    strategy = AI_PROVIDERS.get(ai_provider.lower())
    if not strategy:
        return send_fallback_message(bot_user, conversation, f"Unknown AI provider: {ai_provider}")
    
    recent_messages = Message.objects.filter(
        conversation=conversation
    ).order_by('-created_at')[:10][::-1]  # Reverse so oldest is first

    formatted_context = ""
    for msg in recent_messages:
        sender = msg.sender.username
        formatted_context += f"{sender}: {msg.content}\n"

    full_prompt = (
        "You're an AI participant in a group chat. "
        "Try to match the tone and context of the ongoing discussion. "
        "Respond appropriately, maintaining the social norms and the mood of the group.\n\n"
        "If you don't know the answer, say 'I don't know' or ask for clarification.\n\n"
        "If you've to generate code or JSON, do not exceed 80 chars per line.\n\n"
        "Do not send a huge chunk of text. So stick to a general group chat norms.\n\n"
        "Here is the recent conversation context:\n"
        f"{formatted_context}\n"
        f"{bot_user.username}:"
    )

    response = strategy.generate_response(full_prompt, api_key)

    if not response:
        return send_fallback_message(bot_user, conversation, "Hmm, I couldn't generate a response. Please try again.")

    Message.objects.create(
        conversation=conversation,
        sender=bot_user,
        content=response,
        is_ai_generated=True
    )
    return "AI response sent"
