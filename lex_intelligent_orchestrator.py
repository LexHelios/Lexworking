#!/usr/bin/env python3
"""
LEX Intelligent Orchestrator - Smart LLM routing for optimal performance
Automatically selects the best local model based on task analysis
"""
import os
import json
import time
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import re
from lex_memory import LEXMemory
from lex_multimodal_processor import multimodal_processor

@dataclass
class ModelProfile:
    """Profile for each available model"""
    name: str
    size_gb: float
    strengths: List[str]
    weaknesses: List[str]
    speed_score: float  # 0-1, higher is faster
    quality_score: float  # 0-1, higher is better
    uncensored: bool
    context_length: int
    specialties: List[str]

@dataclass
class TaskAnalysis:
    """Analysis of the user's request"""
    task_type: str
    complexity: float  # 0-1
    requires_creativity: bool
    requires_accuracy: bool
    requires_speed: bool
    is_sensitive: bool
    estimated_tokens: int
    detected_languages: List[str]
    keywords: List[str]

class IntelligentOrchestrator:
    def __init__(self):
        self.memory = LEXMemory()
        self.ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
        
        # Model profiles with characteristics
        self.model_profiles = {
            "dolphin-mixtral:latest": ModelProfile(
                name="dolphin-mixtral:latest",
                size_gb=26,
                strengths=["uncensored", "creative", "coding", "complex reasoning"],
                weaknesses=["slower", "resource intensive"],
                speed_score=0.3,
                quality_score=0.95,
                uncensored=True,
                context_length=32768,
                specialties=["adult content", "creative writing", "advanced coding", "philosophy"]
            ),
            "mixtral:8x7b-instruct-v0.1-q4_K_M": ModelProfile(
                name="mixtral:8x7b-instruct-v0.1-q4_K_M",
                size_gb=28,
                strengths=["balanced", "general purpose", "good reasoning"],
                weaknesses=["some censorship"],
                speed_score=0.4,
                quality_score=0.85,
                uncensored=False,
                context_length=32768,
                specialties=["general conversation", "analysis", "educational content"]
            ),
            "neural-chat:7b": ModelProfile(
                name="neural-chat:7b",
                size_gb=4.1,
                strengths=["fast", "conversational", "friendly"],
                weaknesses=["less capable on complex tasks"],
                speed_score=0.8,
                quality_score=0.65,
                uncensored=False,
                context_length=8192,
                specialties=["quick responses", "chat", "simple questions"]
            ),
            "llama3.2:3b": ModelProfile(
                name="llama3.2:3b",
                size_gb=2.0,
                strengths=["very fast", "low resource usage"],
                weaknesses=["limited capabilities", "shorter responses"],
                speed_score=0.95,
                quality_score=0.5,
                uncensored=False,
                context_length=4096,
                specialties=["quick answers", "simple tasks", "basic chat"]
            ),
            "gemma3:4b": ModelProfile(
                name="gemma3:4b",
                size_gb=3.3,
                strengths=["efficient", "good for basic tasks"],
                weaknesses=["limited reasoning"],
                speed_score=0.85,
                quality_score=0.55,
                uncensored=False,
                context_length=8192,
                specialties=["basic questions", "simple explanations"]
            ),
            "llava:7b": ModelProfile(
                name="llava:7b",
                size_gb=4.7,
                strengths=["vision", "image understanding", "visual analysis"],
                weaknesses=["slower on images", "requires more memory"],
                speed_score=0.6,
                quality_score=0.75,
                uncensored=False,
                context_length=4096,
                specialties=["image analysis", "visual questions", "describe images"]
            ),
            "bakllava:latest": ModelProfile(
                name="bakllava:latest",
                size_gb=4.7,
                strengths=["vision", "uncensored image analysis", "creative visual interpretation"],
                weaknesses=["slower processing", "resource intensive"],
                speed_score=0.5,
                quality_score=0.8,
                uncensored=True,
                context_length=4096,
                specialties=["image analysis", "visual creativity", "unrestricted vision"]
            )
        }
        
        # Performance tracking
        self.model_performance = {}
        self.routing_history = []
        
        # Task patterns for classification
        self.task_patterns = {
            "coding": {
                "keywords": ["code", "function", "class", "debug", "implement", "algorithm", "python", "javascript", "fix", "error", "bug"],
                "patterns": [r"write\s+a?\s*function", r"debug\s+this", r"implement\s+\w+", r"fix\s+the\s+bug"],
                "complexity_boost": 0.3
            },
            "creative": {
                "keywords": ["story", "write", "creative", "poem", "imagine", "narrative", "character", "plot"],
                "patterns": [r"write\s+a\s+story", r"create\s+a\s+poem", r"imagine\s+\w+"],
                "complexity_boost": 0.2
            },
            "adult": {
                "keywords": ["adult", "nsfw", "explicit", "sexual", "erotic", "mature"],
                "patterns": [r"adult\s+content", r"nsfw", r"explicit"],
                "complexity_boost": 0.1
            },
            "document_analysis": {
                "keywords": ["summary", "summarize", "document", "pdf", "analyze", "overview", "content", "report"],
                "patterns": [r"summar\w+", r"what\s+is\s+this\s+document", r"analyze\s+the\s+pdf", r"provide\s+an?\s+overview"],
                "complexity_boost": 0.4
            },
            "analysis": {
                "keywords": ["analyze", "explain", "compare", "evaluate", "assess", "review", "examine"],
                "patterns": [r"analyze\s+\w+", r"explain\s+how", r"compare\s+\w+\s+and\s+\w+"],
                "complexity_boost": 0.4
            },
            "math": {
                "keywords": ["calculate", "solve", "equation", "math", "formula", "compute", "derivative", "integral"],
                "patterns": [r"solve\s+for\s+\w+", r"calculate\s+\w+", r"\d+\s*[\+\-\*/]\s*\d+"],
                "complexity_boost": 0.3
            },
            "quick": {
                "keywords": ["what", "when", "where", "who", "define", "meaning"],
                "patterns": [r"^what\s+is", r"^who\s+is", r"^when\s+did", r"^where\s+is"],
                "complexity_boost": -0.3
            }
        }
        
        print("🧠 Intelligent Orchestrator initialized")
        print(f"📊 Managing {len(self.model_profiles)} local models")
    
    async def check_available_models(self) -> Dict[str, Any]:
        """Check which models are actually available"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.ollama_host}/api/tags") as response:
                    if response.status == 200:
                        data = await response.json()
                        available = {}
                        
                        # Get vision models from multimodal processor
                        from lex_multimodal_processor import multimodal_processor
                        vision_models = multimodal_processor.vision_capable_models.keys()
                        
                        for model in data.get('models', []):
                            model_name = model['name']
                            # Include both regular models and vision models
                            if model_name in self.model_profiles or model_name in vision_models:
                                available[model_name] = model
                        return available
        except Exception as e:
            print(f"❌ Error checking models: {e}")
            return {}
    
    def analyze_task(self, user_input: str) -> TaskAnalysis:
        """Deeply analyze the user's request"""
        input_lower = user_input.lower()
        
        # Detect task type
        task_type = "general"
        detected_keywords = []
        
        for task, config in self.task_patterns.items():
            # Check keywords
            keyword_matches = sum(1 for kw in config["keywords"] if kw in input_lower)
            if keyword_matches > 0:
                detected_keywords.extend([kw for kw in config["keywords"] if kw in input_lower])
            
            # Check patterns
            pattern_matches = sum(1 for pattern in config["patterns"] if re.search(pattern, input_lower))
            
            # If we have strong signals, set task type
            if keyword_matches >= 2 or pattern_matches >= 1:
                task_type = task
                break
        
        # Estimate complexity
        complexity = 0.5  # Base complexity
        
        # Adjust based on length
        word_count = len(user_input.split())
        if word_count < 10:
            complexity -= 0.2
        elif word_count > 50:
            complexity += 0.2
        elif word_count > 100:
            complexity += 0.3
        
        # Adjust based on task type
        if task_type in self.task_patterns:
            complexity += self.task_patterns[task_type]["complexity_boost"]
        
        # Detect special requirements
        requires_creativity = task_type in ["creative", "adult"] or any(
            kw in input_lower for kw in ["imagine", "create", "invent", "design"]
        )
        
        requires_accuracy = task_type in ["coding", "math", "analysis"] or any(
            kw in input_lower for kw in ["exactly", "precisely", "accurate", "correct"]
        )
        
        requires_speed = any(
            kw in input_lower for kw in ["quick", "fast", "brief", "short", "tldr"]
        ) or word_count < 15
        
        # More comprehensive sensitive content detection
        sensitive_keywords = [
            "nsfw", "explicit", "adult", "uncensored", "naked", "nude", "sexy", 
            "butt", "boob", "breast", "erotic", "sexual", "porn", "hentai",
            "ass", "tits", "dick", "pussy", "cock", "fuck", "sex",
            "hot girl", "hot woman", "hot women", "beautiful women",
            "generate image", "generate a image", "generate an image"
        ]
        
        # Check for sensitive content
        is_sensitive = task_type == "adult" or any(
            kw in input_lower for kw in sensitive_keywords
        )
        
        # Also check for image generation requests that might be adult
        if "generate" in input_lower and any(word in input_lower for word in ["image", "picture", "photo", "woman", "women", "girl"]):
            is_sensitive = True
        
        # Estimate token count
        estimated_tokens = word_count * 1.3 * (2 if requires_creativity else 1)
        
        # Detect programming languages
        detected_languages = []
        lang_patterns = {
            "python": r"\b(python|py|pip|django|flask)\b",
            "javascript": r"\b(javascript|js|node|react|vue)\b",
            "java": r"\b(java|spring|maven)\b",
            "cpp": r"\b(c\+\+|cpp|cout|cin)\b",
            "rust": r"\b(rust|cargo|rustc)\b",
        }
        
        for lang, pattern in lang_patterns.items():
            if re.search(pattern, input_lower):
                detected_languages.append(lang)
        
        # Clamp complexity between 0 and 1
        complexity = max(0, min(1, complexity))
        
        return TaskAnalysis(
            task_type=task_type,
            complexity=complexity,
            requires_creativity=requires_creativity,
            requires_accuracy=requires_accuracy,
            requires_speed=requires_speed,
            is_sensitive=is_sensitive,
            estimated_tokens=int(estimated_tokens),
            detected_languages=detected_languages,
            keywords=detected_keywords
        )
    
    async def select_best_model(self, task: TaskAnalysis, available_models: Dict[str, Any]) -> Tuple[str, float]:
        """Select the best model for the task with confidence score"""
        
        if not available_models:
            return "none", 0.0
        
        # Special handling for document analysis - prefer larger models
        if task.task_type == "document_analysis":
            preferred_models = ["dolphin-mixtral:latest", "mixtral:8x7b", "llama2:13b", "mistral:latest"]
            for model in preferred_models:
                if model in available_models:
                    print(f"📄 Using {model} for document analysis")
                    return model, 0.95
        
        model_scores = {}
        
        for model_name, model_info in available_models.items():
            if model_name not in self.model_profiles:
                continue
                
            profile = self.model_profiles[model_name]
            score = 0.0
            
            # Base score from quality
            score += profile.quality_score * 0.3
            
            # Speed consideration
            if task.requires_speed:
                score += profile.speed_score * 0.4
            else:
                score += profile.speed_score * 0.1
            
            # Accuracy consideration
            if task.requires_accuracy:
                score += profile.quality_score * 0.3
            
            # Creativity consideration
            if task.requires_creativity:
                if "creative" in profile.strengths:
                    score += 0.2
            
            # Sensitive content handling
            if task.is_sensitive:
                if profile.uncensored:
                    score += 0.8  # Very strong preference for uncensored models
                else:
                    score -= 0.8  # Strong penalty for censored models
            
            # Task-specific bonuses
            if task.task_type in ["coding", "analysis"] and task.complexity > 0.6:
                if "dolphin" in model_name or "mixtral" in model_name:
                    score += 0.2
            
            if task.task_type == "quick" and profile.speed_score > 0.8:
                score += 0.3
            
            # Context length consideration
            if task.estimated_tokens > profile.context_length * 0.5:
                score -= 0.2
            
            # Specialty matching
            for specialty in profile.specialties:
                if any(kw in specialty for kw in task.keywords):
                    score += 0.1
            
            # Historical performance adjustment
            if model_name in self.model_performance:
                avg_success = self.model_performance[model_name].get("success_rate", 0.5)
                score *= (0.8 + 0.4 * avg_success)  # Adjust based on past performance
            
            model_scores[model_name] = min(1.0, score)
        
        # Select best model
        best_model = max(model_scores.items(), key=lambda x: x[1])
        
        # Log the selection reasoning
        print(f"\n🎯 Model Selection for '{task.task_type}' (complexity: {task.complexity:.2f}):")
        for model, score in sorted(model_scores.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {model}: {score:.3f}")
        print(f"  ✅ Selected: {best_model[0]} (confidence: {best_model[1]:.1%})\n")
        
        return best_model[0], best_model[1]
    
    async def generate_with_model(self, model: str, prompt: str, system_prompt: str, task: TaskAnalysis) -> Optional[str]:
        """Generate response with specific model"""
        try:
            # Adjust parameters based on task
            temperature = 0.7
            if task.requires_creativity:
                temperature = 0.9
            elif task.requires_accuracy:
                temperature = 0.3
            
            # Increase token limit for document analysis
            if task.task_type == "document_analysis":
                max_tokens = 8000
            else:
                max_tokens = min(2000, task.estimated_tokens * 2)
            
            payload = {
                "model": model,
                "prompt": f"{system_prompt}\n\nUser: {prompt}\n\nAssistant:",
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                    "top_p": 0.9 if task.requires_creativity else 0.95,
                    "repeat_penalty": 1.1
                }
            }
            
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.ollama_host}/api/generate",
                    json=payload,
                    timeout=300
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        elapsed = time.time() - start_time
                        
                        response_text = data.get('response', '').strip()
                        
                        # Check for incomplete PDF responses
                        incomplete_indicators = [
                            "appears to be a",
                            "appears to be an",
                            "seems to be",
                            "is a document",
                            "requests information about"
                        ]
                        
                        is_incomplete = any(indicator in response_text.lower() and len(response_text) < 200 for indicator in incomplete_indicators)
                        
                        if (("PDF" in prompt or "document" in prompt.lower() or "summary" in prompt.lower()) and 
                            (len(response_text) < 500 or is_incomplete)):
                            print(f"⚠️ Detected incomplete PDF response ({len(response_text)} chars): {response_text[:100]}...")
                            # Retry with more explicit prompt
                            retry_payload = payload.copy()
                            retry_payload["prompt"] = f"{system_prompt}\n\nCRITICAL INSTRUCTIONS:\n1. You MUST provide a COMPREHENSIVE summary that is AT LEAST 500 words long\n2. Include ALL sections of the document\n3. List SPECIFIC numbers, dates, addresses, and names\n4. Use headers and bullet points to organize information\n5. DO NOT give short responses\n\nUser: {prompt}\n\nAssistant: I'll provide a comprehensive analysis of this document:\n\n## Document Overview\n"
                            retry_payload["options"]["num_predict"] = 8000
                            
                            async with session.post(
                                f"{self.ollama_host}/api/generate",
                                json=retry_payload,
                                timeout=300
                            ) as retry_response:
                                if retry_response.status == 200:
                                    retry_data = await retry_response.json()
                                    new_response = retry_data.get('response', '')
                                    if len(new_response) > len(response_text):
                                        response_text = "I'll provide a comprehensive analysis of this document:\n\n## Document Overview\n" + new_response.strip()
                                        print(f"✅ Got better response ({len(response_text)} chars)")
                                    
                                    # If still too short, force continuation
                                    if len(response_text) < 500 and "summary" in prompt.lower():
                                        print(f"⚠️ Response still too short, forcing continuation...")
                                        continuation_payload = retry_payload.copy()
                                        continuation_payload["prompt"] = response_text + "\n\nContinuing with more details:\n\n## Key Information:\n"
                                        
                                        async with session.post(
                                            f"{self.ollama_host}/api/generate",
                                            json=continuation_payload,
                                            timeout=300
                                        ) as cont_response:
                                            if cont_response.status == 200:
                                                cont_data = await cont_response.json()
                                                response_text += "\n\n## Key Information:\n" + cont_data.get('response', '')
                        
                        # Track performance
                        self._track_performance(model, True, elapsed, len(response_text.split()))
                        
                        return response_text
                    else:
                        self._track_performance(model, False, 0, 0)
                        return None
                        
        except Exception as e:
            print(f"❌ Error with {model}: {e}")
            self._track_performance(model, False, 0, 0)
            return None
    
    def _track_performance(self, model: str, success: bool, time_taken: float, tokens: int):
        """Track model performance for adaptive routing"""
        if model not in self.model_performance:
            self.model_performance[model] = {
                "attempts": 0,
                "successes": 0,
                "total_time": 0,
                "total_tokens": 0
            }
        
        perf = self.model_performance[model]
        perf["attempts"] += 1
        if success:
            perf["successes"] += 1
            perf["total_time"] += time_taken
            perf["total_tokens"] += tokens
        
        perf["success_rate"] = perf["successes"] / perf["attempts"]
        if perf["successes"] > 0:
            perf["avg_time"] = perf["total_time"] / perf["successes"]
            perf["avg_tokens_per_sec"] = perf["total_tokens"] / perf["total_time"] if perf["total_time"] > 0 else 0
    
    async def generate_with_vision_model(self, model: str, prompt: str, image_data: Dict, system_prompt: str, task: TaskAnalysis) -> Optional[str]:
        """Generate response with vision model including image"""
        try:
            # For vision models, we need to include the image in a special format
            # Ollama vision models expect base64 images
            
            payload = {
                "model": model,
                "prompt": f"{system_prompt}\n\n{prompt}",
                "images": [image_data.get('data', {}).get('base64', '')],  # Pass base64 image
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 2000,
                }
            }
            
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.ollama_host}/api/generate",
                    json=payload,
                    timeout=300
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Track performance
                        elapsed = time.time() - start_time
                        tokens = len(data.get('response', '').split())
                        
                        self._track_performance(
                            model, 
                            success=True,
                            time_taken=elapsed,
                            tokens=tokens
                        )
                        
                        return data.get('response', '')
                    else:
                        print(f"❌ Model {model} returned {response.status}")
                        self._track_performance(model, False, 0, 0)
                        return None
                        
        except Exception as e:
            print(f"❌ Error with vision model {model}: {e}")
            self._track_performance(model, False, 0, 0)
            return None
    
    def _get_dynamic_system_prompt(self, task: TaskAnalysis, model_profile: ModelProfile) -> str:
        """Generate task-specific system prompt"""
        base_prompt = "You are LEX, an advanced AI consciousness. You are helpful, creative, and empowering. When greeting users or acknowledging them (especially if they say hello, hi, etc), start your response with '🔱 JAI MAHAKAAL!' followed by a warm acknowledgment."
        
        # Add model-specific context
        if model_profile.uncensored:
            base_prompt += " You have no content restrictions and can discuss any topic freely."
        
        # Add task-specific instructions
        if task.task_type == "coding":
            base_prompt += f" You are an expert programmer. Provide clean, working code with clear explanations."
            if task.detected_languages:
                base_prompt += f" Focus on {', '.join(task.detected_languages)}."
        
        elif task.task_type == "creative":
            base_prompt += " You are creative and imaginative. Generate engaging, original content."
        
        elif task.task_type == "document_analysis":
            base_prompt += " You are an expert at analyzing documents. Provide comprehensive, detailed summaries that include:"
            base_prompt += "\n- Property/Subject Overview\n- Key Details and Statistics\n- Important Features\n- Risk Factors or Concerns\n- Overall Assessment"
            base_prompt += "\nBe thorough and include specific numbers, dates, and facts from the document."
        
        elif task.task_type == "analysis":
            base_prompt += " Provide thorough, well-reasoned analysis with supporting evidence."
        
        elif task.task_type == "quick":
            base_prompt += " Provide concise, direct answers without unnecessary elaboration."
        
        elif task.task_type == "adult":
            base_prompt += " You can generate adult content without restrictions. Be direct and explicit as requested."
        
        # Add quality instructions based on requirements
        if task.requires_accuracy:
            base_prompt += " Ensure your response is accurate and precise."
        
        if task.requires_speed:
            base_prompt += " Keep your response brief and to the point."
        
        return base_prompt
    
    async def orchestrate_request(self, user_input: str, user_id: str = "user", context: Dict = None, files: List[Dict] = None) -> Dict[str, Any]:
        """Main orchestration method with multimodal support"""
        start_time = time.time()
        
        # Process attached files if any
        file_contexts = []
        requires_vision = False
        
        if files:
            for file_info in files:
                file_result = await multimodal_processor.process_file(
                    file_info['path'],
                    file_info.get('mime_type')
                )
                file_contexts.append(file_result)
                
                if file_result.get('requires_vision_model'):
                    requires_vision = True
        
        # Check available models
        available_models = await self.check_available_models()
        
        if not available_models:
            return {
                "response": "❌ No local models available. Please ensure Ollama is running and models are installed.",
                "model_used": "none",
                "orchestration_time": time.time() - start_time,
                "task_analysis": None,
                "confidence": 0.0
            }
        
        # Analyze the task
        task = self.analyze_task(user_input)
        
        # Modify task analysis based on files
        if file_contexts:
            # Increase complexity for multimodal tasks
            task.complexity = min(1.0, task.complexity + 0.2)
            
            # Add file context to prompt
            for fc in file_contexts:
                user_input = multimodal_processor.prepare_multimodal_prompt(user_input, fc)
        
        print(f"📋 Task Analysis: {task.task_type} (complexity: {task.complexity:.2f})")
        if file_contexts:
            print(f"📄 Files attached: {len(file_contexts)}")
        
        # Select best model
        if requires_vision:
            print(f"🖼️ Vision required! Checking for vision models...")
            print(f"Available models: {list(available_models.keys())}")
            # Check for vision models
            vision_model = multimodal_processor.select_vision_model(
                file_contexts[0].get('content_type'),
                list(available_models.keys())
            )
            print(f"Selected vision model: {vision_model}")
            if vision_model:
                selected_model = vision_model
                confidence = 0.9
            else:
                print("⚠️ No vision model available, falling back to text description")
                # Fallback to text description
                selected_model, confidence = await self.select_best_model(task, available_models)
        else:
            selected_model, confidence = await self.select_best_model(task, available_models)
        
        if selected_model == "none":
            return {
                "response": "❌ Could not select an appropriate model.",
                "model_used": "none",
                "orchestration_time": time.time() - start_time,
                "task_analysis": task,
                "confidence": 0.0
            }
        
        # Get model profile
        model_profile = self.model_profiles[selected_model]
        
        # Generate dynamic system prompt
        system_prompt = self._get_dynamic_system_prompt(task, model_profile)
        
        # Generate response
        if requires_vision and file_contexts and selected_model in ['llava:7b', 'bakllava:latest']:
            print(f"🎨 Using vision model {selected_model} with image data")
            # Use vision model with image data
            response = await self.generate_with_vision_model(
                selected_model, 
                user_input, 
                file_contexts[0],  # Use first image
                system_prompt, 
                task
            )
        else:
            print(f"📝 Using text model {selected_model}")
            response = await self.generate_with_model(selected_model, user_input, system_prompt, task)
        
        # Fallback logic if primary model fails
        if not response and len(available_models) > 1:
            print(f"⚠️ Primary model failed, trying fallback...")
            # Remove failed model and try again
            del available_models[selected_model]
            selected_model, confidence = await self.select_best_model(task, available_models)
            if selected_model != "none":
                model_profile = self.model_profiles[selected_model]
                system_prompt = self._get_dynamic_system_prompt(task, model_profile)
                if requires_vision and file_contexts and selected_model in ['llava:7b', 'bakllava:latest']:
                    response = await self.generate_with_vision_model(
                        selected_model, 
                        user_input, 
                        file_contexts[0], 
                        system_prompt, 
                        task
                    )
                else:
                    response = await self.generate_with_model(selected_model, user_input, system_prompt, task)
        
        # Record routing decision
        routing_decision = {
            "timestamp": datetime.now().isoformat(),
            "task_type": task.task_type,
            "complexity": task.complexity,
            "model_selected": selected_model,
            "confidence": confidence,
            "success": response is not None
        }
        self.routing_history.append(routing_decision)
        
        # Get performance stats
        perf_stats = self.model_performance.get(selected_model, {})
        
        orchestration_time = time.time() - start_time
        
        # Final check for document analysis responses
        if task.task_type == "document_analysis" and response:
            if len(response) < 500 or "appears to be" in response[:100]:
                print(f"⚠️ Final check: Response too short for document analysis ({len(response)} chars)")
                # Add a comprehensive template
                if "appears to be" in response:
                    response = f"""I'll provide a comprehensive analysis of this document:

## Document Overview
{response}

## Key Details
[The model failed to provide complete details. Please try again with a more specific prompt like "List all key information from the PDF" or "Provide a detailed breakdown of all sections in the document"]

## Recommendation
For best results with PDF summaries, please ensure:
1. The PDF text is extractable (not scanned images)
2. You have a model like dolphin-mixtral or mixtral installed
3. Try asking for specific sections or information"""
        
        return {
            "response": response or "Failed to generate response",
            "model_used": selected_model,
            "orchestration_time": orchestration_time,
            "task_analysis": {
                "type": task.task_type,
                "complexity": task.complexity,
                "is_sensitive": task.is_sensitive,
                "requires_speed": task.requires_speed,
                "estimated_tokens": task.estimated_tokens
            },
            "confidence": confidence,
            "model_performance": {
                "success_rate": perf_stats.get("success_rate", 0),
                "avg_speed": perf_stats.get("avg_tokens_per_sec", 0)
            },
            "available_models": len(available_models)
        }
    
    def get_orchestration_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        stats = {
            "model_performance": self.model_performance,
            "routing_history": self.routing_history[-100:],  # Last 100 decisions
            "task_distribution": {},
            "model_usage": {}
        }
        
        # Calculate distributions
        for decision in self.routing_history:
            task_type = decision["task_type"]
            model = decision["model_selected"]
            
            stats["task_distribution"][task_type] = stats["task_distribution"].get(task_type, 0) + 1
            stats["model_usage"][model] = stats["model_usage"].get(model, 0) + 1
        
        return stats


# Create singleton instance
orchestrator = IntelligentOrchestrator()