import React, { useState } from 'react';
import { ThemeProvider, createTheme, CssBaseline, Box, Typography, Button, Container, Paper } from '@mui/material';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';

// Import hooks and utilities
import useWebSocket from './hooks/useWebSocket';
import usePerformanceMetrics from './hooks/usePerformanceMetrics';

// Styles
import './App.scss';

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
    },
  },
});

// Theme configuration
const lightTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#6366f1',
      light: '#818cf8',
      dark: '#4f46e5',
    },
    secondary: {
      main: '#10b981',
      light: '#34d399',
      dark: '#059669',
    },
    background: {
      default: '#f8fafc',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontWeight: 700,
    },
    h2: {
      fontWeight: 600,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: '8px',
          fontWeight: 500,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          borderRadius: '12px',
        },
      },
    },
  },
});

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#818cf8',
      light: '#a5b4fc',
      dark: '#6366f1',
    },
    secondary: {
      main: '#34d399',
      light: '#6ee7b7',
      dark: '#10b981',
    },
    background: {
      default: '#0f172a',
      paper: '#1e293b',
    },
    text: {
      primary: '#f1f5f9',
      secondary: '#cbd5e1',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: '8px',
          fontWeight: 500,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          borderRadius: '12px',
          backgroundColor: '#1e293b',
        },
      },
    },
  },
});

const App: React.FC = () => {
  // State management
  const [isDarkMode, setIsDarkMode] = useState<boolean>(
    localStorage.getItem('lex-theme') === 'dark' || false
  );

  // WebSocket connection for real-time features
  const { 
    isConnected, 
    connectionId, 
    sendMessage, 
    messages, 
    streamingResponse,
    connectionStats 
  } = useWebSocket();

  // Performance metrics
  const { 
    performanceData, 
    isLoading: metricsLoading 
  } = usePerformanceMetrics();

  // Theme management
  const theme = isDarkMode ? darkTheme : lightTheme;
  
  const toggleTheme = () => {
    const newMode = !isDarkMode;
    setIsDarkMode(newMode);
    localStorage.setItem('lex-theme', newMode ? 'dark' : 'light');
  };

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Container maxWidth="lg" sx={{ py: 4 }}>
          <Paper elevation={3} sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="h2" component="h1" gutterBottom>
              🔱 LEX Modern Dashboard
            </Typography>
            <Typography variant="h5" color="text.secondary" paragraph>
              Advanced AI Assistant with Real-time Streaming
            </Typography>
            
            <Box sx={{ mt: 4, display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
              <Typography variant="body1">
                Status: {isConnected ? '✅ Connected' : '🔄 Connecting...'}
              </Typography>
              {connectionId && (
                <Typography variant="body2" color="text.secondary">
                  ID: {connectionId.slice(-8)}
                </Typography>
              )}
            </Box>

            <Box sx={{ mt: 4 }}>
              <Button 
                variant="contained" 
                size="large" 
                onClick={toggleTheme}
                sx={{ mr: 2 }}
              >
                {isDarkMode ? '☀️ Light Mode' : '🌙 Dark Mode'}
              </Button>
              
              <Button 
                variant="outlined" 
                size="large"
                disabled={!isConnected}
                onClick={() => sendMessage('Hello LEX! This is a test message from the modern dashboard.')}
              >
                Test Connection
              </Button>
            </Box>

            {performanceData && (
              <Box sx={{ mt: 4 }}>
                <Typography variant="h6" gutterBottom>
                  📊 Performance Metrics
                </Typography>
                <Typography variant="body2">
                  Cache Hit Rate: {performanceData.cache_hit_rate?.toFixed(1) || 0}% | 
                  Optimization: {performanceData.optimization_effectiveness?.toFixed(0) || 0}%
                </Typography>
              </Box>
            )}

            {messages.length > 0 && (
              <Box sx={{ mt: 4 }}>
                <Typography variant="h6" gutterBottom>
                  💬 Recent Messages ({messages.length})
                </Typography>
                <Box sx={{ maxHeight: 300, overflow: 'auto', textAlign: 'left' }}>
                  {messages.slice(-3).map((msg) => (
                    <Paper key={msg.id} elevation={1} sx={{ p: 2, mb: 2 }}>
                      <Typography variant="caption" color="text.secondary">
                        {msg.role.toUpperCase()} - {new Date(msg.timestamp).toLocaleTimeString()}
                      </Typography>
                      <Typography variant="body2" sx={{ mt: 0.5 }}>
                        {msg.content.substring(0, 200)}...
                      </Typography>
                    </Paper>
                  ))}
                </Box>
              </Box>
            )}

            {streamingResponse && (
              <Box sx={{ mt: 4 }}>
                <Typography variant="h6" gutterBottom>
                  ⚡ Live Streaming Response
                </Typography>
                <Paper elevation={1} sx={{ p: 2, textAlign: 'left', border: '2px solid', borderColor: 'primary.main' }}>
                  <Typography variant="body2">
                    {streamingResponse}
                    <span style={{ animation: 'blink 1s infinite' }}>|</span>
                  </Typography>
                </Paper>
              </Box>
            )}
          </Paper>

          {/* Global Toast Notifications */}
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: isDarkMode ? '#1e293b' : '#ffffff',
                color: isDarkMode ? '#f1f5f9' : '#0f172a',
              },
            }}
          />

          <style jsx>{`
            @keyframes blink {
              0%, 50% { opacity: 1; }
              51%, 100% { opacity: 0; }
            }
          `}</style>
        </Container>
      </ThemeProvider>
    </QueryClientProvider>
  );
};

export default App;