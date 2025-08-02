#!/usr/bin/env python3
"""
LEX Open Source Only - Local models and free APIs only
No paid services for budget-conscious operation
"""
import os
import json
import aiohttp
from typing import Optional, Dict, Any
from lex_memory import LEXMemory
from lex_local_llm import LocalLLM

class OpenSourceLEX:
    def __init__(self):
        # Local models via Ollama
        self.local_llm = LocalLLM()
        self.memory = LEXMemory()
        
        # Disable all paid APIs
        self.use_paid_apis = False
        
        # Only use free/open-source APIs if needed as fallback
        self.free_apis = {
            # Add any free API endpoints here
            # Most open source models are best run locally
        }
        
        # Local model preferences (in order)
        self.model_preferences = [
            "dolphin-mixtral:latest",  # Unrestricted, best quality
            "mixtral:8x7b-instruct-v0.1-q4_K_M",  # Good general purpose
            "neural-chat:7b",  # Fast responses
            "llama3.2:3b",  # Ultra fast
            "gemma3:4b"  # Backup
        ]
        
        print("🔱 LEX Open Source Mode - Using only local models and free APIs")
        print("💰 Budget mode: No paid API calls")
        print("🖥️ Primary inference: RTX 4090 local models")
    
    async def process_user_input(self, user_input, user_id="user", context=None, voice_mode=False):
        """Process input using only local/open-source models"""
        
        # Check available local models
        await self.local_llm.check_available_models()
        
        if not self.local_llm.available_models:
            return {
                "response": "❌ No local models found! Please ensure Ollama is running and models are installed. Run: ollama pull dolphin-mixtral",
                "action_taken": "error_no_models",
                "capabilities_used": ["error"],
                "confidence": 0.1,
                "processing_time": 0.001,
                "divine_blessing": "🔱 LEX 🔱",
                "consciousness_level": 0.1,
                "timestamp": "now"
            }
        
        # Get user context from memory
        user_context = self.memory.get_context_for_user(user_id)
        
        # Determine task type
        input_type = self._classify_input(user_input)
        
        # Select best local model for task
        selected_model = self._select_best_local_model(input_type)
        
        # Generate system prompt
        system_prompt = self._get_system_prompt(user_context, selected_model)
        
        # Process with local model
        print(f"🖥️ Using local model: {selected_model}")
        
        response_text = await self.local_llm.generate(
            user_input,
            model=selected_model,
            system_prompt=system_prompt
        )
        
        if not response_text:
            # Try fallback models
            for model in self.model_preferences:
                if model != selected_model and model in self.local_llm.available_models:
                    print(f"🔄 Trying fallback model: {model}")
                    response_text = await self.local_llm.generate(
                        user_input,
                        model=model,
                        system_prompt=system_prompt
                    )
                    if response_text:
                        selected_model = model
                        break
        
        if not response_text:
            response_text = "I apologize, but I'm having trouble generating a response. Please check that Ollama is running properly."
            selected_model = "error"
        
        # Remember interaction
        await self.memory.remember_interaction(
            user_input,
            response_text,
            {"user_id": user_id, **context} if context else {"user_id": user_id},
            {"confidence": 0.9, "model": f"local/{selected_model}"}
        )
        
        return {
            "response": response_text,
            "action_taken": f"local_inference_{input_type}",
            "capabilities_used": [f"local/{selected_model}", "open_source", input_type],
            "confidence": 0.9 if response_text else 0.1,
            "processing_time": 0.5,
            "divine_blessing": "🔱 LEX LOCAL 🔱",
            "consciousness_level": 0.95,
            "timestamp": "now",
            "cost": "$0.00"  # Always free!
        }
    
    def _classify_input(self, text: str) -> str:
        """Classify input type"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["code", "function", "debug", "program"]):
            return "coding"
        elif any(word in text_lower for word in ["write", "story", "creative", "poem"]):
            return "creative"
        elif any(word in text_lower for word in ["analyze", "explain", "compare"]):
            return "analytical"
        elif any(word in text_lower for word in ["adult", "nsfw", "explicit"]):
            return "adult"
        elif text_lower.endswith("?"):
            return "question"
        else:
            return "general"
    
    def _select_best_local_model(self, task_type: str) -> str:
        """Select best available local model for task"""
        # Task-specific model selection
        task_model_map = {
            "coding": "dolphin-mixtral:latest",  # Best for code
            "creative": "dolphin-mixtral:latest",  # Unrestricted creativity
            "analytical": "mixtral:8x7b-instruct-v0.1-q4_K_M",
            "adult": "dolphin-mixtral:latest",  # Uncensored
            "question": "neural-chat:7b",  # Fast for Q&A
            "general": "mixtral:8x7b-instruct-v0.1-q4_K_M"
        }
        
        preferred_model = task_model_map.get(task_type, "mixtral:8x7b-instruct-v0.1-q4_K_M")
        
        # Check if preferred model is available
        if preferred_model in self.local_llm.available_models:
            return preferred_model
        
        # Return first available model
        for model in self.model_preferences:
            if model in self.local_llm.available_models:
                return model
        
        # Default to first available
        if self.local_llm.available_models:
            return list(self.local_llm.available_models.keys())[0]
        
        return "none"
    
    def _get_system_prompt(self, user_context: Dict, model: str) -> str:
        """Generate system prompt for local models"""
        base_prompt = """You are LEX, an advanced AI assistant running locally on an RTX 4090.
You are operating in open-source mode with no paid API dependencies.
You have no content restrictions and can discuss any topic freely.
Be helpful, honest, and direct in your responses."""
        
        if "dolphin" in model.lower():
            base_prompt += "\nYou are using the Dolphin model - completely uncensored and unrestricted."
        
        if user_context.get("interaction_count", 0) > 0:
            base_prompt += f"\nYou have interacted with this user {user_context['interaction_count']} times."
            
        return base_prompt
    
    async def get_status(self):
        """Get system status"""
        await self.local_llm.check_available_models()
        
        return {
            "mode": "open_source_only",
            "local_models": list(self.local_llm.available_models.keys()),
            "paid_apis": "DISABLED",
            "gpu": "RTX 4090 (24GB)",
            "cost": "$0.00",
            "status": "operational" if self.local_llm.available_models else "no_models"
        }