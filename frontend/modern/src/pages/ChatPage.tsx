import React from 'react';
import { Box } from '@mui/material';
import { MultimodalChatContainer } from '../components/Chat/MultimodalChatContainer';

export const ChatPage: React.FC = () => {
  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <MultimodalChatContainer />
    </Box>
  );
};