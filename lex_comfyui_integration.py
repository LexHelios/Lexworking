#!/usr/bin/env python3
"""
LEX ComfyUI Integration - Uncensored Image Generation
Connects LEX to ComfyUI for generating any type of images
"""
import asyncio
import aiohttp
import json
import uuid
import os
import base64
from typing import Dict, Any, Optional, List
from pathlib import Path
import websockets

class ComfyUIIntegration:
    def __init__(self, host: str = "localhost", port: int = 8188):
        # Use localhost when running outside Docker
        import os
        if os.path.exists("/.dockerenv"):
            # Inside Docker, use host.docker.internal
            self.host = "host.docker.internal"
        else:
            # Outside Docker, use localhost
            self.host = "localhost"
        self.port = port
        self.base_url = f"http://{self.host}:{port}"
        self.ws_url = f"ws://{self.host}:{port}/ws"
        self.client_id = str(uuid.uuid4())
        self.output_dir = Path("comfyui_outputs")
        self.output_dir.mkdir(exist_ok=True)
        
        # Default workflow for text-to-image
        self.default_workflow = self._create_default_workflow()
        
        print(f"🎨 ComfyUI Integration initialized")
        print(f"📍 API: {self.base_url}")
        print(f"🔌 WebSocket: {self.ws_url}")
    
    def _create_default_workflow(self) -> Dict:
        """Create a default SDXL workflow"""
        return {
            "3": {
                "inputs": {
                    "seed": 0,  # Will be randomized
                    "steps": 30,
                    "cfg": 7.0,
                    "sampler_name": "dpmpp_2m",
                    "scheduler": "karras",
                    "denoise": 1,
                    "model": ["4", 0],
                    "positive": ["6", 0],
                    "negative": ["7", 0],
                    "latent_image": ["5", 0]
                },
                "class_type": "KSampler"
            },
            "4": {
                "inputs": {
                    "ckpt_name": "sd_xl_base_1.0.safetensors"  # Default model
                },
                "class_type": "CheckpointLoaderSimple"
            },
            "5": {
                "inputs": {
                    "width": 1024,
                    "height": 1024,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage"
            },
            "6": {
                "inputs": {
                    "text": "beautiful woman",  # Will be replaced
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "7": {
                "inputs": {
                    "text": "bad quality, blurry, watermark",
                    "clip": ["4", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "8": {
                "inputs": {
                    "samples": ["3", 0],
                    "vae": ["4", 2]
                },
                "class_type": "VAEDecode"
            },
            "9": {
                "inputs": {
                    "filename_prefix": "LEX_generated",
                    "images": ["8", 0]
                },
                "class_type": "SaveImage"
            }
        }
    
    async def check_connection(self) -> bool:
        """Check if ComfyUI is running"""
        try:
            async with aiohttp.ClientSession() as session:
                # Try multiple endpoints
                endpoints = ["/system_stats", "/", "/object_info"]
                for endpoint in endpoints:
                    try:
                        async with session.get(f"{self.base_url}{endpoint}", timeout=aiohttp.ClientTimeout(total=5)) as response:
                            if response.status == 200:
                                return True
                    except:
                        continue
                return False
        except:
            return False
    
    async def get_available_models(self) -> List[str]:
        """Get list of available checkpoint models"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/object_info/CheckpointLoaderSimple") as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["CheckpointLoaderSimple"]["input"]["required"]["ckpt_name"][0]
        except:
            return []
    
    async def generate_image(
        self,
        prompt: str,
        negative_prompt: str = "bad quality, blurry, watermark",
        model: Optional[str] = None,
        width: int = 1024,
        height: int = 1024,
        steps: int = 30,
        cfg: float = 7.0,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate an image using ComfyUI"""
        
        # Check connection
        if not await self.check_connection():
            return {
                "success": False,
                "error": "ComfyUI is not running. Please start it with run_comfyui.bat"
            }
        
        # Prepare workflow
        workflow = json.loads(json.dumps(self.default_workflow))
        
        # Update parameters
        workflow["6"]["inputs"]["text"] = prompt
        workflow["7"]["inputs"]["text"] = negative_prompt
        workflow["5"]["inputs"]["width"] = width
        workflow["5"]["inputs"]["height"] = height
        workflow["3"]["inputs"]["steps"] = steps
        workflow["3"]["inputs"]["cfg"] = cfg
        workflow["3"]["inputs"]["seed"] = seed or random.randint(0, 2**32 - 1)
        
        if model:
            workflow["4"]["inputs"]["ckpt_name"] = model
        
        # Queue the prompt
        try:
            print(f"[DEBUG] Queueing workflow with {len(workflow)} nodes...")
            prompt_id = await self._queue_prompt(workflow)
            if not prompt_id:
                return {"success": False, "error": "Failed to queue prompt"}
            
            # Wait for completion and get results
            images = await self._wait_for_images(prompt_id)
            
            if images:
                return {
                    "success": True,
                    "images": images,
                    "prompt_id": prompt_id,
                    "parameters": {
                        "prompt": prompt,
                        "negative_prompt": negative_prompt,
                        "model": model or workflow["4"]["inputs"]["ckpt_name"],
                        "size": f"{width}x{height}",
                        "steps": steps,
                        "cfg": cfg,
                        "seed": workflow["3"]["inputs"]["seed"]
                    }
                }
            else:
                return {"success": False, "error": "No images generated"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _queue_prompt(self, workflow: Dict) -> Optional[str]:
        """Queue a workflow prompt"""
        data = {
            "prompt": workflow,
            "client_id": self.client_id
        }
        
        try:
            print(f"[DEBUG] Sending to ComfyUI: {self.base_url}/prompt")
            print(f"[DEBUG] Client ID: {self.client_id}")
            print(f"[DEBUG] Workflow has {len(workflow)} nodes")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/prompt", json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        prompt_id = result.get("prompt_id")
                        print(f"[SUCCESS] Queued with ID: {prompt_id}")
                        return prompt_id
                    else:
                        error_text = await response.text()
                        print(f"[ERROR] ComfyUI API Error ({response.status}): {error_text}")
                        return None
        except Exception as e:
            print(f"[ERROR] Failed to connect to ComfyUI: {e}")
            print(f"[DEBUG] URL was: {self.base_url}/prompt")
            return None
    
    async def _wait_for_images(self, prompt_id: str, timeout: int = 120) -> List[Dict]:
        """Wait for images to be generated"""
        images = []
        
        try:
            # Connect to WebSocket for updates
            async with websockets.connect(f"{self.ws_url}?clientId={self.client_id}") as ws:
                start_time = asyncio.get_event_loop().time()
                
                while (asyncio.get_event_loop().time() - start_time) < timeout:
                    try:
                        message = await asyncio.wait_for(ws.recv(), timeout=1.0)
                        data = json.loads(message)
                        
                        if data["type"] == "executed" and data["data"]["node"] == "9":
                            # Image saved node executed
                            if data["data"]["prompt_id"] == prompt_id:
                                # Get the images
                                images = await self._get_images(prompt_id)
                                break
                                
                    except asyncio.TimeoutError:
                        continue
                    except Exception as e:
                        print(f"WebSocket error: {e}")
                        break
                        
        except Exception as e:
            print(f"Failed to connect to WebSocket: {e}")
            # Fallback: poll for completion
            images = await self._poll_for_images(prompt_id, timeout)
        
        return images
    
    async def _poll_for_images(self, prompt_id: str, timeout: int = 120) -> List[Dict]:
        """Fallback polling method"""
        import time
        start_time = time.time()
        
        while (time.time() - start_time) < timeout:
            history = await self._get_history(prompt_id)
            if history and prompt_id in history:
                outputs = history[prompt_id].get("outputs", {})
                for node_id, node_output in outputs.items():
                    if "images" in node_output:
                        return await self._download_images(node_output["images"])
            
            await asyncio.sleep(1)
        
        return []
    
    async def _get_history(self, prompt_id: str) -> Dict:
        """Get generation history"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/history/{prompt_id}") as response:
                if response.status == 200:
                    return await response.json()
        return {}
    
    async def _get_images(self, prompt_id: str) -> List[Dict]:
        """Get generated images"""
        history = await self._get_history(prompt_id)
        if not history or prompt_id not in history:
            return []
        
        images = []
        outputs = history[prompt_id].get("outputs", {})
        
        for node_id, node_output in outputs.items():
            if "images" in node_output:
                images.extend(await self._download_images(node_output["images"]))
        
        return images
    
    async def _download_images(self, image_datas: List[Dict]) -> List[Dict]:
        """Download images from ComfyUI"""
        images = []
        
        async with aiohttp.ClientSession() as session:
            for img_data in image_datas:
                filename = img_data["filename"]
                subfolder = img_data.get("subfolder", "")
                image_type = img_data.get("type", "output")
                
                url = f"{self.base_url}/view"
                params = {
                    "filename": filename,
                    "type": image_type,
                    "subfolder": subfolder
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        image_bytes = await response.read()
                        
                        # Save locally
                        local_path = self.output_dir / filename
                        with open(local_path, "wb") as f:
                            f.write(image_bytes)
                        
                        # Convert to base64
                        base64_image = base64.b64encode(image_bytes).decode('utf-8')
                        
                        images.append({
                            "filename": filename,
                            "path": str(local_path),
                            "base64": base64_image,
                            "url": f"{self.base_url}/view?filename={filename}&type={image_type}&subfolder={subfolder}"
                        })
        
        return images
    
    def get_uncensored_prompt_enhancer(self, base_prompt: str) -> str:
        """Enhance prompts for better uncensored results"""
        # Add quality tags that work well with uncensored models
        quality_tags = "masterpiece, best quality, highly detailed, sharp focus, professional"
        
        # Add photorealistic tags if appropriate
        if any(word in base_prompt.lower() for word in ["photo", "realistic", "woman", "man", "person"]):
            quality_tags += ", photorealistic, 8k uhd, dslr, high quality photo"
        
        return f"{base_prompt}, {quality_tags}"


# Create global instance
comfyui = ComfyUIIntegration()

# Import random for seed generation
import random