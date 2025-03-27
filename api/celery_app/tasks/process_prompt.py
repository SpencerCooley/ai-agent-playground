from celery_app.celery_app import celery_app
from typing import Optional
from celery import states
from celery.utils.log import get_task_logger
from langchain_community.chat_models import ChatOpenAI
import os
import json
from openai import OpenAI
from .utils import get_default_model, MODEL_CONFIG, redis_client, StreamingCallbackHandler

logger = get_task_logger(__name__)

@celery_app.task(bind=True, name='celery_app.tasks.process_prompt_as_stream')
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
                
                self.update_state(state=states.STARTED, meta={"status": "Processing prompt"})
                logger.info(f"Processing prompt: {prompt} with model: {model} (task_id: {self.request.id})")
                
                full_response = ""
                logger.info("Starting LangChain streaming...")
                for chunk in llm.stream(prompt):
                    logger.info(f"Received chunk: {chunk.content}")
                    full_response += chunk.content
                
                logger.info("LangChain streaming complete")
                return {"response": full_response, "model": model, "status": "success"}
                
            except Exception as langchain_error:
                logger.warning(f"LangChain failed: {str(langchain_error)}. Falling back to raw OpenAI client.")
                # Fallback to raw OpenAI client
                client = OpenAI(api_key=api_key)
                stream = client.chat.completions.create(
                    model=model_config["model_name"],
                    messages=[{
                        "role": "user", 
                        "content": "You are an educated assistant that always responds in Markdown. Please include code examples wrapped in triple backticks, and use appropriate headers, bullet points, and formatting for clarity. Provide your answers accordingly.\n\n" + prompt
                    }],
                    stream=True
                )

                full_response = ""
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        full_response += content
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