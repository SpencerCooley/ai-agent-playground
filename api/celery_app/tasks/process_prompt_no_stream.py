from celery_app.celery_app import celery_app
from typing import Optional
from celery import states
from celery.utils.log import get_task_logger
from langchain.schema import HumanMessage
from langchain_community.chat_models import ChatOpenAI
import os
import json
from openai import OpenAI
from .utils import get_default_model, MODEL_CONFIG, redis_client

logger = get_task_logger(__name__)

@celery_app.task(bind=True, name='celery_app.tasks.process_prompt_no_stream')
def process_prompt_no_stream(self, prompt: str, model: Optional[str] = None) -> dict:
    """Process the prompt using the specified LLM and send complete formatted response."""
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
        
        self.update_state(state=states.STARTED, meta={"status": "Processing prompt"})
        logger.info(f"Processing prompt: {prompt} with model: {model} (task_id: {self.request.id})")

        # Define the instruction for formatted output
        system_instruction = (
            "You are an educated assistant that always responds in Markdown. "
            "Please include code examples wrapped in triple backticks, "
            "and use appropriate headers, bullet points, and formatting for clarity. "
            "Provide your answers accordingly."
        )

        if effective_provider == "openai":
            llm = ChatOpenAI(
                model_name=model_config["model_name"],
                openai_api_key=api_key,
                temperature=1
            )

            logger.info(f"Initialized ChatOpenAI with model: {model_config['model_name']}")
            
            try:
                messages = [
                    HumanMessage(content=system_instruction),
                    HumanMessage(content=prompt)
                ]
                
                response = llm.invoke(messages)
                full_response = response.content
                
                message = {
                    "task_id": self.request.id,
                    "response": full_response,
                    "format": "markdown",
                    "status": "complete",
                    "model": model
                }
                redis_client.publish(f"task:{self.request.id}", json.dumps(full_response))
                redis_client.publish(f"task:{self.request.id}", "[DONE]")
                
                logger.info("Prompt processing complete")
                return {"response": full_response, "model": model, "status": "success"}
                
            except Exception as langchain_error:
                logger.warning(f"LangChain failed: {str(langchain_error)}. Falling back to alternative processing.")
                
                try:
                    llm_fallback = ChatOpenAI(
                        model_name=model_config["model_name"],
                        openai_api_key=api_key,
                        temperature=1
                    )
                    
                    messages = [
                        HumanMessage(content=system_instruction),
                        HumanMessage(content=prompt)
                    ]
                    
                    response = llm_fallback.invoke(messages)
                    full_response = response.content
                    
                    message = {
                        "task_id": self.request.id,
                        "response": full_response,
                        "format": "markdown",
                        "status": "complete",
                        "model": model
                    }
                    redis_client.publish(f"task:{self.request.id}", json.dumps(full_response, ensure_ascii=False))
                    redis_client.publish(f"task:{self.request.id}", "[DONE]")
                    
                    return {"response": full_response, "model": model, "status": "success"}
                
                except Exception as fallback_error:
                     raise Exception(f"Fallback processing failed: {str(fallback_error)}")
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
        error_message = {
            "task_id": self.request.id,
            "error": error_msg,
            "status": "failed"
        }
        redis_client.publish(f"task:{self.request.id}", json.dumps(error_message))
        return {"error": error_msg, "model": model or "unknown", "status": "failed"} 