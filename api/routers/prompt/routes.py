from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from dependencies.llm import use_llm, ProviderType
from langchain.chat_models.base import BaseChatModel

router = APIRouter(
    prefix="/prompt",
    tags=["Prompt"],
    responses={404: {"description": "Not found"}},
)


class PromptRequest(BaseModel):
    prompt: str
    model: Optional[str] = None
    provider: Optional[ProviderType] = "openai"
    temperature: Optional[float] = 0.7


class PromptResponse(BaseModel):
    prompt: str
    response: str
    model: str


@router.post("/", response_model=PromptResponse)
async def submit_prompt(
    request: PromptRequest,
    llm: BaseChatModel = Depends(use_llm)
) -> PromptResponse:
    """
    Submit a prompt and get a response from the language model.
    
    Parameters:
        request (PromptRequest): Contains prompt text and optional model configuration
        llm (BaseChatModel): LangChain chat model instance from dependency injection
    
    Returns:
        PromptResponse: Contains the original prompt and the model's response
    """
    try:
        # Get response from the model
        response = await llm.ainvoke(request.prompt)
        
        return PromptResponse(
            prompt=request.prompt,
            response=response.content,
            model=llm.model_name if hasattr(llm, 'model_name') else str(llm)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing prompt: {str(e)}"
        )
