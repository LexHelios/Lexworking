"""
Enhanced Persistent Memory Manager for LexOS
JAI MAHAKAAL! Complete memory and document management system
"""
import os
import json
import asyncio
import logging
import hashlib
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import aiofiles
import pandas as pd
from dataclasses import dataclass, asdict

from .lmdb_store import memory_store
from .vector_store import vector_store
from ..settings import settings

logger = logging.getLogger(__name__)

@dataclass
class StoredDocument:
    """Represents a stored document"""
    doc_id: str
    original_name: str
    stored_path: str
    file_type: str
    size: int
    checksum: str
    created_at: datetime
    accessed_at: datetime
    metadata: Dict[str, Any]
    extracted_text: Optional[str] = None
    embeddings_stored: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['accessed_at'] = self.accessed_at.isoformat()
        return data

@dataclass
class Memory:
    """Represents a memory entry"""
    memory_id: str
    conversation_id: str
    content: str
    memory_type: str  # 'fact', 'experience', 'preference', 'skill'
    importance: float  # 0.0 to 1.0
    created_at: datetime
    last_accessed: datetime
    access_count: int
    associations: List[str]  # Related memory IDs
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['last_accessed'] = self.last_accessed.isoformat()
        return data

class PersistentMemoryManager:
    """
    Enhanced memory manager with persistent document storage
    
    Features:
    - Document storage and retrieval
    - Memory extraction from documents
    - Change tracking over time
    - Predictive memory recall
    - Automatic categorization
    """
    
    def __init__(self):
        # Base paths from settings or defaults
        self.vault_path = Path(os.getenv('LEXOS_VAULT_PATH', './lex_vault'))
        self.documents_path = self.vault_path / 'documents'
        self.media_path = self.vault_path / 'media'
        self.memories_path = self.vault_path / 'memories'
        self.generated_path = self.vault_path / 'generated'
        self.changes_path = self.vault_path / 'changes'
        self.predictions_path = self.vault_path / 'predictions'
        
        # Ensure directories exist
        for path in [self.documents_path, self.media_path, self.memories_path, 
                    self.generated_path, self.changes_path, self.predictions_path]:
            path.mkdir(parents=True, exist_ok=True)
        
        # Document index
        self.document_index_path = self.vault_path / 'index' / 'documents.json'
        self.memory_index_path = self.vault_path / 'index' / 'memories.json'
        
        # In-memory caches
        self.document_cache = {}
        self.memory_cache = {}
        self.recent_changes = []
        
        # Performance tracking
        self.stats = {
            'documents_stored': 0,
            'memories_created': 0,
            'predictions_made': 0,
            'total_storage_mb': 0
        }
        
        logger.info("Persistent Memory Manager initialized")
    
    async def initialize(self):
        """Initialize the memory manager"""
        try:
            # Load existing indexes
            await self._load_indexes()
            
            # Initialize LMDB and vector stores
            await memory_store.initialize()
            await vector_store.initialize()
            
            # Calculate storage statistics
            await self._update_storage_stats()
            
            logger.info(f"Memory Manager ready. Documents: {len(self.document_cache)}, Memories: {len(self.memory_cache)}")
            
        except Exception as e:
            logger.error(f"Memory Manager initialization error: {e}")
            raise
    
    async def store_document(
        self,
        file_path: str,
        file_type: str,
        metadata: Optional[Dict[str, Any]] = None,
        extract_text: bool = True,
        generate_embeddings: bool = True
    ) -> StoredDocument:
        """
        Store a document in the persistent vault
        """
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Generate document ID
            doc_id = self._generate_document_id(file_path)
            
            # Determine storage location
            if file_type in ['pdf', 'doc', 'docx', 'txt', 'csv', 'xlsx']:
                storage_dir = self.documents_path
            elif file_type in ['png', 'jpg', 'jpeg', 'gif', 'mp4', 'mp3']:
                storage_dir = self.media_path
            else:
                storage_dir = self.documents_path
            
            # Create dated subdirectory
            date_dir = storage_dir / datetime.now().strftime('%Y/%m/%d')
            date_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy file to vault
            stored_filename = f"{doc_id}_{file_path.name}"
            stored_path = date_dir / stored_filename
            shutil.copy2(file_path, stored_path)
            
            # Calculate checksum
            checksum = await self._calculate_checksum(stored_path)
            
            # Extract text if requested
            extracted_text = None
            if extract_text:
                # Import enhanced PDF processor if available
                try:
                    from ...enhanced_pdf_processor import enhanced_pdf_processor
                    result = await enhanced_pdf_processor.process_file(
                        str(stored_path),
                        extract_images=True,
                        extract_tables=True,
                        ocr_mode="auto"
                    )
                    if result.get('success'):
                        extracted_text = result.get('text', '')
                except:
                    pass
            
            # Create document record
            document = StoredDocument(
                doc_id=doc_id,
                original_name=file_path.name,
                stored_path=str(stored_path.relative_to(self.vault_path)),
                file_type=file_type,
                size=stored_path.stat().st_size,
                checksum=checksum,
                created_at=datetime.now(),
                accessed_at=datetime.now(),
                metadata=metadata or {},
                extracted_text=extracted_text,
                embeddings_stored=False
            )
            
            # Generate embeddings if requested
            if generate_embeddings and extracted_text:
                await self._generate_document_embeddings(document)
                document.embeddings_stored = True
            
            # Store in cache and index
            self.document_cache[doc_id] = document
            await self._save_document_index()
            
            # Track change
            await self._track_change('document_added', {
                'doc_id': doc_id,
                'name': file_path.name,
                'type': file_type,
                'size': document.size
            })
            
            # Update stats
            self.stats['documents_stored'] += 1
            
            logger.info(f"Document stored: {doc_id} ({file_path.name})")
            return document
            
        except Exception as e:
            logger.error(f"Document storage error: {e}")
            raise
    
    async def create_memory(
        self,
        conversation_id: str,
        content: str,
        memory_type: str = 'experience',
        importance: float = 0.5,
        associations: List[str] = None
    ) -> Memory:
        """
        Create a new memory entry
        """
        try:
            # Generate memory ID
            memory_id = self._generate_memory_id(conversation_id, content)
            
            # Create memory object
            memory = Memory(
                memory_id=memory_id,
                conversation_id=conversation_id,
                content=content,
                memory_type=memory_type,
                importance=min(1.0, max(0.0, importance)),
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                access_count=1,
                associations=associations or []
            )
            
            # Store in LMDB
            await memory_store.save_experience(conversation_id, memory.to_dict())
            
            # Generate embeddings
            embeddings = await vector_store.generate_embeddings(content)
            await vector_store.store_embeddings(
                memory_id,
                embeddings,
                metadata=memory.to_dict()
            )
            
            # Store in cache and index
            self.memory_cache[memory_id] = memory
            await self._save_memory_index()
            
            # Track change
            await self._track_change('memory_created', {
                'memory_id': memory_id,
                'type': memory_type,
                'importance': importance
            })
            
            # Update stats
            self.stats['memories_created'] += 1
            
            # Make predictions if important
            if importance > 0.7:
                await self._generate_predictions(memory)
            
            logger.info(f"Memory created: {memory_id} (type: {memory_type})")
            return memory
            
        except Exception as e:
            logger.error(f"Memory creation error: {e}")
            raise
    
    async def recall_memories(
        self,
        query: str,
        memory_types: Optional[List[str]] = None,
        limit: int = 10,
        min_importance: float = 0.0
    ) -> List[Memory]:
        """
        Recall relevant memories based on query
        """
        try:
            # Search in vector store
            search_results = await vector_store.search_similar(
                query,
                top_k=limit * 2  # Get more to filter
            )
            
            recalled_memories = []
            for result in search_results:
                memory_id = result['id']
                if memory_id in self.memory_cache:
                    memory = self.memory_cache[memory_id]
                    
                    # Apply filters
                    if memory_types and memory.memory_type not in memory_types:
                        continue
                    if memory.importance < min_importance:
                        continue
                    
                    # Update access stats
                    memory.last_accessed = datetime.now()
                    memory.access_count += 1
                    
                    recalled_memories.append(memory)
                    
                    if len(recalled_memories) >= limit:
                        break
            
            # Sort by relevance and importance
            recalled_memories.sort(
                key=lambda m: (result['score'] * m.importance),
                reverse=True
            )
            
            return recalled_memories
            
        except Exception as e:
            logger.error(f"Memory recall error: {e}")
            return []
    
    async def get_document(self, doc_id: str) -> Optional[StoredDocument]:
        """Retrieve a stored document"""
        if doc_id in self.document_cache:
            document = self.document_cache[doc_id]
            document.accessed_at = datetime.now()
            return document
        return None
    
    async def search_documents(
        self,
        query: str,
        file_types: Optional[List[str]] = None,
        limit: int = 20
    ) -> List[StoredDocument]:
        """Search stored documents"""
        try:
            results = []
            query_lower = query.lower()
            
            for doc in self.document_cache.values():
                # Filter by file type
                if file_types and doc.file_type not in file_types:
                    continue
                
                # Search in name and extracted text
                if (query_lower in doc.original_name.lower() or
                    (doc.extracted_text and query_lower in doc.extracted_text.lower())):
                    results.append(doc)
                    
                if len(results) >= limit:
                    break
            
            # Sort by access time
            results.sort(key=lambda d: d.accessed_at, reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"Document search error: {e}")
            return []
    
    async def get_recent_changes(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent changes tracked by the system"""
        changes_file = self.changes_path / 'recent_changes.json'
        
        try:
            if changes_file.exists():
                async with aiofiles.open(changes_file, 'r') as f:
                    content = await f.read()
                    all_changes = json.loads(content)
                    return all_changes[-limit:]
            return []
        except Exception as e:
            logger.error(f"Error loading changes: {e}")
            return []
    
    async def get_predictions(self) -> List[Dict[str, Any]]:
        """Get system predictions based on patterns"""
        predictions_file = self.predictions_path / 'current_predictions.json'
        
        try:
            if predictions_file.exists():
                async with aiofiles.open(predictions_file, 'r') as f:
                    content = await f.read()
                    return json.loads(content)
            return []
        except Exception as e:
            logger.error(f"Error loading predictions: {e}")
            return []
    
    async def _track_change(self, change_type: str, details: Dict[str, Any]):
        """Track a system change"""
        try:
            change = {
                'timestamp': datetime.now().isoformat(),
                'type': change_type,
                'details': details
            }
            
            # Add to recent changes
            self.recent_changes.append(change)
            if len(self.recent_changes) > 1000:
                self.recent_changes = self.recent_changes[-500:]
            
            # Save to file
            changes_file = self.changes_path / 'recent_changes.json'
            async with aiofiles.open(changes_file, 'w') as f:
                await f.write(json.dumps(self.recent_changes, indent=2))
                
        except Exception as e:
            logger.error(f"Change tracking error: {e}")
    
    async def _generate_predictions(self, memory: Memory):
        """Generate predictions based on memory patterns"""
        try:
            # Simple prediction logic - can be enhanced with ML
            predictions = []
            
            # Predict based on memory type and content
            if memory.memory_type == 'preference':
                predictions.append({
                    'type': 'user_preference',
                    'prediction': f"User will likely want similar to: {memory.content[:100]}",
                    'confidence': 0.7,
                    'based_on': memory.memory_id
                })
            
            if memory.memory_type == 'experience' and memory.importance > 0.8:
                predictions.append({
                    'type': 'important_recall',
                    'prediction': f"This will be referenced again: {memory.content[:100]}",
                    'confidence': 0.8,
                    'based_on': memory.memory_id
                })
            
            # Save predictions
            if predictions:
                predictions_file = self.predictions_path / 'current_predictions.json'
                existing = []
                if predictions_file.exists():
                    async with aiofiles.open(predictions_file, 'r') as f:
                        content = await f.read()
                        existing = json.loads(content)
                
                existing.extend(predictions)
                
                async with aiofiles.open(predictions_file, 'w') as f:
                    await f.write(json.dumps(existing[-100:], indent=2))  # Keep last 100
                
                self.stats['predictions_made'] += len(predictions)
                
        except Exception as e:
            logger.error(f"Prediction generation error: {e}")
    
    async def _generate_document_embeddings(self, document: StoredDocument):
        """Generate and store embeddings for a document"""
        try:
            if document.extracted_text:
                # Split into chunks for large documents
                chunks = self._split_text_into_chunks(document.extracted_text)
                
                for i, chunk in enumerate(chunks):
                    chunk_id = f"{document.doc_id}_chunk_{i}"
                    embeddings = await vector_store.generate_embeddings(chunk)
                    
                    await vector_store.store_embeddings(
                        chunk_id,
                        embeddings,
                        metadata={
                            'doc_id': document.doc_id,
                            'chunk_index': i,
                            'total_chunks': len(chunks),
                            'file_type': document.file_type
                        }
                    )
                    
        except Exception as e:
            logger.error(f"Embedding generation error: {e}")
    
    def _split_text_into_chunks(self, text: str, chunk_size: int = 1000) -> List[str]:
        """Split text into chunks for embedding"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i + chunk_size])
            chunks.append(chunk)
        
        return chunks
    
    def _generate_document_id(self, file_path: Path) -> str:
        """Generate unique document ID"""
        content = f"{file_path.name}_{file_path.stat().st_size}_{datetime.now().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def _generate_memory_id(self, conversation_id: str, content: str) -> str:
        """Generate unique memory ID"""
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:8]
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f"{conversation_id[:8]}_{timestamp}_{content_hash}"
    
    async def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate file checksum"""
        sha256_hash = hashlib.sha256()
        
        async with aiofiles.open(file_path, 'rb') as f:
            while chunk := await f.read(8192):
                sha256_hash.update(chunk)
        
        return sha256_hash.hexdigest()
    
    async def _load_indexes(self):
        """Load document and memory indexes"""
        try:
            # Load document index
            if self.document_index_path.exists():
                async with aiofiles.open(self.document_index_path, 'r') as f:
                    content = await f.read()
                    doc_data = json.loads(content)
                    
                    for doc_dict in doc_data:
                        doc_dict['created_at'] = datetime.fromisoformat(doc_dict['created_at'])
                        doc_dict['accessed_at'] = datetime.fromisoformat(doc_dict['accessed_at'])
                        doc = StoredDocument(**doc_dict)
                        self.document_cache[doc.doc_id] = doc
            
            # Load memory index
            if self.memory_index_path.exists():
                async with aiofiles.open(self.memory_index_path, 'r') as f:
                    content = await f.read()
                    mem_data = json.loads(content)
                    
                    for mem_dict in mem_data:
                        mem_dict['created_at'] = datetime.fromisoformat(mem_dict['created_at'])
                        mem_dict['last_accessed'] = datetime.fromisoformat(mem_dict['last_accessed'])
                        memory = Memory(**mem_dict)
                        self.memory_cache[memory.memory_id] = memory
                        
        except Exception as e:
            logger.error(f"Index loading error: {e}")
    
    async def _save_document_index(self):
        """Save document index"""
        try:
            self.document_index_path.parent.mkdir(parents=True, exist_ok=True)
            
            doc_list = [doc.to_dict() for doc in self.document_cache.values()]
            
            async with aiofiles.open(self.document_index_path, 'w') as f:
                await f.write(json.dumps(doc_list, indent=2))
                
        except Exception as e:
            logger.error(f"Document index save error: {e}")
    
    async def _save_memory_index(self):
        """Save memory index"""
        try:
            self.memory_index_path.parent.mkdir(parents=True, exist_ok=True)
            
            mem_list = [mem.to_dict() for mem in self.memory_cache.values()]
            
            async with aiofiles.open(self.memory_index_path, 'w') as f:
                await f.write(json.dumps(mem_list, indent=2))
                
        except Exception as e:
            logger.error(f"Memory index save error: {e}")
    
    async def _update_storage_stats(self):
        """Update storage statistics"""
        try:
            total_size = 0
            
            for path in [self.documents_path, self.media_path, self.generated_path]:
                for file_path in path.rglob('*'):
                    if file_path.is_file():
                        total_size += file_path.stat().st_size
            
            self.stats['total_storage_mb'] = total_size / (1024 * 1024)
            
        except Exception as e:
            logger.error(f"Stats update error: {e}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get memory manager statistics"""
        await self._update_storage_stats()
        
        return {
            **self.stats,
            'documents_cached': len(self.document_cache),
            'memories_cached': len(self.memory_cache),
            'recent_changes': len(self.recent_changes)
        }

# Global instance
persistent_memory = PersistentMemoryManager()