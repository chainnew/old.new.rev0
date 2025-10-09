"""
OpenRouter client with API key rotation for HECTIC SWARM
Supports multiple models: grok-beta, claude-3.5, gpt-4, etc.
"""
import os
import random
from typing import List, Optional
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential


class OpenRouterClient:
    """
    OpenRouter API client with:
    - 3 API key rotation (load balancing)
    - Retry logic
    - OpenAI-compatible interface
    """
    
    def __init__(self):
        # Load 3 API keys from env
        self.api_keys = [
            os.getenv('OPENROUTER_API_KEY1'),
            os.getenv('OPENROUTER_API_KEY2'),
            os.getenv('OPENROUTER_API_KEY3'),
        ]
        
        # Filter out None values
        self.api_keys = [key for key in self.api_keys if key]
        
        if not self.api_keys:
            raise ValueError("No OpenRouter API keys found in environment")
        
        print(f"✅ Loaded {len(self.api_keys)} OpenRouter API keys")
        
        # OpenRouter endpoint
        self.base_url = "https://openrouter.ai/api/v1"
        
        # App identification (optional but recommended)
        self.app_name = os.getenv('NEXT_PUBLIC_APP_URL', 'http://localhost:3000')
    
    def _get_client(self) -> AsyncOpenAI:
        """Get client with random API key (load balancing)"""
        api_key = random.choice(self.api_keys)
        
        return AsyncOpenAI(
            api_key=api_key,
            base_url=self.base_url,
            default_headers={
                "HTTP-Referer": self.app_name,
                "X-Title": "HECTIC SWARM"
            }
        )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def chat_completion(
        self,
        messages: List[dict],
        model: str = "x-ai/grok-4-fast",  # Grok 4 Fast
        max_tokens: int = 4096,
        temperature: float = 0.7,
        stream: bool = False,
        **kwargs
    ):
        """
        Chat completion with retry logic
        
        Using: x-ai/grok-4-fast
        - Fast inference
        - Cost-effective
        - Great for code generation
        """
        client = self._get_client()
        
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=stream,
            **kwargs
        )
        
        return response
    
    async def generate_embedding(self, text: str, model: str = "openai/text-embedding-3-small"):
        """Generate embeddings for RAG"""
        client = self._get_client()
        
        response = await client.embeddings.create(
            model=model,
            input=text
        )
        
        return response.data[0].embedding


# Singleton instance
_client_instance: Optional[OpenRouterClient] = None

def get_openrouter_client() -> OpenRouterClient:
    """Get or create singleton client"""
    global _client_instance
    if _client_instance is None:
        _client_instance = OpenRouterClient()
    return _client_instance
