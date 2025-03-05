from fastapi import APIRouter, HTTPException, WebSocket
from fastapi.websockets import WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional
from api.dependencies.llm import ProviderType
from api.celery_app.tasks import process_prompt
import asyncio
from celery.result import AsyncResult

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
    task_id: str


class TaskResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[dict] = None


@router.post("/", response_model=PromptResponse)
async def submit_prompt(request: PromptRequest) -> PromptResponse:
    """
    Submit a prompt for async processing via Celery.
    """
    task = process_prompt.delay(
        prompt=request.prompt,
        model=request.model,
        provider=request.provider,
        temperature=request.temperature
    )
    
    return PromptResponse(task_id=task.id)


@router.get("/status/{task_id}", response_model=TaskResponse)
async def get_task_status(task_id: str) -> TaskResponse:
    """
    Get the status and result of a task by its ID.
    """
    task = AsyncResult(task_id)
    response = {
        "task_id": task_id,
        "status": task.status,
    }
    
    if task.ready():
        response["result"] = task.get()
    
    return TaskResponse(**response)


@router.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    """
    WebSocket endpoint for streaming chat completion results.
    """
    await websocket.accept()
    try:
        task = AsyncResult(task_id)
        
        # If task doesn't exist or is already complete, send error and close
        if not task.id or task.ready():
            await websocket.send_json({
                "error": "Task not found or already complete"
            })
            await websocket.close()
            return

        # Subscribe to task events
        while not task.ready():
            if hasattr(task.result, 'events'):
                for event in task.result.events:
                    await websocket.send_json({
                        "type": "token",
                        "content": event
                    })
            await asyncio.sleep(0.1)  # Prevent tight loop

        # Send completion message
        await websocket.send_json({
            "type": "complete",
            "content": task.get()
        })
        
    except WebSocketDisconnect:
        print(f"Client disconnected from task {task_id}")
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "content": str(e)
        })
    finally:
        await websocket.close()
