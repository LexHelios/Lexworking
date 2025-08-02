#!/usr/bin/env python3
"""
Mock ComfyUI Server - Simulates ComfyUI API for testing
"""
from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse
import uvicorn
import uuid
import asyncio
from datetime import datetime

app = FastAPI()

# Mock workflow storage
workflows = {}

@app.get("/")
async def root():
    return {"status": "ComfyUI Mock Server Running"}

@app.get("/system_stats")
async def system_stats():
    """Mock system stats endpoint"""
    return {
        "system": {
            "os": "windows",
            "python_version": "3.11.0",
            "embedded_python": False
        },
        "devices": [
            {
                "name": "cuda:0 NVIDIA GeForce RTX 4090",
                "type": "cuda",
                "index": 0,
                "vram_total": 25769803776,
                "vram_free": 20000000000
            }
        ]
    }

@app.get("/object_info/CheckpointLoaderSimple")
async def get_checkpoint_info():
    """Mock checkpoint loader info"""
    return {
        "CheckpointLoaderSimple": {
            "input": {
                "required": {
                    "ckpt_name": [
                        [
                            "ponyDiffusionV6XL.safetensors",
                            "realisticVisionV51.safetensors", 
                            "juggernautXL_v9.safetensors",
                            "sdxl_base_1.0.safetensors"
                        ]
                    ]
                }
            }
        }
    }

@app.post("/prompt")
async def queue_prompt(request: dict):
    """Mock prompt queueing"""
    prompt_id = str(uuid.uuid4())
    workflows[prompt_id] = {
        "prompt": request.get("prompt", {}),
        "status": "queued",
        "outputs": {}
    }
    
    # Simulate processing after a delay
    asyncio.create_task(process_workflow(prompt_id))
    
    return {"prompt_id": prompt_id}

async def process_workflow(prompt_id: str):
    """Simulate workflow processing"""
    await asyncio.sleep(2)  # Simulate processing time
    
    # Generate mock output
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ComfyUI_{timestamp}_{prompt_id[:8]}.png"
    
    workflows[prompt_id]["outputs"] = {
        "9": {  # SaveImage node
            "images": [
                {
                    "filename": filename,
                    "subfolder": "",
                    "type": "output"
                }
            ]
        }
    }
    workflows[prompt_id]["status"] = "completed"

@app.get("/history/{prompt_id}")
async def get_history(prompt_id: str):
    """Mock history endpoint"""
    if prompt_id in workflows:
        workflow = workflows[prompt_id]
        if workflow["status"] == "completed":
            return {
                prompt_id: {
                    "outputs": workflow["outputs"]
                }
            }
    return {}

@app.get("/view")
async def view_image(filename: str):
    """Mock image viewing"""
    return JSONResponse({
        "message": f"Mock image: {filename}",
        "note": "In real ComfyUI, this would return the actual image"
    })

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Mock WebSocket for real-time updates"""
    await websocket.accept()
    try:
        while True:
            # Just keep connection alive
            await asyncio.sleep(30)
            await websocket.send_json({"type": "ping"})
    except:
        pass

if __name__ == "__main__":
    print("Mock ComfyUI Server Starting...")
    print("This simulates ComfyUI API for testing")
    print("WARNING: No actual images will be generated")
    print("API: http://localhost:8188")
    print("")
    
    uvicorn.run(app, host="0.0.0.0", port=8188)