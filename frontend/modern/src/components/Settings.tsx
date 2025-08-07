import React from 'react';
import { Container, Typography, Paper } from '@mui/material';

const Settings: React.FC = () => {
  return (
    <Container maxWidth="lg">
      <Paper sx={{ p: 3 }}>
        <Typography variant="h4" gutterBottom>
          ⚙️ Settings
        </Typography>
        <Typography variant="body1">
          Settings panel for the OMNIPOTENT system.
        </Typography>
      </Paper>
    </Container>
  );
};

export default Settings;