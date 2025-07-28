import React from 'react';
import { Box, Typography, Paper } from '@mui/material';
import { Settings } from '@mui/icons-material';

export const SettingsPage: React.FC = () => {
  return (
    <Box sx={{ height: '100%', p: 3 }}>
      <Paper elevation={1} sx={{ p: 4, textAlign: 'center', height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
        <Settings sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
        <Typography variant="h4" gutterBottom>
          🔱 LEX Settings
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Configuration and preferences coming soon...
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
          This will provide settings for API keys, preferences, and consciousness parameters.
        </Typography>
      </Paper>
    </Box>
  );
};