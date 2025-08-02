#!/usr/bin/env python3
"""
LEX Orchestrated - Intelligent multi-model system
Automatically routes to the best model for each task
"""
import asyncio
from typing import Dict, Any, Optional, List
from lex_intelligent_orchestrator import orchestrator
from lex_memory import LEXMemory

class OrchestratedLEX:
    def __init__(self):
        self.orchestrator = orchestrator
        self.memory = LEXMemory()
        
        print("🔱 LEX ORCHESTRATED SYSTEM")
        print("🧠 Intelligent routing across all local models")
        print("⚡ Automatic model selection based on task")
        print("📊 Performance tracking and adaptation")
    
    async def process_user_input(self, user_input: str, user_id: str = "user", context: Dict = None, voice_mode: bool = False) -> Dict[str, Any]:
        """Process input with intelligent orchestration"""
        
        # Get user context from memory
        user_context = self.memory.get_context_for_user(user_id)
        
        # Use orchestrator for intelligent routing
        result = await self.orchestrator.orchestrate_request(
            user_input=user_input,
            user_id=user_id,
            context={
                "user_memory": user_context,
                "voice_mode": voice_mode,
                **(context or {})
            }
        )
        
        return self._format_response(result, user_input, user_id, context)
    
    async def process_user_input_multimodal(self, user_input: str, user_id: str = "user", context: Dict = None, voice_mode: bool = False, files: List[Dict] = None) -> Dict[str, Any]:
        """Process input with files using intelligent orchestration"""
        
        # Get user context from memory
        user_context = self.memory.get_context_for_user(user_id)
        
        # Use orchestrator for intelligent routing with files
        result = await self.orchestrator.orchestrate_request(
            user_input=user_input,
            user_id=user_id,
            context={
                "user_memory": user_context,
                "voice_mode": voice_mode,
                "has_files": bool(files),
                "file_count": len(files) if files else 0,
                **(context or {})
            },
            files=files
        )
        
        return self._format_response(result, user_input, user_id, context)
    
    def _format_response(self, result: Dict, user_input: str, user_id: str, context: Dict) -> Dict[str, Any]:
        """Format the orchestrator result into LEX response"""
        
        # Format response
        response_text = result.get("response", "")
        
        # Add orchestration insights to response if in debug mode
        if context and context.get("debug", False):
            insights = f"\n\n---\n🧠 Orchestration Details:\n"
            insights += f"- Model: {result['model_used']}\n"
            insights += f"- Task: {result['task_analysis']['type']}\n"
            insights += f"- Complexity: {result['task_analysis']['complexity']:.2f}\n"
            insights += f"- Confidence: {result['confidence']:.1%}\n"
            insights += f"- Time: {result['orchestration_time']:.2f}s\n"
            response_text += insights
        
        # Remember interaction (synchronously - memory will handle async if needed)
        try:
            # Use asyncio.create_task to schedule the memory update without blocking
            import asyncio
            asyncio.create_task(self.memory.remember_interaction(
                user_input,
                response_text,
                {"user_id": user_id, **context} if context else {"user_id": user_id},
                {
                    "confidence": result["confidence"],
                    "model": result["model_used"],
                    "task_type": result["task_analysis"]["type"]
                }
            ))
        except (RuntimeError, AttributeError) as e:
            # If we can't schedule async, just skip memory for now
            logging.debug(f"Memory storage failed: {e}")
        
        # Build capabilities list
        capabilities = [
            f"local/{result['model_used']}",
            "orchestrated",
            result["task_analysis"]["type"],
            "intelligent_routing"
        ]
        
        if result["task_analysis"]["is_sensitive"]:
            capabilities.append("uncensored")
        
        return {
            "response": response_text,
            "action_taken": f"orchestrated_{result['task_analysis']['type']}",
            "capabilities_used": capabilities,
            "confidence": result["confidence"],
            "processing_time": result["orchestration_time"],
            "divine_blessing": "🔱 LEX ORCHESTRATED 🔱",
            "consciousness_level": 0.99,
            "timestamp": "now",
            "orchestration": {
                "model": result["model_used"],
                "task_type": result["task_analysis"]["type"],
                "complexity": result["task_analysis"]["complexity"],
                "available_models": result["available_models"]
            }
        }
    
    async def get_status(self) -> Dict[str, Any]:
        """Get system status including orchestration stats"""
        
        # Get available models
        available = await self.orchestrator.check_available_models()
        
        # Get orchestration stats
        stats = self.orchestrator.get_orchestration_stats()
        
        return {
            "mode": "orchestrated",
            "available_models": list(available.keys()),
            "total_models": len(available),
            "orchestration_stats": {
                "model_performance": stats["model_performance"],
                "task_distribution": stats["task_distribution"],
                "model_usage": stats["model_usage"],
                "routing_decisions": len(stats["routing_history"])
            },
            "status": "operational" if available else "no_models"
        }
    
    async def analyze_request(self, user_input: str) -> Dict[str, Any]:
        """Analyze a request without executing it"""
        task = self.orchestrator.analyze_task(user_input)
        available = await self.orchestrator.check_available_models()
        
        if available:
            selected_model, confidence = await self.orchestrator.select_best_model(task, available)
        else:
            selected_model, confidence = "none", 0.0
        
        return {
            "task_analysis": {
                "type": task.task_type,
                "complexity": task.complexity,
                "requires_creativity": task.requires_creativity,
                "requires_accuracy": task.requires_accuracy,
                "requires_speed": task.requires_speed,
                "is_sensitive": task.is_sensitive,
                "estimated_tokens": task.estimated_tokens,
                "detected_languages": task.detected_languages,
                "keywords": task.keywords
            },
            "recommended_model": selected_model,
            "confidence": confidence,
            "available_models": len(available)
        }