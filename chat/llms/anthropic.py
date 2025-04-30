import logging
import requests
from chat.llms.base import AIProviderStrategy


logger = logging.getLogger(__name__)

class AnthropicStrategy(AIProviderStrategy):
    def generate_response(self, message, api_key):
        try:
            headers = {
                "anthropic-version": "2023-06-01",
                "x-api-key": api_key,
                "Content-Type": "application/json"
            }
            data = {
                "messages": [{"role": "user", "content": message}],
                "model": "claude-3-7-sonnet-20250219",
                "max_tokens": 1024,
            }
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data,
                timeout=10
            )
            if response.status_code == 200:
                return response.json()['content'][0]['text']
            logger.warning("Anthropic API failed: %s", response.text)
            return response.json()['error']['message']
        except Exception as e:
            logger.exception("Error calling Anthropic: %s", str(e))
        return None