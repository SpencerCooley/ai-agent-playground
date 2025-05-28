from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from celery_app.tasks.utils import get_default_model, MODEL_CONFIG
from langchain_openai import ChatOpenAI
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.schema import SystemMessage
from huggingface_hub import InferenceClient
from PIL import Image
import os
import json
import io
import base64

router = APIRouter(
    prefix="/tools",
    tags=["Tools"],
    responses={404: {"description": "Not found"}},
)

class GeneratePlanRequest(BaseModel):
    intent: str # give some context for the plan. "I want to get stronger, but I work every monday and tuesday"
    plan_type: str # strength, endurance, mobility, etc. 
    response_schema: object # tell the llm what you want your response to look like. 

class PlanResponse(BaseModel):
    plan: object #unstructured. 

model = get_default_model()
model_config = MODEL_CONFIG[model]
effective_provider = model_config["provider"]
api_key_env = model_config["api_key_env"]
api_key = os.getenv(api_key_env)

#huggingface api key
huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY")

# Initialize the LLM
llm = ChatOpenAI(
    model_name=model_config["model_name"],
    openai_api_key=api_key,
    streaming=True,
    temperature=1
)

@router.post("/plan", response_model=PlanResponse)
async def generate_plan(plan_request: GeneratePlanRequest):
    """
    Generate a plan based on the user's input.
    """
    try:
        # Create a system message that explains the task
        system_message = SystemMessage(
            content="You are an expert planner that creates detailed, personalized plans based on user requirements."
        )
        
        # Create a human message template that includes the intent, plan type, and schema
        human_template = """
        I need a {plan_type} plan with the following context:
        
        {intent}
        
        Please format your response according to this schema:
        {response_schema}
        
        Make sure your response is valid JSON that matches the schema exactly.
        """
        
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
        
        chat_prompt = ChatPromptTemplate.from_messages([
            system_message,
            human_message_prompt
        ])
        
        # Format the prompt with the user's input
        formatted_prompt = chat_prompt.format_prompt(
            plan_type=plan_request.plan_type,
            intent=plan_request.intent,
            schema=json.dumps(plan_request.response_schema, indent=2)
        )
        
        # Get the response from the LLM
        response = llm.invoke(formatted_prompt.to_messages())
        
        # Try to parse the response as JSON
        try:
            # The response might be in a code block or have extra text
            content = response.content
            
            # Try to extract JSON if it's in a code block
            if "```json" in content and "```" in content.split("```json", 1)[1]:
                json_str = content.split("```json", 1)[1].split("```", 1)[0].strip()
                plan_data = json.loads(json_str)
            elif "```" in content and "```" in content.split("```", 1)[1]:
                json_str = content.split("```", 1)[1].split("```", 1)[0].strip()
                plan_data = json.loads(json_str)
            else:
                # Try to parse the whole response as JSON
                plan_data = json.loads(content)
                
            return PlanResponse(plan=plan_data)
        except json.JSONDecodeError:
            # If we can't parse as JSON, return the raw text
            return PlanResponse(plan={"raw_response": response.content})
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating plan: {str(e)}")

class GenerateImageRequest(BaseModel):
    description: str
    style: str

class ImageResponse(BaseModel):
    image_url: str

def pil_to_base64(image: Image.Image, format: str = "PNG") -> str:
    # Create a BytesIO buffer to hold the image data
    buffer = io.BytesIO()
    # Save the PIL image to the buffer in the specified format
    image.save(buffer, format=format)
    # Get the byte data from the buffer
    img_bytes = buffer.getvalue()
    # Encode the bytes to base64 and convert to string
    base64_string = base64.b64encode(img_bytes).decode("utf-8")
    return base64_string

# FLUX.1-dev image generation
@router.post("/generate-image", response_model=ImageResponse)
async def generate_image(image_request: GenerateImageRequest):
    """
    Generate an image based on the user's input.
    """
    client = InferenceClient(
        provider="hf-inference",
        api_key=huggingface_api_key
    )

    image = client.text_to_image(
        f"{image_request.description}, {image_request.style}",
        model="black-forest-labs/FLUX.1-dev",
    )

    base64_image = pil_to_base64(image)

    return ImageResponse(image_url=base64_image)
