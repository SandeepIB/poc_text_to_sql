"""LLM client configuration and initialization."""

import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class LLMConfig:
    """Configuration for LLM client."""
    provider: str = "openai"  # openai, anthropic, local
    model: str = "gpt-3.5-turbo"
    api_key: Optional[str] = None
    base_url: Optional[str] = None  # For local models
    temperature: float = 0.1
    max_tokens: int = 500


class LLMClientFactory:
    """Factory for creating LLM clients."""
    
    @staticmethod
    def create_client(config: LLMConfig = None):
        """Create LLM client based on configuration."""
        if config is None:
            config = LLMConfig()
        
        # Try OpenAI first
        if config.provider == "openai":
            return LLMClientFactory._create_openai_client(config)
        
        # Try local model (Ollama, etc.)
        elif config.provider == "local":
            return LLMClientFactory._create_local_client(config)
        
        # No LLM available
        return None
    
    @staticmethod
    def _create_openai_client(config: LLMConfig):
        """Create OpenAI client."""
        try:
            from openai import OpenAI
            
            api_key = config.api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("❌ OpenAI API key not found")
                return None
            
            # Test the client
            client = OpenAI(api_key=api_key)
            try:
                # Quick test call
                client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "test"}],
                    max_tokens=1
                )
                print("✅ OpenAI client working")
                return client
            except Exception as e:
                print(f"❌ OpenAI API test failed: {e}")
                return None
                
        except ImportError:
            print("❌ OpenAI library not installed: pip install openai")
            return None
        except Exception as e:
            print(f"❌ Failed to create OpenAI client: {e}")
            return None
    
    @staticmethod
    def _create_local_client(config: LLMConfig):
        """Create local model client (Ollama, etc.)."""
        try:
            from openai import OpenAI
            import requests
            
            # Use OpenAI-compatible API for local models
            base_url = config.base_url or "http://localhost:11434/v1"
            
            # Test if Ollama is running
            try:
                response = requests.get("http://localhost:11434/api/tags", timeout=2)
                if response.status_code != 200:
                    print("❌ Ollama service not running")
                    return None
                    
                models = response.json().get('models', [])
                if not models:
                    print("❌ No models available in Ollama")
                    return None
                    
                print(f"✅ Ollama running with {len(models)} models")
                
            except requests.exceptions.RequestException:
                print("❌ Cannot connect to Ollama service")
                return None
            
            return OpenAI(
                base_url=base_url,
                api_key="ollama"  # Dummy key for local
            )
        except Exception as e:
            print(f"❌ Failed to create local client: {e}")
            return None


def get_available_llm():
    """Get the first available LLM client."""
    configs = [
        LLMConfig(provider="openai", model="gpt-3.5-turbo"),
        LLMConfig(provider="local", model="llama2", base_url="http://localhost:11434/v1"),
    ]
    
    for config in configs:
        client = LLMClientFactory.create_client(config)
        if client:
            print(f"Using {config.provider} LLM: {config.model}")
            return client, config
    
    print("No LLM available, using rule-based fallback")
    return None, None