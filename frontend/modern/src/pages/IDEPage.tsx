import React from 'react';
import { Box, Typography, Paper } from '@mui/material';
import { Code } from '@mui/icons-material';

export const IDEPage: React.FC = () => {
  return (
    <Box sx={{ height: '100%', p: 3 }}>
      <Paper elevation={1} sx={{ p: 4, textAlign: 'center', height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
        <Code sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
        <Typography variant="h4" gutterBottom>
          🔱 LEX IDE
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Integrated Development Environment coming soon...
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
          This will provide a full code editor with LEX consciousness integration for development tasks.
        </Typography>
      </Paper>
    </Box>
  );
};