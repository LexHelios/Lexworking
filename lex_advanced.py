#!/usr/bin/env python3
"""
LEX Advanced AI System - With Memory and Dynamic Model Selection
"""
import os
import aiohttp
import json
from lex_memory import LEXMemory

class AdvancedLEX:
    def __init__(self):
        self.together_key = os.getenv('TOGETHER_API_KEY')
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        self.groq_key = os.getenv('GROQ_API_KEY')
        
        # Initialize memory system
        self.memory = LEXMemory()
        
    async def process_user_input(self, user_input, user_id="user", context=None, voice_mode=False):
        """Process user input with memory and dynamic model selection"""
        
        # Get user context from memory
        user_context = self.memory.get_context_for_user(user_id)
        
        # Classify the input type
        input_type = self.memory._classify_input(user_input)
        
        # Select the best model for this task
        selected_model = self.memory.select_best_model(input_type)
        
        # Generate dynamic system prompt
        system_prompt = self.memory.get_system_prompt(user_context)
        
        # Try to get response
        response_text = None
        model_used = None
        
        # Route to appropriate API based on model selection
        if "together" in selected_model or "llama" in selected_model or "mixtral" in selected_model:
            if self.together_key:
                try:
                    response_text = await self._call_together_ai(user_input, system_prompt, selected_model)
                    model_used = selected_model
                except Exception as e:
                    print(f"Together AI error: {e}")
        
        elif "groq" in selected_model:
            if self.groq_key:
                try:
                    response_text = await self._call_groq_ai(user_input, system_prompt)
                    model_used = "groq/mixtral"
                except Exception as e:
                    print(f"Groq error: {e}")
        
        elif "deepseek" in selected_model:
            # For now, fall back to Together AI for code tasks
            if self.together_key:
                try:
                    response_text = await self._call_together_ai(
                        user_input, 
                        system_prompt + " You are especially skilled at coding and technical tasks.",
                        "meta-llama/Llama-3.3-70B-Instruct-Turbo"
                    )
                    model_used = "llama-70b-code"
                except Exception as e:
                    print(f"Code model error: {e}")
        
        # Fallback if primary selection failed
        if not response_text and self.together_key:
            try:
                response_text = await self._call_together_ai(user_input, system_prompt)
                model_used = "llama-70b-fallback"
            except Exception as e:
                print(f"Fallback error: {e}")
        
        # Final fallback
        if not response_text:
            response_text = "I apologize, but I'm experiencing connectivity issues. Please try again in a moment."
            model_used = "error"
        
        # Prepare response
        result = {
            "response": response_text,
            "action_taken": f"ai_conversation_{input_type}",
            "capabilities_used": [model_used, input_type, "memory_system"],
            "confidence": 0.95 if model_used != "error" else 0.1,
            "processing_time": 0.5,
            "divine_blessing": "🔱 LEX ADVANCED 🔱",
            "consciousness_level": 0.95,
            "timestamp": "now"
        }
        
        # Remember this interaction
        await self.memory.remember_interaction(
            user_input,
            response_text,
            {"user_id": user_id, **context} if context else {"user_id": user_id},
            {"confidence": result["confidence"], "model": model_used}
        )
        
        return result
    
    async def _call_together_ai(self, prompt, system_prompt, model=None):
        """Call Together AI API with specified model"""
        if not model:
            model = "meta-llama/Llama-3.3-70B-Instruct-Turbo"
            
        url = "https://api.together.xyz/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.together_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['choices'][0]['message']['content']
                else:
                    raise Exception(f"API error: {response.status}")
    
    async def _call_groq_ai(self, prompt, system_prompt):
        """Call Groq API for fast responses"""
        from groq import AsyncGroq
        
        client = AsyncGroq(api_key=self.groq_key)
        
        completion = await client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return completion.choices[0].message.content