from celery_app.celery_app import celery_app
from langchain.chat_models import ChatOpenAI
from typing import Optional
from celery import states
from celery.utils.log import get_task_logger
from langchain.callbacks.base import BaseCallbackHandler
import os
from dotenv import load_dotenv
import redis
from openai import OpenAI  # Added for fallback

load_dotenv()
logger = get_task_logger(__name__)
redis_client = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

class StreamingCallbackHandler(BaseCallbackHandler):
    def __init__(self, task_id: str):
        self.task_id = task_id

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        logger.info(f"New token for task {self.task_id}: {token}")
        redis_client.publish(f"task:{self.task_id}", token)

    def on_llm_end(self, response, **kwargs) -> None:
        logger.info(f"LLM processing complete for task {self.task_id}")
        redis_client.publish(f"task:{self.task_id}", "[DONE]")

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

@celery_app.task(bind=True, name='celery_app.tasks.process_prompt')
def process_prompt(self, prompt: str, model: Optional[str] = None) -> dict:
    """Process the prompt using the specified LLM with streaming support."""
    try:
        model = model or get_default_model()
        if model not in MODEL_CONFIG:
            raise ValueError(f"Unsupported model: {model}. Supported models: {', '.join(MODEL_CONFIG.keys())}")
        
        model_config = MODEL_CONFIG[model]
        effective_provider = model_config["provider"]
        api_key_env = model_config["api_key_env"]
        api_key = os.getenv(api_key_env)
        if not api_key:
            raise ValueError(f"API key not set for {api_key_env}")

        logger.info(f"Attempting to process prompt with model: {model_config['model_name']} (task_id: {self.request.id})")

        if effective_provider == "openai":
            try:
                # First attempt with LangChain
                llm = ChatOpenAI(
                    model_name=model_config["model_name"],
                    openai_api_key=api_key,
                    streaming=True,
                    callbacks=[StreamingCallbackHandler(self.request.id)],
                    temperature=1
                )
                logger.info(f"Initialized ChatOpenAI with model: {model_config['model_name']}")
            except Exception as langchain_error:
                logger.warning(f"LangChain failed: {str(langchain_error)}. Falling back to raw OpenAI client.")
                # Fallback to raw OpenAI client
                client = OpenAI(api_key=api_key)
                stream = client.chat.completions.create(
                    model=model_config["model_name"],
                    messages=[{"role": "user", "content": prompt}],
                    stream=True
                )
                full_response = ""
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        redis_client.publish(f"task:{self.request.id}", content)
                        full_response += content
                redis_client.publish(f"task:{self.request.id}", "[DONE]")
                logger.info(f"Completed processing with raw OpenAI client. Response: {full_response}")
                return {"response": full_response, "model": model, "status": "success"}
        
        self.update_state(state=states.STARTED, meta={"status": "Processing prompt"})
        logger.info(f"Processing prompt: {prompt} with model: {model} (task_id: {self.request.id})")
        
        full_response = ""
        for chunk in llm.stream(prompt):
            full_response += chunk.content
        
        logger.info(f"Completed processing with LangChain. Response: {full_response}")
        return {"response": full_response, "model": model, "status": "success"}
    
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error processing prompt: {error_msg}")
        self.update_state(
            state=states.FAILURE,
            meta={
                "status": "error",
                "error": error_msg,
                "exc_type": type(e).__name__,
                "exc_module": type(e).__module__
            }
        )
        redis_client.publish(f"task:{self.request.id}", f"[ERROR] {error_msg}")
        return {"error": error_msg, "model": model or "unknown", "status": "failed"}