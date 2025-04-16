from abc import ABC, abstractmethod

class AIProviderStrategy(ABC):
    @abstractmethod
    def generate_response(self, message: str, api_key: str) -> str:
        pass
