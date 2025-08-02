#!/usr/bin/env python3
"""
Fix vision support in the orchestrator
"""

# We need to modify the generate_with_model function to support images
# Vision models in Ollama expect images in the prompt

vision_generate_code = '''
    async def generate_with_vision_model(self, model: str, prompt: str, image_data: Dict, system_prompt: str, task: TaskAnalysis) -> Optional[str]:
        """Generate response with vision model including image"""
        try:
            # For vision models, we need to include the image in a special format
            # Ollama vision models expect base64 images
            
            payload = {
                "model": model,
                "prompt": prompt,
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
                        
                        self.update_model_performance(
                            model, 
                            success=True,
                            time_taken=elapsed,
                            tokens_generated=tokens
                        )
                        
                        return data.get('response', '')
                    else:
                        print(f"❌ Model {model} returned {response.status}")
                        self.update_model_performance(model, success=False)
                        return None
                        
        except Exception as e:
            print(f"❌ Error with model {model}: {e}")
            self.update_model_performance(model, success=False)
            return None
'''

print("To fix vision support, add the generate_with_vision_model method to lex_intelligent_orchestrator.py")
print("Then modify the orchestrate_request method to use it when vision models are selected")