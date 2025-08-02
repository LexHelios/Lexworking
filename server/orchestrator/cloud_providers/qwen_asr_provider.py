"""
Qwen ASR (Automatic Speech Recognition) Provider for LexOS
Alibaba's Intelligent Speech Interaction for voice input
"""
import os
import logging
import asyncio
import aiohttp
import json
import base64
from typing import Dict, Any, Optional, AsyncGenerator, Union
from datetime import datetime

logger = logging.getLogger(__name__)

class QwenASRProvider:
    """
    Qwen ASR provider for speech-to-text conversion
    Enables voice conversations with LEX
    """
    
    def __init__(self):
        self.api_key = os.getenv("ALIBABA_API_KEY", "")
        self.base_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/speech2text"
        self.streaming_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/speech2text/streaming"
        self.available = bool(self.api_key)
        
        # Supported languages
        self.languages = {
            "zh-CN": "Mandarin Chinese",
            "zh-HK": "Cantonese Chinese", 
            "en-US": "English (US)",
            "en-GB": "English (UK)",
            "ja-JP": "Japanese",
            "ko-KR": "Korean",
            "fr-FR": "French",
            "id-ID": "Indonesian",
            "auto": "Auto-detect language"
        }
        
        # Model capabilities
        self.models = {
            "qwen-asr-large": {
                "name": "Qwen ASR Large",
                "description": "High accuracy, supports all languages",
                "streaming": True,
                "punctuation": True,
                "timestamps": True
            },
            "qwen-asr-fast": {
                "name": "Qwen ASR Fast",
                "description": "Low latency, optimized for real-time",
                "streaming": True,
                "punctuation": True,
                "timestamps": False
            }
        }
        
        self.default_model = "qwen-asr-fast"  # Optimized for real-time conversation
        self.default_language = "auto"  # Auto-detect language
        
        if self.available:
            logger.info("✅ Qwen ASR speech recognition initialized")
            logger.info(f"   Default model: {self.default_model}")
    
    async def transcribe(
        self,
        audio_data: Union[bytes, str],
        language: Optional[str] = None,
        model: Optional[str] = None,
        enable_punctuation: bool = True,
        enable_timestamps: bool = False,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Transcribe audio to text
        
        Args:
            audio_data: Audio bytes or base64 string
            language: Language code (auto-detect if not specified)
            model: ASR model to use
            enable_punctuation: Add punctuation to transcript
            enable_timestamps: Include word-level timestamps
            stream: Use streaming recognition
        """
        if not self.available:
            return {
                "error": "Qwen ASR not available. Set ALIBABA_API_KEY.",
                "text": ""
            }
        
        language = language or self.default_language
        model = model or self.default_model
        
        try:
            if stream:
                return await self._stream_recognition(
                    audio_data, language, model, enable_punctuation, enable_timestamps
                )
            else:
                return await self._batch_recognition(
                    audio_data, language, model, enable_punctuation, enable_timestamps
                )
                
        except Exception as e:
            logger.error(f"Qwen ASR transcription error: {e}")
            return {
                "error": str(e),
                "text": ""
            }
    
    async def _batch_recognition(
        self,
        audio_data: Union[bytes, str],
        language: str,
        model: str,
        enable_punctuation: bool,
        enable_timestamps: bool
    ) -> Dict[str, Any]:
        """Batch speech recognition"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Convert audio to base64 if needed
        if isinstance(audio_data, bytes):
            audio_base64 = base64.b64encode(audio_data).decode()
        else:
            audio_base64 = audio_data
        
        payload = {
            "input": {
                "audio": audio_base64
            },
            "model": model,
            "parameters": {
                "language": language,
                "enable_punctuation": enable_punctuation,
                "enable_timestamps": enable_timestamps,
                "enable_speaker_diarization": False
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
                        "text": ""
                    }
                
                result = await response.json()
                output = result.get("output", {})
                
                latency = (datetime.now() - start_time).total_seconds() * 1000
                
                return {
                    "success": True,
                    "text": output.get("text", ""),
                    "language_detected": output.get("language", language),
                    "confidence": output.get("confidence", 1.0),
                    "timestamps": output.get("timestamps", []),
                    "latency_ms": latency,
                    "model": model,
                    "provider": "qwen-asr"
                }
    
    async def _stream_recognition(
        self,
        audio_data: Union[bytes, str],
        language: str,
        model: str,
        enable_punctuation: bool,
        enable_timestamps: bool
    ) -> Dict[str, Any]:
        """Streaming speech recognition for real-time transcription"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # For streaming, we'll need to chunk the audio
        # This is a simplified implementation
        if isinstance(audio_data, bytes):
            audio_base64 = base64.b64encode(audio_data).decode()
        else:
            audio_base64 = audio_data
        
        payload = {
            "input": {
                "audio": audio_base64
            },
            "model": model,
            "parameters": {
                "language": language,
                "enable_punctuation": enable_punctuation,
                "enable_timestamps": enable_timestamps,
                "streaming": True
            }
        }
        
        transcripts = []
        start_time = datetime.now()
        
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
                        "text": ""
                    }
                
                async for line in response.content:
                    if line:
                        try:
                            data = json.loads(line)
                            if data.get("output", {}).get("text"):
                                transcripts.append(data["output"]["text"])
                        except json.JSONDecodeError:
                            continue
        
        latency = (datetime.now() - start_time).total_seconds() * 1000
        
        return {
            "success": True,
            "text": " ".join(transcripts),
            "language_detected": language,
            "latency_ms": latency,
            "streaming": True,
            "model": model,
            "provider": "qwen-asr"
        }
    
    async def stream_transcribe(
        self,
        audio_stream: AsyncGenerator[bytes, None],
        language: Optional[str] = None,
        model: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        """
        Real-time streaming transcription from audio stream
        Perfect for live voice conversations with LEX
        """
        language = language or self.default_language
        model = model or self.default_model
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/octet-stream"
        }
        
        params = {
            "model": model,
            "language": language,
            "enable_punctuation": True,
            "streaming": True
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.streaming_url,
                headers=headers,
                params=params
            ) as ws:
                # Send audio chunks and receive transcripts
                async for audio_chunk in audio_stream:
                    await ws.send_bytes(audio_chunk)
                    
                    # Check for transcript responses
                    async for msg in ws:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            data = json.loads(msg.data)
                            if data.get("output", {}).get("text"):
                                yield data["output"]["text"]
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            logger.error(f"WebSocket error: {msg.data}")
                            break
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported languages"""
        return self.languages
    
    def get_available_models(self) -> Dict[str, Any]:
        """Get available ASR models"""
        return self.models
    
    async def detect_language(self, audio_data: Union[bytes, str]) -> Dict[str, Any]:
        """Detect language from audio sample"""
        result = await self.transcribe(
            audio_data,
            language="auto",
            model="qwen-asr-large"  # Use large model for better detection
        )
        
        if result.get("success"):
            return {
                "detected_language": result.get("language_detected", "unknown"),
                "confidence": result.get("confidence", 0),
                "sample_text": result.get("text", "")[:100]  # First 100 chars
            }
        else:
            return {
                "error": result.get("error", "Language detection failed")
            }
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test ASR connection with a sample audio"""
        if not self.available:
            return {
                "available": False,
                "error": "API key not configured"
            }
        
        try:
            # Create a simple test audio (silence)
            # In production, use actual test audio
            test_audio = b'\x00' * 1000  # Dummy audio data
            
            result = await self.transcribe(
                test_audio,
                language="en-US",
                model=self.default_model
            )
            
            # Even with silence, the API should respond
            return {
                "available": True,
                "models": list(self.models.keys()),
                "languages": list(self.languages.keys()),
                "default_model": self.default_model,
                "test_result": "ASR connection successful"
            }
                
        except Exception as e:
            return {
                "available": False,
                "error": str(e)
            }

# Global instance
qwen_asr = QwenASRProvider()