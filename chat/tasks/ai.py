import logging

from celery import shared_task
from django.contrib.auth import get_user_model
from chat.models import Conversation, Message
from chat.utils import send_fallback_message
from chat.llms.openai import get_openai_response
from chat.llms.anthropic import get_anthropic_response

User = get_user_model()
logger = logging.getLogger(__name__)


@shared_task
def process_ai_message_task(conversation_id, message_content, user_id, ai_provider, api_key):
    """
    Processes an LLM response and sends it as a bot user into the conversation.
    """
    logger.info("[AI] Starting AI task with %s for conversation %d for user %d", ai_provider, conversation_id, user_id)

    bot_username = 'chatgpt' if ai_provider == 'openai' else 'claude'

    try:
        bot_user = User.objects.get(username=bot_username, is_bot=True)
    except User.DoesNotExist:
        return f"Bot user @{bot_username} not found"

    try:
        conversation = Conversation.objects.get(id=conversation_id)
    except Conversation.DoesNotExist:
        return f"Conversation {conversation_id} not found"

    if not api_key:
        return send_fallback_message(bot_user, conversation, "Sorry, I could not find an API Key.")

    if ai_provider == 'openai':
        response = get_openai_response(message_content, api_key)
    elif ai_provider == 'anthropic':
        response = get_anthropic_response(message_content, api_key)
    else:
        return send_fallback_message(bot_user, conversation, f"Unknown AI provider: {ai_provider}")

    if not response:
        return send_fallback_message(bot_user, conversation, "Hmm, I couldn't generate a response. Please try again.")

    Message.objects.create(
        conversation=conversation,
        sender=bot_user,
        encrypted_content=response,
        is_ai_generated=True
    )
    return "AI response sent"
