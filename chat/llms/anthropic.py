import logging
import requests
from chat.llms.base import AIProviderStrategy


logger = logging.getLogger(__name__)

class AnthropicStrategy(AIProviderStrategy):
    def generate_response(self, message, api_key):
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
                return response.json()['completion']
            logger.warning("Anthropic API failed: %s", response.text)
        except Exception as e:
            logger.exception("Error calling Anthropic: %s", str(e))
        return None
