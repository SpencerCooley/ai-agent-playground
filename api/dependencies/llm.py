from fastapi import HTTPException
from typing import Optional, Literal
from langchain_openai import ChatOpenAI
from langchain_xai import ChatXAI
from langchain.chat_models.base import BaseChatModel
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

PROVIDER_CONFIGS = {
    "openai": {
        "models": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview"],
        "env_key": "OPENAI_API_KEY",
        "class": ChatOpenAI,
        "default_model": "gpt-3.5-turbo"
    },
    "xai": {
        "models": ["grok-beta"],
        "env_key": "XAI_API_KEY",
        "class": ChatXAI,
        "default_model": "grok-beta"
    }
}

ProviderType = Literal["openai", "xai"]

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

async def use_llm(
    model: Optional[str] = None,
    provider: Optional[ProviderType] = "openai",
    temperature: float = 0.7
) -> BaseChatModel:
    """
    Dependency to initialize and return a LangChain chat model instance.
    
    Parameters:
        model (str): The name of the model to use
        provider (str): The provider to use (openai or xai)
        temperature (float): Temperature for model responses
        
    Returns:
        BaseChatModel: Configured LangChain chat model instance
    
    Raises:
        HTTPException: If the model/provider is not supported or API key is missing
    """
    try:
        # If model is specified, determine provider from it
        if model:
            provider, config = get_provider_from_model(model)
        else:
            if provider not in PROVIDER_CONFIGS:
                raise HTTPException(
                    status_code=400,
                    detail=f"Provider {provider} not supported. Available providers: {list(PROVIDER_CONFIGS.keys())}"
                )
            config = PROVIDER_CONFIGS[provider]
            model = config["default_model"]

        # Verify API key exists
        api_key = os.getenv(config["env_key"])
        if not api_key:
            raise HTTPException(
                status_code=500,
                detail=f"{config['env_key']} not found in environment variables"
            )

        # Initialize model with provider-specific configuration
        if provider == "openai":
            return ChatOpenAI(
                model_name=model,
                temperature=temperature,
                api_key=api_key
            )
        else:  # xai
            return ChatXAI(
                model=model,
                temperature=temperature,
                xai_api_key=api_key
            )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error initializing chat model: {str(e)}"
        ) 