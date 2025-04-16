from chat.llms.openai import OpenAIStrategy
from chat.llms.anthropic import AnthropicStrategy
from chat.llms.gemini import GeminiStrategy

# Registry for strategies
AI_PROVIDERS = {
    'openai': OpenAIStrategy(),
    'anthropic': AnthropicStrategy(),
    'gemini': GeminiStrategy(),
}
