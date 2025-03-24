from celery_app.celery_app import celery_app
from langchain_community.chat_models import ChatOpenAI
from typing import Optional
from celery import states
from celery.utils.log import get_task_logger
from langchain.callbacks.base import BaseCallbackHandler
import os
from dotenv import load_dotenv
import redis
from openai import OpenAI  # Added for fallback
import json
from langchain.schema import HumanMessage, AIMessage
from agents.adaptive_conversational_agent import AdaptiveConversationalAgent
import asyncio

load_dotenv()
logger = get_task_logger(__name__)
redis_client = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

class StreamingCallbackHandler(BaseCallbackHandler):
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.last_token = None  # Add this to track the last token

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        # Skip if this is a duplicate token
        if token == self.last_token:
            return
        self.last_token = token
        print("LOOOK HEREEEE")
        print(token)
        # logger.info(f"Publishing token for task {self.task_id}: {token}")
        redis_client.publish(f"task:{self.task_id}", token)

    def on_llm_end(self, response, **kwargs) -> None:
        # logger.info(f"LLM processing complete for task {self.task_id}")
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
                model=model_config["model_name"]  # Pass the model name from config
            )
            print("Agent initialized successfully")
            response = asyncio.run(agent.run(prompt))  # Sync call for Celery
            print("Agent run completed")
            response_dict = response.dict()  # Serialize Pydantic model to dict
            print(f"Response dict: {response_dict}")
            
            redis_client.publish(f"task:{self.request.id}", json.dumps(response_dict))
            redis_client.publish(f"task:{self.request.id}", "[DONE]")

            return {"response": response_dict, "model": model, "status": "success"}
        except Exception as agent_error:
            print(f"Agent error: {str(agent_error)}")
            raise  # Re-raise to be caught by outer try-except

    except Exception as e:
        print(f"Task error: {str(e)}")
        error_message = {
            "task_id": self.request.id,
            "error": str(e),
            "status": "failed"
        }
        redis_client.publish(f"task:{self.request.id}", json.dumps(error_message))
        return {"error": str(e), "model": model or "unknown", "status": "failed"}



@celery_app.task(bind=True)
def process_with_adaptive_conversational_agent_no_run(self, prompt: str, model: Optional[str] = None) -> dict:
    """Process a question using the AdaptiveAgent and return a serialized response."""
    try:
                # Publish the response to Redis
        redis_client.publish(f"task:{self.request.id}", "hello")
        redis_client.publish(f"task:{self.request.id}", "[DONE]")

        model = model or get_default_model()
        if model not in MODEL_CONFIG:
            raise ValueError(f"Unsupported model: {model}. Supported models: {', '.join(MODEL_CONFIG.keys())}")
        
        model_config = MODEL_CONFIG[model]
        api_key_env = model_config["api_key_env"]
        
        print(self.request.id)

        # agent = AdaptiveConversationalAgent(api_key=os.getenv(api_key_env))
        # print(agent)
        # print(agent)
        # print(agent)
        # print(agent)
        # print(agent)
        # print(agent)
        # print(agent)
        print("hello world")
        # response = agent.run(prompt)  # Sync call for Celery
        # response_dict = response.dict()  # Serialize Pydantic model to dict
        
        # print(response_dict)
        



        return {"response": "hello", "model": model, "status": "success"}

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error processing prompt with adaptive agent: {error_msg}")
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
            # Initialize ChatOpenAI without streaming
            llm = ChatOpenAI(
                model_name=model_config["model_name"],
                openai_api_key=api_key,
                temperature=1
            )

            logger.info(f"Initialized ChatOpenAI with model: {model_config['model_name']}")
            
            try:
                # Create message with system instruction and user prompt
                messages = [
                    HumanMessage(content=system_instruction),
                    HumanMessage(content=prompt)
                ]
                
                # Get complete response in one go
                response = llm.invoke(messages)
                full_response = response.content  # This will be Markdown-formatted text
                
                # Prepare structured message for Redis
                message = {
                    "task_id": self.request.id,
                    "response": full_response,  # Markdown-formatted string
                    "format": "markdown",
                    "status": "complete",
                    "model": model
                }
                print("hello world")
                redis_client.publish(f"task:{self.request.id}", json.dumps(full_response))
                redis_client.publish(f"task:{self.task_id}", "[DONE]")
                
                logger.info("Prompt processing complete")
                return {"response": full_response, "model": model, "status": "success"}
                
            except Exception as langchain_error:
                logger.warning(f"LangChain failed: {str(langchain_error)}. Falling back to alternative processing.")
                
                # Fallback using same LangChain approach (avoiding raw client)
                try:
                    # Retry with minimal configuration
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
                    
                    # Send structured message
                    message = {
                        "task_id": self.request.id,
                        "response": full_response,
                        "format": "markdown",
                        "status": "complete",
                        "model": model
                    }
                    redis_client.publish(f"task:{self.request.id}", json.dumps(full_response, ensure_ascii=False))
                    redis_client.publish(f"task:{self.task_id}", "[DONE]")
                    
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