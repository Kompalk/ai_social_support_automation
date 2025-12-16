"""Base agent class with common functionality."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import httpx
from config.settings import settings
import logging

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all AI agents."""
    
    def __init__(self, name: str):
        self.name = name
        self.ollama_base_url = settings.ollama_base_url
        self.ollama_model = settings.ollama_model
    
    def call_llm(self, prompt: str, model: Optional[str] = None) -> str:
        """Call local LLM via Ollama."""
        try:
            model = model or self.ollama_model
            response = httpx.post(
                f"{self.ollama_base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=60.0
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            return f"Error: {str(e)}"
    
    def call_llm_with_context(self, system_prompt: str, user_prompt: str, 
                              model: Optional[str] = None) -> str:
        """Call LLM with system and user prompts."""
        full_prompt = f"{system_prompt}\n\nUser: {user_prompt}\n\nAssistant:"
        return self.call_llm(full_prompt, model)
    
    @abstractmethod
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent logic. Must be implemented by subclasses."""
        pass
    
    def log_action(self, action: str, details: Dict[str, Any]):
        """Log agent action for observability."""
        logger.info(f"[{self.name}] {action}: {details}")

