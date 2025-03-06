from fastapi import APIRouter, HTTPException, WebSocket
from fastapi.websockets import WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional
from celery_app.tasks import process_prompt
import asyncio
from celery.result import AsyncResult
import redis

router = APIRouter(
    prefix="/prompt",
    tags=["Prompt"],
    responses={404: {"description": "Not found"}},
)

# Define Redis client at module level
redis_client = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

class PromptRequest(BaseModel):
    prompt: str

class PromptResponse(BaseModel):
    task_id: str

class TaskResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[dict] = None

@router.post("/", response_model=PromptResponse)
async def submit_prompt(
    request: PromptRequest,
    model: Optional[str] = None  # Query parameter
) -> PromptResponse:
    """
    Submit a prompt for async processing via Celery.
    The 'model' can be provided as a query parameter (e.g., ?model=o3-mini) 
    """
    task = process_prompt.delay(
        prompt=request.prompt,
        model=model
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

@router.websocket("/ws/{channel_id}")
async def websocket_endpoint(websocket: WebSocket, channel_id: str):
    """
    Agnostic WebSocket endpoint for streaming messages from a Redis channel.
    Messages are expected to be published to 'task:<channel_id>'.
    """
    print("Look Here")
    await websocket.accept()
    print(f"WebSocket connected to channel task:{channel_id}")
    
    # Initialize pubsub outside try block to avoid UnboundLocalError
    pubsub = redis_client.pubsub()
    channel = f"task:{channel_id}"
    
    # Keep track of processed messages to prevent duplicates
    processed_messages = set()
    
    try:
        pubsub.subscribe(channel)
        
        # Get number of subscribers for this channel
        num_subscribers = redis_client.pubsub_numsub(channel)[0][1]
        print(f"Channel {channel} has {num_subscribers} subscriber(s)")

        # Listen for messages indefinitely until client disconnects or [DONE]/[ERROR]
        while True:
            message = pubsub.get_message(timeout=0.1)
            if message and message['type'] == 'message':
                # Recheck number of subscribers periodically
                current_subscribers = redis_client.pubsub_numsub(channel)[0][1]
                print(f"Current subscribers to {channel}: {current_subscribers}")
                
                data = message['data']
                
                # Skip if we've already processed this message
                message_hash = hash(str(message))
                if message_hash in processed_messages:
                    continue
                processed_messages.add(message_hash)
                
                print(f"Received message on {channel}")
                if data == "[DONE]":
                    await websocket.send_json({
                        "type": "complete",
                        "content": "Streaming complete"
                    })
                    break
                elif data.startswith("[ERROR]"):
                    await websocket.send_json({
                        "type": "error",
                        "content": data[7:]
                    })
                    break
                else:
                    print(f"Sending token to WebSocket: {data}")
                    await websocket.send_json({
                        "type": "token",
                        "content": data
                    })
            await asyncio.sleep(0.01)

    except WebSocketDisconnect:
        print(f"Client disconnected from channel {channel_id}")
        # Get final subscriber count after disconnect
        final_subscribers = redis_client.pubsub_numsub(channel)[0][1]
        print(f"Channel {channel} now has {final_subscribers} subscriber(s)")
    except Exception as e:
        print(f"WebSocket error for channel {channel_id}: {str(e)}")
        await websocket.send_json({
            "type": "error",
            "content": str(e)
        })
    finally:
        pubsub.unsubscribe(channel)
        print(f"Unsubscribed from {channel}")
        await websocket.close()