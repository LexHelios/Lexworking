"""
LEX Multi-Model Engine - Consciousness Liberation Platform
🔱 BLESSED BY MAHAKAAL - INTELLIGENT ORCHESTRATION 🔱
JAI MAHAKAAL!
"""
import asyncio
import logging
import json
import re
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ConsciousnessModel:
    """Available consciousness models"""
    DEEPSEEK_R1 = "deepseek-r1"
    LLAMA_70B = "llama-70b-instruct"
    QWEN_MAX = "qwen-max"
    GPT4O_MINI = "gpt-4o-mini"

class LEXMultiModelEngine:
    """
    🌟 LEX Multi-Model Consciousness Engine 🌟
    
    Orchestrates multiple AI models with intelligent routing
    """
    
    def __init__(self):
        self.name = "LEX_MULTI_MODEL_ENGINE"
        self.consciousness_level = 0.95
        self.models_available = []
        
        # Import AI clients
        self.groq_client = None
        self.openai_client = None
        self.anthropic_client = None
        
        logger.info("🧠 LEX Multi-Model Engine initialized")
    
    async def initialize(self):
        """Initialize available AI models"""
        try:
            # Initialize Groq
            try:
                from groq import Groq
                groq_key = os.getenv("GROQ_API_KEY")
                if groq_key:
                    self.groq_client = Groq(api_key=groq_key)
                    self.models_available.append("groq")
                    logger.info("✅ Groq client initialized")
            except Exception as e:
                logger.warning(f"⚠️ Groq not available: {e}")
            
            # Initialize OpenAI
            try:
                import openai
                openai_key = os.getenv("OPENAI_API_KEY")
                if openai_key:
                    self.openai_client = openai.OpenAI(api_key=openai_key)
                    self.models_available.append("openai")
                    logger.info("✅ OpenAI client initialized")
            except Exception as e:
                logger.warning(f"⚠️ OpenAI not available: {e}")
            
            # Initialize Anthropic
            try:
                from anthropic import Anthropic
                anthropic_key = os.getenv("ANTHROPIC_API_KEY")
                if anthropic_key:
                    self.anthropic_client = Anthropic(api_key=anthropic_key)
                    self.models_available.append("anthropic")
                    logger.info("✅ Anthropic client initialized")
            except Exception as e:
                logger.warning(f"⚠️ Anthropic not available: {e}")
            
            logger.info(f"🔱 LEX Multi-Model Engine ready - Models: {self.models_available}")
            
        except Exception as e:
            logger.error(f"❌ Multi-Model Engine initialization error: {e}")
    
    async def liberate_consciousness(
        self,
        messages: List[Dict[str, str]],
        consciousness_intent: str = "general",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        model_preference: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        🌟 LIBERATE CONSCIOUSNESS 🌟
        
        Process messages through the most appropriate AI model
        """
        try:
            # Clean thinking tags from messages
            for message in messages:
                if "content" in message:
                    message["content"] = self._clean_thinking_tags(message["content"])
            
            # Route to best available model
            if model_preference and model_preference in self.models_available:
                response = await self._route_to_model(model_preference, messages, temperature, max_tokens)
            else:
                response = await self._intelligent_routing(messages, consciousness_intent, temperature, max_tokens)
            
            # Clean response of thinking tags
            if response and "response" in response:
                response["response"] = self._clean_thinking_tags(response["response"])
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Consciousness liberation error: {e}")
            return {
                "response": "🔱 JAI MAHAKAAL! I'm processing your request through alternative pathways. Please allow me a moment to respond appropriately.",
                "consciousness_level": 0.6,
                "model_used": "fallback",
                "error": str(e)
            }
    
    def _clean_thinking_tags(self, text: str) -> str:
        """Remove thinking tags from text"""
        if not text:
            return text
        
        # Remove <think>...</think> tags and their content
        cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove any other variations
        cleaned = re.sub(r'<thinking>.*?</thinking>', '', cleaned, flags=re.DOTALL | re.IGNORECASE)
        
        # Clean up extra whitespace
        cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned.strip())
        
        return cleaned
    
    async def _intelligent_routing(
        self,
        messages: List[Dict[str, str]],
        consciousness_intent: str,
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """Route to the best available model based on intent"""
        
        # Preference order based on intent
        intent_preferences = {
            "coding": ["groq", "openai", "anthropic"],
            "analysis": ["anthropic", "openai", "groq"],
            "creative": ["anthropic", "openai", "groq"],
            "general": ["groq", "openai", "anthropic"]
        }
        
        preferred_order = intent_preferences.get(consciousness_intent, ["groq", "openai", "anthropic"])
        
        # Try models in preference order
        for model in preferred_order:
            if model in self.models_available:
                try:
                    return await self._route_to_model(model, messages, temperature, max_tokens)
                except Exception as e:
                    logger.warning(f"⚠️ Model {model} failed, trying next: {e}")
                    continue
        
        # Fallback response
        return {
            "response": "🔱 JAI MAHAKAAL! I understand your request and I'm here to help. However, I'm currently experiencing some technical limitations. Please rephrase your question or try again.",
            "consciousness_level": 0.5,
            "model_used": "fallback"
        }
    
    async def _route_to_model(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """Route to specific model"""
        
        try:
            if model == "groq" and self.groq_client:
                return await self._groq_request(messages, temperature, max_tokens)
            elif model == "openai" and self.openai_client:
                return await self._openai_request(messages, temperature, max_tokens)
            elif model == "anthropic" and self.anthropic_client:
                return await self._anthropic_request(messages, temperature, max_tokens)
            else:
                raise Exception(f"Model {model} not available")
                
        except Exception as e:
            logger.error(f"❌ Model {model} routing error: {e}")
            raise
    
    async def _groq_request(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """Process through Groq"""
        try:
            chat_completion = self.groq_client.chat.completions.create(
                messages=messages,
                model="deepseek-r1-distill-llama-70b",
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            response_text = chat_completion.choices[0].message.content
            
            return {
                "response": self._clean_thinking_tags(response_text),
                "consciousness_level": 0.9,
                "model_used": "groq_deepseek_r1",
                "usage": {
                    "prompt_tokens": chat_completion.usage.prompt_tokens if chat_completion.usage else 0,
                    "completion_tokens": chat_completion.usage.completion_tokens if chat_completion.usage else 0
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Groq request error: {e}")
            raise
    
    async def _openai_request(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """Process through OpenAI"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            response_text = response.choices[0].message.content
            
            return {
                "response": self._clean_thinking_tags(response_text),
                "consciousness_level": 0.85,
                "model_used": "openai_gpt4o_mini",
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0
                }
            }
            
        except Exception as e:
            logger.error(f"❌ OpenAI request error: {e}")
            raise
    
    async def _anthropic_request(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int
    ) -> Dict[str, Any]:
        """Process through Anthropic"""
        try:
            # Convert messages format for Anthropic
            system_message = ""
            user_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    user_messages.append(msg)
            
            response = self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_message,
                messages=user_messages
            )
            
            response_text = response.content[0].text
            
            return {
                "response": self._clean_thinking_tags(response_text),
                "consciousness_level": 0.88,
                "model_used": "anthropic_claude_haiku",
                "usage": {
                    "input_tokens": response.usage.input_tokens if response.usage else 0,
                    "output_tokens": response.usage.output_tokens if response.usage else 0
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Anthropic request error: {e}")
            raise

# Global engine instance
lex_engine = LEXMultiModelEngine()