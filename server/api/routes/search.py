"""
Web Search API Routes
Provides endpoints for web search functionality
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any
import logging

from ...web.search_engine import web_search_engine
from ...lex.web_search_consciousness import web_search_consciousness

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/search",
    tags=["search"],
    responses={404: {"description": "Not found"}}
)

@router.get("/web")
async def search_web(
    q: str = Query(..., description="Search query"),
    num_results: int = Query(10, ge=1, le=50, description="Number of results"),
    search_type: str = Query("general", description="Type of search: general, news, images"),
    time_range: Optional[str] = Query(None, description="Time range: day, week, month, year")
) -> Dict[str, Any]:
    """
    Perform web search
    """
    try:
        results = await web_search_engine.search(
            query=q,
            num_results=num_results,
            search_type=search_type,
            time_range=time_range
        )
        
        return {
            "success": True,
            "query": q,
            "results": results.get("results", []),
            "total_results": results.get("total_results", 0),
            "provider": results.get("provider", "unknown"),
            "timestamp": results.get("timestamp")
        }
        
    except Exception as e:
        logger.error(f"Web search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/news")
async def search_news(
    q: str = Query(..., description="News search query"),
    num_results: int = Query(10, ge=1, le=50, description="Number of results"),
    time_range: str = Query("day", description="Time range: day, week, month")
) -> Dict[str, Any]:
    """
    Search for news articles
    """
    try:
        results = await web_search_engine.search_news(
            query=q,
            num_results=num_results,
            time_range=time_range
        )
        
        return {
            "success": True,
            "query": q,
            "results": results.get("results", []),
            "total_results": results.get("total_results", 0),
            "provider": results.get("provider", "unknown"),
            "search_type": "news",
            "timestamp": results.get("timestamp")
        }
        
    except Exception as e:
        logger.error(f"News search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/realtime")
async def search_realtime(
    q: str = Query(..., description="Real-time search query"),
    num_results: int = Query(5, ge=1, le=20, description="Number of results")
) -> Dict[str, Any]:
    """
    Search for real-time/current information
    """
    try:
        results = await web_search_engine.search_realtime(
            query=q,
            num_results=num_results
        )
        
        return {
            "success": True,
            "query": q,
            "results": results.get("results", []),
            "total_results": results.get("total_results", 0),
            "provider": results.get("provider", "unknown"),
            "search_type": "realtime",
            "timestamp": results.get("timestamp")
        }
        
    except Exception as e:
        logger.error(f"Real-time search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/providers")
async def get_search_providers() -> Dict[str, Any]:
    """
    Get available search providers and their status
    """
    providers_status = {}
    
    for provider, config in web_search_engine.providers.items():
        providers_status[provider] = {
            "enabled": config["enabled"],
            "requires_key": config.get("requires_key", False),
            "rate_limit": config.get("rate_limit", 0)
        }
    
    return {
        "success": True,
        "providers": providers_status,
        "cache_ttl": web_search_engine.cache_ttl
    }

@router.post("/natural")
async def natural_language_search(
    request: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Process natural language search request through LEX consciousness
    """
    try:
        user_input = request.get("query", "")
        context = request.get("context", {})
        
        # Process through web search consciousness
        result = await web_search_consciousness.process_search_intent(user_input, context)
        
        if result:
            return {
                "success": True,
                "response": result.get("response", ""),
                "data": result.get("data", {}),
                "formatting": result.get("formatting", "plain"),
                "show_ui": result.get("show_ui", False)
            }
        else:
            return {
                "success": False,
                "message": "No search intent detected in query"
            }
            
    except Exception as e:
        logger.error(f"Natural language search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))