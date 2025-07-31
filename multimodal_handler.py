#!/usr/bin/env python3
"""
Multimodal Handler for LEX - Process images, PDFs, and other attachments
"""

import base64
import io
import os
from typing import Dict, List, Any, Optional, Tuple
from PIL import Image
import fitz  # PyMuPDF for PDF handling
import aiohttp
import json
import asyncio

class MultimodalHandler:
    """Handle various file types and convert them for LLM processing"""
    
    def __init__(self):
        self.supported_image_types = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        self.supported_doc_types = ['.pdf', '.txt', '.md', '.csv']
        self.max_image_size = (1024, 1024)  # Resize large images
        
    async def process_attachments(self, attachments: List[Dict]) -> Tuple[str, List[Dict]]:
        """Process attachments and return text description + processed data"""
        if not attachments:
            return "", []
            
        processed_attachments = []
        descriptions = []
        
        for attachment in attachments:
            file_path = attachment.get('path') or attachment.get('url')
            file_type = attachment.get('type', '').lower()
            file_name = attachment.get('name', 'unknown')
            
            # Determine file type from extension if not provided
            if not file_type and file_path:
                ext = os.path.splitext(file_path)[1].lower()
                if ext in self.supported_image_types:
                    file_type = 'image'
                elif ext in self.supported_doc_types:
                    file_type = 'document'
            
            try:
                if file_type == 'image' or any(file_path.endswith(ext) for ext in self.supported_image_types):
                    description, data = await self.process_image(file_path, file_name)
                    descriptions.append(description)
                    processed_attachments.append(data)
                    
                elif file_type == 'document' or file_path.endswith('.pdf'):
                    description, data = await self.process_pdf(file_path, file_name)
                    descriptions.append(description)
                    processed_attachments.append(data)
                    
                elif file_path.endswith(('.txt', '.md')):
                    description, data = await self.process_text_file(file_path, file_name)
                    descriptions.append(description)
                    processed_attachments.append(data)
                    
            except Exception as e:
                descriptions.append(f"[Error processing {file_name}: {str(e)}]")
                
        combined_description = "\n\n".join(descriptions)
        return combined_description, processed_attachments
    
    async def process_image(self, image_path: str, file_name: str) -> Tuple[str, Dict]:
        """Process image file and prepare for vision API"""
        try:
            # Handle URL or local path
            if image_path.startswith(('http://', 'https://')):
                async with aiohttp.ClientSession() as session:
                    async with session.get(image_path) as resp:
                        image_data = await resp.read()
                        image = Image.open(io.BytesIO(image_data))
            else:
                image = Image.open(image_path)
            
            # Get image info
            width, height = image.size
            mode = image.mode
            
            # Resize if too large
            if width > self.max_image_size[0] or height > self.max_image_size[1]:
                image.thumbnail(self.max_image_size, Image.Resampling.LANCZOS)
                width, height = image.size
            
            # Convert to base64
            buffered = io.BytesIO()
            image.save(buffered, format=image.format or 'PNG')
            base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            # Use vision API to analyze
            analysis = await self.analyze_image_with_vision_api(base64_image)
            
            description = f"[Image: {file_name} ({width}x{height}, {mode} mode)]\n{analysis}"
            
            return description, {
                'type': 'image',
                'name': file_name,
                'base64': base64_image,
                'analysis': analysis,
                'dimensions': f"{width}x{height}"
            }
            
        except Exception as e:
            return f"[Error processing image {file_name}: {str(e)}]", {}
    
    async def analyze_image_with_vision_api(self, base64_image: str) -> str:
        """Analyze image using OpenAI Vision API or similar"""
        # First try OpenAI Vision API
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key and openai_key.startswith('sk-'):
            try:
                import openai
                client = openai.OpenAI(api_key=openai_key)
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Describe this image in detail. What do you see?"
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{base64_image}",
                                        "detail": "low"
                                    }
                                }
                            ]
                        }
                    ],
                    max_tokens=300
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"OpenAI Vision error: {e}")
        
        # Fallback to Replicate's BLIP or LLaVA
        replicate_token = os.getenv('REPLICATE_API_TOKEN')
        if replicate_token:
            try:
                async with aiohttp.ClientSession() as session:
                    headers = {
                        "Authorization": f"Bearer {replicate_token}",
                        "Content-Type": "application/json"
                    }
                    
                    # Use BLIP for image captioning
                    payload = {
                        "version": "2e1dddc8621f72155f24cf2e0adbde548458d3cab9f00c0139eea840d0ac4746",
                        "input": {
                            "image": f"data:image/png;base64,{base64_image}",
                            "task": "image_captioning"
                        }
                    }
                    
                    async with session.post("https://api.replicate.com/v1/predictions", 
                                          headers=headers, json=payload) as resp:
                        if resp.status == 201:
                            result = await resp.json()
                            prediction_id = result["id"]
                            
                            # Poll for result
                            for _ in range(30):
                                await asyncio.sleep(1)
                                get_url = f"https://api.replicate.com/v1/predictions/{prediction_id}"
                                async with session.get(get_url, headers=headers) as poll_resp:
                                    poll_result = await poll_resp.json()
                                    if poll_result["status"] == "succeeded":
                                        return poll_result["output"]
                                    elif poll_result["status"] == "failed":
                                        break
            except Exception as e:
                print(f"Replicate vision error: {e}")
        
        # Basic fallback
        return "Image uploaded - vision analysis not available without valid API keys"
    
    async def process_pdf(self, pdf_path: str, file_name: str) -> Tuple[str, Dict]:
        """Extract text and images from PDF"""
        try:
            text_content = []
            images_found = 0
            
            # Handle URL or local path
            if pdf_path.startswith(('http://', 'https://')):
                async with aiohttp.ClientSession() as session:
                    async with session.get(pdf_path) as resp:
                        pdf_data = await resp.read()
                        pdf_document = fitz.open(stream=pdf_data, filetype="pdf")
            else:
                pdf_document = fitz.open(pdf_path)
            
            total_pages = len(pdf_document)
            
            # Extract text from each page (limit to first 10 pages)
            for page_num, page in enumerate(pdf_document):
                if page_num >= 10:  # Limit to prevent huge texts
                    text_content.append(f"\n[... {total_pages - 10} more pages ...]")
                    break
                    
                text = page.get_text()
                if text.strip():
                    text_content.append(f"\n--- Page {page_num + 1} ---\n{text}")
                
                # Count images
                image_list = page.get_images()
                images_found += len(image_list)
            
            pdf_document.close()
            
            extracted_text = "\n".join(text_content)
            
            # Limit text length
            if len(extracted_text) > 5000:
                extracted_text = extracted_text[:5000] + "\n\n[... text truncated ...]"
            
            description = f"[PDF: {file_name} ({total_pages} pages, {images_found} images)]\n\nExtracted text:\n{extracted_text}"
            
            return description, {
                'type': 'pdf',
                'name': file_name,
                'pages': total_pages,
                'images': images_found,
                'text': extracted_text
            }
            
        except Exception as e:
            return f"[Error processing PDF {file_name}: {str(e)}]", {}
    
    async def process_text_file(self, file_path: str, file_name: str) -> Tuple[str, Dict]:
        """Process text files"""
        try:
            if file_path.startswith(('http://', 'https://')):
                async with aiohttp.ClientSession() as session:
                    async with session.get(file_path) as resp:
                        content = await resp.text()
            else:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            
            # Limit content length
            if len(content) > 5000:
                content = content[:5000] + "\n\n[... text truncated ...]"
            
            description = f"[Text file: {file_name}]\n\n{content}"
            
            return description, {
                'type': 'text',
                'name': file_name,
                'content': content
            }
            
        except Exception as e:
            return f"[Error processing text file {file_name}: {str(e)}]", {}

# Create singleton instance
multimodal_handler = MultimodalHandler()