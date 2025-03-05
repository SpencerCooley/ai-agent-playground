from .celery_app import celery_app
from langchain.chat_models.base import BaseChatModel
from typing import Optional
from api.dependencies.llm import use_llm
from celery import states
from celery.utils.log import get_task_logger
from langchain.callbacks.base import BaseCallbackHandler

logger = get_task_logger(__name__)

class StreamingCallbackHandler(BaseCallbackHandler):
    """Callback handler for streaming tokens."""
    def __init__(self, task):
        self.task = task
        self.tokens = []

    def on_llm_new_token(self, token: str, **kwargs):
        """Stream tokens as they're generated."""
        self.tokens.append(token)
        # Update task state with current tokens
        self.task.update_state(
            state=states.STARTED,
            meta={'events': self.tokens}
        )

@celery_app.task(bind=True)
async def process_prompt(self, prompt: str, model: Optional[str] = None, 
                  provider: str = "openai", temperature: float = 0.7) -> dict:
    """Process the prompt using the specified LLM with streaming support"""
    try:
        # Get LLM instance
        llm: BaseChatModel = await use_llm(model, provider, temperature)
        
        # Add streaming callback
        callback = StreamingCallbackHandler(self)
        llm.callbacks = [callback]
        
        # Get response from the model with streaming
        response = await llm.ainvoke(
            prompt,
            streaming=True
        )
        
        result = {
            "prompt": prompt,
            "response": response.content,
            "model": llm.model_name if hasattr(llm, 'model_name') else str(llm)
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing prompt: {str(e)}")
        return {"error": str(e)}
