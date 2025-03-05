from fastapi import HTTPException
from typing import Optional, Literal
from langchain_openai import ChatOpenAI
from langchain_xai import ChatXAI
from langchain.chat_models.base import BaseChatModel
import os
from dotenv import load_dotenv
from enum import Enum

# Load environment variables
load_dotenv()

PROVIDER_CONFIGS = {
    "openai": {
        "models": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview", "o3-mini"],
        "class": ChatOpenAI,
        "default_model": "gpt-3.5-turbo"
    },
    "xai": {
        "models": ["grok-beta"],
        "class": ChatXAI,
        "default_model": "grok-beta"
    }
}

class ProviderType(str, Enum):
    OPENAI = "openai"

def get_provider_from_model(model_name: str) -> tuple[str, dict]:
    """Determine the provider based on the model name."""
    for provider, config in PROVIDER_CONFIGS.items():
        if model_name in config["models"]:
            return provider, config
    raise HTTPException(
        status_code=400,
        detail=f"Model {model_name} not supported. Available models: " + 
        ", ".join([m for c in PROVIDER_CONFIGS.values() for m in c["models"]])
    )

async def use_llm(model: Optional[str] = 'o3-mini', 
                 provider: str = ProviderType.OPENAI, 
                 temperature: float = 0.7) -> BaseChatModel:
    """
    Factory function to create LLM instances with streaming support.
    """
    if provider == ProviderType.OPENAI:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set in environment variables")
        
        # Validate model
        model_name = model or PROVIDER_CONFIGS["openai"]["default_model"]
        if model_name not in PROVIDER_CONFIGS["openai"]["models"]:
            raise ValueError(f"Model {model_name} not supported for OpenAI provider")

        return ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            api_key=api_key,  # Use api_key instead of openai_api_key for clarity
            streaming=True,   # Enable streaming
        )
    else:
        raise ValueError(f"Unsupported provider: {provider}")