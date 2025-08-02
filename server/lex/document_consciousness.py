"""
Document Consciousness Extension for LEX
Integrates document management directly into LEX's capabilities
"""
import logging
import base64
from typing import Dict, List, Any, Optional
from pathlib import Path

from ..memory.persistent_memory_manager import persistent_memory
from ..multimodal.vision_processor import vision_processor

logger = logging.getLogger(__name__)

class DocumentConsciousness:
    """
    Document awareness and management capabilities for LEX
    """
    
    def __init__(self):
        self.commands = {
            "show documents": self.list_documents,
            "show files": self.list_documents,
            "search documents": self.search_documents,
            "find document": self.search_documents,
            "open document": self.open_document,
            "view document": self.open_document,
            "show pdf": self.show_specific_type,
            "show images": self.show_specific_type,
            "recent documents": self.recent_documents,
            "upload": self.guide_upload,
            "store document": self.guide_upload
        }
        
        logger.info("Document Consciousness initialized")
    
    async def process_document_intent(self, user_input: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process document-related intents
        """
        lower_input = user_input.lower()
        
        # Check for document commands
        for command, handler in self.commands.items():
            if command in lower_input:
                return await handler(user_input, context)
        
        # Check if user is asking about a specific document
        if any(word in lower_input for word in ['document', 'file', 'pdf', 'image', 'spreadsheet']):
            return await self.handle_document_query(user_input, context)
        
        return None
    
    async def list_documents(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """List all stored documents"""
        try:
            # Get document type filter if specified
            file_type = None
            if 'pdf' in user_input.lower():
                file_type = 'pdf'
            elif 'image' in user_input.lower():
                file_type = 'image'
            elif 'spreadsheet' in user_input.lower() or 'excel' in user_input.lower():
                file_type = 'spreadsheet'
            
            # Get documents
            documents = list(persistent_memory.document_cache.values())
            
            if file_type:
                documents = [d for d in documents if d.file_type == file_type]
            
            # Sort by recent access
            documents.sort(key=lambda d: d.accessed_at, reverse=True)
            
            # Format response
            if not documents:
                return {
                    "type": "document_list",
                    "response": "No documents found in the vault.",
                    "documents": []
                }
            
            # Create formatted list
            doc_list = []
            for i, doc in enumerate(documents[:20]):  # Limit to 20 most recent
                doc_list.append({
                    "index": i + 1,
                    "name": doc.original_name,
                    "type": doc.file_type,
                    "size": self._format_size(doc.size),
                    "created": doc.created_at.strftime("%Y-%m-%d"),
                    "doc_id": doc.doc_id
                })
            
            response_text = f"📁 **Document Vault** - {len(documents)} documents stored\n\n"
            
            for doc in doc_list[:10]:  # Show first 10 in text
                response_text += f"{doc['index']}. **{doc['name']}** ({doc['type']}) - {doc['size']}\n"
            
            if len(documents) > 10:
                response_text += f"\n... and {len(documents) - 10} more documents"
            
            response_text += "\n\nYou can say 'open document 1' or 'view [document name]' to see any document."
            
            return {
                "type": "document_list",
                "response": response_text,
                "documents": doc_list,
                "total_count": len(documents),
                "show_ui": True  # Signal to show document UI panel
            }
            
        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            return {
                "type": "error",
                "response": "I encountered an error accessing the document vault."
            }
    
    async def search_documents(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Search for specific documents"""
        try:
            # Extract search query
            search_terms = user_input.lower().replace('search documents', '').replace('find document', '').strip()
            
            if not search_terms or search_terms in ['for', 'about']:
                return {
                    "type": "search_prompt",
                    "response": "What would you like to search for? Please provide keywords or document names."
                }
            
            # Perform search
            results = await persistent_memory.search_documents(search_terms, limit=10)
            
            if not results:
                return {
                    "type": "search_results",
                    "response": f"No documents found matching '{search_terms}'",
                    "documents": []
                }
            
            # Format results
            response_text = f"🔍 **Search Results** for '{search_terms}':\n\n"
            
            doc_list = []
            for i, doc in enumerate(results):
                doc_list.append({
                    "index": i + 1,
                    "name": doc.original_name,
                    "type": doc.file_type,
                    "doc_id": doc.doc_id,
                    "preview": doc.extracted_text[:200] if doc.extracted_text else None
                })
                
                response_text += f"{i+1}. **{doc.original_name}** ({doc.file_type})\n"
                if doc.extracted_text:
                    preview = doc.extracted_text[:100].replace('\n', ' ')
                    response_text += f"   *{preview}...*\n"
                response_text += "\n"
            
            return {
                "type": "search_results",
                "response": response_text,
                "documents": doc_list,
                "query": search_terms
            }
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return {
                "type": "error",
                "response": "I encountered an error searching documents."
            }
    
    async def open_document(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Open a specific document"""
        try:
            # Extract document reference (by index or name)
            words = user_input.lower().split()
            
            # Check for index reference (e.g., "open document 1")
            for i, word in enumerate(words):
                if word.isdigit():
                    index = int(word) - 1
                    recent_docs = list(persistent_memory.document_cache.values())
                    recent_docs.sort(key=lambda d: d.accessed_at, reverse=True)
                    
                    if 0 <= index < len(recent_docs):
                        doc = recent_docs[index]
                        return await self._format_document_response(doc)
            
            # Search by name
            search_terms = user_input.lower().replace('open document', '').replace('view document', '').strip()
            results = await persistent_memory.search_documents(search_terms, limit=1)
            
            if results:
                return await self._format_document_response(results[0])
            
            return {
                "type": "document_not_found",
                "response": f"I couldn't find a document matching '{search_terms}'. Try 'show documents' to see available files."
            }
            
        except Exception as e:
            logger.error(f"Error opening document: {e}")
            return {
                "type": "error",
                "response": "I encountered an error opening the document."
            }
    
    async def _format_document_response(self, document) -> Dict[str, Any]:
        """Format a document for display"""
        try:
            response = {
                "type": "document_view",
                "document": {
                    "doc_id": document.doc_id,
                    "name": document.original_name,
                    "type": document.file_type,
                    "size": self._format_size(document.size),
                    "created": document.created_at.strftime("%Y-%m-%d %H:%M")
                }
            }
            
            # Add content based on type
            if document.file_type == 'image':
                # Get image as base64
                file_path = persistent_memory.vault_path / document.stored_path
                if file_path.exists():
                    with open(file_path, 'rb') as f:
                        img_data = f.read()
                        img_base64 = base64.b64encode(img_data).decode('utf-8')
                        response["document"]["image_data"] = f"data:image/{file_path.suffix[1:]};base64,{img_base64}"
                
                response["response"] = f"📷 **{document.original_name}**\n\nShowing image ({document.file_type}, {self._format_size(document.size)})"
                
            elif document.extracted_text:
                # Show text preview
                preview = document.extracted_text[:1000]
                if len(document.extracted_text) > 1000:
                    preview += "\n\n... (document continues)"
                
                response["document"]["text_content"] = preview
                response["response"] = f"📄 **{document.original_name}**\n\n{preview}"
                
            else:
                response["response"] = f"📎 **{document.original_name}**\n\nType: {document.file_type}\nSize: {self._format_size(document.size)}\n\nNo preview available. You can download this file to view it."
            
            # Add action buttons
            response["actions"] = [
                {"type": "download", "label": "Download", "doc_id": document.doc_id},
                {"type": "view_full", "label": "View Full", "doc_id": document.doc_id}
            ]
            
            return response
            
        except Exception as e:
            logger.error(f"Error formatting document: {e}")
            return {
                "type": "error",
                "response": "Error displaying document"
            }
    
    async def recent_documents(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Show recently accessed documents"""
        documents = list(persistent_memory.document_cache.values())
        documents.sort(key=lambda d: d.accessed_at, reverse=True)
        
        recent = documents[:5]
        
        if not recent:
            return {
                "type": "document_list",
                "response": "No documents have been accessed recently.",
                "documents": []
            }
        
        response_text = "📅 **Recently Accessed Documents**:\n\n"
        
        for i, doc in enumerate(recent):
            response_text += f"{i+1}. **{doc.original_name}** - accessed {self._format_time_ago(doc.accessed_at)}\n"
        
        return {
            "type": "document_list",
            "response": response_text,
            "documents": [{"name": d.original_name, "doc_id": d.doc_id} for d in recent]
        }
    
    async def show_specific_type(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Show documents of a specific type"""
        if 'pdf' in user_input.lower():
            file_type = 'pdf'
        elif 'image' in user_input.lower():
            file_type = 'image'
        else:
            file_type = None
        
        # Reuse list_documents with type filter
        return await self.list_documents(f"show {file_type} documents", context)
    
    async def guide_upload(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Guide user on how to upload documents"""
        return {
            "type": "upload_guide",
            "response": "📤 **To upload documents:**\n\n1. Drag and drop files onto this chat window\n2. Click the paperclip 📎 icon to browse files\n3. Paste images directly into the chat\n\nI support PDFs, Word docs, Excel files, images, and more. Once uploaded, I'll store them securely in your document vault for easy access anytime.",
            "show_upload": True
        }
    
    async def handle_document_query(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general document queries"""
        # Check if asking about a specific document
        documents = list(persistent_memory.document_cache.values())
        
        for doc in documents:
            if doc.original_name.lower() in user_input.lower():
                return await self._format_document_response(doc)
        
        # General document question
        return {
            "type": "document_help",
            "response": "I can help you manage documents. Try:\n\n• 'Show documents' - View all stored files\n• 'Search documents about [topic]' - Find specific files\n• 'Recent documents' - See recently accessed files\n• 'Upload' - Add new documents\n\nWhat would you like to do?"
        }
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    
    def _format_time_ago(self, dt) -> str:
        """Format time as 'X ago'"""
        from datetime import datetime
        diff = datetime.now() - dt
        
        if diff.days > 0:
            return f"{diff.days} days ago"
        elif diff.seconds > 3600:
            return f"{diff.seconds // 3600} hours ago"
        elif diff.seconds > 60:
            return f"{diff.seconds // 60} minutes ago"
        else:
            return "just now"

# Global instance
document_consciousness = DocumentConsciousness()