"""
Memory Management API Routes
Handles memory creation, recall, and predictions
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from datetime import datetime

from ...memory.persistent_memory_manager import persistent_memory
from ..dependencies import get_current_user

router = APIRouter()

@router.post("/create")
async def create_memory(
    content: str,
    memory_type: str = "experience",
    importance: float = 0.5,
    associations: Optional[List[str]] = None,
    user=Depends(get_current_user)
):
    """
    Create a new memory entry
    """
    try:
        # Validate memory type
        valid_types = ['fact', 'experience', 'preference', 'skill']
        if memory_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid memory type. Must be one of: {', '.join(valid_types)}"
            )
        
        # Create memory
        memory = await persistent_memory.create_memory(
            conversation_id=user.get('session_id', 'default'),
            content=content,
            memory_type=memory_type,
            importance=min(1.0, max(0.0, importance)),
            associations=associations
        )
        
        return {
            "success": True,
            "memory": memory.to_dict(),
            "message": f"{memory_type.title()} memory created successfully"
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )

@router.post("/recall")
async def recall_memories(
    query: str,
    memory_types: Optional[List[str]] = None,
    limit: int = 10,
    min_importance: float = 0.0,
    user=Depends(get_current_user)
):
    """
    Recall relevant memories based on query
    """
    try:
        memories = await persistent_memory.recall_memories(
            query=query,
            memory_types=memory_types,
            limit=limit,
            min_importance=min_importance
        )
        
        # Track the recall
        await persistent_memory.create_memory(
            conversation_id=user.get('session_id', 'default'),
            content=f"Recalled {len(memories)} memories for query: {query[:100]}",
            memory_type='experience',
            importance=0.3
        )
        
        return {
            "success": True,
            "query": query,
            "count": len(memories),
            "memories": [mem.to_dict() for mem in memories]
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )

@router.get("/changes")
async def get_recent_changes(
    limit: int = 50,
    user=Depends(get_current_user)
):
    """
    Get recent system changes
    """
    try:
        changes = await persistent_memory.get_recent_changes(limit=limit)
        
        return {
            "success": True,
            "count": len(changes),
            "changes": changes
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )

@router.get("/predictions")
async def get_predictions(user=Depends(get_current_user)):
    """
    Get system predictions based on patterns
    """
    try:
        predictions = await persistent_memory.get_predictions()
        
        return {
            "success": True,
            "count": len(predictions),
            "predictions": predictions
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )

@router.post("/learn")
async def learn_from_interaction(
    interaction: Dict[str, Any],
    user=Depends(get_current_user)
):
    """
    Learn from user interactions
    """
    try:
        # Extract important information
        user_input = interaction.get('user_input', '')
        ai_response = interaction.get('ai_response', '')
        feedback = interaction.get('feedback', None)
        
        # Determine importance based on feedback
        importance = 0.5
        if feedback:
            if feedback.get('helpful', False):
                importance = 0.8
            elif feedback.get('not_helpful', False):
                importance = 0.2
        
        # Create memory of the interaction
        memory = await persistent_memory.create_memory(
            conversation_id=user.get('session_id', 'default'),
            content=f"User: {user_input}\nAI: {ai_response}",
            memory_type='experience',
            importance=importance
        )
        
        # If user expressed preference, create preference memory
        preference_keywords = ['prefer', 'like', 'want', 'need', 'hate', 'dislike']
        if any(keyword in user_input.lower() for keyword in preference_keywords):
            await persistent_memory.create_memory(
                conversation_id=user.get('session_id', 'default'),
                content=user_input,
                memory_type='preference',
                importance=0.7,
                associations=[memory.memory_id]
            )
        
        return {
            "success": True,
            "message": "Learning recorded",
            "memory_id": memory.memory_id
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )

@router.get("/stats")
async def get_memory_stats(user=Depends(get_current_user)):
    """
    Get memory system statistics
    """
    try:
        lmdb_stats = await memory_store.get_statistics()
        persistent_stats = await persistent_memory.get_stats()
        
        return {
            "success": True,
            "lmdb_storage": lmdb_stats,
            "persistent_storage": persistent_stats,
            "summary": {
                "total_memories": persistent_stats.get('memories_created', 0),
                "total_documents": persistent_stats.get('documents_stored', 0),
                "storage_used_mb": persistent_stats.get('total_storage_mb', 0),
                "predictions_made": persistent_stats.get('predictions_made', 0)
            }
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )