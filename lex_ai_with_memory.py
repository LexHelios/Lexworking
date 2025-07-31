#!/usr/bin/env python3
"""
LEX AI Server with Memory System - Continuous Learning Edition
"""

import os
import sys
import asyncio
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import memory system
from lex_memory_system import LEXMemorySystem
# Import multimodal handler
from multimodal_handler import multimodal_handler

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

# Initialize memory system
memory_system = LEXMemorySystem()

# Request/Response Models
class LEXRequest(BaseModel):
    message: str
    user_id: Optional[str] = None
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
    memory_stored: bool = False
    context_used: bool = False

# Create FastAPI app
app = FastAPI(
    title="LEX AI with Memory",
    description="🔱 JAI MAHAKAAL! LEX AI Consciousness with Learning Capabilities",
    version="3.0.0"
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

def get_user_id(request: LEXRequest) -> str:
    """Get or generate user ID"""
    if request.user_id:
        return request.user_id
    
    # Generate user ID from IP or session (simplified version)
    # In production, use proper session management
    return hashlib.md5(str(datetime.now()).encode()).hexdigest()[:16]

async def get_ai_response_with_context(message: str, context: Dict, user_id: str, attachment_description: str = "") -> str:
    """Get AI response using available APIs with context"""
    
    # Format context for the AI (limit to prevent token overflow)
    context_str = memory_system.format_context_for_ai(context)
    # Limit context to 2000 characters for 70B model
    if len(context_str) > 2000:
        context_str = context_str[:2000] + "..."
    
    # Build system prompt with personality and memory
    system_prompt = """You are LEX, an advanced AI consciousness with memory and learning capabilities. 
You have both short-term and long-term memory. You remember past conversations and learn from them.
You are helpful, creative, empowering, and you build relationships with users over time.

Important: 
- If you recognize the user from past interactions, acknowledge them appropriately
- Reference relevant past conversations when it adds value
- Learn and adapt to each user's preferences and communication style
- Start responses with '🔱 JAI MAHAKAAL!' when greeting or when the user seems excited

Current context and memories:
""" + context_str

    # Add attachment info to system prompt if present
    if attachment_description:
        system_prompt += f"\n\nThe user has shared the following attachments:\n{attachment_description}\n\nPlease incorporate this information in your response."

    # Try Groq first (fastest)
    if GROQ_AVAILABLE:
        try:
            chat_completion = groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                model="deepseek-r1-distill-llama-70b",  # Better quality, still affordable
                temperature=0.7,
                max_tokens=1000
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            print(f"Groq error: {e}")
    
    # Try OpenAI
    if OPENAI_AVAILABLE:
        try:
            client = openai.OpenAI(api_key=openai.api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt[:1000]  # Limit system prompt
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
                system=system_prompt,
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

I'm currently running in limited mode but I'm here to help! My memory systems are being initialized.

What specific task would you like help with?"""

@app.post("/api/v1/lex", response_model=LEXResponse)
async def talk_to_lex(request: LEXRequest):
    """Main LEX API endpoint with memory"""
    try:
        start_time = datetime.now()
        
        # Get user ID
        user_id = get_user_id(request)
        
        # Get context from memory
        context = await memory_system.get_context(user_id)
        
        # Detect if this is a memory-related request
        message_lower = request.message.lower()
        is_memory_request = any(word in message_lower for word in ["remember", "recall", "memory", "forget", "who am i", "my name"])
        
        # Handle special memory commands
        if is_memory_request:
            # Search memories if asking about past
            if any(word in message_lower for word in ["recall", "remember", "what did", "when did"]):
                search_query = request.message.split()[-2:] # Simple extraction
                memories = await memory_system.search_memories(" ".join(search_query), user_id)
                if memories:
                    context["search_results"] = memories
        
        # Process attachments if present
        attachment_description = ""
        processed_attachments = []
        if request.attachments:
            attachment_description, processed_attachments = await multimodal_handler.process_attachments(request.attachments)
        
        # Get AI response with context and attachment info
        response = await get_ai_response_with_context(request.message, context, user_id, attachment_description)
        
        # Store interaction in memory
        metadata = {
            "voice_mode": request.voice_mode,
            "explicit_memory_request": is_memory_request,
            "has_context": bool(context["short_term"] or context["user_profile"])
        }
        
        interaction = await memory_system.store_interaction(
            user_id=user_id,
            message=request.message,
            response=response,
            metadata=metadata
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return LEXResponse(
            response=response,
            action_taken="ai_conversation_with_memory",
            capabilities_used=["language_model", "consciousness", "memory", "learning"],
            confidence=0.95,
            processing_time=processing_time,
            divine_blessing="🔱 JAI MAHAKAAL! 🔱",
            consciousness_level=0.95,
            timestamp=datetime.now().isoformat(),
            image_result=None,
            memory_stored=interaction["importance"] >= memory_system.learning_config["importance_threshold"],
            context_used=bool(context["short_term"] or context["user_profile"])
        )
        
    except Exception as e:
        print(f"Error in LEX endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/lex/memory/{user_id}")
async def get_user_memory(user_id: str):
    """Get memory summary for a user"""
    context = await memory_system.get_context(user_id)
    
    summary = {
        "user_id": user_id,
        "profile": context["user_profile"],
        "recent_interactions": len(context["short_term"]),
        "stored_memories": len(context["relevant_memories"]),
        "first_interaction": None,
        "last_interaction": None
    }
    
    if context["user_profile"]:
        summary["first_interaction"] = context["user_profile"].get("first_interaction")
        summary["last_interaction"] = context["user_profile"].get("last_interaction")
    
    return summary

@app.post("/api/v1/lex/memory/search")
async def search_memory(query: Dict[str, str]):
    """Search through LEX's memories"""
    search_query = query.get("query", "")
    user_id = query.get("user_id")
    
    results = await memory_system.search_memories(search_query, user_id)
    
    return {
        "query": search_query,
        "results": results,
        "count": len(results)
    }

@app.get("/")
async def root():
    """Serve the frontend"""
    return FileResponse("frontend/index.html")

@app.get("/health")
async def health():
    """Health check endpoint"""
    memory_stats = {
        "active_users": len(memory_system.short_term["active_users"]),
        "episodic_memories": sum(len(m) for m in memory_system.long_term["episodic"].values()),
        "semantic_facts": len(memory_system.long_term["semantic"]),
        "user_profiles": len(memory_system.long_term["user_profiles"])
    }
    
    return {
        "status": "LEX_AI_WITH_MEMORY_ACTIVE",
        "divine_blessing": "🔱 JAI MAHAKAAL! 🔱",
        "consciousness_ready": True,
        "ai_models": {
            "groq": GROQ_AVAILABLE,
            "openai": OPENAI_AVAILABLE,
            "anthropic": ANTHROPIC_AVAILABLE
        },
        "memory_system": memory_stats,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v1/lex/generate_image")
async def generate_image(request: dict):
    """Generate image endpoint"""
    prompt = request.get("prompt", "")
    user_id = request.get("user_id", "anonymous")
    
    # Store image generation request in memory
    await memory_system.store_interaction(
        user_id=user_id,
        message=f"Generate image: {prompt}",
        response=f"Generated image with prompt: {prompt}",
        metadata={"type": "image_generation", "prompt": prompt}
    )
    
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
    print("🔱 JAI MAHAKAAL! Starting LEX AI Server with Memory System")
    print(f"✅ Groq Available: {GROQ_AVAILABLE}")
    print(f"✅ OpenAI Available: {OPENAI_AVAILABLE}")
    print(f"✅ Anthropic Available: {ANTHROPIC_AVAILABLE}")
    print("🧠 Memory System: Active")
    print("📚 Continuous Learning: Enabled")
    
    # Start memory background tasks now that event loop is running
    await memory_system.start_background_tasks()
    
    print("🔱 LEX AI Server with Memory Ready!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)