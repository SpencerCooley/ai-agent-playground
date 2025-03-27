from langchain.callbacks.base import BaseCallbackHandler
import redis
import os
from dotenv import load_dotenv

load_dotenv()

# Redis client
redis_client = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

# Model configuration
MODEL_CONFIG = {
    "o3-mini": {
        "provider": "openai",
        "model_name": "o3-mini",
        "api_key_env": "OPENAI_API_KEY",
        "default": True
    },
    "o3-max": {
        "provider": "openai",
        "model_name": "gpt-4",
        "api_key_env": "OPENAI_API_KEY"
    }
}

def get_default_model() -> str:
    for model_name, config in MODEL_CONFIG.items():
        if config.get("default", False):
            return model_name
    raise ValueError("No default model configured")

class StreamingCallbackHandler(BaseCallbackHandler):
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.last_token = None

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        if token == self.last_token:
            return
        self.last_token = token
        redis_client.publish(f"task:{self.task_id}", token)

    def on_llm_end(self, response, **kwargs) -> None:
        redis_client.publish(f"task:{self.task_id}", "[DONE]") 