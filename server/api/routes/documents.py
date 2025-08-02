"""
Document Management API Routes
Handles file uploads, storage, and retrieval
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from typing import List, Optional, Dict, Any
import os
import aiofiles
from pathlib import Path
import mimetypes
from datetime import datetime
import base64
from PIL import Image
import io

from ...memory.persistent_memory_manager import persistent_memory
from ..dependencies import get_current_user

router = APIRouter()

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    'documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'],
    'spreadsheets': ['.xlsx', '.xls', '.csv'],
    'presentations': ['.pptx', '.ppt'],
    'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'],
    'audio': ['.mp3', '.wav', '.m4a', '.ogg'],
    'video': ['.mp4', '.avi', '.mov', '.mkv', '.webm']
}

def get_file_type(filename: str) -> str:
    """Determine file type from extension"""
    ext = Path(filename).suffix.lower()
    
    for file_type, extensions in ALLOWED_EXTENSIONS.items():
        if ext in extensions:
            return file_type.rstrip('s')  # Remove plural
    
    return 'document'  # Default

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    extract_text: bool = True,
    generate_embeddings: bool = True,
    user=Depends(get_current_user)
):
    """
    Upload and store a document
    """
    try:
        # Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        allowed_exts = [ext for exts in ALLOWED_EXTENSIONS.values() for ext in exts]
        
        if file_ext not in allowed_exts:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_ext} not allowed. Allowed types: {', '.join(allowed_exts)}"
            )
        
        # Create temporary file
        temp_dir = Path("./temp")
        temp_dir.mkdir(exist_ok=True)
        temp_path = temp_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        
        # Save uploaded file
        async with aiofiles.open(temp_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Determine file type
        file_type = get_file_type(file.filename)
        
        # Store document
        stored_doc = await persistent_memory.store_document(
            file_path=str(temp_path),
            file_type=file_type,
            metadata={
                'original_filename': file.filename,
                'content_type': file.content_type,
                'uploaded_by': user.get('id', 'anonymous'),
                'upload_timestamp': datetime.now().isoformat()
            },
            extract_text=extract_text,
            generate_embeddings=generate_embeddings
        )
        
        # Clean up temp file
        temp_path.unlink()
        
        # Create memory of the upload
        await persistent_memory.create_memory(
            conversation_id=user.get('session_id', 'default'),
            content=f"Uploaded {file_type}: {file.filename}",
            memory_type='experience',
            importance=0.6
        )
        
        return {
            "success": True,
            "document": stored_doc.to_dict(),
            "message": f"Document '{file.filename}' uploaded successfully"
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )

@router.get("/list")
async def list_documents(
    file_type: Optional[str] = None,
    limit: int = 50,
    user=Depends(get_current_user)
):
    """
    List stored documents
    """
    try:
        # Get all documents
        all_docs = list(persistent_memory.document_cache.values())
        
        # Filter by type if specified
        if file_type:
            all_docs = [doc for doc in all_docs if doc.file_type == file_type]
        
        # Sort by access time
        all_docs.sort(key=lambda d: d.accessed_at, reverse=True)
        
        # Apply limit
        documents = all_docs[:limit]
        
        return {
            "success": True,
            "total": len(all_docs),
            "returned": len(documents),
            "documents": [doc.to_dict() for doc in documents]
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )

@router.get("/search")
async def search_documents(
    query: str,
    file_types: Optional[List[str]] = None,
    limit: int = 20,
    user=Depends(get_current_user)
):
    """
    Search stored documents
    """
    try:
        results = await persistent_memory.search_documents(
            query=query,
            file_types=file_types,
            limit=limit
        )
        
        return {
            "success": True,
            "query": query,
            "results": [doc.to_dict() for doc in results]
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )

@router.get("/download/{doc_id}")
async def download_document(
    doc_id: str,
    user=Depends(get_current_user)
):
    """
    Download a stored document
    """
    try:
        document = await persistent_memory.get_document(doc_id)
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get full path
        file_path = persistent_memory.vault_path / document.stored_path
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Document file not found")
        
        # Create memory of access
        await persistent_memory.create_memory(
            conversation_id=user.get('session_id', 'default'),
            content=f"Downloaded document: {document.original_name}",
            memory_type='experience',
            importance=0.3
        )
        
        return FileResponse(
            path=str(file_path),
            filename=document.original_name,
            media_type=mimetypes.guess_type(document.original_name)[0] or 'application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )

@router.get("/preview/{doc_id}")
async def preview_document(
    doc_id: str,
    user=Depends(get_current_user)
):
    """
    Get document preview (text content or thumbnail)
    """
    try:
        document = await persistent_memory.get_document(doc_id)
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get full path
        file_path = persistent_memory.vault_path / document.stored_path
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Document file not found")
        
        preview_data = {
            "doc_id": doc_id,
            "name": document.original_name,
            "type": document.file_type,
            "size": document.size,
            "created": document.created_at.isoformat()
        }
        
        # Generate preview based on file type
        if document.file_type in ['image']:
            # Create thumbnail for images
            try:
                img = Image.open(file_path)
                img.thumbnail((300, 300))
                
                buf = io.BytesIO()
                img.save(buf, format='PNG')
                img_base64 = base64.b64encode(buf.getvalue()).decode()
                
                preview_data['preview'] = {
                    'type': 'image',
                    'data': f"data:image/png;base64,{img_base64}"
                }
            except:
                preview_data['preview'] = {'type': 'error', 'message': 'Could not generate thumbnail'}
        
        elif document.extracted_text:
            # Use extracted text for documents
            preview_data['preview'] = {
                'type': 'text',
                'data': document.extracted_text[:1000] + ('...' if len(document.extracted_text) > 1000 else '')
            }
        
        else:
            preview_data['preview'] = {
                'type': 'none',
                'message': 'No preview available'
            }
        
        return preview_data
        
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )

@router.get("/view/{doc_id}")
async def view_document(
    doc_id: str,
    user=Depends(get_current_user)
):
    """
    View document in browser
    """
    try:
        document = await persistent_memory.get_document(doc_id)
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get full path
        file_path = persistent_memory.vault_path / document.stored_path
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Document file not found")
        
        # For text files, return content directly
        if document.file_type in ['text', 'document'] and document.extracted_text:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>{document.original_name}</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        max-width: 800px;
                        margin: 0 auto;
                        padding: 20px;
                        background: #1a1a1a;
                        color: #e0e0e0;
                    }}
                    .header {{
                        border-bottom: 2px solid #444;
                        padding-bottom: 10px;
                        margin-bottom: 20px;
                    }}
                    .content {{
                        white-space: pre-wrap;
                        line-height: 1.6;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>{document.original_name}</h1>
                    <p>Type: {document.file_type} | Size: {document.size / 1024:.1f} KB</p>
                </div>
                <div class="content">{document.extracted_text or 'No text content available'}</div>
            </body>
            </html>
            """
            return HTMLResponse(content=html_content)
        
        # For other files, serve them directly
        return FileResponse(
            path=str(file_path),
            filename=document.original_name,
            media_type=mimetypes.guess_type(document.original_name)[0] or 'application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )

@router.get("/stats")
async def get_storage_stats(user=Depends(get_current_user)):
    """
    Get storage statistics
    """
    try:
        stats = await persistent_memory.get_stats()
        
        return {
            "success": True,
            "stats": stats
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )