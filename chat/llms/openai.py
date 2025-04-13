import logging
import requests


logger = logging.getLogger(__name__)

def get_openai_response(message, api_key):
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
            return response.json()['choices'][0]['message']['content']
        logger.warning("OpenAI API failed: %s", response.text)
    except Exception as e:
        logger.exception("Error calling OpenAI: %s", str(e))
    return None
