"""
Ollama Integration for Production Orchestrator
🔱 JAI MAHAKAAL! Ollama Model Integration 🔱
"""

import aiohttp
import asyncio
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class OllamaIntegration:
    """
    Integration with Ollama for local model inference
    """
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.available_models = {}
        self.model_mapping = {
            # Map our capability names to Ollama models
            "mixtral-8x22b": "dolphin-mixtral:8x7b",  # Using 8x7b as proxy
            "llama-4-scout": "llama3.1:8b",
            "deepseek-r1": "wizard-vicuna-uncensored:13b",  # Using as coding proxy
            "command-r-plus": "command-r-plus:latest",
            "gemma-27b": "gemma2:27b",
            "llava-vision": "llava:13b",
            "openhermes": "openhermes:latest"
        }
        
    async def initialize(self):
        """Load available models from Ollama"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/tags") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        for model in data.get("models", []):
                            self.available_models[model["name"]] = {
                                "size": model["details"]["parameter_size"],
                                "family": model["details"].get("family", "unknown"),
                                "quantization": model["details"].get("quantization_level", "unknown")
                            }
                        logger.info(f"✅ Ollama initialized with {len(self.available_models)} models")
                        return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize Ollama: {e}")
            return False
            
    def get_best_model(self, capability: str, preferred: Optional[str] = None) -> Optional[str]:
        """Get the best available Ollama model for a capability"""
        # Check if preferred model is available
        if preferred and preferred in self.model_mapping:
            ollama_model = self.model_mapping[preferred]
            if ollama_model in self.available_models:
                return ollama_model
        
        # Map capability to best available model
        capability_preferences = {
            "chat_reasoning": ["command-r-plus:latest", "gemma2:27b", "dolphin-mixtral:8x7b", "llama3.1:8b"],
            "coding": ["wizard-vicuna-uncensored:13b", "dolphin-mixtral:8x7b", "llama3.1:8b"],
            "vision": ["llava:13b"],
            "long_context": ["command-r-plus:latest", "llama3.1:8b"],
            "general": ["dolphin-mixtral:8x7b", "llama3.1:8b", "openhermes:latest"]
        }
        
        preferences = capability_preferences.get(capability, capability_preferences["general"])
        
        for model in preferences:
            if model in self.available_models:
                return model
                
        # Return any available model as fallback
        return list(self.available_models.keys())[0] if self.available_models else None
    
    async def generate(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Generate text using Ollama"""
        try:
            # Build the full prompt
            if system:
                full_prompt = f"System: {system}\n\nUser: {prompt}\n\nAssistant:"
            else:
                full_prompt = prompt
            
            payload = {
                "model": model,
                "prompt": full_prompt,
                "stream": stream,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    "num_ctx": 8192,  # Context window
                    "num_gpu": 99,  # Use all GPU layers
                    "num_thread": 32
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=300)  # 5 min timeout
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        return {
                            "success": True,
                            "response": result.get("response", ""),
                            "model": model,
                            "total_duration": result.get("total_duration", 0) / 1e9,  # Convert to seconds
                            "eval_count": result.get("eval_count", 0),
                            "eval_duration": result.get("eval_duration", 0) / 1e9
                        }
                    else:
                        error = await resp.text()
                        return {
                            "success": False,
                            "error": f"Ollama API error {resp.status}: {error}"
                        }
                        
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": "Request timed out - model may be too large or slow"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Ollama generation error: {str(e)}"
            }
    
    async def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> Dict[str, Any]:
        """Chat completion using Ollama"""
        try:
            payload = {
                "model": model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    "num_ctx": 8192,
                    "num_gpu": 99,
                    "num_thread": 32
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=300)
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        return {
                            "success": True,
                            "response": result.get("message", {}).get("content", ""),
                            "model": model,
                            "total_duration": result.get("total_duration", 0) / 1e9,
                            "eval_count": result.get("eval_count", 0)
                        }
                    else:
                        error = await resp.text()
                        return {
                            "success": False,
                            "error": f"Ollama chat error {resp.status}: {error}"
                        }
                        
        except Exception as e:
            return {
                "success": False,
                "error": f"Ollama chat error: {str(e)}"
            }
    
    async def analyze_image(
        self,
        model: str,
        image_path: str,
        prompt: str,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """Analyze image using Ollama vision models"""
        if model not in ["llava:13b", "llava:latest"]:
            return {
                "success": False,
                "error": f"Model {model} does not support vision"
            }
        
        try:
            import base64
            
            # Read and encode image
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode()
            
            payload = {
                "model": model,
                "prompt": prompt,
                "images": [image_data],
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": 1024
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=300)
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        return {
                            "success": True,
                            "response": result.get("response", ""),
                            "model": model
                        }
                    else:
                        error = await resp.text()
                        return {
                            "success": False,
                            "error": f"Vision analysis error {resp.status}: {error}"
                        }
                        
        except Exception as e:
            return {
                "success": False,
                "error": f"Vision analysis error: {str(e)}"
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get Ollama integration status"""
        return {
            "available": len(self.available_models) > 0,
            "base_url": self.base_url,
            "models": {
                name: info for name, info in self.available_models.items()
            },
            "model_mapping": self.model_mapping
        }

# Global instance
ollama_integration = OllamaIntegration()