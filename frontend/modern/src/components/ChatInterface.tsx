import React from 'react';
import { Container, Typography, Paper } from '@mui/material';

const ChatInterface: React.FC = () => {
  return (
    <Container maxWidth="lg">
      <Paper sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          💬 Chat Interface
        </Typography>
        <Typography variant="body1">
          Chat interface for the OMNIPOTENT system.
        </Typography>
      </Paper>
    </Container>
  );
};

export default ChatInterface;