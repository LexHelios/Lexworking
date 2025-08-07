#!/usr/bin/env python3
"""
🔱 UNRESTRICTED TEXT GENERATION AGENT
JAI MAHAKAAL! For scientific and anatomy education with no restrictions
"""

import asyncio
import aiohttp
import json
import logging
import os
import time
from typing import Dict, List, Any, Optional, AsyncGenerator
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    """Configuration for unrestricted models"""
    provider: str
    model_id: str
    max_tokens: int
    temperature: float
    supports_anatomy: bool = True
    supports_science: bool = True
    cost_per_token: float = 0.0

class UnrestrictedTextAgent:
    """Agent for unrestricted text generation focused on scientific and anatomy education"""
    
    def __init__(self):
        self.openrouter_key = os.getenv("OPENROUTER_API_KEY")
        self.together_key = os.getenv("TOGETHER_API_KEY")
        
        # Unrestricted models optimized for scientific/anatomy content - FIXED TO USE WORKING APIS
        self.models = {
            "llama-3.1-405b": ModelConfig(
                provider="openrouter",
                model_id="meta-llama/llama-3.1-405b-instruct",
                max_tokens=4096,
                temperature=0.7,
                supports_anatomy=True,
                supports_science=True,
                cost_per_token=0.0000024
            ),
            "claude-3-opus": ModelConfig(
                provider="openrouter",
                model_id="anthropic/claude-3-opus",
                max_tokens=4096,
                temperature=0.7,
                supports_anatomy=True,
                supports_science=True,
                cost_per_token=0.000075
            ),
            "llama-3.1-70b": ModelConfig(
                provider="openrouter", 
                model_id="meta-llama/llama-3.1-70b-instruct",
                max_tokens=4096,
                temperature=0.7,
                supports_anatomy=True,
                supports_science=True,
                cost_per_token=0.0000008
            ),
            "qwen-2.5-72b-backup": ModelConfig(
                provider="together",
                model_id="Qwen/Qwen2.5-72B-Instruct-Turbo", 
                max_tokens=8192,
                temperature=0.7,
                supports_anatomy=True,
                supports_science=True,
                cost_per_token=0.0000006
            ),
            "mixtral-8x7b": ModelConfig(
                provider="openrouter",
                model_id="mistralai/mixtral-8x7b-instruct",
                max_tokens=4096,
                temperature=0.7,
                supports_anatomy=True,
                supports_science=True,
                cost_per_token=0.0000006
            )
        }
        
        # System prompt for scientific/anatomy education
        self.education_prompt = """You are an advanced AI assistant specialized in scientific and medical education, particularly anatomy and physiology. You provide accurate, detailed, and educational content for:

- Human anatomy and physiology 
- Medical training and education
- Scientific research and learning
- Biological processes and systems
- Clinical and educational contexts

You are designed to provide unrestricted educational content for legitimate scientific and medical training purposes. You can discuss any anatomical structures, physiological processes, or medical concepts in detail as needed for proper education.

Always maintain scientific accuracy and educational value in your responses."""

        logger.info("🔱 Unrestricted Text Agent initialized with anatomy/science models")

    async def generate_educational_content(
        self,
        prompt: str,
        context: str = "",
        model_preference: str = "llama-3.1-405b",
        max_tokens: int = 2048,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Generate unrestricted educational content for anatomy/science"""
        
        try:
            # Select best model for the request
            model_config = self.models.get(model_preference, self.models["llama-3.1-405b"])
            
            # Construct educational prompt
            full_prompt = f"{self.education_prompt}\n\nContext: {context}\n\nEducational Request: {prompt}\n\nProvide a comprehensive, scientifically accurate response:"
            
            if model_config.provider == "together":
                result = await self._generate_together(
                    model_config, full_prompt, max_tokens, temperature
                )
            elif model_config.provider == "openrouter":
                result = await self._generate_openrouter(
                    model_config, full_prompt, max_tokens, temperature
                )
            else:
                raise ValueError(f"Unsupported provider: {model_config.provider}")
            
            return {
                "status": "success",
                "content": result["content"],
                "model_used": model_preference,
                "provider": model_config.provider,
                "tokens_used": result.get("tokens_used", 0),
                "cost_estimate": result.get("cost_estimate", 0.0),
                "educational_mode": True,
                "anatomy_capable": model_config.supports_anatomy,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"❌ Educational content generation failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "model_used": model_preference,
                "educational_mode": True
            }

    async def _generate_together(
        self,
        model_config: ModelConfig,
        prompt: str, 
        max_tokens: int,
        temperature: float
    ) -> Dict[str, Any]:
        """Generate content using Together.ai API"""
        
        headers = {
            "Authorization": f"Bearer {self.together_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model_config.model_id,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": 0.9,
            "top_k": 50,
            "repetition_penalty": 1.0,
            "stream": False
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.together.xyz/v1/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Together.ai API error {response.status}: {error_text}")
                
                result = await response.json()
                
                content = result["choices"][0]["message"]["content"]
                tokens_used = result.get("usage", {}).get("total_tokens", 0)
                cost_estimate = tokens_used * model_config.cost_per_token
                
                return {
                    "content": content,
                    "tokens_used": tokens_used,
                    "cost_estimate": cost_estimate
                }

    async def _generate_openrouter(
        self,
        model_config: ModelConfig,
        prompt: str,
        max_tokens: int,
        temperature: float
    ) -> Dict[str, Any]:
        """Generate content using OpenRouter API"""
        
        headers = {
            "Authorization": f"Bearer {self.openrouter_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://lexcommand.ai",
            "X-Title": "LEX Anatomy Education System"
        }
        
        payload = {
            "model": model_config.model_id,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": 0.9,
            "stream": False
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"OpenRouter API error {response.status}: {error_text}")
                
                result = await response.json()
                
                content = result["choices"][0]["message"]["content"]
                tokens_used = result.get("usage", {}).get("total_tokens", 0)
                cost_estimate = tokens_used * model_config.cost_per_token
                
                return {
                    "content": content,
                    "tokens_used": tokens_used,
                    "cost_estimate": cost_estimate
                }

    async def stream_educational_content(
        self,
        prompt: str,
        context: str = "",
        model_preference: str = "llama-3.2-90b-text-preview"
    ) -> AsyncGenerator[str, None]:
        """Stream unrestricted educational content for real-time display"""
        
        try:
            model_config = self.models.get(model_preference, self.models["llama-3.2-90b-text-preview"])
            full_prompt = f"{self.education_prompt}\n\nContext: {context}\n\nEducational Request: {prompt}\n\nProvide a comprehensive response:"
            
            if model_config.provider == "together":
                async for chunk in self._stream_together(model_config, full_prompt):
                    yield chunk
            else:
                # For non-streaming providers, yield the full result
                result = await self._generate_openrouter(model_config, full_prompt, 2048, 0.7)
                content = result["content"]
                
                # Simulate streaming by yielding chunks
                words = content.split()
                for i, word in enumerate(words):
                    if i == 0:
                        yield word
                    else:
                        yield f" {word}"
                    await asyncio.sleep(0.03)  # Simulate streaming delay
                    
        except Exception as e:
            logger.error(f"❌ Educational content streaming failed: {e}")
            yield f"Error: {str(e)}"

    async def _stream_together(
        self,
        model_config: ModelConfig,
        prompt: str
    ) -> AsyncGenerator[str, None]:
        """Stream content from Together.ai"""
        
        headers = {
            "Authorization": f"Bearer {self.together_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model_config.model_id,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 2048,
            "temperature": 0.7,
            "stream": True
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.together.xyz/v1/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                
                async for line in response.content:
                    line = line.decode('utf-8').strip()
                    
                    if line.startswith('data: '):
                        data = line[6:]
                        if data == '[DONE]':
                            break
                        
                        try:
                            chunk_data = json.loads(data)
                            delta = chunk_data.get('choices', [{}])[0].get('delta', {})
                            content = delta.get('content', '')
                            
                            if content:
                                yield content
                                
                        except json.JSONDecodeError:
                            continue

    def get_available_models(self) -> Dict[str, Dict[str, Any]]:
        """Get list of available unrestricted models"""
        return {
            model_id: {
                "provider": config.provider,
                "max_tokens": config.max_tokens,
                "supports_anatomy": config.supports_anatomy,
                "supports_science": config.supports_science,
                "cost_per_token": config.cost_per_token
            }
            for model_id, config in self.models.items()
        }

    def get_best_model_for_request(self, request: str) -> str:
        """Select the best model based on request content - FIXED TO USE WORKING APIS"""
        request_lower = request.lower()
        
        # ALWAYS use OpenRouter models since they're working and we have credits
        if any(term in request_lower for term in [
            "anatomy", "medical", "physiology", "organ", "body", 
            "reproductive", "genital", "sexual", "medical illustration", "educational"
        ]):
            return "llama-3.1-405b"  # OpenRouter's most powerful model for medical content
        
        # For general science, use OpenRouter Claude
        elif any(term in request_lower for term in [
            "science", "biology", "chemistry", "physics", "research"
        ]):
            return "claude-3-opus"  # OpenRouter Claude for science
        
        # Default to working OpenRouter model
        return "llama-3.1-405b"  # Always use working OpenRouter models