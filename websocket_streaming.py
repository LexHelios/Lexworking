#!/usr/bin/env python3
"""
WebSocket Streaming Manager for LEX Real-Time Responses
🔱 JAI MAHAKAAL! Real-time streaming like ChatGPT for enhanced UX
"""
import asyncio
import json
import logging
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Set, AsyncGenerator
from dataclasses import dataclass, asdict
from enum import Enum
import websockets
from websockets.exceptions import ConnectionClosed, WebSocketException

# Import our optimization components
from cache_manager import get_cache_manager
from response_optimizer import get_response_optimizer
from security_config import sanitize_input, generate_request_id

logger = logging.getLogger(__name__)

class StreamType(Enum):
    MESSAGE = "message"
    TOKEN = "token"
    STATUS = "status"
    ERROR = "error"
    COMPLETE = "complete"
    METADATA = "metadata"

@dataclass
class StreamChunk:
    """Individual stream chunk data"""
    id: str
    type: StreamType
    content: str
    metadata: Dict = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
        if self.metadata is None:
            self.metadata = {}

class WebSocketConnectionManager:
    """Manages WebSocket connections for real-time streaming"""
    
    def __init__(self):
        # Active connections storage
        self.active_connections: Dict[str, Dict] = {}
        self.connection_groups: Dict[str, Set[str]] = {}
        
        # Performance tracking
        self.total_connections = 0
        self.total_messages_sent = 0
        self.total_stream_time = 0.0
        
        # Components
        self.cache_manager = get_cache_manager()
        self.response_optimizer = get_response_optimizer()
        
        logger.info("✅ WebSocket Connection Manager initialized")
    
    async def connect(self, websocket, connection_id: str = None, user_id: str = None, group: str = "default") -> str:
        """Register new WebSocket connection"""
        if connection_id is None:
            connection_id = str(uuid.uuid4())
        
        try:
            connection_info = {
                'websocket': websocket,
                'connection_id': connection_id,
                'user_id': user_id or f"user_{connection_id[:8]}",
                'group': group,
                'connected_at': datetime.utcnow(),
                'last_ping': time.time(),
                'messages_sent': 0,
                'total_stream_time': 0.0
            }
            
            self.active_connections[connection_id] = connection_info
            
            # Add to group
            if group not in self.connection_groups:
                self.connection_groups[group] = set()
            self.connection_groups[group].add(connection_id)
            
            self.total_connections += 1
            
            # Send welcome message
            await self.send_to_connection(connection_id, StreamChunk(
                id=generate_request_id(),
                type=StreamType.STATUS,
                content="🔱 LEX WebSocket connected! Real-time streaming active.",
                metadata={
                    'connection_id': connection_id,
                    'user_id': connection_info['user_id'],
                    'features': ['streaming', 'real_time', 'performance_optimized']
                }
            ))
            
            logger.info(f"✅ WebSocket connected: {connection_id} (User: {connection_info['user_id']}, Group: {group})")
            return connection_id
            
        except Exception as e:
            logger.error(f"❌ WebSocket connection failed: {e}")
            raise
    
    async def disconnect(self, connection_id: str):
        """Remove WebSocket connection"""
        if connection_id in self.active_connections:
            connection_info = self.active_connections[connection_id]
            group = connection_info['group']
            
            # Remove from group
            if group in self.connection_groups:
                self.connection_groups[group].discard(connection_id)
                if not self.connection_groups[group]:
                    del self.connection_groups[group]
            
            # Log connection stats
            duration = (datetime.utcnow() - connection_info['connected_at']).total_seconds()
            logger.info(f"🔌 WebSocket disconnected: {connection_id} "
                       f"(Duration: {duration:.1f}s, Messages: {connection_info['messages_sent']})")
            
            del self.active_connections[connection_id]
    
    async def send_to_connection(self, connection_id: str, chunk: StreamChunk) -> bool:
        """Send data to specific connection"""
        if connection_id not in self.active_connections:
            logger.warning(f"⚠️ Connection not found: {connection_id}")
            return False
        
        connection = self.active_connections[connection_id]
        websocket = connection['websocket']
        
        try:
            message = {
                'id': chunk.id,
                'type': chunk.type.value,
                'content': chunk.content,
                'metadata': chunk.metadata,
                'timestamp': chunk.timestamp
            }
            
            await websocket.send(json.dumps(message))
            
            # Update connection stats
            connection['messages_sent'] += 1
            connection['last_ping'] = time.time()
            self.total_messages_sent += 1
            
            return True
            
        except ConnectionClosed:
            logger.info(f"🔌 Connection closed during send: {connection_id}")
            await self.disconnect(connection_id)
            return False
        except Exception as e:
            logger.error(f"❌ Send error for {connection_id}: {e}")
            return False
    
    async def broadcast_to_group(self, group: str, chunk: StreamChunk) -> int:
        """Broadcast message to all connections in group"""
        if group not in self.connection_groups:
            return 0
        
        connection_ids = list(self.connection_groups[group])
        successful_sends = 0
        
        for connection_id in connection_ids:
            if await self.send_to_connection(connection_id, chunk):
                successful_sends += 1
        
        logger.debug(f"📡 Broadcast to {group}: {successful_sends}/{len(connection_ids)} successful")
        return successful_sends
    
    async def stream_response(
        self, 
        connection_id: str, 
        prompt: str, 
        context: Optional[Dict] = None,
        stream_delay: float = 0.03  # 30ms delay between tokens for natural typing effect
    ) -> bool:
        """Stream LEX response with real-time token delivery"""
        if connection_id not in self.active_connections:
            return False
        
        stream_id = generate_request_id()
        start_time = time.time()
        
        try:
            # Send initial status
            await self.send_to_connection(connection_id, StreamChunk(
                id=stream_id,
                type=StreamType.STATUS,
                content="🔱 LEX is thinking...",
                metadata={'prompt_length': len(prompt), 'stream_id': stream_id}
            ))
            
            # Get optimized response
            user_id = self.active_connections[connection_id]['user_id']
            
            response_data = await self.response_optimizer.get_optimized_response(
                prompt=prompt,
                context=context,
                user_id=user_id,
                voice_mode=False
            )
            
            if not response_data or 'response' not in response_data:
                await self.send_to_connection(connection_id, StreamChunk(
                    id=stream_id,
                    type=StreamType.ERROR,
                    content="❌ LEX encountered an error processing your request."
                ))
                return False
            
            full_response = response_data['response']
            
            # Send metadata first
            await self.send_to_connection(connection_id, StreamChunk(
                id=stream_id,
                type=StreamType.METADATA,
                content="",
                metadata={
                    'model_used': response_data.get('model_used', 'unknown'),
                    'confidence': response_data.get('confidence', 0.0),
                    'cache_hit': response_data.get('cache_hit', False),
                    'optimization_applied': response_data.get('optimization_applied', False),
                    'estimated_tokens': len(full_response.split())
                }
            ))
            
            # Stream response token by token
            tokens = self._tokenize_response(full_response)
            
            for i, token in enumerate(tokens):
                await self.send_to_connection(connection_id, StreamChunk(
                    id=stream_id,
                    type=StreamType.TOKEN,
                    content=token,
                    metadata={
                        'token_index': i,
                        'total_tokens': len(tokens),
                        'progress': round((i + 1) / len(tokens) * 100, 1)
                    }
                ))
                
                # Natural typing delay
                await asyncio.sleep(stream_delay)
            
            # Send completion
            stream_time = time.time() - start_time
            
            await self.send_to_connection(connection_id, StreamChunk(
                id=stream_id,
                type=StreamType.COMPLETE,
                content="",
                metadata={
                    'total_time': round(stream_time, 3),
                    'tokens_streamed': len(tokens),
                    'action_taken': response_data.get('action_taken', 'streamed_response'),
                    'capabilities_used': response_data.get('capabilities_used', []),
                    'divine_blessing': response_data.get('divine_blessing', '🔱 LEX STREAMING 🔱'),
                    'performance_score': response_data.get('performance_score', 85.0)
                }
            ))
            
            # Update connection stats
            connection = self.active_connections[connection_id]
            connection['total_stream_time'] += stream_time
            self.total_stream_time += stream_time
            
            logger.info(f"⚡ Stream completed: {connection_id} ({len(tokens)} tokens in {stream_time:.2f}s)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Streaming error for {connection_id}: {e}")
            
            await self.send_to_connection(connection_id, StreamChunk(
                id=stream_id,
                type=StreamType.ERROR,
                content=f"❌ Streaming error: {str(e)}",
                metadata={'error_type': 'streaming_error'}
            ))
            return False
    
    def _tokenize_response(self, response: str, chunk_size: int = 3) -> List[str]:
        """Tokenize response for streaming (word-based with small chunks)"""
        # Split by words but keep punctuation
        import re
        
        # More sophisticated tokenization
        tokens = []
        
        # Split by words and punctuation, but keep them together naturally
        words = re.findall(r'\w+|\s+|[^\w\s]', response)
        
        current_chunk = ""
        for word in words:
            current_chunk += word
            
            # Send chunk when we hit word boundaries and have enough content
            if (word.isspace() or not word.isalnum()) and len(current_chunk.strip()) >= chunk_size:
                if current_chunk.strip():
                    tokens.append(current_chunk)
                current_chunk = ""
        
        # Add remaining content
        if current_chunk.strip():
            tokens.append(current_chunk)
        
        # Ensure we have at least some tokens
        if not tokens and response:
            # Fallback: character-based chunking
            chunk_size = max(1, len(response) // 20)  # ~20 chunks
            tokens = [response[i:i + chunk_size] for i in range(0, len(response), chunk_size)]
        
        return [token for token in tokens if token.strip()]
    
    async def send_performance_update(self, connection_id: str) -> bool:
        """Send real-time performance metrics update"""
        try:
            # Get current performance metrics
            cache_stats = self.cache_manager.get_cache_statistics()
            optimizer_metrics = self.response_optimizer.get_optimization_metrics()
            
            performance_data = {
                'cache_hit_rate': cache_stats['performance_metrics']['hit_rate_percent'],
                'total_cost_saved': cache_stats['performance_metrics']['total_cost_savings_usd'],
                'requests_processed': optimizer_metrics['response_optimization']['total_requests'],
                'optimization_effectiveness': optimizer_metrics['performance_improvements'].get('optimization_effectiveness', 0),
                'active_connections': len(self.active_connections),
                'total_messages_sent': self.total_messages_sent,
                'avg_stream_time': self.total_stream_time / max(1, self.total_messages_sent)
            }
            
            await self.send_to_connection(connection_id, StreamChunk(
                id=generate_request_id(),
                type=StreamType.MESSAGE,
                content="📊 Performance Update",
                metadata={
                    'type': 'performance_update',
                    'data': performance_data,
                    'timestamp': datetime.utcnow().isoformat()
                }
            ))
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Performance update failed: {e}")
            return False
    
    async def handle_ping_pong(self, connection_id: str) -> bool:
        """Handle WebSocket ping/pong for connection health"""
        if connection_id in self.active_connections:
            connection = self.active_connections[connection_id]
            connection['last_ping'] = time.time()
            
            await self.send_to_connection(connection_id, StreamChunk(
                id=generate_request_id(),
                type=StreamType.STATUS,
                content="pong",
                metadata={'ping_time': connection['last_ping']}
            ))
            return True
        return False
    
    async def cleanup_stale_connections(self, timeout: int = 300):  # 5 minutes
        """Clean up connections that haven't pinged recently"""
        current_time = time.time()
        stale_connections = []
        
        for connection_id, connection in self.active_connections.items():
            if current_time - connection['last_ping'] > timeout:
                stale_connections.append(connection_id)
        
        for connection_id in stale_connections:
            logger.info(f"🧹 Cleaning stale connection: {connection_id}")
            await self.disconnect(connection_id)
        
        return len(stale_connections)
    
    def get_connection_stats(self) -> Dict:
        """Get comprehensive connection statistics"""
        active_count = len(self.active_connections)
        group_stats = {group: len(connections) for group, connections in self.connection_groups.items()}
        
        # Calculate average metrics
        avg_messages_per_connection = 0
        avg_connection_time = 0
        
        if active_count > 0:
            total_messages = sum(conn['messages_sent'] for conn in self.active_connections.values())
            total_time = sum(
                (datetime.utcnow() - conn['connected_at']).total_seconds()
                for conn in self.active_connections.values()
            )
            
            avg_messages_per_connection = total_messages / active_count
            avg_connection_time = total_time / active_count
        
        return {
            'active_connections': active_count,
            'total_connections_served': self.total_connections,
            'group_distribution': group_stats,
            'total_messages_sent': self.total_messages_sent,
            'total_stream_time': round(self.total_stream_time, 2),
            'averages': {
                'messages_per_connection': round(avg_messages_per_connection, 1),
                'connection_duration_seconds': round(avg_connection_time, 1),
                'stream_time_per_message': round(
                    self.total_stream_time / max(1, self.total_messages_sent), 3
                )
            }
        }

# Global WebSocket manager instance
websocket_manager = WebSocketConnectionManager()

def get_websocket_manager() -> WebSocketConnectionManager:
    """Get global WebSocket manager instance"""
    return websocket_manager