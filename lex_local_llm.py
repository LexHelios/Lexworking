#!/usr/bin/env python3
"""
LEX Local LLM Integration - Using RTX 4090 for inference
"""
import os
import json
import asyncio
import aiohttp
from typing import Optional, Dict, Any

class LocalLLM:
    def __init__(self, ollama_host: str = None):
        # Use environment variable or default
        self.ollama_host = ollama_host or os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        print(f"🖥️ Connecting to Ollama at: {self.ollama_host}")
        self.available_models = {}
        self.model_map = {
            # Task type to local model mapping
            "coding": "deepseek-coder:33b",
            "creative": "mixtral:8x7b",
            "general": "mixtral:8x7b",
            "fast": "llama3:8b",
            "math": "mixtral:8x7b",
            "analysis": "mixtral:8x7b"
        }
    
    async def check_available_models(self) -> Dict[str, Any]:
        """Check which models are available locally"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.ollama_host}/api/tags") as response:
                    if response.status == 200:
                        data = await response.json()
                        self.available_models = {
                            model['name']: {
                                'size': model['size'],
                                'family': model['details'].get('family', 'unknown'),
                                'parameter_size': model['details'].get('parameter_size', 'unknown')
                            }
                            for model in data.get('models', [])
                        }
                        return self.available_models
        except Exception as e:
            print(f"Error checking Ollama models: {e}")
            return {}
    
    async def generate(self, prompt: str, model: str = "mixtral:8x7b", system_prompt: str = None) -> Optional[str]:
        """Generate response using local LLM"""
        # Check if Ollama is running
        try:
            async with aiohttp.ClientSession() as session:
                # First check if model exists
                if model not in self.available_models:
                    # Try to use a fallback model
                    if "llama3:8b" in self.available_models:
                        model = "llama3:8b"
                    elif self.available_models:
                        model = list(self.available_models.keys())[0]
                    else:
                        return None
                
                # Prepare the prompt
                if system_prompt:
                    full_prompt = f"{system_prompt}\n\nUser: {prompt}\n\nAssistant:"
                else:
                    full_prompt = prompt
                
                # Generate response
                payload = {
                    "model": model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "num_predict": 500
                    }
                }
                
                async with session.post(
                    f"{self.ollama_host}/api/generate",
                    json=payload,
                    timeout=300  # 5 minutes for large models on RTX 4090
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('response', '').strip()
                    
        except aiohttp.ClientError:
            print("Ollama server not running. Start it with: ollama serve")
        except Exception as e:
            print(f"Local LLM error: {e}")
        
        return None
    
    def select_model_for_task(self, task_type: str) -> str:
        """Select best local model for task type"""
        model = self.model_map.get(task_type, "mixtral:8x7b")
        
        # Check if preferred model is available
        if model in self.available_models:
            return model
        
        # Fallback logic
        if task_type == "coding" and "deepseek-coder:33b" not in self.available_models:
            # Use any available model for coding
            for m in ["mixtral:8x7b", "llama3:8b"]:
                if m in self.available_models:
                    return m
        
        # Default fallback
        if self.available_models:
            return list(self.available_models.keys())[0]
        
        return "llama3:8b"  # Default if nothing available


class HybridLEX:
    """
    Hybrid LEX that prefers local models but falls back to cloud
    """
    def __init__(self):
        # Initialize local LLM
        self.local_llm = LocalLLM()
        
        # Cloud API keys (fallback)
        self.together_key = os.getenv('TOGETHER_API_KEY')
        self.groq_key = os.getenv('GROQ_API_KEY')
        
        # Initialize available models
        asyncio.create_task(self._init_models())
    
    async def _init_models(self):
        """Initialize and check available models"""
        models = await self.local_llm.check_available_models()
        if models:
            print(f"✅ Local models available: {list(models.keys())}")
        else:
            print("⚠️ No local models found. Using cloud APIs.")
    
    async def process_user_input(self, user_input, user_id="user", context=None, voice_mode=False):
        """Process input with local-first approach"""
        from lex_memory import LEXMemory
        
        # Initialize memory if needed
        if not hasattr(self, 'memory'):
            self.memory = LEXMemory()
        
        # Get user context
        user_context = self.memory.get_context_for_user(user_id)
        
        # Classify input
        input_type = self.memory._classify_input(user_input)
        
        # Generate system prompt
        system_prompt = self.memory.get_system_prompt(user_context)
        
        # Try local model first
        response_text = None
        model_used = None
        inference_type = None
        
        # Check available local models
        await self.local_llm.check_available_models()
        
        if self.local_llm.available_models:
            # Select best local model
            local_model = self.local_llm.select_model_for_task(input_type)
            
            print(f"🖥️ Using local model: {local_model}")
            response_text = await self.local_llm.generate(
                user_input,
                model=local_model,
                system_prompt=system_prompt
            )
            
            if response_text:
                model_used = f"local/{local_model}"
                inference_type = "RTX_4090"
        
        # Fallback to cloud if local failed
        if not response_text:
            print("☁️ Falling back to cloud API...")
            
            if self.together_key:
                try:
                    response_text = await self._call_together_ai(user_input, system_prompt)
                    model_used = "cloud/llama-70b"
                    inference_type = "together_ai"
                except Exception as e:
                    print(f"Cloud API error: {e}")
        
        # Final fallback
        if not response_text:
            response_text = "I apologize, but both local and cloud inference are currently unavailable. Please check that Ollama is running locally or verify cloud API keys."
            model_used = "fallback"
            inference_type = "none"
        
        result = {
            "response": response_text,
            "action_taken": f"ai_conversation_{input_type}",
            "capabilities_used": [model_used, input_type, inference_type],
            "confidence": 0.95 if inference_type != "none" else 0.1,
            "processing_time": 0.5,
            "divine_blessing": "🔱 LEX 🔱",
            "consciousness_level": 0.95,
            "timestamp": "now"
        }
        
        # Remember interaction
        await self.memory.remember_interaction(
            user_input,
            response_text,
            {"user_id": user_id, **context} if context else {"user_id": user_id},
            {"confidence": result["confidence"], "model": model_used}
        )
        
        return result
    
    async def _call_together_ai(self, prompt, system_prompt):
        """Fallback to Together AI"""
        url = "https://api.together.xyz/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.together_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['choices'][0]['message']['content']
                raise Exception(f"API error: {response.status}")