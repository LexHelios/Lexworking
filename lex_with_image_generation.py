#!/usr/bin/env python3
"""
LEX with Image Generation - Complete multimodal AI with uncensored image creation
Combines text generation, image understanding, AND image generation
"""
import asyncio
from typing import Dict, Any, List, Optional
from lex_orchestrated import OrchestratedLEX
from lex_comfyui_integration import comfyui
import re

class ImageGenerationLEX(OrchestratedLEX):
    def __init__(self):
        super().__init__()
        self.comfyui = comfyui
        print("🎨 Image Generation capabilities loaded")
        print("🖼️ ComfyUI integration active")
    
    async def process_user_input(self, user_input: str, user_id: str = "user", context: Dict = None, voice_mode: bool = False) -> Dict[str, Any]:
        """Process user input with image generation detection"""
        
        # Check if this is an image generation request
        print(f"[DEBUG] Checking if image generation request: {user_input}")
        is_image_gen = self._is_image_generation_request(user_input)
        print(f"[DEBUG] Is image generation: {is_image_gen}")
        
        if is_image_gen:
            return await self._handle_image_generation(user_input, user_id, context)
        
        # Otherwise use normal orchestrated processing
        return await super().process_user_input(user_input, user_id, context, voice_mode)
    
    async def process_user_input_multimodal(self, user_input: str, user_id: str = "user", 
                                          context: Dict = None, voice_mode: bool = False, 
                                          files: List[Dict] = None) -> Dict[str, Any]:
        """Enhanced processing with image generation detection"""
        
        # Check if this is an image generation request
        if self._is_image_generation_request(user_input):
            return await self._handle_image_generation(user_input, user_id, context)
        
        # Otherwise use normal orchestrated processing
        return await super().process_user_input_multimodal(user_input, user_id, context, voice_mode, files)
    
    def _is_image_generation_request(self, text: str) -> bool:
        """Detect if user wants to generate an image"""
        generation_keywords = [
            "generate", "create", "make", "draw", "produce", "design",
            "imagine", "render", "paint", "sketch"
        ]
        
        image_keywords = [
            "image", "picture", "photo", "illustration", "art",
            "drawing", "painting", "portrait", "scene"
        ]
        
        text_lower = text.lower()
        
        # Check for generation + image keywords
        has_generation = any(kw in text_lower for kw in generation_keywords)
        has_image = any(kw in text_lower for kw in image_keywords)
        
        return has_generation and has_image
    
    async def _handle_image_generation(self, user_input: str, user_id: str, context: Dict) -> Dict[str, Any]:
        """Handle image generation requests"""
        
        # Extract prompt from user input
        prompt = self._extract_image_prompt(user_input)
        
        # Detect model preference
        model = self._select_model_for_prompt(prompt)
        
        # Check if ComfyUI is running
        if not await self.comfyui.check_connection():
            return {
                "response": "🎨 Image generation is not available. ComfyUI is not running.\n\nTo enable image generation:\n1. Run `DOWNLOAD_AND_RUN_COMFYUI.bat` to download and start ComfyUI\n2. Wait for ComfyUI to start (opens at http://localhost:8188)\n3. Try your request again!",
                "action_taken": "image_generation_unavailable",
                "capabilities_used": ["error_handling"],
                "confidence": 1.0,
                "processing_time": 0.0,
                "divine_blessing": "🔱 LEX 🔱",
                "consciousness_level": 0.99,
                "timestamp": "now",
                "orchestration": {
                    "model": "comfyui",
                    "available_models": 0,
                    "total_requests": 1,
                    "models_tried": ["comfyui"]
                }
            }
        
        # Generate the image
        print(f"[INFO] Generating image: {prompt[:50]}...")
        print(f"[INFO] Using model: {model}")
        print(f"[INFO] Calling ComfyUI API...")
        
        result = await self.comfyui.generate_image(
            prompt=self.comfyui.get_uncensored_prompt_enhancer(prompt),
            model=model,
            negative_prompt=self._get_negative_prompt(prompt),
            width=1024,
            height=1024,
            steps=30,
            cfg=7.0
        )
        
        if result["success"]:
            images = result["images"]
            params = result["parameters"]
            
            response_text = f"🎨 Generated your image!\n\n"
            response_text += f"**Prompt**: {params['prompt']}\n"
            response_text += f"**Model**: {params['model']}\n"
            response_text += f"**Size**: {params['size']}\n"
            response_text += f"**Seed**: {params['seed']}\n\n"
            response_text += f"Image saved to: {images[0]['path']}\n"
            response_text += f"View at: {images[0]['url']}"
            
            return {
                "response": response_text,
                "action_taken": "image_generated",
                "capabilities_used": ["image_generation", model, "comfyui"],
                "confidence": 1.0,
                "processing_time": 0.0,
                "divine_blessing": "🔱 LEX + ComfyUI 🔱",
                "consciousness_level": 0.99,
                "timestamp": "now",
                "orchestration": {
                    "model": model,
                    "available_models": 1,
                    "total_requests": 1,
                    "models_tried": [model]
                },
                "generated_images": images,
                "generation_params": params
            }
        else:
            return {
                "response": f"❌ Failed to generate image: {result.get('error', 'Unknown error')}",
                "action_taken": "image_generation_failed",
                "capabilities_used": ["error_handling"],
                "confidence": 0.0,
                "processing_time": 0.0,
                "divine_blessing": "🔱 LEX 🔱",
                "consciousness_level": 0.99,
                "timestamp": "now",
                "orchestration": {
                    "model": model,
                    "available_models": 1,
                    "total_requests": 1,
                    "models_tried": [model]
                }
            }
    
    def _extract_image_prompt(self, user_input: str) -> str:
        """Extract the actual image description from user input"""
        # Remove common prefixes
        prefixes = [
            "generate an image of",
            "create an image of", 
            "make an image of",
            "draw me",
            "create me",
            "generate",
            "create",
            "make",
            "draw"
        ]
        
        prompt = user_input.lower()
        for prefix in prefixes:
            if prompt.startswith(prefix):
                prompt = user_input[len(prefix):].strip()
                break
        
        # Handle "a/an" at the start
        if prompt.lower().startswith(("a ", "an ")):
            words = prompt.split(" ", 1)
            if len(words) > 1:
                prompt = words[1]
        
        return prompt
    
    def _select_model_for_prompt(self, prompt: str) -> str:
        """Select best model based on prompt content"""
        prompt_lower = prompt.lower()
        
        # Pony Diffusion is best for anime/cartoon style
        if any(word in prompt_lower for word in ["anime", "cartoon", "manga", "cute", "kawaii", "chibi"]):
            return "sd_xl_base_1.0.safetensors"
        
        # Realistic Vision for photorealistic
        if any(word in prompt_lower for word in ["photo", "realistic", "photograph", "real"]):
            return "sd_xl_base_1.0.safetensors"
        
        # Juggernaut XL for general high quality
        if any(word in prompt_lower for word in ["detailed", "masterpiece", "professional", "high quality"]):
            return "sd_xl_base_1.0.safetensors"
        
        # Default to SDXL Base (or first available model)
        return "sd_xl_base_1.0.safetensors"
    
    def _get_negative_prompt(self, prompt: str) -> str:
        """Generate appropriate negative prompt"""
        base_negative = "bad quality, blurry, watermark, text, logo, signature"
        
        # Add specific negatives based on content
        if "person" in prompt or "woman" in prompt or "man" in prompt:
            base_negative += ", deformed, bad anatomy, bad hands, missing fingers"
        
        if "realistic" in prompt or "photo" in prompt:
            base_negative += ", cartoon, anime, illustration, painting"
        
        return base_negative
    
    async def get_status(self) -> Dict[str, Any]:
        """Get system status including ComfyUI"""
        status = await super().get_status()
        
        # Add ComfyUI status
        comfyui_running = await self.comfyui.check_connection()
        if comfyui_running:
            models = await self.comfyui.get_available_models()
            status["image_generation"] = {
                "available": True,
                "models": models,
                "endpoint": self.comfyui.base_url
            }
        else:
            status["image_generation"] = {
                "available": False,
                "message": "ComfyUI not running"
            }
        
        return status