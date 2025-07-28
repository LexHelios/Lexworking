import React, { useState, useRef, useCallback } from 'react';
import { IconButton, Tooltip, Box, Typography, Dialog, DialogContent } from '@mui/material';
import { Videocam, VideocamOff, Stop, Close } from '@mui/icons-material';

interface VideoRecorderProps {
  onRecordingComplete: (videoBlob: Blob) => void;
  disabled?: boolean;
}

export const VideoRecorder: React.FC<VideoRecorderProps> = ({
  onRecordingComplete,
  disabled = false,
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const videoRef = useRef<HTMLVideoElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          frameRate: { ideal: 30 },
        },
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
        }
      });
      
      streamRef.current = stream;
      chunksRef.current = [];

      // Show preview
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }
      setShowPreview(true);

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'video/webm;codecs=vp9,opus',
      });

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const videoBlob = new Blob(chunksRef.current, { type: 'video/webm' });
        onRecordingComplete(videoBlob);
        
        // Cleanup
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop());
          streamRef.current = null;
        }
        
        if (timerRef.current) {
          clearInterval(timerRef.current);
          timerRef.current = null;
        }
        
        setRecordingTime(0);
        setShowPreview(false);
      };

      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start();
      setIsRecording(true);

      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);

    } catch (error) {
      console.error('Error starting video recording:', error);
      alert('Could not access camera/microphone. Please check permissions.');
    }
  }, [onRecordingComplete]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  }, [isRecording]);

  const cancelRecording = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
    
    setIsRecording(false);
    setShowPreview(false);
    setRecordingTime(0);
  }, []);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Tooltip title={isRecording ? 'Stop Video Recording' : 'Start Video Recording'}>
          <IconButton
            onClick={isRecording ? stopRecording : startRecording}
            disabled={disabled}
            color={isRecording ? 'error' : 'primary'}
            sx={{
              backgroundColor: isRecording ? 'error.main' : 'transparent',
              color: isRecording ? 'error.contrastText' : 'primary.main',
              '&:hover': {
                backgroundColor: isRecording ? 'error.dark' : 'primary.light',
              },
              animation: isRecording ? 'pulse 1.5s infinite' : 'none',
              '@keyframes pulse': {
                '0%': { transform: 'scale(1)' },
                '50%': { transform: 'scale(1.1)' },
                '100%': { transform: 'scale(1)' },
              },
            }}
          >
            {isRecording ? <Stop /> : <Videocam />}
          </IconButton>
        </Tooltip>
        
        {isRecording && (
          <Typography variant="caption" color="error.main" sx={{ minWidth: 40 }}>
            {formatTime(recordingTime)}
          </Typography>
        )}
      </Box>

      {/* Video Preview Dialog */}
      <Dialog
        open={showPreview}
        onClose={cancelRecording}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: { backgroundColor: 'background.paper' }
        }}
      >
        <DialogContent sx={{ p: 0, position: 'relative' }}>
          <IconButton
            onClick={cancelRecording}
            sx={{
              position: 'absolute',
              top: 8,
              right: 8,
              backgroundColor: 'rgba(0,0,0,0.7)',
              color: 'white',
              zIndex: 1,
              '&:hover': {
                backgroundColor: 'rgba(0,0,0,0.9)',
              },
            }}
          >
            <Close />
          </IconButton>
          
          <video
            ref={videoRef}
            autoPlay
            muted
            style={{
              width: '100%',
              height: 'auto',
              maxHeight: '70vh',
              backgroundColor: '#000',
            }}
          />
          
          {isRecording && (
            <Box
              sx={{
                position: 'absolute',
                bottom: 16,
                left: '50%',
                transform: 'translateX(-50%)',
                display: 'flex',
                alignItems: 'center',
                gap: 2,
                backgroundColor: 'rgba(0,0,0,0.8)',
                color: 'white',
                px: 2,
                py: 1,
                borderRadius: 2,
              }}
            >
              <Box
                sx={{
                  width: 12,
                  height: 12,
                  borderRadius: '50%',
                  backgroundColor: 'error.main',
                  animation: 'pulse 1s infinite',
                }}
              />
              <Typography variant="body2">
                Recording: {formatTime(recordingTime)}
              </Typography>
              <IconButton
                size="small"
                onClick={stopRecording}
                sx={{ color: 'white' }}
              >
                <Stop />
              </IconButton>
            </Box>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
};