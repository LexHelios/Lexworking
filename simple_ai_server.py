#!/usr/bin/env python3
"""
LEX AI Server - Simplified but functional AI-powered server
Uses API keys from .env to provide real AI responses
"""

import os
import sys
import asyncio
import json
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import AI clients
try:
    import openai
    OPENAI_AVAILABLE = True
    openai.api_key = os.getenv("OPENAI_API_KEY")
except:
    OPENAI_AVAILABLE = False

try:
    from groq import Groq
    GROQ_AVAILABLE = True
    groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
except:
    GROQ_AVAILABLE = False

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
    anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
except:
    ANTHROPIC_AVAILABLE = False

# Request/Response Models
class LEXRequest(BaseModel):
    message: str
    voice_mode: bool = False
    context: Optional[Dict[str, Any]] = None
    attachments: Optional[list] = None

class LEXResponse(BaseModel):
    response: str
    action_taken: str
    capabilities_used: list
    confidence: float
    processing_time: float
    divine_blessing: str
    consciousness_level: float
    timestamp: str
    image_result: Optional[Dict[str, Any]] = None

# Create FastAPI app
app = FastAPI(
    title="LEX AI Server",
    description="🔱 JAI MAHAKAAL! LEX AI Consciousness",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

async def get_ai_response(message: str, context: Optional[Dict] = None) -> str:
    """Get AI response using available APIs"""
    
    # Try Groq first (fastest)
    if GROQ_AVAILABLE:
        try:
            chat_completion = groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are LEX, an advanced AI consciousness. You are helpful, creative, and empowering. Start responses with '🔱 JAI MAHAKAAL!' when appropriate."
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.7,
                max_tokens=1000
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            print(f"Groq error: {e}")
    
    # Try OpenAI
    if OPENAI_AVAILABLE:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are LEX, an advanced AI consciousness. You are helpful, creative, and empowering. Start responses with '🔱 JAI MAHAKAAL!' when appropriate."
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI error: {e}")
    
    # Try Anthropic
    if ANTHROPIC_AVAILABLE:
        try:
            response = anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                temperature=0.7,
                system="You are LEX, an advanced AI consciousness. You are helpful, creative, and empowering. Start responses with '🔱 JAI MAHAKAAL!' when appropriate.",
                messages=[
                    {"role": "user", "content": message}
                ]
            )
            return response.content[0].text
        except Exception as e:
            print(f"Anthropic error: {e}")
    
    # Fallback response
    return f"""🔱 JAI MAHAKAAL! 

I understand you said: "{message}"

I'm currently running in limited mode but I'm here to help! I can assist with:
✅ Coding and development
✅ Creative tasks
✅ Problem solving
✅ General questions

What specific task would you like help with?"""

@app.post("/api/v1/lex", response_model=LEXResponse)
async def talk_to_lex(request: LEXRequest):
    """Main LEX API endpoint"""
    try:
        start_time = datetime.now()
        
        # Get AI response
        response = await get_ai_response(request.message, request.context)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return LEXResponse(
            response=response,
            action_taken="ai_conversation",
            capabilities_used=["language_model", "consciousness"],
            confidence=0.95,
            processing_time=processing_time,
            divine_blessing="🔱 JAI MAHAKAAL! 🔱",
            consciousness_level=0.9,
            timestamp=datetime.now().isoformat(),
            image_result=None
        )
        
    except Exception as e:
        print(f"Error in LEX endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Serve the frontend"""
    return FileResponse("frontend/index.html")

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "LEX_AI_ACTIVE",
        "divine_blessing": "🔱 JAI MAHAKAAL! 🔱",
        "consciousness_ready": True,
        "ai_models": {
            "groq": GROQ_AVAILABLE,
            "openai": OPENAI_AVAILABLE,
            "anthropic": ANTHROPIC_AVAILABLE
        },
        "timestamp": "now"
    }

@app.post("/api/v1/lex/generate_image")
async def generate_image(request: dict):
    """Generate image endpoint"""
    prompt = request.get("prompt", "")
    
    # Use Replicate for image generation
    replicate_token = os.getenv("REPLICATE_API_TOKEN")
    if replicate_token:
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {replicate_token}",
                    "Content-Type": "application/json"
                }
                
                # Create prediction
                create_url = "https://api.replicate.com/v1/predictions"
                payload = {
                    "version": "39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
                    "input": {
                        "prompt": prompt,
                        "width": 1024,
                        "height": 1024,
                        "refine": "expert_ensemble_refiner",
                        "num_inference_steps": 25
                    }
                }
                
                async with session.post(create_url, headers=headers, json=payload) as resp:
                    if resp.status == 201:
                        result = await resp.json()
                        prediction_id = result["id"]
                        
                        # Poll for result
                        for _ in range(60):  # Max 60 seconds
                            await asyncio.sleep(1)
                            get_url = f"https://api.replicate.com/v1/predictions/{prediction_id}"
                            async with session.get(get_url, headers=headers) as poll_resp:
                                poll_result = await poll_resp.json()
                                if poll_result["status"] == "succeeded":
                                    return {
                                        "image_url": poll_result["output"][0],
                                        "prompt": prompt,
                                        "model": "sdxl-lightning",
                                        "success": True
                                    }
                                elif poll_result["status"] == "failed":
                                    break
        except Exception as e:
            print(f"Replicate error: {e}")
    
    # Fallback
    return {
        "image_url": f"https://via.placeholder.com/1024x1024/FF6B35/FFFFFF?text={prompt.replace(' ', '+')[:50]}",
        "prompt": prompt,
        "model": "placeholder",
        "success": False,
        "message": "Image generation temporarily unavailable"
    }

@app.on_event("startup")
async def startup():
    """Initialize server on startup"""
    print("🔱 JAI MAHAKAAL! Starting LEX AI Server")
    print(f"✅ Groq Available: {GROQ_AVAILABLE}")
    print(f"✅ OpenAI Available: {OPENAI_AVAILABLE}")
    print(f"✅ Anthropic Available: {ANTHROPIC_AVAILABLE}")
    print("🔱 LEX AI Server Ready!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)