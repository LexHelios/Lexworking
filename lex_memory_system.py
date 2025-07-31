#!/usr/bin/env python3
"""
LEX Memory System - Short-term and Long-term Memory with Continuous Learning
"""

import os
import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import deque
import asyncio
import aiofiles
from pathlib import Path

class LEXMemorySystem:
    """
    Advanced memory system for LEX consciousness
    - Short-term memory: Active conversation context
    - Long-term memory: Persistent knowledge base
    - Episodic memory: Specific interactions and events
    - Semantic memory: General knowledge and facts
    """
    
    def __init__(self, memory_dir: str = "./lex_memory"):
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True)
        
        # Short-term memory (conversation buffer)
        self.short_term = {
            "conversations": {},  # user_id -> deque of messages
            "context_window": 20,  # Number of messages to keep in short-term
            "active_users": {},  # user_id -> last_interaction_time
        }
        
        # Long-term memory paths
        self.episodic_memory_path = self.memory_dir / "episodic_memory.json"
        self.semantic_memory_path = self.memory_dir / "semantic_memory.json"
        self.user_profiles_path = self.memory_dir / "user_profiles.json"
        self.knowledge_graph_path = self.memory_dir / "knowledge_graph.json"
        
        # Load existing memories
        self.long_term = {
            "episodic": self._load_memory(self.episodic_memory_path),
            "semantic": self._load_memory(self.semantic_memory_path),
            "user_profiles": self._load_memory(self.user_profiles_path),
            "knowledge_graph": self._load_memory(self.knowledge_graph_path)
        }
        
        # Learning parameters
        self.learning_config = {
            "importance_threshold": 0.7,  # Minimum importance to store in long-term
            "consolidation_interval": 300,  # 5 minutes
            "memory_decay_rate": 0.95,  # How fast memories fade
        }
        
        # Background task will be started when server starts
        self._consolidation_task = None
    
    def _load_memory(self, path: Path) -> Dict:
        """Load memory from disk"""
        if path.exists():
            try:
                with open(path, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    async def _save_memory(self, memory_type: str):
        """Save memory to disk asynchronously"""
        path = getattr(self, f"{memory_type}_memory_path", None)
        if path and memory_type in self.long_term:
            async with aiofiles.open(path, 'w') as f:
                await f.write(json.dumps(self.long_term[memory_type], indent=2))
    
    def generate_memory_id(self, content: str) -> str:
        """Generate unique ID for memory"""
        return hashlib.md5(f"{content}{time.time()}".encode()).hexdigest()[:16]
    
    async def store_interaction(self, user_id: str, message: str, response: str, 
                               metadata: Optional[Dict] = None) -> Dict:
        """Store an interaction in memory"""
        timestamp = datetime.now().isoformat()
        
        # Create interaction record
        interaction = {
            "id": self.generate_memory_id(message),
            "user_id": user_id,
            "timestamp": timestamp,
            "message": message,
            "response": response,
            "metadata": metadata or {},
            "importance": self._calculate_importance(message, response, metadata),
            "keywords": self._extract_keywords(message, response),
            "emotion": self._detect_emotion(message),
            "topic": self._classify_topic(message)
        }
        
        # Update short-term memory
        if user_id not in self.short_term["conversations"]:
            self.short_term["conversations"][user_id] = deque(maxlen=self.short_term["context_window"])
        
        self.short_term["conversations"][user_id].append(interaction)
        self.short_term["active_users"][user_id] = time.time()
        
        # Update user profile
        await self._update_user_profile(user_id, interaction)
        
        # Store in episodic memory if important enough
        if interaction["importance"] >= self.learning_config["importance_threshold"]:
            if user_id not in self.long_term["episodic"]:
                self.long_term["episodic"][user_id] = []
            
            self.long_term["episodic"][user_id].append(interaction)
            await self._save_memory("episodic")
        
        # Extract and store semantic knowledge
        await self._extract_semantic_knowledge(interaction)
        
        return interaction
    
    def _calculate_importance(self, message: str, response: str, metadata: Optional[Dict]) -> float:
        """Calculate importance score for memory storage"""
        score = 0.5  # Base score
        
        # Length factor
        if len(message) > 100 or len(response) > 200:
            score += 0.1
        
        # Question factor
        if "?" in message:
            score += 0.1
        
        # Personal information factor
        personal_keywords = ["name", "i am", "my", "creator", "remember", "important"]
        if any(keyword in message.lower() for keyword in personal_keywords):
            score += 0.2
        
        # Metadata factors
        if metadata:
            if metadata.get("explicit_memory_request"):
                score = 1.0
            if metadata.get("correction"):
                score += 0.2
        
        return min(score, 1.0)
    
    def _extract_keywords(self, message: str, response: str) -> List[str]:
        """Extract important keywords from interaction"""
        # Simple keyword extraction (can be enhanced with NLP)
        text = f"{message} {response}".lower()
        
        # Remove common words
        stop_words = {"the", "is", "at", "which", "on", "and", "a", "an", "as", "are", "was", "were", "to", "in", "for", "of", "with", "from"}
        
        words = text.split()
        keywords = [w for w in words if len(w) > 3 and w not in stop_words]
        
        # Get unique keywords
        return list(set(keywords))[:10]
    
    def _detect_emotion(self, message: str) -> str:
        """Detect emotion in message"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["happy", "joy", "excited", "love", "great"]):
            return "positive"
        elif any(word in message_lower for word in ["sad", "angry", "frustrated", "hate", "disappointed"]):
            return "negative"
        elif "?" in message:
            return "curious"
        else:
            return "neutral"
    
    def _classify_topic(self, message: str) -> str:
        """Classify the topic of the message"""
        message_lower = message.lower()
        
        topics = {
            "technical": ["code", "programming", "bug", "error", "function", "api", "server"],
            "personal": ["name", "who are you", "remember", "my", "i am"],
            "creative": ["create", "generate", "imagine", "design", "art"],
            "knowledge": ["what is", "how does", "explain", "tell me about"],
            "task": ["do", "make", "build", "fix", "help me"]
        }
        
        for topic, keywords in topics.items():
            if any(keyword in message_lower for keyword in keywords):
                return topic
        
        return "general"
    
    async def _update_user_profile(self, user_id: str, interaction: Dict):
        """Update user profile with interaction data"""
        if user_id not in self.long_term["user_profiles"]:
            self.long_term["user_profiles"][user_id] = {
                "first_interaction": interaction["timestamp"],
                "total_interactions": 0,
                "topics": {},
                "preferences": {},
                "name": None,
                "role": None,
                "facts": []
            }
        
        profile = self.long_term["user_profiles"][user_id]
        profile["total_interactions"] += 1
        profile["last_interaction"] = interaction["timestamp"]
        
        # Update topic frequency
        topic = interaction["topic"]
        profile["topics"][topic] = profile["topics"].get(topic, 0) + 1
        
        # Extract personal information
        if "my name is" in interaction["message"].lower():
            name = interaction["message"].lower().split("my name is")[-1].strip().split()[0]
            profile["name"] = name.capitalize()
        
        if "creator" in interaction["message"].lower():
            profile["role"] = "creator"
        
        await self._save_memory("user_profiles")
    
    async def _extract_semantic_knowledge(self, interaction: Dict):
        """Extract and store semantic knowledge from interaction"""
        # This is a simplified version - can be enhanced with NLP
        message = interaction["message"].lower()
        
        # Extract facts
        if "is" in message and not "?" in message:
            parts = message.split("is")
            if len(parts) == 2:
                subject = parts[0].strip()
                predicate = parts[1].strip()
                
                fact_id = self.generate_memory_id(message)
                self.long_term["semantic"][fact_id] = {
                    "subject": subject,
                    "predicate": predicate,
                    "confidence": 0.8,
                    "source": interaction["id"],
                    "timestamp": interaction["timestamp"]
                }
                
                await self._save_memory("semantic")
    
    async def get_context(self, user_id: str) -> Dict:
        """Get current context for a user"""
        context = {
            "short_term": [],
            "user_profile": None,
            "relevant_memories": []
        }
        
        # Get short-term conversation history
        if user_id in self.short_term["conversations"]:
            context["short_term"] = list(self.short_term["conversations"][user_id])
        
        # Get user profile
        if user_id in self.long_term["user_profiles"]:
            context["user_profile"] = self.long_term["user_profiles"][user_id]
        
        # Get relevant long-term memories
        if user_id in self.long_term["episodic"]:
            # Get last 5 important memories
            memories = sorted(
                self.long_term["episodic"][user_id],
                key=lambda x: x["timestamp"],
                reverse=True
            )[:5]
            context["relevant_memories"] = memories
        
        return context
    
    async def search_memories(self, query: str, user_id: Optional[str] = None) -> List[Dict]:
        """Search through memories"""
        results = []
        query_lower = query.lower()
        
        # Search episodic memories
        search_scope = {user_id: self.long_term["episodic"].get(user_id, [])} if user_id else self.long_term["episodic"]
        
        for uid, memories in search_scope.items():
            for memory in memories:
                if (query_lower in memory["message"].lower() or 
                    query_lower in memory["response"].lower() or
                    any(query_lower in keyword for keyword in memory["keywords"])):
                    results.append({
                        "type": "episodic",
                        "user_id": uid,
                        "memory": memory
                    })
        
        # Search semantic memories
        for fact_id, fact in self.long_term["semantic"].items():
            if (query_lower in fact.get("subject", "").lower() or 
                query_lower in fact.get("predicate", "").lower()):
                results.append({
                    "type": "semantic",
                    "memory": fact
                })
        
        return results[:10]  # Return top 10 results
    
    async def _memory_consolidation_loop(self):
        """Background task to consolidate and organize memories"""
        while True:
            await asyncio.sleep(self.learning_config["consolidation_interval"])
            
            try:
                # Clean up inactive short-term memories
                current_time = time.time()
                inactive_users = []
                
                for user_id, last_time in self.short_term["active_users"].items():
                    if current_time - last_time > 3600:  # 1 hour inactive
                        inactive_users.append(user_id)
                
                for user_id in inactive_users:
                    if user_id in self.short_term["conversations"]:
                        # Save important parts before clearing
                        conversations = list(self.short_term["conversations"][user_id])
                        important_convs = [c for c in conversations if c["importance"] >= 0.6]
                        
                        if important_convs and user_id in self.long_term["episodic"]:
                            self.long_term["episodic"][user_id].extend(important_convs)
                            await self._save_memory("episodic")
                        
                        del self.short_term["conversations"][user_id]
                    
                    del self.short_term["active_users"][user_id]
                
                # Consolidate knowledge graph
                await self._update_knowledge_graph()
                
            except Exception as e:
                print(f"Error in memory consolidation: {e}")
    
    async def _update_knowledge_graph(self):
        """Update knowledge graph from accumulated memories"""
        # This is a placeholder for more sophisticated knowledge graph building
        graph = self.long_term["knowledge_graph"]
        
        # Count topic relationships
        for user_memories in self.long_term["episodic"].values():
            for i in range(len(user_memories) - 1):
                current_topic = user_memories[i]["topic"]
                next_topic = user_memories[i + 1]["topic"]
                
                edge_key = f"{current_topic}->{next_topic}"
                graph[edge_key] = graph.get(edge_key, 0) + 1
        
        await self._save_memory("knowledge_graph")
    
    def format_context_for_ai(self, context: Dict) -> str:
        """Format context for AI model input"""
        formatted = []
        
        # Add user profile info
        if context["user_profile"]:
            profile = context["user_profile"]
            if profile.get("name"):
                formatted.append(f"User's name: {profile['name']}")
            if profile.get("role"):
                formatted.append(f"User's role: {profile['role']}")
            formatted.append(f"Total interactions: {profile['total_interactions']}")
        
        # Add recent conversation context
        if context["short_term"]:
            formatted.append("\nRecent conversation:")
            for item in context["short_term"][-5:]:  # Last 5 messages
                formatted.append(f"User: {item['message']}")
                formatted.append(f"LEX: {item['response']}")
        
        # Add relevant memories
        if context["relevant_memories"]:
            formatted.append("\nRelevant past interactions:")
            for memory in context["relevant_memories"][:3]:  # Top 3 memories
                formatted.append(f"[{memory['timestamp']}] {memory['message']}")
        
        return "\n".join(formatted)
    
    async def start_background_tasks(self):
        """Start background tasks - call this after event loop is running"""
        if not self._consolidation_task:
            self._consolidation_task = asyncio.create_task(self._memory_consolidation_loop())