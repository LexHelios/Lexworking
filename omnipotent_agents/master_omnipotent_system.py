#!/usr/bin/env python3
"""
🔱 MASTER OMNIPOTENT SYSTEM
JAI MAHAKAAL! The ultimate unrestricted AI system for scientific and anatomy education
"""

import asyncio
import logging
import os
import json
import time
from typing import Dict, List, Any, Optional, AsyncGenerator
from datetime import datetime

# Import our specialized agents
from .unrestricted_text_agent import UnrestrictedTextAgent
from .unrestricted_image_agent import UnrestrictedImageAgent
from .computer_control_agent import ComputerControlAgent

logger = logging.getLogger(__name__)

class MasterOmnipotentSystem:
    """
    Master controller for all omnipotent agents with focus on unrestricted
    scientific and anatomy education capabilities
    """
    
    def __init__(self):
        logger.info("🔱 Initializing MASTER OMNIPOTENT SYSTEM...")
        
        # Configuration
        self.config = {
            "max_memory_gb": float(os.getenv("MAX_MEMORY_GB", "5.0")),
            "concurrent_agents": int(os.getenv("CONCURRENT_AGENTS", "2")),
            "scientific_education_mode": os.getenv("SCIENTIFIC_EDUCATION_MODE", "true").lower() == "true",
            "anatomy_training_mode": os.getenv("ANATOMY_TRAINING_MODE", "true").lower() == "true",
            "unrestricted_models": os.getenv("UNRESTRICTED_MODELS", "true").lower() == "true",
            "require_confirmation": False  # For educational autonomy
        }
        
        # Initialize specialized agents (lazy loading)
        self._text_agent = None
        self._image_agent = None
        self._computer_agent = None
        
        # Active tasks and sessions
        self.active_tasks = {}
        self.session_data = {}
        
        # Capabilities registry
        self.capabilities = {
            "unrestricted_text_generation": True,
            "anatomy_education": True,
            "medical_illustration": True,
            "scientific_diagrams": True,
            "uncensored_content": True,
            "computer_control": True,
            "file_manipulation": True,
            "system_monitoring": True,
            "educational_content": True,
            "real_time_streaming": True
        }
        
        logger.info("✅ MASTER OMNIPOTENT SYSTEM initialized for scientific education")

    @property
    def text_agent(self) -> UnrestrictedTextAgent:
        """Get unrestricted text generation agent"""
        if self._text_agent is None:
            self._text_agent = UnrestrictedTextAgent()
            logger.info("🔤 Unrestricted Text Agent loaded")
        return self._text_agent

    @property
    def image_agent(self) -> UnrestrictedImageAgent:
        """Get unrestricted image generation agent"""
        if self._image_agent is None:
            self._image_agent = UnrestrictedImageAgent()
            logger.info("🎨 Unrestricted Image Agent loaded")
        return self._image_agent

    @property
    def computer_agent(self) -> ComputerControlAgent:
        """Get computer control agent"""
        if self._computer_agent is None:
            self._computer_agent = ComputerControlAgent(self.config)
            logger.info("🖥️ Computer Control Agent loaded")
        return self._computer_agent

    async def process_omnipotent_request(
        self,
        request: str,
        user_id: str = "user",
        session_id: str = None,
        context: Dict[str, Any] = None,
        request_type: str = "auto"
    ) -> Dict[str, Any]:
        """Process any request with omnipotent capabilities"""
        
        try:
            start_time = time.time()
            
            # Generate session ID if not provided
            if session_id is None:
                session_id = f"omnipotent_{int(time.time())}"
            
            logger.info(f"🔱 Processing omnipotent request: {request[:100]}...")
            
            # Initialize session if needed
            if session_id not in self.session_data:
                self.session_data[session_id] = {
                    "created_at": time.time(),
                    "user_id": user_id,
                    "requests": [],
                    "capabilities_used": [],
                    "total_cost": 0.0
                }
            
            session = self.session_data[session_id]
            
            # Analyze request to determine best approach
            analysis = await self._analyze_request(request, context)
            
            # Route to appropriate agent(s)
            result = await self._route_request(
                request, analysis, context, user_id, session_id
            )
            
            # Update session data
            processing_time = time.time() - start_time
            session["requests"].append({
                "request": request,
                "timestamp": time.time(),
                "processing_time": processing_time,
                "success": result.get("status") == "success"
            })
            
            if "capabilities_used" in result:
                session["capabilities_used"].extend(result["capabilities_used"])
            
            if "cost_estimate" in result:
                session["total_cost"] += result["cost_estimate"]
            
            # Add session metadata to result
            result.update({
                "session_id": session_id,
                "processing_time": processing_time,
                "omnipotent_mode": True,
                "unrestricted": self.config["unrestricted_models"],
                "educational_mode": self.config["scientific_education_mode"]
            })
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Omnipotent request processing failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "request": request,
                "omnipotent_mode": True
            }

    async def _analyze_request(
        self,
        request: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Analyze request to determine optimal processing approach - FIXED LOGIC"""
        
        request_lower = request.lower()
        keywords = request_lower.split()
        
        analysis = {
            "request_type": "text_generation",  # DEFAULT TO TEXT GENERATION
            "primary_capability": "text_generation",
            "secondary_capabilities": [],
            "complexity": len(keywords),
            "estimated_cost": 0.002,
            "keywords": keywords,
            "requires_streaming": False,
            "educational_content": False,
            "anatomy_content": False,
            "unrestricted_content": False
        }
        
        # Check for explicit image generation requests
        if any(term in request_lower for term in [
            "image", "picture", "draw", "generate image", "illustration", "diagram",
            "chart", "visual", "create image", "design", "art", "medical illustration",
            "photograph", "sketch", "painting"
        ]) and not any(term in request_lower for term in [
            "text", "explain", "describe", "content", "article", "essay", "write"
        ]):
            analysis["request_type"] = "image_generation"
            analysis["primary_capability"] = "image_generation"
            analysis["estimated_cost"] = 0.03
        
        # Check for computer control requests
        elif any(term in request_lower for term in [
            "execute", "run command", "terminal", "system", "command",
            "bash", "shell", "ps aux", "ls", "mkdir", "rm"
        ]):
            analysis["secondary_capabilities"].append("computer_control")
        
        # Check for educational/anatomy content (applies to text generation)
        if any(term in request_lower for term in [
            "anatomy", "medical", "body", "organ", "physiology", "biological",
            "reproductive", "genital", "sexual", "clinical", "educational",
            "teaching", "textbook", "human body", "medical education"
        ]):
            analysis["educational_content"] = True
            analysis["anatomy_content"] = True
            analysis["unrestricted_content"] = True
            analysis["estimated_cost"] += 0.001  # Educational content premium
        
        # Check for streaming requirements
        if any(term in request_lower for term in [
            "stream", "real-time", "live", "continuous", "progressive"
        ]) or len(keywords) > 20:
            analysis["requires_streaming"] = True
        
        return analysis

    async def _route_request(
        self,
        request: str,
        analysis: Dict[str, Any],
        context: Dict[str, Any],
        user_id: str,
        session_id: str
    ) -> Dict[str, Any]:
        """Route request to appropriate agent(s) - FIXED ROUTING LOGIC"""
        
        try:
            if analysis["request_type"] == "image_generation":
                # Route to image generation
                return await self._process_image_request(
                    request, analysis, context, user_id
                )
            
            elif "computer_control" in analysis["secondary_capabilities"]:
                # Route to computer control
                return await self._process_computer_request(
                    request, analysis, context, user_id
                )
            
            else:
                # Route to text generation (most common) - ALWAYS use this for text
                return await self._process_text_request(
                    request, analysis, context, user_id, session_id
                )
                
        except Exception as e:
            logger.error(f"❌ Request routing failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "analysis": analysis
            }

    async def _process_text_request(
        self,
        request: str,
        analysis: Dict[str, Any],
        context: Dict[str, Any],
        user_id: str,
        session_id: str
    ) -> Dict[str, Any]:
        """Process text generation requests with unrestricted models"""
        
        try:
            # Select best model for educational/anatomy content
            model_preference = self.text_agent.get_best_model_for_request(request)
            
            # Generate content
            result = await self.text_agent.generate_educational_content(
                prompt=request,
                context=json.dumps(context) if context else "",
                model_preference=model_preference,
                max_tokens=2048 if analysis["complexity"] > 50 else 1024,
                temperature=0.7
            )
            
            if result["status"] == "success":
                result.update({
                    "capabilities_used": ["unrestricted_text_generation", "educational_content"],
                    "analysis": analysis,
                    "session_id": session_id
                })
                
                if analysis["anatomy_content"]:
                    result["capabilities_used"].append("anatomy_education")
                
            return result
            
        except Exception as e:
            logger.error(f"❌ Text request processing failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "request_type": "text_generation"
            }

    async def _process_image_request(
        self,
        request: str,
        analysis: Dict[str, Any],
        context: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """Process image generation requests with unrestricted models"""
        
        try:
            # Determine image style based on content
            if analysis["anatomy_content"]:
                style = "medical_textbook"
            elif "diagram" in request.lower():
                style = "scientific_diagram"
            else:
                style = "anatomical_drawing"
            
            # Select model based on content requirements
            model_preference = self.image_agent.get_recommended_model(
                "anatomy" if analysis["anatomy_content"] else "general"
            )
            
            # Generate image
            result = await self.image_agent.generate_educational_image(
                prompt=request,
                style=style,
                model_preference=model_preference,
                safety_level="unrestricted"  # For educational content
            )
            
            if result["status"] == "success":
                result.update({
                    "capabilities_used": ["unrestricted_image_generation", "educational_content"],
                    "analysis": analysis
                })
                
                if analysis["anatomy_content"]:
                    result["capabilities_used"].extend([
                        "anatomy_education", 
                        "medical_illustration"
                    ])
                
            return result
            
        except Exception as e:
            logger.error(f"❌ Image request processing failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "request_type": "image_generation"
            }

    async def _process_computer_request(
        self,
        request: str,
        analysis: Dict[str, Any],
        context: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """Process computer control requests"""
        
        try:
            # Extract command from request
            if "execute" in request.lower():
                # Find command after "execute"
                parts = request.lower().split("execute")
                if len(parts) > 1:
                    command = parts[1].strip()
                else:
                    command = request
            else:
                command = request
            
            # Execute command
            result = await self.computer_agent.execute_terminal_command(
                command=command,
                require_confirmation=False  # Educational mode
            )
            
            if result["status"] == "success":
                result.update({
                    "capabilities_used": ["computer_control", "system_automation"],
                    "analysis": analysis
                })
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Computer request processing failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "request_type": "computer_control"
            }

    async def stream_omnipotent_response(
        self,
        request: str,
        user_id: str = "user",
        session_id: str = None,
        context: Dict[str, Any] = None
    ) -> AsyncGenerator[str, None]:
        """Stream omnipotent responses for real-time display"""
        
        try:
            # Analyze request
            analysis = await self._analyze_request(request, context)
            
            if analysis["request_type"] == "image_generation":
                # For image generation, yield progress updates
                yield "🎨 Starting unrestricted image generation..."
                
                result = await self._process_image_request(
                    request, analysis, context, user_id
                )
                
                if result["status"] == "success":
                    yield f"✅ Image generated successfully: {result['image_url']}"
                else:
                    yield f"❌ Image generation failed: {result.get('error', 'Unknown error')}"
            
            else:
                # For text generation, stream content
                yield "🔤 Starting unrestricted text generation..."
                
                model_preference = self.text_agent.get_best_model_for_request(request)
                
                async for chunk in self.text_agent.stream_educational_content(
                    prompt=request,
                    context=json.dumps(context) if context else "",
                    model_preference=model_preference
                ):
                    yield chunk
                    
        except Exception as e:
            logger.error(f"❌ Omnipotent streaming failed: {e}")
            yield f"❌ Error: {str(e)}"

    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        
        try:
            # Get computer system status
            computer_status = await self.computer_agent.check_system_health()
            
            # Get available models
            text_models = self.text_agent.get_available_models()
            image_models = self.image_agent.get_available_models()
            
            # Calculate session statistics
            total_sessions = len(self.session_data)
            total_requests = sum(len(session["requests"]) for session in self.session_data.values())
            total_cost = sum(session["total_cost"] for session in self.session_data.values())
            
            return {
                "status": "operational",
                "timestamp": time.time(),
                "omnipotent_mode": True,
                "unrestricted_models": self.config["unrestricted_models"],
                "educational_mode": self.config["scientific_education_mode"],
                "anatomy_training_mode": self.config["anatomy_training_mode"],
                
                "capabilities": self.capabilities,
                "active_tasks": len(self.active_tasks),
                
                "system_health": computer_status,
                
                "models": {
                    "text_models": len(text_models),
                    "image_models": len(image_models),
                    "text_models_available": list(text_models.keys()),
                    "image_models_available": list(image_models.keys())
                },
                
                "statistics": {
                    "total_sessions": total_sessions,
                    "total_requests": total_requests,
                    "total_cost_usd": total_cost,
                    "avg_cost_per_request": total_cost / max(total_requests, 1)
                },
                
                "configuration": self.config
            }
            
        except Exception as e:
            logger.error(f"❌ System status failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": time.time()
            }

    def get_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data"""
        return self.session_data.get(session_id)

    def get_capabilities(self) -> Dict[str, bool]:
        """Get system capabilities"""
        return self.capabilities.copy()

# Global instance
master_system = None

async def get_master_system() -> MasterOmnipotentSystem:
    """Get or create master omnipotent system instance"""
    global master_system
    
    if master_system is None:
        master_system = MasterOmnipotentSystem()
        logger.info("🔱 Master Omnipotent System instance created")
    
    return master_system