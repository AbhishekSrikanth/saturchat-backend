import logging
import requests
from chat.llms.base import AIProviderStrategy

logger = logging.getLogger(__name__)

class GeminiStrategy(AIProviderStrategy):
    def generate_response(self, message, api_key):
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "contents": [{"parts": [{"text": message}]}]
            }
            response = requests.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
                headers=headers,
                json=data,
                timeout=10
            )
            if response.status_code == 200:
                return response.json()['candidates'][0]['content']['parts'][0]['text']
            logger.warning("Gemini API failed: %s", response.text)
        except Exception as e:
            logger.exception("Error calling Gemini: %s", str(e))
        return None
