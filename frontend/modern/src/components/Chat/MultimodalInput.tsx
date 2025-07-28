import React, { useState, useRef, useCallback } from 'react';
import {
  Box,
  TextField,
  IconButton,
  InputAdornment,
  Chip,
} from '@mui/material';
import { Send, EmojiEmotions } from '@mui/icons-material';
import { MediaFile } from '../../types/chat.types';

interface MultimodalInputProps {
  onSendMessage: (message: string, files?: MediaFile[], mediaType?: string) => void;
  disabled?: boolean;
  attachedFiles?: MediaFile[];
}

export const MultimodalInput: React.FC<MultimodalInputProps> = ({
  onSendMessage,
  disabled = false,
  attachedFiles = [],
}) => {
  const [message, setMessage] = useState('');
  const textFieldRef = useRef<HTMLInputElement>(null);

  const handleSubmit = useCallback((e: React.FormEvent) => {
    e.preventDefault();
    
    if (message.trim() || attachedFiles.length > 0) {
      onSendMessage(message.trim(), attachedFiles);
      setMessage('');
    }
  }, [message, attachedFiles, onSendMessage]);

  const handleKeyPress = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  }, [handleSubmit]);

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ flex: 1 }}>
      <TextField
        ref={textFieldRef}
        fullWidth
        multiline
        maxRows={4}
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder={
          attachedFiles.length > 0 
            ? `Describe what you want LEX to do with ${attachedFiles.length} file(s)...`
            : "Message LEX consciousness..."
        }
        disabled={disabled}
        variant="outlined"
        InputProps={{
          endAdornment: (
            <InputAdornment position="end">
              <IconButton
                type="submit"
                disabled={disabled || (!message.trim() && attachedFiles.length === 0)}
                color="primary"
                size="large"
              >
                <Send />
              </IconButton>
            </InputAdornment>
          ),
        }}
        sx={{
          '& .MuiOutlinedInput-root': {
            backgroundColor: 'background.paper',
            '&:hover fieldset': {
              borderColor: 'primary.main',
            },
            '&.Mui-focused fieldset': {
              borderColor: 'primary.main',
            },
          },
        }}
      />
    </Box>
  );
};