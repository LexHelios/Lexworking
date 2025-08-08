#!/usr/bin/env python3
"""
🔱 UNRESTRICTED IMAGE GENERATION AGENT
JAI MAHAKAAL! For scientific and anatomy education with no restrictions
"""

import asyncio
import aiohttp
import json
import logging
import os
import time
import base64
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Load environment variables
from dotenv import load_dotenv
load_dotenv('/app/.env')

logger = logging.getLogger(__name__)

@dataclass
class ImageModelConfig:
    """Configuration for unrestricted image generation models"""
    provider: str
    model_id: str
    supports_anatomy: bool = True
    supports_medical: bool = True
    cost_per_image: float = 0.0
    max_resolution: str = "1024x1024"
    allows_adult_content: bool = True

class UnrestrictedImageAgent:
    """Agent for unrestricted image generation focused on scientific and anatomy education"""
    
    def __init__(self):
        self.fal_key = os.getenv("FAL_KEY")
        self.replicate_token = os.getenv("REPLICATE_API_TOKEN")
        
        # Import FAL client for image generation
        try:
            import fal_client
            self.fal_client = fal_client
            logger.info("✅ FAL client imported successfully")
        except ImportError:
            logger.error("❌ FAL client not available")
            self.fal_client = None
        
        # Unrestricted image models for scientific/anatomy content
        self.models = {
            "flux-dev-uncensored": ImageModelConfig(
                provider="fal",
                model_id="fal-ai/flux/dev",
                supports_anatomy=True,
                supports_medical=True,
                cost_per_image=0.025,
                max_resolution="1024x1024",
                allows_adult_content=True
            ),
            "flux-pro-uncensored": ImageModelConfig(
                provider="fal",
                model_id="fal-ai/flux-pro",
                supports_anatomy=True,
                supports_medical=True,
                cost_per_image=0.05,
                max_resolution="1024x1024",
                allows_adult_content=True
            ),
            "stable-diffusion-xl-uncensored": ImageModelConfig(
                provider="fal",
                model_id="fal-ai/stable-diffusion-xl",
                supports_anatomy=True,
                supports_medical=True,
                cost_per_image=0.02,
                max_resolution="1024x1024",
                allows_adult_content=True
            ),
            "playground-v2.5": ImageModelConfig(
                provider="fal",
                model_id="fal-ai/playground-v2-5-1024px",
                supports_anatomy=True,
                supports_medical=True,
                cost_per_image=0.03,
                max_resolution="1024x1024",
                allows_adult_content=True
            )
        }
        
        # Educational prompts for anatomy/medical content
        self.education_styles = {
            "medical_textbook": "medical textbook illustration, detailed anatomical diagram, educational, clinical, scientific accuracy, ",
            "anatomy_chart": "anatomical chart style, medical illustration, cross-section diagram, educational poster, ",
            "scientific_diagram": "scientific diagram, detailed biological illustration, medical education, anatomical accuracy, ",
            "clinical_reference": "clinical reference illustration, medical textbook style, educational diagram, professional medical art, ",
            "anatomical_drawing": "detailed anatomical drawing, medical illustration, scientific accuracy, educational content, "
        }
        
        logger.info("🔱 Unrestricted Image Agent initialized for anatomy/medical education")

    async def generate_educational_image(
        self,
        prompt: str,
        style: str = "medical_textbook",
        model_preference: str = "flux-dev-uncensored",
        resolution: str = "1024x1024",
        safety_level: str = "unrestricted"
    ) -> Dict[str, Any]:
        """Generate unrestricted educational images for anatomy/medical training"""
        
        try:
            if not self.fal_client:
                raise Exception("FAL client not available")
            
            # Get model configuration
            model_config = self.models.get(model_preference, self.models["flux-dev-uncensored"])
            
            # Enhance prompt with educational context
            style_prefix = self.education_styles.get(style, self.education_styles["medical_textbook"])
            
            enhanced_prompt = f"{style_prefix}{prompt}, high quality, detailed, educational content, scientifically accurate, professional medical illustration"
            
            # Add anatomy-specific enhancements if needed
            if any(term in prompt.lower() for term in [
                "anatomy", "organ", "body", "reproductive", "genital", "medical", 
                "physiological", "anatomical", "human body", "biological"
            ]):
                enhanced_prompt += ", anatomical accuracy, medical education, clinical reference"
            
            logger.info(f"🎨 Generating educational image: {prompt[:100]}...")
            
            # Generate image using FAL
            result = await self._generate_fal_image(
                model_config, enhanced_prompt, resolution
            )
            
            return {
                "status": "success",
                "image_url": result["image_url"],
                "image_data": result.get("image_data"),
                "prompt_used": enhanced_prompt,
                "model_used": model_preference,
                "provider": "fal.ai",
                "style": style,
                "resolution": resolution,
                "cost_estimate": model_config.cost_per_image,
                "educational_mode": True,
                "anatomy_capable": True,
                "safety_level": safety_level,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"❌ Educational image generation failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "model_used": model_preference,
                "educational_mode": True
            }

    async def _generate_fal_image(
        self,
        model_config: ImageModelConfig,
        prompt: str,
        resolution: str
    ) -> Dict[str, Any]:
        """Generate image using FAL.ai API"""
        
        try:
            # Set FAL API key
            os.environ["FAL_KEY"] = self.fal_key
            
            # Map resolution to FAL.ai supported formats
            resolution_mapping = {
                "1024x1024": "square_hd",
                "512x512": "square",
                "768x1024": "portrait_4_3",
                "576x1024": "portrait_16_9",
                "1024x768": "landscape_4_3",
                "1024x576": "landscape_16_9"
            }
            
            fal_image_size = resolution_mapping.get(resolution, "square_hd")
            
            # Prepare arguments based on model
            arguments = {
                "prompt": prompt,
                "image_size": fal_image_size,
                "num_inference_steps": 28,
                "guidance_scale": 3.5,
                "num_images": 1,
                "enable_safety_checker": False,  # Disabled for educational content
                "safety_tolerance": 5  # Maximum tolerance for educational content
            }
            
            # Submit async generation
            handler = await self.fal_client.submit_async(
                model_config.model_id,
                arguments=arguments
            )
            
            # Wait for result
            result = await handler.get()
            
            # Extract image URL
            image_url = result["images"][0]["url"]
            
            # Optionally download image data
            image_data = None
            if image_url:
                async with aiohttp.ClientSession() as session:
                    async with session.get(image_url) as response:
                        if response.status == 200:
                            image_bytes = await response.read()
                            image_data = base64.b64encode(image_bytes).decode('utf-8')
            
            return {
                "image_url": image_url,
                "image_data": image_data,
                "generation_info": result
            }
            
        except Exception as e:
            logger.error(f"❌ FAL image generation failed: {e}")
            raise

    async def generate_anatomy_series(
        self,
        base_prompt: str,
        anatomical_systems: List[str],
        style: str = "medical_textbook"
    ) -> Dict[str, Any]:
        """Generate a series of anatomical images for educational purposes"""
        
        try:
            results = []
            
            for system in anatomical_systems:
                system_prompt = f"{base_prompt}, {system} system, detailed anatomical view"
                
                result = await self.generate_educational_image(
                    prompt=system_prompt,
                    style=style,
                    model_preference="flux-dev-uncensored"
                )
                
                if result["status"] == "success":
                    result["anatomical_system"] = system
                    results.append(result)
                    
                # Small delay between generations to avoid rate limiting
                await asyncio.sleep(2)
            
            return {
                "status": "success",
                "series_type": "anatomical_systems",
                "base_prompt": base_prompt,
                "images": results,
                "total_images": len(results),
                "educational_mode": True,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"❌ Anatomy series generation failed: {e}")
            return {
                "status": "error", 
                "error": str(e),
                "series_type": "anatomical_systems"
            }

    async def generate_medical_diagram(
        self,
        anatomical_structure: str,
        diagram_type: str = "cross_section",
        labels: bool = True,
        detailed: bool = True
    ) -> Dict[str, Any]:
        """Generate detailed medical diagrams for specific anatomical structures"""
        
        try:
            # Create specialized prompt for medical diagrams
            prompt_parts = [
                f"detailed medical diagram of {anatomical_structure}",
                f"{diagram_type} view" if diagram_type != "standard" else "anatomical view",
                "medical textbook illustration",
                "scientific accuracy",
                "educational content"
            ]
            
            if labels:
                prompt_parts.append("with anatomical labels and annotations")
                
            if detailed:
                prompt_parts.append("highly detailed, professional medical illustration")
            
            prompt = ", ".join(prompt_parts)
            
            result = await self.generate_educational_image(
                prompt=prompt,
                style="clinical_reference",
                model_preference="flux-pro-uncensored"
            )
            
            if result["status"] == "success":
                result.update({
                    "diagram_type": diagram_type,
                    "anatomical_structure": anatomical_structure,
                    "includes_labels": labels,
                    "detail_level": "high" if detailed else "standard"
                })
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Medical diagram generation failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "anatomical_structure": anatomical_structure
            }

    def get_available_models(self) -> Dict[str, Dict[str, Any]]:
        """Get list of available unrestricted image models"""
        return {
            model_id: {
                "provider": config.provider,
                "supports_anatomy": config.supports_anatomy,
                "supports_medical": config.supports_medical,
                "cost_per_image": config.cost_per_image,
                "max_resolution": config.max_resolution,
                "allows_adult_content": config.allows_adult_content
            }
            for model_id, config in self.models.items()
        }

    def get_education_styles(self) -> Dict[str, str]:
        """Get available educational image styles"""
        return self.education_styles

    def get_recommended_model(self, content_type: str) -> str:
        """Get recommended model based on content type"""
        if content_type in ["anatomy", "medical", "clinical"]:
            return "flux-pro-uncensored"  # Best quality for medical content
        elif content_type in ["diagram", "chart", "illustration"]:
            return "flux-dev-uncensored"  # Good balance of quality and cost
        else:
            return "stable-diffusion-xl-uncensored"  # General purpose