"""
Voice API Routes for LEX
Real-time voice conversation with ultra-low latency
"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.responses import StreamingResponse
from typing import Dict, Any, Optional
import asyncio
import json
import base64
import logging

from ..lex.unified_consciousness import lex_consciousness
from ..lex.voice_consciousness import voice_consciousness

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/voice", tags=["voice"])

@router.get("/status")
async def get_voice_status() -> Dict[str, Any]:
    """Get voice system status"""
    if not voice_consciousness.available:
        return {
            "available": False,
            "error": "Voice system not configured"
        }
    
    test_results = await voice_consciousness.test_voice_system()
    
    return {
        "available": test_results["overall_status"],
        "tts": test_results.get("tts", {}),
        "asr": test_results.get("asr", {}),
        "current_voice": voice_consciousness.current_voice,
        "voice_enabled": voice_consciousness.voice_enabled,
        "auto_speak": voice_consciousness.auto_speak
    }

@router.post("/speak")
async def speak_text(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert text to speech
    
    Request body:
    {
        "text": "Text to speak",
        "voice": "max" (optional),
        "emotion": "confident" (optional),
        "stream": true (optional)
    }
    """
    text = request.get("text", "")
    if not text:
        raise HTTPException(status_code=400, detail="No text provided")
    
    result = await voice_consciousness.speak(
        text=text,
        voice=request.get("voice"),
        stream=request.get("stream", True),
        emotion=request.get("emotion")
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Voice synthesis failed"))
    
    return {
        "success": True,
        "audio_base64": base64.b64encode(result["audio"]).decode() if result.get("audio") else None,
        "latency_ms": result.get("latency_ms", 0),
        "voice_used": result.get("voice_used")
    }

@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Convert speech to text
    """
    audio_data = await file.read()
    
    result = await voice_consciousness.listen(
        audio_data=audio_data,
        language=None  # Auto-detect
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Transcription failed"))
    
    return {
        "success": True,
        "text": result.get("text", ""),
        "language_detected": result.get("language_detected"),
        "confidence": result.get("confidence", 1.0),
        "latency_ms": result.get("latency_ms", 0)
    }

@router.post("/process")
async def process_voice_input(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Process voice input through LEX and return voice response
    """
    # Transcribe audio
    audio_data = await file.read()
    
    transcription = await voice_consciousness.listen(audio_data=audio_data)
    
    if not transcription.get("success"):
        raise HTTPException(status_code=500, detail="Failed to transcribe audio")
    
    user_text = transcription.get("text", "")
    
    # Process through LEX with voice mode
    lex_response = await lex_consciousness.process_user_input(
        user_text,
        voice_mode=True
    )
    
    return {
        "transcription": user_text,
        "response": lex_response.get("response"),
        "audio_base64": base64.b64encode(lex_response.get("voice_audio", b"")).decode() if lex_response.get("voice_audio") else None,
        "action_taken": lex_response.get("action_taken"),
        "total_latency_ms": transcription.get("latency_ms", 0) + lex_response.get("voice_latency_ms", 0)
    }

@router.websocket("/conversation")
async def voice_conversation(websocket: WebSocket):
    """
    Real-time voice conversation WebSocket
    
    Client sends: audio chunks (binary)
    Server sends: {
        "type": "transcript" | "response" | "audio" | "error",
        "data": <content>
    }
    """
    await websocket.accept()
    
    if not voice_consciousness.available:
        await websocket.send_json({
            "type": "error",
            "data": "Voice system not available"
        })
        await websocket.close()
        return
    
    logger.info("🎤 Voice conversation started")
    
    try:
        # Send initial greeting
        greeting = "Hello! I'm LEX, your AI assistant. How can I help you today?"
        greeting_audio = await voice_consciousness.speak(greeting, emotion="confident")
        
        if greeting_audio.get("success"):
            await websocket.send_json({
                "type": "audio",
                "data": base64.b64encode(greeting_audio["audio"]).decode()
            })
        
        # Process incoming audio
        audio_buffer = bytearray()
        
        while True:
            # Receive audio chunk
            data = await websocket.receive_bytes()
            audio_buffer.extend(data)
            
            # Process when we have enough audio (e.g., 1 second worth)
            if len(audio_buffer) > 16000:  # Assuming 16kHz sample rate
                # Transcribe
                transcription = await voice_consciousness.listen(bytes(audio_buffer))
                
                if transcription.get("success") and transcription.get("text"):
                    # Send transcript
                    await websocket.send_json({
                        "type": "transcript",
                        "data": transcription["text"]
                    })
                    
                    # Process through LEX
                    lex_response = await lex_consciousness.process_user_input(
                        transcription["text"],
                        voice_mode=True
                    )
                    
                    # Send text response
                    await websocket.send_json({
                        "type": "response",
                        "data": lex_response.get("response")
                    })
                    
                    # Send audio response
                    if lex_response.get("voice_audio"):
                        await websocket.send_json({
                            "type": "audio",
                            "data": base64.b64encode(lex_response["voice_audio"]).decode()
                        })
                
                # Clear buffer
                audio_buffer.clear()
                
    except WebSocketDisconnect:
        logger.info("🎤 Voice conversation ended")
    except Exception as e:
        logger.error(f"Voice conversation error: {e}")
        await websocket.send_json({
            "type": "error",
            "data": str(e)
        })
        await websocket.close()

@router.get("/voices")
async def get_available_voices() -> Dict[str, Any]:
    """Get list of available voices"""
    return {
        "voices": voice_consciousness.tts_provider.get_voice_list(),
        "current_voice": voice_consciousness.current_voice
    }

@router.post("/set-voice")
async def set_voice(request: Dict[str, str]) -> Dict[str, Any]:
    """
    Set LEX's speaking voice
    
    Request body:
    {
        "voice": "max" | "alex" | "emma" | etc.
    }
    """
    voice = request.get("voice", "")
    if not voice:
        raise HTTPException(status_code=400, detail="No voice specified")
    
    success = voice_consciousness.set_voice(voice)
    
    if not success:
        raise HTTPException(status_code=400, detail="Invalid voice")
    
    return {
        "success": True,
        "voice": voice,
        "description": voice_consciousness.tts_provider.voices.get(voice, {}).get("description", "")
    }

@router.post("/toggle-voice")
async def toggle_voice(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enable or disable voice output
    
    Request body:
    {
        "enabled": true | false (optional, toggles if not provided)
    }
    """
    enabled = request.get("enabled")
    new_state = voice_consciousness.toggle_voice(enabled)
    
    return {
        "voice_enabled": new_state
    }