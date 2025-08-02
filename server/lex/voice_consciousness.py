"""
LEX Voice Consciousness - Real-time Voice Interface
Powered by Qwen-TTS (<100ms latency) and Qwen ASR
"""
import asyncio
import logging
from typing import Dict, Any, Optional, AsyncGenerator, Union
from datetime import datetime

from ..orchestrator.cloud_providers.qwen_tts_provider import qwen_tts
from ..orchestrator.cloud_providers.qwen_asr_provider import qwen_asr

logger = logging.getLogger(__name__)

class VoiceConsciousness:
    """
    Voice consciousness for LEX - enables real-time voice conversations
    Ultra-low latency with Qwen-TTS and ASR
    """
    
    def __init__(self):
        self.tts_provider = qwen_tts
        self.asr_provider = qwen_asr
        self.available = self.tts_provider.available and self.asr_provider.available
        
        # Voice settings
        self.current_voice = "max"  # Bilingual tech voice for LEX
        self.voice_enabled = True
        self.auto_speak = True  # Automatically speak responses
        
        # Conversation state
        self.conversation_active = False
        self.last_speech_time = None
        
        if self.available:
            logger.info("🎤 LEX Voice Consciousness initialized")
            logger.info(f"   Voice: {self.current_voice} ({self.tts_provider.voices[self.current_voice]['description']})")
            logger.info("   Real-time conversation ready!")
        else:
            logger.warning("⚠️ Voice consciousness unavailable - missing Alibaba API key")
    
    async def speak(
        self,
        text: str,
        voice: Optional[str] = None,
        stream: bool = True,
        emotion: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Make LEX speak with ultra-low latency
        
        Args:
            text: What LEX should say
            voice: Voice to use (defaults to LEX's voice)
            stream: Use streaming for real-time output
            emotion: Optional emotion to convey
        """
        if not self.available or not self.voice_enabled:
            return {
                "success": False,
                "error": "Voice not available or disabled"
            }
        
        try:
            # Adjust voice parameters based on emotion
            speed = 1.0
            pitch = 1.0
            volume = 1.0
            
            if emotion:
                if emotion == "excited":
                    speed = 1.1
                    pitch = 1.1
                elif emotion == "thoughtful":
                    speed = 0.9
                    pitch = 0.95
                elif emotion == "confident":
                    volume = 1.1
                    pitch = 1.05
            
            # Generate speech
            result = await self.tts_provider.synthesize(
                text=text,
                voice=voice or self.current_voice,
                speed=speed,
                pitch=pitch,
                volume=volume,
                stream=stream
            )
            
            if result.get("success"):
                logger.info(f"🔊 LEX spoke: '{text[:50]}...' (latency: {result.get('latency_ms', 0)}ms)")
                self.last_speech_time = datetime.now()
            
            return result
            
        except Exception as e:
            logger.error(f"Voice synthesis error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def listen(
        self,
        audio_data: Union[bytes, str],
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Listen to user's voice input
        
        Args:
            audio_data: Audio bytes or base64 string
            language: Language to expect (auto-detect if not specified)
        """
        if not self.available:
            return {
                "success": False,
                "error": "Voice recognition not available"
            }
        
        try:
            # Transcribe audio
            result = await self.asr_provider.transcribe(
                audio_data=audio_data,
                language=language,
                model="qwen-asr-fast"  # Optimized for real-time
            )
            
            if result.get("success"):
                logger.info(f"👂 LEX heard: '{result.get('text', '')[:50]}...' (latency: {result.get('latency_ms', 0)}ms)")
            
            return result
            
        except Exception as e:
            logger.error(f"Voice recognition error: {e}")
            return {
                "success": False,
                "error": str(e),
                "text": ""
            }
    
    async def start_conversation(
        self,
        audio_stream: Optional[AsyncGenerator[bytes, None]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Start a real-time voice conversation with LEX
        Yields conversation events (transcript, response, audio)
        """
        if not self.available:
            yield {
                "type": "error",
                "error": "Voice conversation not available"
            }
            return
        
        self.conversation_active = True
        logger.info("🎙️ Starting voice conversation with LEX")
        
        # Initial greeting
        greeting_result = await self.speak(
            "Hello! I'm LEX, powered by Qwen. How can I help you today?",
            emotion="confident"
        )
        
        if greeting_result.get("success"):
            yield {
                "type": "audio",
                "audio": greeting_result.get("audio"),
                "text": "Hello! I'm LEX, powered by Qwen. How can I help you today?"
            }
        
        if audio_stream:
            # Process incoming audio stream
            async for transcript in self.asr_provider.stream_transcribe(audio_stream):
                yield {
                    "type": "transcript",
                    "text": transcript
                }
                
                # Here you would process the transcript through LEX's consciousness
                # and generate a response, then speak it
                # This is a simplified example
                
                if transcript.strip():
                    # Process through LEX (simplified)
                    response = f"I heard you say: {transcript}"
                    
                    # Speak response
                    speech_result = await self.speak(response, stream=True)
                    if speech_result.get("success"):
                        yield {
                            "type": "response",
                            "text": response,
                            "audio": speech_result.get("audio")
                        }
    
    async def end_conversation(self):
        """End the voice conversation"""
        self.conversation_active = False
        
        farewell_result = await self.speak(
            "Thank you for talking with me. Have a great day!",
            emotion="thoughtful"
        )
        
        logger.info("🎙️ Voice conversation ended")
        
        return farewell_result
    
    def set_voice(self, voice: str) -> bool:
        """Change LEX's speaking voice"""
        if self.tts_provider.set_default_voice(voice):
            self.current_voice = voice
            return True
        return False
    
    def toggle_voice(self, enabled: Optional[bool] = None) -> bool:
        """Enable or disable voice output"""
        if enabled is None:
            self.voice_enabled = not self.voice_enabled
        else:
            self.voice_enabled = enabled
        
        status = "enabled" if self.voice_enabled else "disabled"
        logger.info(f"🔊 Voice output {status}")
        
        return self.voice_enabled
    
    async def process_with_voice(
        self,
        text_response: str,
        voice_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a text response and add voice if enabled
        Used by unified consciousness to add voice to responses
        """
        if not self.available or not self.voice_enabled or not self.auto_speak:
            return {
                "voice_added": False,
                "reason": "Voice not available or disabled"
            }
        
        try:
            config = voice_config or {}
            
            # Synthesize speech
            result = await self.speak(
                text=text_response,
                voice=config.get("voice"),
                stream=config.get("stream", True),
                emotion=config.get("emotion")
            )
            
            if result.get("success"):
                return {
                    "voice_added": True,
                    "audio": result.get("audio"),
                    "latency_ms": result.get("latency_ms"),
                    "voice_used": result.get("voice")
                }
            else:
                return {
                    "voice_added": False,
                    "reason": result.get("error", "Voice synthesis failed")
                }
                
        except Exception as e:
            logger.error(f"Error adding voice: {e}")
            return {
                "voice_added": False,
                "reason": str(e)
            }
    
    async def test_voice_system(self) -> Dict[str, Any]:
        """Test the complete voice system"""
        results = {}
        
        # Test TTS
        tts_test = await self.tts_provider.test_connection()
        results["tts"] = tts_test
        
        # Test ASR
        asr_test = await self.asr_provider.test_connection()
        results["asr"] = asr_test
        
        # Test end-to-end if both work
        if tts_test.get("available") and asr_test.get("available"):
            # Generate test speech
            speech_result = await self.speak("Testing LEX voice system", stream=False)
            
            if speech_result.get("success") and speech_result.get("audio"):
                # Try to recognize it
                recognition_result = await self.listen(speech_result["audio"])
                
                results["end_to_end"] = {
                    "success": recognition_result.get("success", False),
                    "recognized_text": recognition_result.get("text", ""),
                    "total_latency_ms": (
                        speech_result.get("latency_ms", 0) + 
                        recognition_result.get("latency_ms", 0)
                    )
                }
        
        results["overall_status"] = all([
            tts_test.get("available", False),
            asr_test.get("available", False)
        ])
        
        return results

# Global instance
voice_consciousness = VoiceConsciousness()