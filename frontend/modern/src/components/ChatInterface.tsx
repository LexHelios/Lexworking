import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Paper,
  TextField,
  IconButton,
  Typography,
  Chip,
  CircularProgress,
  Tooltip
} from '@mui/material';
import {
  Send,
  Mic,
  MicOff,
  Clear,
  Speed,
  Psychology,
  Settings
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';

// Types
interface WebSocketMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: number;
  metadata?: any;
  streaming?: boolean;
  tokens?: string[];
}

interface ChatInterfaceProps {
  isConnected: boolean;
  connectionId: string | null;
  sendMessage: (message: string, options?: any) => void;
  messages: WebSocketMessage[];
  streamingResponse: string;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  isConnected,
  connectionId,
  sendMessage,
  messages,
  streamingResponse
}) => {
  // State
  const [input, setInput] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [priority, setPriority] = useState<'speed' | 'balanced' | 'quality'>('balanced');

  // Refs
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const speechRecognition = useRef<any>(null);

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingResponse]);

  // Initialize speech recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      speechRecognition.current = new SpeechRecognition();
      speechRecognition.current.continuous = false;
      speechRecognition.current.interimResults = false;
      speechRecognition.current.lang = 'en-US';

      speechRecognition.current.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setInput(transcript);
        setIsListening(false);
      };

      speechRecognition.current.onerror = () => {
        setIsListening(false);
      };

      speechRecognition.current.onend = () => {
        setIsListening(false);
      };
    }
  }, []);

  // Handle form submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!input.trim() || !isConnected) {
      return;
    }

    const messageOptions = {
      priority,
      use_cache: true,
      max_response_time: priority === 'speed' ? 15 : priority === 'balanced' ? 30 : 60,
      context: {
        conversation_id: connectionId,
        user_preferences: {
          priority,
          voice_enabled: false
        }
      }
    };

    sendMessage(input.trim(), messageOptions);
    setInput('');
  };

  // Handle voice input
  const toggleVoiceInput = () => {
    if (!speechRecognition.current) {
      return;
    }

    if (isListening) {
      speechRecognition.current.stop();
      setIsListening(false);
    } else {
      speechRecognition.current.start();
      setIsListening(true);
    }
  };

  // Format timestamp
  const formatTime = (timestamp: number) => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Render message content
  const renderMessageContent = (message: WebSocketMessage) => {
    if (message.role === 'user') {
      return (
        <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
          {message.content}
        </Typography>
      );
    }

    // Assistant message with markdown support
    return (
      <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
        {message.content}
      </Typography>
    );
  };

  // Render message metadata
  const renderMessageMetadata = (message: WebSocketMessage) => {
    if (!message.metadata) return null;

    const { model_used, confidence, cache_hit, performance_score } = message.metadata;

    return (
      <Box sx={{ display: 'flex', gap: 1, mt: 1, flexWrap: 'wrap' }}>
        {model_used && (
          <Chip
            label={`Model: ${model_used.split('/').pop()?.split(':')[0] || 'Unknown'}`}
            size="small"
            variant="outlined"
            color="primary"
          />
        )}
        {confidence && (
          <Chip
            label={`Confidence: ${(confidence * 100).toFixed(0)}%`}
            size="small"
            variant="outlined"
            color={confidence > 0.8 ? 'success' : confidence > 0.5 ? 'warning' : 'error'}
          />
        )}
        {cache_hit && (
          <Chip
            label="Cached"
            size="small"
            variant="filled"
            color="success"
            icon={<Speed />}
          />
        )}
        {performance_score && (
          <Chip
            label={`Performance: ${performance_score.toFixed(0)}%`}
            size="small"
            variant="outlined"
            color={performance_score > 80 ? 'success' : performance_score > 60 ? 'warning' : 'error'}
          />
        )}
      </Box>
    );
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Paper
        elevation={2}
        sx={{
          p: 2,
          mb: 2,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}
      >
        <Box>
          <Typography variant="h5" component="h1" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            🔱 LEX Chat Interface
            {isConnected && (
              <Chip
                label="Connected"
                size="small"
                color="success"
                variant="filled"
                sx={{ ml: 1 }}
              />
            )}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Real-time AI conversation with performance optimization
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {/* Priority Selection */}
          <Tooltip title="Response Priority">
            <Box sx={{ display: 'flex', gap: 0.5 }}>
              {(['speed', 'balanced', 'quality'] as const).map((p) => (
                <Chip
                  key={p}
                  label={p.charAt(0).toUpperCase() + p.slice(1)}
                  size="small"
                  variant={priority === p ? 'filled' : 'outlined'}
                  color={priority === p ? 'primary' : 'default'}
                  onClick={() => setPriority(p)}
                  icon={
                    p === 'speed' ? <Speed /> : 
                    p === 'quality' ? <Psychology /> : 
                    <Settings />
                  }
                />
              ))}
            </Box>
          </Tooltip>
        </Box>
      </Paper>

      {/* Messages Area */}
      <Paper
        elevation={1}
        sx={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          mb: 2
        }}
      >
        <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
          {messages.length === 0 ? (
            <Box
              sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                textAlign: 'center',
                color: 'text.secondary'
              }}
            >
              <Typography variant="h6" gutterBottom>
                🔱 Welcome to LEX
              </Typography>
              <Typography variant="body1" paragraph>
                Start a conversation with the advanced AI assistant
              </Typography>
              <Typography variant="body2">
                • Real-time streaming responses<br />
                • Intelligent model selection<br />
                • Performance optimization<br />
                • Voice input support
              </Typography>
            </Box>
          ) : (
            <Box>
              <AnimatePresence>
                {messages.map((message) => (
                  <motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.3 }}
                  >
                    <Box
                      sx={{
                        display: 'flex',
                        flexDirection: message.role === 'user' ? 'row-reverse' : 'row',
                        mb: 3,
                        alignItems: 'flex-start'
                      }}
                    >
                      <Paper
                        elevation={2}
                        sx={{
                          p: 2,
                          maxWidth: '70%',
                          bgcolor: message.role === 'user' ? 'primary.main' : 'background.paper',
                          color: message.role === 'user' ? 'primary.contrastText' : 'text.primary',
                          borderRadius: 2,
                          ...(message.role === 'user' ? {
                            borderBottomRightRadius: 8,
                          } : {
                            borderBottomLeftRadius: 8,
                          })
                        }}
                      >
                        {/* Message Content */}
                        {renderMessageContent(message)}

                        {/* Message Footer */}
                        <Box
                          sx={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            mt: 1
                          }}
                        >
                          <Typography
                            variant="caption"
                            sx={{
                              opacity: 0.7,
                              color: message.role === 'user' ? 'inherit' : 'text.secondary'
                            }}
                          >
                            {formatTime(message.timestamp)}
                          </Typography>
                        </Box>

                        {/* Metadata */}
                        {message.role === 'assistant' && renderMessageMetadata(message)}
                      </Paper>
                    </Box>
                  </motion.div>
                ))}
              </AnimatePresence>

              {/* Streaming Response */}
              {streamingResponse && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <Box
                    sx={{
                      display: 'flex',
                      mb: 3,
                      alignItems: 'flex-start'
                    }}
                  >
                    <Paper
                      elevation={2}
                      sx={{
                        p: 2,
                        maxWidth: '70%',
                        bgcolor: 'background.paper',
                        borderRadius: 2,
                        borderBottomLeftRadius: 8,
                        border: '2px solid',
                        borderColor: 'primary.main',
                        position: 'relative'
                      }}
                    >
                      {/* Streaming Indicator */}
                      <Box
                        sx={{
                          position: 'absolute',
                          top: -1,
                          right: -1,
                          bgcolor: 'primary.main',
                          color: 'primary.contrastText',
                          px: 1,
                          py: 0.5,
                          borderRadius: 1,
                          fontSize: '0.75rem',
                          display: 'flex',
                          alignItems: 'center',
                          gap: 0.5
                        }}
                      >
                        <CircularProgress size={12} color="inherit" />
                        Streaming...
                      </Box>

                      <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                        {streamingResponse}
                        <span 
                          style={{ 
                            animation: 'blink 1s infinite',
                            marginLeft: 2
                          }}
                        >
                          |
                        </span>
                      </Typography>


                    </Paper>
                  </Box>
                </motion.div>
              )}

              <div ref={messagesEndRef} />
            </Box>
          )}
        </Box>
      </Paper>

      {/* Input Area */}
      <Paper elevation={2} sx={{ p: 2 }}>
        <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', gap: 1, alignItems: 'flex-end' }}>
          <TextField
            ref={inputRef}
            fullWidth
            multiline
            maxRows={4}
            placeholder={
              isConnected
                ? "Ask LEX anything... (supports markdown, code, and complex queries)"
                : "Connecting to LEX..."
            }
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={!isConnected}
            variant="outlined"
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: 3,
              }
            }}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e as any);
              }
            }}
          />

          {/* Voice Input Button */}
          {speechRecognition.current && (
            <Tooltip title={isListening ? "Stop listening" : "Voice input"}>
              <IconButton
                onClick={toggleVoiceInput}
                color={isListening ? "secondary" : "default"}
                disabled={!isConnected}
                sx={{ borderRadius: 2 }}
              >
                {isListening ? <MicOff /> : <Mic />}
              </IconButton>
            </Tooltip>
          )}

          {/* Clear Button */}
          <Tooltip title="Clear input">
            <IconButton
              onClick={() => setInput('')}
              disabled={!input.trim()}
              sx={{ borderRadius: 2 }}
            >
              <Clear />
            </IconButton>
          </Tooltip>

          {/* Send Button */}
          <Tooltip title="Send message">
            <IconButton
              type="submit"
              color="primary"
              disabled={!input.trim() || !isConnected}
              sx={{ borderRadius: 2 }}
            >
              <Send />
            </IconButton>
          </Tooltip>
        </Box>

        {/* Status Bar */}
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            mt: 1,
            pt: 1,
            borderTop: 1,
            borderColor: 'divider'
          }}
        >
          <Typography variant="caption" color="text.secondary">
            Priority: {priority.charAt(0).toUpperCase() + priority.slice(1)} • 
            {isConnected ? ` Connected (${connectionId?.slice(-8) || 'N/A'})` : ' Disconnected'}
          </Typography>

          <Typography variant="caption" color="text.secondary">
            {input.length}/10000 characters
          </Typography>
        </Box>
      </Paper>

      {/* Global Styles for Animations */}
      <style jsx global>{`
        @keyframes blink {
          0%, 50% { opacity: 1; }
          51%, 100% { opacity: 0; }
        }
      `}</style>
    </Box>
  );
};

export default ChatInterface;