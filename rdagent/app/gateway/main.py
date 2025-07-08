
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import time
import asyncio
from rdagent.app.data_science.conf import DS_RD_SETTING
from rdagent.scenarios.data_science.loop import DataScienceRDLoop

app = FastAPI()

class ChatCompletionRequest(BaseModel):
    model: str
    messages: list
    stream: bool = False

@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    
    competition = "bms-molecular-translation"
    if request.model.startswith("rd-agent-"):
        competition = request.model.split("rd-agent-")[1]
    
    DS_RD_SETTING.competition = competition
    
    kaggle_loop = DataScienceRDLoop(DS_RD_SETTING)

    async def response_generator():
        async for result in kaggle_loop.run(step_n=1):
            yield f"data: {json.dumps({'id': 'chatcmpl-123', 'object': 'chat.completion.chunk', 'created': int(time.time()), 'model': request.model, 'choices': [{'index': 0, 'delta': {'role': 'assistant', 'content': str(result)}, 'finish_reason': None}]})}\n\n"
        yield f"data: {json.dumps({'id': 'chatcmpl-123', 'object': 'chat.completion.chunk', 'created': int(time.time()), 'model': request.model, 'choices': [{'index': 0, 'delta': {}, 'finish_reason': 'stop'}]})}\n\n"
        yield "data: [DONE]\n"

    if request.stream:
        return StreamingResponse(response_generator(), media_type="application/x-ndjson")
    else:
        # For non-streaming, we'll collect all results and return them at once.
        results = []
        async for result in kaggle_loop.run(step_n=1):
            results.append(str(result))
        
        return {
            "id": "chatcmpl-123",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": request.model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "\n".join(results),
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            }
        }

@app.get("/v1/models")
async def list_models():
    # Placeholder for model listing
    return {
        "object": "list",
        "data": [
            {
                "id": "rd-agent-model",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "microsoft"
            }
        ]
    }



