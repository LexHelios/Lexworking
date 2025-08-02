"""
Qwen-TTS Voice Synthesis Provider for LexOS
Alibaba's state-of-the-art text-to-speech with < 100ms latency
Released June 2025
"""
import os
import logging
import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional, AsyncGenerator
from datetime import datetime

logger = logging.getLogger(__name__)

class QwenTTSProvider:
    """
    Qwen-TTS provider for ultra-low latency voice synthesis
    Supports streaming audio for real-time conversation with LEX
    """
    
    def __init__(self):
        self.api_key = os.getenv("ALIBABA_API_KEY", "")
        self.base_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2speech"
        self.streaming_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2speech/streaming"
        self.available = bool(self.api_key)
        
        # Available voices with descriptions
        self.voices = {
            "dylan": {
                "name": "Dylan",
                "language": "zh-CN",
                "dialect": "Beijing",
                "gender": "male",
                "description": "Natural Beijing accent, professional tone"
            },
            "jada": {
                "name": "Jada", 
                "language": "zh-CN",
                "dialect": "Shanghai",
                "gender": "female",
                "description": "Elegant Shanghai accent, warm tone"
            },
            "sunny": {
                "name": "Sunny",
                "language": "zh-CN", 
                "dialect": "Sichuan",
                "gender": "female",
                "description": "Friendly Sichuan accent, cheerful tone"
            },
            "alex": {
                "name": "Alex",
                "language": "en-US",
                "gender": "male",
                "description": "Professional English voice, clear articulation"
            },
            "emma": {
                "name": "Emma",
                "language": "en-US",
                "gender": "female", 
                "description": "Natural English voice, conversational tone"
            },
            "eva": {
                "name": "Eva",
                "language": "mixed",
                "gender": "female",
                "description": "Bilingual Chinese/English, seamless switching"
            },
            "max": {
                "name": "Max",
                "language": "mixed",
                "gender": "male",
                "description": "Bilingual Chinese/English, tech-savvy tone"
            }
        }
        
        # Default voice for LEX
        self.default_voice = "max"  # Bilingual tech voice fits LEX perfectly
        
        if self.available:
            logger.info("✅ Qwen-TTS voice synthesis initialized")
            logger.info(f"   Default voice: {self.default_voice} ({self.voices[self.default_voice]['description']})")
    
    async def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        speed: float = 1.0,
        pitch: float = 1.0,
        volume: float = 1.0,
        output_format: str = "mp3",
        stream: bool = True
    ) -> Dict[str, Any]:
        """
        Synthesize speech from text
        
        Args:
            text: Text to synthesize
            voice: Voice ID (defaults to LEX's voice)
            speed: Speech speed (0.5-2.0)
            pitch: Voice pitch (0.5-2.0)
            volume: Output volume (0-1.0)
            output_format: Audio format (mp3, wav, pcm)
            stream: Use streaming for real-time output
        """
        if not self.available:
            return {
                "error": "Qwen-TTS not available. Set ALIBABA_API_KEY.",
                "audio": None
            }
        
        voice = voice or self.default_voice
        if voice not in self.voices:
            voice = self.default_voice
        
        try:
            if stream:
                return await self._stream_synthesis(
                    text, voice, speed, pitch, volume, output_format
                )
            else:
                return await self._batch_synthesis(
                    text, voice, speed, pitch, volume, output_format
                )
                
        except Exception as e:
            logger.error(f"Qwen-TTS synthesis error: {e}")
            return {
                "error": str(e),
                "audio": None
            }
    
    async def _stream_synthesis(
        self,
        text: str,
        voice: str,
        speed: float,
        pitch: float,
        volume: float,
        output_format: str
    ) -> Dict[str, Any]:
        """Stream audio synthesis for real-time playback"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "input": {
                "text": text
            },
            "model": "qwen-tts-v1",
            "voice": voice,
            "parameters": {
                "speed": speed,
                "pitch": pitch,
                "volume": volume,
                "format": output_format,
                "streaming": True
            }
        }
        
        start_time = datetime.now()
        audio_chunks = []
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.streaming_url,
                headers=headers,
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    return {
                        "error": f"API error: {response.status} - {error_text}",
                        "audio": None
                    }
                
                # Stream audio chunks
                async for chunk in response.content.iter_chunked(4096):
                    audio_chunks.append(chunk)
                    # Could yield chunks here for real-time playback
        
        latency = (datetime.now() - start_time).total_seconds() * 1000
        
        return {
            "success": True,
            "audio": b"".join(audio_chunks),
            "voice": voice,
            "voice_info": self.voices[voice],
            "format": output_format,
            "latency_ms": latency,
            "streaming": True,
            "provider": "qwen-tts"
        }
    
    async def _batch_synthesis(
        self,
        text: str,
        voice: str,
        speed: float,
        pitch: float,
        volume: float,
        output_format: str
    ) -> Dict[str, Any]:
        """Batch synthesis for non-real-time use"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "input": {
                "text": text
            },
            "model": "qwen-tts-v1",
            "voice": voice,
            "parameters": {
                "speed": speed,
                "pitch": pitch,
                "volume": volume,
                "format": output_format,
                "streaming": False
            }
        }
        
        start_time = datetime.now()
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.base_url,
                headers=headers,
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    return {
                        "error": f"API error: {response.status} - {error_text}",
                        "audio": None
                    }
                
                result = await response.json()
                audio_data = result.get("output", {}).get("audio")
                
                if not audio_data:
                    return {
                        "error": "No audio data in response",
                        "audio": None
                    }
                
                # Decode base64 audio if needed
                import base64
                audio_bytes = base64.b64decode(audio_data)
                
                latency = (datetime.now() - start_time).total_seconds() * 1000
                
                return {
                    "success": True,
                    "audio": audio_bytes,
                    "voice": voice,
                    "voice_info": self.voices[voice],
                    "format": output_format,
                    "latency_ms": latency,
                    "streaming": False,
                    "provider": "qwen-tts"
                }
    
    async def stream_conversation(
        self,
        text_generator: AsyncGenerator[str, None],
        voice: Optional[str] = None
    ) -> AsyncGenerator[bytes, None]:
        """
        Stream audio synthesis from streaming text (for real-time conversation)
        Perfect for LEX's consciousness stream
        """
        voice = voice or self.default_voice
        buffer = ""
        
        async for text_chunk in text_generator:
            buffer += text_chunk
            
            # Synthesize when we have a complete sentence
            if any(buffer.endswith(p) for p in ['.', '!', '?', '。', '！', '？']):
                result = await self.synthesize(
                    buffer.strip(),
                    voice=voice,
                    stream=True
                )
                
                if result.get("success") and result.get("audio"):
                    yield result["audio"]
                
                buffer = ""
        
        # Synthesize any remaining text
        if buffer.strip():
            result = await self.synthesize(
                buffer.strip(),
                voice=voice,
                stream=True
            )
            
            if result.get("success") and result.get("audio"):
                yield result["audio"]
    
    def get_voice_list(self) -> Dict[str, Any]:
        """Get available voices with descriptions"""
        return self.voices
    
    def set_default_voice(self, voice: str):
        """Set LEX's default speaking voice"""
        if voice in self.voices:
            self.default_voice = voice
            logger.info(f"LEX voice updated to: {voice} ({self.voices[voice]['description']})")
            return True
        return False
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test Qwen-TTS connection with a simple synthesis"""
        if not self.available:
            return {
                "available": False,
                "error": "API key not configured"
            }
        
        try:
            result = await self.synthesize(
                "Hello, I am LEX, powered by Qwen TTS.",
                stream=False
            )
            
            if result.get("success"):
                return {
                    "available": True,
                    "voices": list(self.voices.keys()),
                    "default_voice": self.default_voice,
                    "latency_ms": result.get("latency_ms", 0),
                    "test_result": "Voice synthesis successful"
                }
            else:
                return {
                    "available": False,
                    "error": result.get("error", "Unknown error")
                }
                
        except Exception as e:
            return {
                "available": False,
                "error": str(e)
            }

# Global instance
qwen_tts = QwenTTSProvider()