import requests
from celery import shared_task
from django.contrib.auth import get_user_model

from chat.utils import decrypt_api_key
from chat.models import Message, Conversation

User = get_user_model()

@shared_task
def process_ai_message(conversation_id, message_content, user_id, ai_provider, api_key_encrypted):
    """
    Process a message intended for an AI chatbot and get a response.
    This runs asynchronously with Celery.
    """

    # Decrypt the API key
    api_key = decrypt_api_key(api_key_encrypted)
    if not api_key:
        return None

    # Get AI response based on provider
    if ai_provider == 'openai':
        response = get_openai_response(message_content, api_key)
    elif ai_provider == 'anthropic':
        response = get_anthropic_response(message_content, api_key)
    else:
        return None

    if not response:
        return None

    # Create AI message in the database
    user = User.objects.get(id=user_id)
    conversation = Conversation.objects.get(id=conversation_id)

    Message.objects.create(
        conversation=conversation,
        sender=user,  # AI messages are associated with the user who owns the API key
        encrypted_content=response,  # In a real app, the frontend would encrypt this
        is_ai_generated=True
    )

    return True


def get_openai_response(message, api_key):
    """Get a response from OpenAI's API"""
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": message}],
            "max_tokens": 150
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=10
        )

        if response.status_code == 200:
            response_data = response.json()
            return response_data['choices'][0]['message']['content']
        return None

    except Exception as e:
        print(f"OpenAI API error: {str(e)}")
        return None


def get_anthropic_response(message, api_key):
    """Get a response from Anthropic's API"""
    try:
        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json"
        }

        data = {
            "prompt": f"\n\nHuman: {message}\n\nAssistant:",
            "model": "claude-v1",
            "max_tokens_to_sample": 150,
            "stop_sequences": ["\n\nHuman:"]
        }

        response = requests.post(
            "https://api.anthropic.com/v1/complete",
            headers=headers,
            json=data,
            timeout=10
        )

        if response.status_code == 200:
            response_data = response.json()
            return response_data['completion']
        return None

    except Exception as e:
        print(f"Anthropic API error: {str(e)}")
        return None
