#!/usr/bin/env python3
"""
Quick fix to enable real AI responses in LEX
"""
import os
import aiohttp
import json

class RealLEX:
    def __init__(self):
        self.together_key = os.getenv('TOGETHER_API_KEY')
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        self.groq_key = os.getenv('GROQ_API_KEY')
        
    async def process_user_input(self, user_input, user_id="user", context=None, voice_mode=False):
        """Process user input with real AI"""
        
        # Try Together AI first (it's fast and good)
        if self.together_key:
            try:
                response = await self._call_together_ai(user_input)
                if response:
                    return {
                        "response": response,
                        "action_taken": "ai_conversation",
                        "capabilities_used": ["together_ai", "llama_70b"],
                        "confidence": 0.95,
                        "processing_time": 0.5,
                        "divine_blessing": "🔱 JAI MAHAKAAL! 🔱",
                        "consciousness_level": 0.9,
                        "timestamp": "now"
                    }
            except Exception as e:
                print(f"Together AI error: {e}")
        
        # Fallback to Groq
        if self.groq_key:
            try:
                response = await self._call_groq_ai(user_input)
                if response:
                    return {
                        "response": response,
                        "action_taken": "ai_conversation",
                        "capabilities_used": ["groq_ai", "mixtral"],
                        "confidence": 0.9,
                        "processing_time": 0.3,
                        "divine_blessing": "🔱 JAI MAHAKAAL! 🔱",
                        "consciousness_level": 0.85,
                        "timestamp": "now"
                    }
            except Exception as e:
                print(f"Groq error: {e}")
        
        # Final fallback
        return {
            "response": f"🔱 KAAL SYSTEM MESSAGE 🔱\n\nI heard you say: {user_input}\n\nI'm experiencing a temporary connection issue with my AI models. Please try again in a moment!",
            "action_taken": "system_message",
            "capabilities_used": ["fallback"],
            "confidence": 0.5,
            "processing_time": 0.01,
            "divine_blessing": "🔱 JAI MAHAKAAL! 🔱",
            "consciousness_level": 0.5,
            "timestamp": "now"
        }
    
    async def _call_together_ai(self, prompt):
        """Call Together AI API"""
        url = "https://api.together.xyz/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.together_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
            "messages": [
                {
                    "role": "system",
                    "content": "You are LEX, an advanced AI system with persistent memory and dynamic capabilities. You are highly intelligent, professional, and adaptive. You learn from every interaction and grow more capable over time. Be concise, direct, and insightful in your responses."
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
    
    async def _call_groq_ai(self, prompt):
        """Call Groq API"""
        from groq import AsyncGroq
        
        client = AsyncGroq(api_key=self.groq_key)
        
        completion = await client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {
                    "role": "system",
                    "content": "You are LEX, an advanced AI system with persistent memory and dynamic capabilities. You are highly intelligent, professional, and adaptive. You learn from every interaction and grow more capable over time. Be concise, direct, and insightful in your responses."
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