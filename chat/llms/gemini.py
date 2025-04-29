import logging
import requests
from chat.llms.base import AIProviderStrategy

logger = logging.getLogger(__name__)

class GeminiStrategy(AIProviderStrategy):
    def generate_response(self, message, api_key):
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-lite:generateContent?key={api_key}"
            headers = {
                "Content-Type": "application/json",
            }
            data = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": message
                            }
                        ]
                    }
                ]
            }

            response = requests.post(url, headers=headers, json=data, timeout=10)

            if response.status_code == 200:
                return response.json()['candidates'][0]['content']['parts'][0]['text']

            logger.warning("Gemini API failed: %s", response.text)

        except Exception as e:
            logger.exception("Error calling Gemini API: %s", str(e))

        return None
