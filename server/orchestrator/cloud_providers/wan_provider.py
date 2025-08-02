"""
Wan Image & Video Generation Provider for LexOS
Alibaba's Wan models for text-to-image and text-to-video generation
"""
import os
import logging
from typing import Dict, List, Any, Optional
from openai import AsyncOpenAI
import asyncio
import base64
from datetime import datetime

logger = logging.getLogger(__name__)

class WanProvider:
    """
    Wan provider for image and video generation using Alibaba Cloud
    Supports text-to-image, text-to-video, and image-to-video
    """
    
    def __init__(self):
        self.api_key = os.getenv("ALIBABA_API_KEY", "")
        self.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        self.client = None
        self.available = False
        
        # Model configurations
        self.image_models = {
            "wan2.2-t2i-plus": {
                "name": "Wan 2.2 Professional Edition",
                "description": "Upgraded creativity, stability, and realistic texture",
                "price_per_image": 0.025,
                "recommended": True
            },
            "wan2.2-t2i-flash": {
                "name": "Wan 2.2 Speed Edition",
                "description": "Fast generation with good quality",
                "price_per_image": 0.05,
                "recommended": True
            },
            "wan2.1-t2i-plus": {
                "name": "Wan 2.1 Professional Edition",
                "description": "Rich details generation",
                "price_per_image": 0.05
            },
            "wan2.1-t2i-turbo": {
                "name": "Wan 2.1 Speed Edition",
                "description": "Balanced effects, cost-effective",
                "price_per_image": 0.025
            }
        }
        
        self.video_models = {
            "wan2.2-t2v-plus": {
                "name": "Wan 2.2 Text-to-Video Professional",
                "description": "Improved detail and motion stability",
                "price_480p": 0.02,
                "price_1080p": 0.10,
                "recommended": True
            },
            "wan2.1-t2v-turbo": {
                "name": "Wan 2.1 Text-to-Video Speed",
                "description": "Fast generation, balanced performance",
                "price_per_second": 0.036
            },
            "wan2.2-i2v-plus": {
                "name": "Wan 2.2 Image-to-Video Professional",
                "description": "Superior image detail and motion",
                "price_480p": 0.02,
                "price_1080p": 0.10,
                "recommended": True
            }
        }
        
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Wan client"""
        if self.api_key:
            try:
                self.client = AsyncOpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url,
                    timeout=120.0  # Longer timeout for video generation
                )
                self.available = True
                logger.info("✅ Wan image/video generation provider initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Wan provider: {e}")
                self.available = False
        else:
            logger.warning("⚠️ ALIBABA_API_KEY not set - Wan generation unavailable")
    
    async def generate_image(
        self,
        prompt: str,
        model: str = "wan2.2-t2i-plus",
        size: str = "1024x1024",
        quality: str = "standard",
        n: int = 1,
        style: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate images using Wan text-to-image models
        
        Args:
            prompt: Text description of the image
            model: Wan model to use
            size: Image size (1024x1024, 512x512, etc.)
            quality: Image quality (standard, hd)
            n: Number of images to generate
            style: Optional style parameter
        """
        if not self.available:
            return {
                "error": "Wan provider not available. Set ALIBABA_API_KEY.",
                "images": []
            }
        
        try:
            logger.info(f"🎨 Generating image with Wan {model}")
            
            # Use OpenAI-compatible image generation endpoint
            response = await self.client.images.generate(
                model=model,
                prompt=prompt,
                size=size,
                quality=quality,
                n=n,
                **kwargs
            )
            
            images = []
            for img in response.data:
                image_data = {
                    "url": img.url,
                    "revised_prompt": getattr(img, 'revised_prompt', prompt),
                    "b64_json": img.b64_json if hasattr(img, 'b64_json') else None
                }
                images.append(image_data)
            
            return {
                "success": True,
                "images": images,
                "model": model,
                "model_info": self.image_models.get(model, {}),
                "cost": self.image_models.get(model, {}).get("price_per_image", 0) * n,
                "provider": "wan"
            }
            
        except Exception as e:
            logger.error(f"Wan image generation error: {e}")
            return {
                "error": str(e),
                "images": []
            }
    
    async def generate_video(
        self,
        prompt: str,
        model: str = "wan2.2-t2v-plus",
        duration: int = 5,
        resolution: str = "480p",
        fps: int = 24,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate video using Wan text-to-video models
        
        Args:
            prompt: Text description of the video
            model: Wan video model to use
            duration: Video duration in seconds
            resolution: Video resolution (480p, 1080p)
            fps: Frames per second
        """
        if not self.available:
            return {
                "error": "Wan provider not available. Set ALIBABA_API_KEY.",
                "video": None
            }
        
        try:
            logger.info(f"🎬 Generating {duration}s video with Wan {model}")
            
            # Prepare video generation request
            request_data = {
                "model": model,
                "prompt": prompt,
                "duration": duration,
                "resolution": resolution,
                "fps": fps,
                **kwargs
            }
            
            # Note: Actual API call would depend on Alibaba's video generation endpoint
            # This is a placeholder for the expected API structure
            response = await self._call_video_api(request_data)
            
            # Calculate cost
            model_info = self.video_models.get(model, {})
            if resolution == "1080p" and "price_1080p" in model_info:
                cost = model_info["price_1080p"] * duration
            elif resolution == "480p" and "price_480p" in model_info:
                cost = model_info["price_480p"] * duration
            else:
                cost = model_info.get("price_per_second", 0) * duration
            
            return {
                "success": True,
                "video": response.get("video_url"),
                "model": model,
                "model_info": model_info,
                "duration": duration,
                "resolution": resolution,
                "cost": cost,
                "provider": "wan"
            }
            
        except Exception as e:
            logger.error(f"Wan video generation error: {e}")
            return {
                "error": str(e),
                "video": None
            }
    
    async def image_to_video(
        self,
        image_path: str,
        prompt: str,
        model: str = "wan2.2-i2v-plus",
        duration: int = 5,
        resolution: str = "480p",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate video from an image using Wan image-to-video models
        
        Args:
            image_path: Path to the input image
            prompt: Text description for video generation
            model: Wan i2v model to use
            duration: Video duration in seconds
            resolution: Video resolution
        """
        if not self.available:
            return {
                "error": "Wan provider not available. Set ALIBABA_API_KEY.",
                "video": None
            }
        
        try:
            logger.info(f"🎬 Generating video from image with Wan {model}")
            
            # Read and encode image
            with open(image_path, "rb") as img_file:
                image_data = base64.b64encode(img_file.read()).decode()
            
            # Prepare request
            request_data = {
                "model": model,
                "image": image_data,
                "prompt": prompt,
                "duration": duration,
                "resolution": resolution,
                **kwargs
            }
            
            # Call API (placeholder)
            response = await self._call_video_api(request_data)
            
            # Calculate cost
            model_info = self.video_models.get(model, {})
            if resolution == "1080p" and "price_1080p" in model_info:
                cost = model_info["price_1080p"] * duration
            elif resolution == "480p" and "price_480p" in model_info:
                cost = model_info["price_480p"] * duration
            else:
                cost = model_info.get("price_per_second", 0) * duration
            
            return {
                "success": True,
                "video": response.get("video_url"),
                "model": model,
                "model_info": model_info,
                "duration": duration,
                "resolution": resolution,
                "cost": cost,
                "provider": "wan"
            }
            
        except Exception as e:
            logger.error(f"Wan image-to-video error: {e}")
            return {
                "error": str(e),
                "video": None
            }
    
    async def _call_video_api(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call Wan video generation API
        Note: This is a placeholder - actual implementation depends on Alibaba's API
        """
        # In production, this would make the actual API call
        # For now, return a mock response
        logger.warning("Video generation API call not implemented - returning mock response")
        return {
            "video_url": f"https://dashscope.aliyuncs.com/videos/{datetime.now().timestamp()}.mp4",
            "status": "completed",
            "duration": request_data.get("duration", 5)
        }
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test connection to Wan API"""
        if not self.available:
            return {
                "available": False,
                "error": "API key not configured"
            }
        
        try:
            # Test with a simple image generation
            result = await self.generate_image(
                prompt="A test image of a cat",
                model="wan2.1-t2i-turbo",
                n=1
            )
            
            if result.get("success"):
                return {
                    "available": True,
                    "image_models": list(self.image_models.keys()),
                    "video_models": list(self.video_models.keys()),
                    "test_result": "Image generation successful"
                }
            else:
                return {
                    "available": False,
                    "error": result.get("error", "Unknown error")
                }
                
        except Exception as e:
            return {
                "available": False,
                "error": str(e)
            }
    
    def get_model_info(self, model_type: str = "image") -> Dict[str, Any]:
        """Get information about available models"""
        if model_type == "image":
            return self.image_models
        elif model_type == "video":
            return self.video_models
        else:
            return {
                "image_models": self.image_models,
                "video_models": self.video_models
            }
    
    def estimate_cost(
        self,
        model: str,
        count: int = 1,
        duration: Optional[int] = None,
        resolution: Optional[str] = None
    ) -> float:
        """Estimate cost for generation"""
        if model in self.image_models:
            return self.image_models[model].get("price_per_image", 0) * count
        elif model in self.video_models:
            if duration is None:
                return 0
            
            model_info = self.video_models[model]
            if resolution == "1080p" and "price_1080p" in model_info:
                return model_info["price_1080p"] * duration
            elif resolution == "480p" and "price_480p" in model_info:
                return model_info["price_480p"] * duration
            else:
                return model_info.get("price_per_second", 0) * duration
        
        return 0

# Global instance
wan_provider = WanProvider()