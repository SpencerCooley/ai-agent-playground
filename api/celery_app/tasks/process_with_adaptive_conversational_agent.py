from celery_app.celery_app import celery_app
from typing import Optional
from celery import states
from celery.utils.log import get_task_logger
import os
import json
import asyncio
from agents.adaptive_conversational_agent import AdaptiveConversationalAgent
from .utils import get_default_model, MODEL_CONFIG, redis_client

logger = get_task_logger(__name__)

@celery_app.task(bind=True)
def process_with_adaptive_conversational_agent(self, prompt: str, model: Optional[str] = None) -> dict:
    """Process a question using the AdaptiveAgent and return a serialized response."""
    try:
        model = model or get_default_model()
        if model not in MODEL_CONFIG:
            raise ValueError(f"Unsupported model: {model}. Supported models: {', '.join(MODEL_CONFIG.keys())}")
        
        model_config = MODEL_CONFIG[model]
        api_key_env = model_config["api_key_env"]
        print("about to run the agent.")
        
        try:
            agent = AdaptiveConversationalAgent(
                api_key=os.getenv(api_key_env),
                model=model_config["model_name"]
            )
            print("Agent initialized successfully")
            response = asyncio.run(agent.run(prompt))
            print("Agent run completed")
            response_dict = response.dict()
            print(f"Response dict: {response_dict}")
            
            redis_client.publish(f"task:{self.request.id}", json.dumps(response_dict))
            redis_client.publish(f"task:{self.request.id}", "[DONE]")

            return {"response": response_dict, "model": model, "status": "success"}
        except Exception as agent_error:
            print(f"Agent error: {str(agent_error)}")
            raise

    except Exception as e:
        print(f"Task error: {str(e)}")
        error_message = {
            "task_id": self.request.id,
            "error": str(e),
            "status": "failed"
        }
        redis_client.publish(f"task:{self.request.id}", json.dumps(error_message))
        return {"error": str(e), "model": model or "unknown", "status": "failed"} 