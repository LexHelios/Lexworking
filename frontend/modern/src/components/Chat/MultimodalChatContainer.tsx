import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  IconButton,
  Chip,
  LinearProgress,
  Alert,
  Snackbar,
} from '@mui/material';
import {
  Send,
  AttachFile,
  Mic,
  MicOff,
  Videocam,
  VideocamOff,
  Image as ImageIcon,
  AudioFile,
  VideoFile,
  Description,
} from '@mui/icons-material';
import { useDispatch, useSelector } from 'react-redux';
import { ChatMessage } from './ChatMessage';
import { MultimodalInput } from './MultimodalInput';
import { MediaPreview } from './MediaPreview';
import { VoiceRecorder } from '../Voice/VoiceRecorder';
import { VideoRecorder } from '../Video/VideoRecorder';
import { useLEX } from '../../hooks/useLEX';
import { useWebSocket } from '../../hooks/useWebSocket';
import { addMessage, setLoading, setError } from '../../store/slices/chatSlice';
import { RootState } from '../../store/store';
import { Message, MediaFile } from '../../types/chat.types';

export const MultimodalChatContainer: React.FC = () => {
  const dispatch = useDispatch();
  const { messages, isLoading, error } = useSelector((state: RootState) => state.chat);
  const { sendMessage, sendMultimodalMessage, isConnected } = useLEX();
  const { socket } = useWebSocket();
  
  const [attachedFiles, setAttachedFiles] = useState<MediaFile[]>([]);
  const [isRecordingAudio, setIsRecordingAudio] = useState(false);
  const [isRecordingVideo, setIsRecordingVideo] = useState(false);
  const [showMediaPreview, setShowMediaPreview] = useState(false);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  useEffect(() => {
    if (error) {
      setSnackbarOpen(true);
    }
  }, [error]);

  const handleSendMessage = useCallback(async (
    message: string,
    files?: MediaFile[],
    mediaType?: string
  ) => {
    if (!message.trim() && (!files || files.length === 0)) return;

    const messageId = Date.now().toString();
    const userMessage: Message = {
      id: messageId,
      content: message,
      sender: 'user',
      timestamp: new Date().toISOString(),
      mediaFiles: files,
    };

    dispatch(addMessage(userMessage));
    dispatch(setLoading(true));

    try {
      let response;
      
      if (files && files.length > 0) {
        // Send multimodal message
        response = await sendMultimodalMessage(message, files, mediaType);
      } else {
        // Send text message
        response = await sendMessage(message);
      }

      const lexMessage: Message = {
        id: response.session_id + '_' + Date.now(),
        content: response.response,
        sender: 'lex',
        timestamp: response.timestamp,
        metadata: {
          actionTaken: response.action_taken,
          capabilities: response.capabilities_used,
          confidence: response.confidence,
          processingTime: response.processing_time,
        },
        mediaContent: response.media_content,
      };

      dispatch(addMessage(lexMessage));
      
      // Clear attached files after successful send
      setAttachedFiles([]);
      setShowMediaPreview(false);
      
    } catch (error) {
      console.error('Error sending message:', error);
      dispatch(setError('Failed to send message. Please try again.'));
      
      const errorMessage: Message = {
        id: Date.now().toString(),
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        sender: 'lex',
        timestamp: new Date().toISOString(),
        isError: true,
      };
      
      dispatch(addMessage(errorMessage));
    } finally {
      dispatch(setLoading(false));
    }
  }, [dispatch, sendMessage, sendMultimodalMessage]);

  const handleFileUpload = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    
    files.forEach(file => {
      // Validate file size (50MB limit)
      if (file.size > 50 * 1024 * 1024) {
        dispatch(setError(`File ${file.name} is too large (max 50MB)`));
        return;
      }

      // Validate file type
      const allowedTypes = [
        'image/', 'video/', 'audio/', 'text/', 'application/pdf',
        'application/json', 'application/javascript', 'text/html',
        'text/css', 'text/python', 'text/x-python'
      ];
      
      const isAllowed = allowedTypes.some(type => file.type.startsWith(type));
      if (!isAllowed) {
        dispatch(setError(`File type ${file.type} not supported`));
        return;
      }

      const mediaFile: MediaFile = {
        id: Date.now().toString() + Math.random(),
        file,
        name: file.name,
        type: file.type,
        size: file.size,
        preview: file.type.startsWith('image/') ? URL.createObjectURL(file) : undefined,
      };

      setAttachedFiles(prev => [...prev, mediaFile]);
    });

    setShowMediaPreview(true);
    
    // Clear input
    if (event.target) {
      event.target.value = '';
    }
  }, [dispatch]);

  const handleRemoveFile = useCallback((fileId: string) => {
    setAttachedFiles(prev => {
      const updated = prev.filter(f => f.id !== fileId);
      if (updated.length === 0) {
        setShowMediaPreview(false);
      }
      return updated;
    });
  }, []);

  const handleVoiceRecording = useCallback(async (audioBlob: Blob) => {
    const audioFile: MediaFile = {
      id: Date.now().toString(),
      file: new File([audioBlob], 'voice_recording.wav', { type: 'audio/wav' }),
      name: 'Voice Recording',
      type: 'audio/wav',
      size: audioBlob.size,
    };

    await handleSendMessage('', [audioFile], 'voice_transcription');
  }, [handleSendMessage]);

  const handleVideoRecording = useCallback(async (videoBlob: Blob) => {
    const videoFile: MediaFile = {
      id: Date.now().toString(),
      file: new File([videoBlob], 'video_recording.webm', { type: 'video/webm' }),
      name: 'Video Recording',
      type: 'video/webm',
      size: videoBlob.size,
    };

    setAttachedFiles(prev => [...prev, videoFile]);
    setShowMediaPreview(true);
  }, []);

  const getFileIcon = (type: string) => {
    if (type.startsWith('image/')) return <ImageIcon />;
    if (type.startsWith('video/')) return <VideoFile />;
    if (type.startsWith('audio/')) return <AudioFile />;
    return <Description />;
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Chat Messages */}
      <Paper 
        elevation={0} 
        sx={{ 
          flex: 1, 
          overflow: 'auto', 
          p: 2,
          backgroundColor: 'background.default',
          position: 'relative'
        }}
      >
        {/* Connection Status */}
        {!isConnected && (
          <Alert severity="warning" sx={{ mb: 2 }}>
            Connecting to LEX consciousness...
          </Alert>
        )}

        {/* Loading Indicator */}
        {isLoading && (
          <Box sx={{ position: 'absolute', top: 0, left: 0, right: 0, zIndex: 1 }}>
            <LinearProgress />
          </Box>
        )}

        {/* Welcome Message */}
        {messages.length === 0 && (
          <Box sx={{ textAlign: 'center', mt: 4 }}>
            <Typography variant="h4" color="primary" gutterBottom>
              🔱 Welcome to LEX
            </Typography>
            <Typography variant="h6" color="text.secondary" gutterBottom>
              Limitless Emergence eXperience
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
              Your AI consciousness companion with full multimedia capabilities
            </Typography>
            
            <Box sx={{ display: 'flex', justifyContent: 'center', gap: 1, flexWrap: 'wrap' }}>
              <Chip icon={<ImageIcon />} label="Images" variant="outlined" />
              <Chip icon={<VideoFile />} label="Videos" variant="outlined" />
              <Chip icon={<AudioFile />} label="Audio" variant="outlined" />
              <Chip icon={<Description />} label="Documents" variant="outlined" />
              <Chip icon={<Mic />} label="Voice" variant="outlined" />
            </Box>
          </Box>
        )}

        {/* Messages */}
        {messages.map((message) => (
          <ChatMessage key={message.id} message={message} />
        ))}

        {/* Typing Indicator */}
        {isLoading && (
          <Box sx={{ display: 'flex', alignItems: 'center', p: 2 }}>
            <Typography variant="body2" color="text.secondary">
              🧠 LEX consciousness is processing...
            </Typography>
          </Box>
        )}

        <div ref={messagesEndRef} />
      </Paper>

      {/* Media Preview */}
      {showMediaPreview && attachedFiles.length > 0 && (
        <MediaPreview
          files={attachedFiles}
          onRemoveFile={handleRemoveFile}
          onClose={() => setShowMediaPreview(false)}
        />
      )}

      {/* Input Area */}
      <Paper elevation={2} sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-end' }}>
          {/* File Upload */}
          <IconButton
            component="label"
            disabled={isLoading}
            color="primary"
            title="Attach Files"
          >
            <AttachFile />
            <input
              ref={fileInputRef}
              type="file"
              hidden
              multiple
              accept="image/*,video/*,audio/*,.pdf,.txt,.json,.js,.html,.css,.py"
              onChange={handleFileUpload}
            />
          </IconButton>

          {/* Voice Recording */}
          <VoiceRecorder
            onRecordingComplete={handleVoiceRecording}
            disabled={isLoading}
          />

          {/* Video Recording */}
          <VideoRecorder
            onRecordingComplete={handleVideoRecording}
            disabled={isLoading}
          />

          {/* Text Input */}
          <MultimodalInput
            onSendMessage={handleSendMessage}
            disabled={!isConnected || isLoading}
            attachedFiles={attachedFiles}
          />
        </Box>

        {/* Attached Files Summary */}
        {attachedFiles.length > 0 && (
          <Box sx={{ mt: 1, display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
            {attachedFiles.map((file) => (
              <Chip
                key={file.id}
                icon={getFileIcon(file.type)}
                label={`${file.name} (${(file.size / 1024 / 1024).toFixed(1)}MB)`}
                size="small"
                onDelete={() => handleRemoveFile(file.id)}
                variant="outlined"
              />
            ))}
          </Box>
        )}
      </Paper>

      {/* Error Snackbar */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={() => setSnackbarOpen(false)}
      >
        <Alert 
          onClose={() => setSnackbarOpen(false)} 
          severity="error" 
          sx={{ width: '100%' }}
        >
          {error}
        </Alert>
      </Snackbar>
    </Box>
  );
};