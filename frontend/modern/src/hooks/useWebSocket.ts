import { useState, useEffect, useCallback, useRef } from 'react';
import { toast } from 'react-hot-toast';

// Types
interface StreamMessage {
  id: string;
  type: 'message' | 'token' | 'status' | 'error' | 'complete' | 'metadata';
  content: string;
  metadata?: any;
  timestamp: number;
}

interface WebSocketMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: number;
  metadata?: any;
  streaming?: boolean;
  tokens?: string[];
}

interface ConnectionStats {
  activeConnections: number;
  totalMessagesSent: number;
  averageResponseTime: number;
}

interface UseWebSocketReturn {
  isConnected: boolean;
  connectionId: string | null;
  sendMessage: (message: string, options?: any) => void;
  messages: WebSocketMessage[];
  streamingResponse: string;
  connectionStats: ConnectionStats | null;
  clearMessages: () => void;
  reconnect: () => void;
}

const useWebSocket = (
  customUrl?: string,
  options: { autoReconnect?: boolean } = { autoReconnect: true }
): UseWebSocketReturn => {
  // Get WebSocket URL from environment variables
  const getWebSocketUrl = () => {
    if (customUrl) return customUrl;
    
    const wsUrl = process.env.REACT_APP_WS_URL;
    const backendUrl = process.env.REACT_APP_BACKEND_URL;
    
    if (wsUrl) {
      return `${wsUrl}/ws`;
    } else if (backendUrl) {
      // Convert HTTP to WebSocket URL
      const url = backendUrl.replace(/^https?:/, window.location.protocol === 'https:' ? 'wss:' : 'ws:');
      return `${url}/ws`;
    } else {
      // Fallback to same host
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      return `${protocol}//${window.location.host}/ws`;
    }
  };

  // State
  const [isConnected, setIsConnected] = useState(false);
  const [connectionId, setConnectionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<WebSocketMessage[]>([]);
  const [streamingResponse, setStreamingResponse] = useState('');
  const [connectionStats, setConnectionStats] = useState<ConnectionStats | null>(null);

  // Refs
  const ws = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;
  const currentStreamingMessage = useRef<WebSocketMessage | null>(null);

  // Connect to WebSocket
  const connect = useCallback(() => {
    try {
      // Close existing connection
      if (ws.current) {
        ws.current.close();
      }

      const wsUrl = getWebSocketUrl();
      console.log('🔗 Connecting to WebSocket:', wsUrl);

      ws.current = new WebSocket(wsUrl);

      ws.current.onopen = () => {
        console.log('🔗 WebSocket connected to', wsUrl);
        setIsConnected(true);
        reconnectAttempts.current = 0;
        
        toast.success('🔱 LEX Connected! Real-time streaming active.', {
          duration: 3000,
        });
      };

      ws.current.onmessage = (event) => {
        try {
          const data: StreamMessage = JSON.parse(event.data);
          handleStreamMessage(data);
        } catch (error) {
          console.error('❌ Error parsing WebSocket message:', error);
        }
      };

      ws.current.onclose = (event) => {
        console.log('🔌 WebSocket disconnected:', event.code, event.reason);
        setIsConnected(false);
        setConnectionId(null);
        setStreamingResponse('');
        currentStreamingMessage.current = null;

        // Auto-reconnect logic
        if (options.autoReconnect && reconnectAttempts.current < maxReconnectAttempts) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 10000);
          console.log(`🔄 Reconnecting in ${delay}ms (attempt ${reconnectAttempts.current + 1})`);
          
          reconnectTimer.current = setTimeout(() => {
            reconnectAttempts.current++;
            connect();
          }, delay);
        } else if (reconnectAttempts.current >= maxReconnectAttempts) {
          toast.error('❌ Connection lost. Please refresh the page.', {
            duration: 0, // Don't auto-dismiss
          });
        }
      };

      ws.current.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
        toast.error('🔄 Connection error. Attempting to reconnect...');
      };

    } catch (error) {
      console.error('❌ Failed to create WebSocket connection:', error);
      toast.error('❌ Failed to connect to LEX.');
    }
  }, [options.autoReconnect]);

  // Handle stream messages
  const handleStreamMessage = (data: StreamMessage) => {
    switch (data.type) {
      case 'status':
        if (data.content.includes('connected')) {
          setConnectionId(data.metadata?.connection_id || null);
        }
        break;

      case 'metadata':
        // Start new streaming message
        if (currentStreamingMessage.current) {
          // Finish previous message if any
          setMessages(prev => [...prev, currentStreamingMessage.current!]);
        }

        currentStreamingMessage.current = {
          id: data.id,
          role: 'assistant',
          content: '',
          timestamp: Date.now(),
          metadata: data.metadata,
          streaming: true,
          tokens: []
        };
        setStreamingResponse('');
        break;

      case 'token':
        // Add token to streaming response
        if (currentStreamingMessage.current) {
          currentStreamingMessage.current.content += data.content;
          currentStreamingMessage.current.tokens?.push(data.content);
          setStreamingResponse(currentStreamingMessage.current.content);
        }
        break;

      case 'complete':
        // Finish streaming message
        if (currentStreamingMessage.current) {
          currentStreamingMessage.current.streaming = false;
          currentStreamingMessage.current.metadata = {
            ...currentStreamingMessage.current.metadata,
            ...data.metadata
          };
          
          setMessages(prev => [...prev, currentStreamingMessage.current!]);
          currentStreamingMessage.current = null;
          setStreamingResponse('');
        }
        break;

      case 'error':
        toast.error(`❌ ${data.content}`);
        
        if (currentStreamingMessage.current) {
          currentStreamingMessage.current.content = data.content;
          currentStreamingMessage.current.streaming = false;
          setMessages(prev => [...prev, currentStreamingMessage.current!]);
          currentStreamingMessage.current = null;
          setStreamingResponse('');
        }
        break;

      case 'message':
        // Handle special messages (performance updates, etc.)
        if (data.metadata?.type === 'performance_update') {
          setConnectionStats(data.metadata.data);
        } else {
          // Regular message
          setMessages(prev => [...prev, {
            id: data.id,
            role: 'system',
            content: data.content,
            timestamp: Date.now(),
            metadata: data.metadata
          }]);
        }
        break;
    }
  };

  // Send message
  const sendMessage = useCallback((message: string, options: any = {}) => {
    if (!ws.current || ws.current.readyState !== WebSocket.OPEN) {
      toast.error('❌ Not connected to LEX. Please wait for connection.');
      return;
    }

    if (!message.trim()) {
      return;
    }

    try {
      // Add user message to chat
      const userMessage: WebSocketMessage = {
        id: `user_${Date.now()}`,
        role: 'user',
        content: message,
        timestamp: Date.now(),
        metadata: options
      };
      
      setMessages(prev => [...prev, userMessage]);

      // Send streaming request
      const request = {
        type: 'stream_request',
        prompt: message,
        context: options.context || {},
        stream_delay: options.streamDelay || 0.03,
        metadata: options
      };

      ws.current.send(JSON.stringify(request));

      // Show typing indicator
      toast.success('🔱 LEX is processing your request...', {
        duration: 2000,
      });

    } catch (error) {
      console.error('❌ Error sending message:', error);
      toast.error('❌ Failed to send message to LEX.');
    }
  }, []);

  // Clear messages
  const clearMessages = useCallback(() => {
    setMessages([]);
    setStreamingResponse('');
    currentStreamingMessage.current = null;
  }, []);

  // Reconnect manually
  const reconnect = useCallback(() => {
    reconnectAttempts.current = 0;
    connect();
  }, [connect]);

  // Initialize connection
  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimer.current) {
        clearTimeout(reconnectTimer.current);
      }
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [connect]);

  // Request performance updates periodically
  useEffect(() => {
    if (!isConnected) return;

    const interval = setInterval(() => {
      if (ws.current && ws.current.readyState === WebSocket.OPEN) {
        ws.current.send(JSON.stringify({ type: 'performance_request' }));
      }
    }, 30000); // Every 30 seconds

    return () => clearInterval(interval);
  }, [isConnected]);

  return {
    isConnected,
    connectionId,
    sendMessage,
    messages,
    streamingResponse,
    connectionStats,
    clearMessages,
    reconnect
  };
};

export default useWebSocket;
