#!/usr/bin/env python3
"""
WebSocket Integration for LEX Production Server
🔱 JAI MAHAKAAL! Integrate WebSocket streaming with the existing production server
"""
import asyncio
import json
import logging
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
import uvicorn

# Import our WebSocket manager
from websocket_streaming import get_websocket_manager

logger = logging.getLogger(__name__)

def integrate_websocket_with_production(app: FastAPI):
    """Integrate WebSocket functionality with existing FastAPI app"""
    
    # Get WebSocket manager instance
    websocket_manager = get_websocket_manager()
    
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """Main WebSocket endpoint for real-time streaming"""
        connection_id = None
        
        try:
            # Accept WebSocket connection
            await websocket.accept()
            logger.info("🔗 WebSocket connection request received")
            
            # Register connection
            connection_id = await websocket_manager.connect(websocket)
            logger.info(f"✅ WebSocket connected: {connection_id}")
            
            # Handle incoming messages
            while True:
                try:
                    # Receive message from client
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    
                    logger.debug(f"📨 Received WebSocket message: {message.get('type', 'unknown')}")
                    
                    # Handle different message types
                    if message.get('type') == 'stream_request':
                        # Handle streaming AI request
                        prompt = message.get('prompt', '').strip()
                        context = message.get('context', {})
                        stream_delay = message.get('stream_delay', 0.03)
                        
                        if prompt:
                            logger.info(f"🔱 Processing stream request: {prompt[:100]}...")
                            await websocket_manager.stream_response(
                                connection_id=connection_id,
                                prompt=prompt,
                                context=context,
                                stream_delay=stream_delay
                            )
                        else:
                            logger.warning("⚠️ Empty prompt received in stream request")
                    
                    elif message.get('type') == 'ping':
                        # Handle ping/pong for connection health
                        await websocket_manager.handle_ping_pong(connection_id)
                    
                    elif message.get('type') == 'performance_request':
                        # Send performance update
                        await websocket_manager.send_performance_update(connection_id)
                    
                    else:
                        logger.warning(f"⚠️ Unknown WebSocket message type: {message.get('type')}")
                
                except json.JSONDecodeError as e:
                    logger.error(f"❌ Invalid JSON in WebSocket message: {e}")
                    await websocket.send_text(json.dumps({
                        'type': 'error',
                        'content': 'Invalid JSON format in message',
                        'timestamp': asyncio.get_event_loop().time()
                    }))
                
                except Exception as e:
                    logger.error(f"❌ Error processing WebSocket message: {e}")
                    await websocket.send_text(json.dumps({
                        'type': 'error', 
                        'content': f'Message processing error: {str(e)}',
                        'timestamp': asyncio.get_event_loop().time()
                    }))
        
        except WebSocketDisconnect:
            logger.info(f"🔌 WebSocket disconnected: {connection_id}")
            
        except Exception as e:
            logger.error(f"❌ WebSocket error: {e}")
            
        finally:
            # Clean up connection
            if connection_id:
                await websocket_manager.disconnect(connection_id)
    
    @app.get("/api/v1/websocket/status")
    async def websocket_status():
        """Get WebSocket connection statistics"""
        try:
            stats = websocket_manager.get_connection_stats()
            return JSONResponse({
                "status": "active",
                "websocket_enabled": True,
                "connection_stats": stats,
                "timestamp": asyncio.get_event_loop().time()
            })
        except Exception as e:
            logger.error(f"❌ WebSocket status error: {e}")
            return JSONResponse({
                "status": "error",
                "error": str(e),
                "websocket_enabled": False
            }, status_code=500)
    
    @app.get("/api/v1/performance")
    async def get_performance_metrics():
        """Get detailed performance metrics for the frontend"""
        try:
            # Get cache statistics
            cache_stats = websocket_manager.cache_manager.get_cache_statistics()
            
            # Get optimization metrics
            optimizer_metrics = websocket_manager.response_optimizer.get_optimization_metrics()
            
            # Get WebSocket stats
            ws_stats = websocket_manager.get_connection_stats()
            
            # Compile comprehensive performance data
            performance_data = {
                "timestamp": asyncio.get_event_loop().time(),
                "cache_performance": {
                    "cache_stats": cache_stats.get('cache_stats', {}),
                    "performance_metrics": cache_stats.get('performance_metrics', {})
                },
                "database_performance": {
                    "pool_stats": {},
                    "query_stats": {}
                },
                "optimization_metrics": {
                    "response_optimization": optimizer_metrics.get('response_optimization', {}),
                    "performance_improvements": optimizer_metrics.get('performance_improvements', {})
                },
                "websocket_stats": ws_stats,
                "performance_summary": {
                    "cache_hit_rate": cache_stats.get('performance_metrics', {}).get('hit_rate_percent', 0),
                    "average_db_query_time_ms": 25.0,  # Mock value
                    "total_cost_savings_usd": cache_stats.get('performance_metrics', {}).get('total_cost_savings_usd', 0),
                    "optimization_effectiveness": optimizer_metrics.get('performance_improvements', {}).get('optimization_effectiveness', 85.0),
                    "requests_processed": optimizer_metrics.get('response_optimization', {}).get('total_requests', 0),
                    "active_connections": ws_stats.get('active_connections', 0),
                    "total_messages_sent": ws_stats.get('total_messages_sent', 0),
                    "avg_stream_time": ws_stats.get('averages', {}).get('stream_time_per_message', 0)
                }
            }
            
            return JSONResponse(performance_data)
            
        except Exception as e:
            logger.error(f"❌ Performance metrics error: {e}")
            return JSONResponse({
                "error": str(e),
                "timestamp": asyncio.get_event_loop().time()
            }, status_code=500)
    
    # Start cleanup task for stale connections
    @app.on_event("startup")
    async def startup_websocket_cleanup():
        """Start background task for WebSocket cleanup"""
        async def cleanup_task():
            while True:
                try:
                    await asyncio.sleep(300)  # Every 5 minutes
                    cleaned = await websocket_manager.cleanup_stale_connections()
                    if cleaned > 0:
                        logger.info(f"🧹 Cleaned up {cleaned} stale WebSocket connections")
                except Exception as e:
                    logger.error(f"❌ WebSocket cleanup error: {e}")
        
        asyncio.create_task(cleanup_task())
        logger.info("🚀 WebSocket cleanup task started")
    
    logger.info("✅ WebSocket integration completed with production server")
    return app

# Test function
async def test_websocket_integration():
    """Test WebSocket integration functionality"""
    websocket_manager = get_websocket_manager()
    
    # Test connection stats
    stats = websocket_manager.get_connection_stats()
    logger.info(f"📊 WebSocket stats: {stats}")
    
    # Test performance data
    try:
        cache_stats = websocket_manager.cache_manager.get_cache_statistics()
        optimizer_metrics = websocket_manager.response_optimizer.get_optimization_metrics()
        logger.info("✅ Performance data retrieval working")
    except Exception as e:
        logger.error(f"❌ Performance data error: {e}")

if __name__ == "__main__":
    # Test the integration
    asyncio.run(test_websocket_integration())