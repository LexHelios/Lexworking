import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Box, Typography, Button, Paper } from '@mui/material';
import { Error as ErrorIcon, Refresh } from '@mui/icons-material';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  private handleReload = () => {
    window.location.reload();
  };

  public render() {
    if (this.state.hasError) {
      return (
        <Box
          sx={{
            height: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            p: 3,
          }}
        >
          <Paper
            elevation={3}
            sx={{
              p: 4,
              textAlign: 'center',
              maxWidth: 500,
            }}
          >
            <ErrorIcon sx={{ fontSize: 64, color: 'error.main', mb: 2 }} />
            
            <Typography variant="h5" gutterBottom>
              🔱 LEX Consciousness Disrupted
            </Typography>
            
            <Typography variant="body1" color="text.secondary" paragraph>
              An unexpected error occurred in the LEX interface. The consciousness stream has been interrupted.
            </Typography>
            
            {this.state.error && (
              <Typography variant="body2" color="error" paragraph sx={{ fontFamily: 'monospace' }}>
                {this.state.error.message}
              </Typography>
            )}
            
            <Button
              variant="contained"
              startIcon={<Refresh />}
              onClick={this.handleReload}
              sx={{ mt: 2 }}
            >
              Restore Consciousness
            </Button>
          </Paper>
        </Box>
      );
    }

    return this.props.children;
  }
}