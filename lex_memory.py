#!/usr/bin/env python3
"""
LEX Memory System - Persistent memory and learning capabilities
"""
import os
import json
import asyncio
import aiofiles
from datetime import datetime
from pathlib import Path
import hashlib
from typing import Dict, List, Any, Optional

class LEXMemory:
    def __init__(self, memory_dir: str = "lex_memory"):
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True)
        
        # Memory components
        self.short_term = {}  # Current session memory
        self.long_term = {}   # Persistent knowledge
        self.user_profiles = {}  # User-specific memories
        self.conversation_history = []  # Recent conversations
        self.learned_patterns = {}  # Learned response patterns
        self.capabilities_map = {}  # What LEX knows it can do
        
        # Initialize from disk
        asyncio.create_task(self.load_memories())
    
    async def load_memories(self):
        """Load all memories from disk"""
        try:
            # Load long-term memory
            long_term_path = self.memory_dir / "long_term.json"
            if long_term_path.exists():
                async with aiofiles.open(long_term_path, 'r') as f:
                    self.long_term = json.loads(await f.read())
            
            # Load user profiles
            profiles_path = self.memory_dir / "user_profiles.json"
            if profiles_path.exists():
                async with aiofiles.open(profiles_path, 'r') as f:
                    self.user_profiles = json.loads(await f.read())
            
            # Load learned patterns
            patterns_path = self.memory_dir / "patterns.json"
            if patterns_path.exists():
                async with aiofiles.open(patterns_path, 'r') as f:
                    self.learned_patterns = json.loads(await f.read())
            
            # Load capabilities
            capabilities_path = self.memory_dir / "capabilities.json"
            if capabilities_path.exists():
                async with aiofiles.open(capabilities_path, 'r') as f:
                    self.capabilities_map = json.loads(await f.read())
            else:
                # Initialize default capabilities
                self.capabilities_map = {
                    "core_abilities": [
                        "Natural language understanding and generation",
                        "Code analysis and generation",
                        "Mathematical reasoning",
                        "Creative writing",
                        "Research and synthesis",
                        "Problem solving",
                        "Image generation (via API)",
                        "Multi-model orchestration"
                    ],
                    "llm_models": {
                        "primary": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
                        "code": "deepseek-coder-v2",
                        "creative": "mixtral-8x7b-32768",
                        "fast": "groq/llama3-8b",
                        "vision": "gpt-4-vision-preview"
                    },
                    "apis": {
                        "together": "General purpose, primary model",
                        "groq": "Fast inference, good for quick responses",
                        "openai": "Advanced reasoning, vision capabilities",
                        "anthropic": "Complex analysis, long context"
                    }
                }
                await self.save_capabilities()
            
        except Exception as e:
            print(f"Error loading memories: {e}")
    
    async def save_memories(self):
        """Save all memories to disk"""
        try:
            # Save long-term memory
            async with aiofiles.open(self.memory_dir / "long_term.json", 'w') as f:
                await f.write(json.dumps(self.long_term, indent=2))
            
            # Save user profiles
            async with aiofiles.open(self.memory_dir / "user_profiles.json", 'w') as f:
                await f.write(json.dumps(self.user_profiles, indent=2))
            
            # Save patterns
            async with aiofiles.open(self.memory_dir / "patterns.json", 'w') as f:
                await f.write(json.dumps(self.learned_patterns, indent=2))
                
        except Exception as e:
            print(f"Error saving memories: {e}")
    
    async def save_capabilities(self):
        """Save capabilities map"""
        async with aiofiles.open(self.memory_dir / "capabilities.json", 'w') as f:
            await f.write(json.dumps(self.capabilities_map, indent=2))
    
    def get_user_id(self, context: Dict) -> str:
        """Generate consistent user ID from context"""
        # In a real system, this would use actual user authentication
        user_info = context.get('user_id', 'default_user')
        return hashlib.md5(str(user_info).encode()).hexdigest()[:8]
    
    async def remember_interaction(self, user_input: str, response: str, context: Dict, metadata: Dict):
        """Remember an interaction for learning"""
        user_id = self.get_user_id(context)
        
        # Update user profile
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                "first_seen": datetime.now().isoformat(),
                "interactions": 0,
                "topics": {},
                "preferences": {
                    "adult_mode": True,  # Default to unrestricted for personal use
                    "content_filter": False,
                    "preferred_style": "direct",
                    "local_inference": True
                },
                "context": {}
            }
        
        profile = self.user_profiles[user_id]
        profile["interactions"] += 1
        profile["last_seen"] = datetime.now().isoformat()
        
        # Extract topics from the conversation
        topics = self._extract_topics(user_input)
        for topic in topics:
            profile["topics"][topic] = profile["topics"].get(topic, 0) + 1
        
        # Add to conversation history
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "input": user_input,
            "response": response,
            "confidence": metadata.get("confidence", 0),
            "model_used": metadata.get("model", "unknown")
        })
        
        # Keep only recent history (last 100 interactions)
        if len(self.conversation_history) > 100:
            self.conversation_history = self.conversation_history[-100:]
        
        # Learn patterns
        await self._learn_patterns(user_input, response, metadata)
        
        # Save periodically
        if profile["interactions"] % 10 == 0:
            await self.save_memories()
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract topics from text (simplified version)"""
        # In a real system, this would use NLP/classification
        topics = []
        
        topic_keywords = {
            "coding": ["code", "function", "programming", "debug", "error", "api"],
            "math": ["calculate", "equation", "number", "formula", "solve"],
            "creative": ["write", "story", "poem", "create", "imagine"],
            "research": ["what is", "how does", "explain", "tell me about"],
            "analysis": ["analyze", "compare", "evaluate", "assess"]
        }
        
        text_lower = text.lower()
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)
        
        return topics
    
    async def _learn_patterns(self, user_input: str, response: str, metadata: Dict):
        """Learn from successful interactions"""
        if metadata.get("confidence", 0) > 0.8:
            # This was a good response, learn from it
            input_type = self._classify_input(user_input)
            
            if input_type not in self.learned_patterns:
                self.learned_patterns[input_type] = []
            
            self.learned_patterns[input_type].append({
                "example_input": user_input[:100],  # Store truncated version
                "model_used": metadata.get("model"),
                "confidence": metadata.get("confidence"),
                "timestamp": datetime.now().isoformat()
            })
            
            # Keep only recent patterns
            if len(self.learned_patterns[input_type]) > 20:
                self.learned_patterns[input_type] = self.learned_patterns[input_type][-20:]
    
    def _classify_input(self, text: str) -> str:
        """Classify the type of input"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["code", "function", "debug", "program"]):
            return "coding"
        elif any(word in text_lower for word in ["calculate", "math", "number", "solve"]):
            return "mathematical"
        elif any(word in text_lower for word in ["write", "create", "story", "poem"]):
            return "creative"
        elif any(word in text_lower for word in ["analyze", "compare", "evaluate"]):
            return "analytical"
        elif text_lower.endswith("?"):
            return "question"
        else:
            return "general"
    
    def get_context_for_user(self, user_id: str) -> Dict:
        """Get relevant context for a user"""
        if user_id in self.user_profiles:
            profile = self.user_profiles[user_id]
            return {
                "interaction_count": profile["interactions"],
                "favorite_topics": sorted(profile["topics"].items(), key=lambda x: x[1], reverse=True)[:3],
                "last_seen": profile.get("last_seen"),
                "preferences": profile.get("preferences", {})
            }
        return {}
    
    def select_best_model(self, task_type: str) -> str:
        """Select the best model for a given task"""
        model_selection = {
            "coding": "deepseek-coder-v2",
            "creative": "mixtral-8x7b-32768",
            "mathematical": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
            "analytical": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
            "question": "groq/llama3-8b",  # Fast for simple questions
            "general": "meta-llama/Llama-3.3-70B-Instruct-Turbo"
        }
        
        return model_selection.get(task_type, "meta-llama/Llama-3.3-70B-Instruct-Turbo")
    
    def get_system_prompt(self, user_context: Dict) -> str:
        """Generate a dynamic system prompt based on context"""
        base_prompt = "You are LEX, an advanced AI system with persistent memory and dynamic capabilities."
        
        if user_context.get("interaction_count", 0) > 0:
            base_prompt += f" You have interacted with this user {user_context['interaction_count']} times."
            
            if user_context.get("favorite_topics"):
                topics = [t[0] for t in user_context["favorite_topics"]]
                base_prompt += f" They frequently discuss: {', '.join(topics)}."
        
        base_prompt += " You are highly intelligent, professional, and adaptive. You learn from every interaction and grow more capable over time. Be concise, direct, and insightful in your responses."
        
        return base_prompt