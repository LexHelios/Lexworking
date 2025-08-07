import React, { useState } from 'react';
import { 
  ThemeProvider, 
  createTheme, 
  CssBaseline, 
  Box, 
  Typography, 
  Button, 
  Container, 
  Paper,
  Grid,
  Card,
  CardContent,
  TextField,
  IconButton,
  Chip,
  LinearProgress,
  Fade,
  Slide
} from '@mui/material';
import {
  Send,
  Psychology,
  Speed,
  Brightness4,
  Brightness7,
  Chat as ChatIcon,
  Dashboard as DashboardIcon,
  Analytics
} from '@mui/icons-material';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster, toast } from 'react-hot-toast';

// Import hooks and utilities
import useWebSocket from './hooks/useWebSocket';
import usePerformanceMetrics from './hooks/usePerformanceMetrics';

// Styles
import './App.scss';

// Create query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

// Theme configurations
const lightTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#6366f1',
    },
    secondary: {
      main: '#10b981',
    },
  },
  typography: {
    fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
  },
});

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#818cf8',
    },
    secondary: {
      main: '#34d399',
    },
    background: {
      default: '#0f172a',
      paper: '#1e293b',
    },
  },
  typography: {
    fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
  },
});

const App: React.FC = () => {
  // State management
  const [isDarkMode, setIsDarkMode] = useState<boolean>(
    localStorage.getItem('lex-theme') === 'dark' || false
  );
  const [currentView, setCurrentView] = useState<'dashboard' | 'chat' | 'performance'>('dashboard');
  const [userInput, setUserInput] = useState<string>('');

  // WebSocket connection for real-time features
  const { 
    isConnected, 
    connectionId, 
    sendMessage, 
    messages, 
    streamingResponse
  } = useWebSocket();

  // Performance metrics
  const { 
    performanceData 
  } = usePerformanceMetrics();

  // Theme management
  const theme = isDarkMode ? darkTheme : lightTheme;
  
  const toggleTheme = () => {
    const newMode = !isDarkMode;
    setIsDarkMode(newMode);
    localStorage.setItem('lex-theme', newMode ? 'dark' : 'light');
    toast.success(`🎨 Switched to ${newMode ? 'dark' : 'light'} mode`);
  };

  const handleSendMessage = () => {
    if (!userInput.trim()) return;
    
    if (!isConnected) {
      toast.error('❌ Not connected to LEX. Please wait for connection.');
      return;
    }

    sendMessage(userInput.trim());
    setUserInput('');
    toast.success('🔱 Message sent to LEX');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Render Dashboard View
  const renderDashboard = () => (
    <Box sx={{ p: 3 }}>
      <Typography variant="h3" component="h1" gutterBottom align="center">
        🔱 LEX Command Center
      </Typography>
      <Typography variant="h6" color="text.secondary" paragraph align="center">
        Advanced AI Assistant with Real-time Streaming & Performance Optimization
      </Typography>

      <Grid container spacing={3} sx={{ mt: 2 }}>
        {/* Connection Status Card */}
        <Grid item xs={12} md={6}>
          <Card elevation={3} sx={{ height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Psychology sx={{ mr: 2, color: 'primary.main' }} />
                <Typography variant="h6">System Status</Typography>
              </Box>
              
              <Chip 
                label={isConnected ? '🔗 Connected' : '🔄 Connecting'} 
                color={isConnected ? 'success' : 'warning'}
                variant="filled"
                sx={{ mb: 2 }}
              />
              
              {connectionId && (
                <Typography variant="body2" color="text.secondary">
                  Connection ID: {connectionId.slice(-12)}
                </Typography>
              )}
              
              <Typography variant="body2" sx={{ mt: 1 }}>
                Messages: {messages.length}
              </Typography>
              
              <LinearProgress 
                variant="determinate" 
                value={isConnected ? 100 : 30} 
                sx={{ mt: 2 }} 
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Performance Metrics Card */}
        <Grid item xs={12} md={6}>
          <Card elevation={3} sx={{ height: '100%' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Speed sx={{ mr: 2, color: 'secondary.main' }} />
                <Typography variant="h6">Performance</Typography>
              </Box>
              
              {performanceData ? (
                <>
                  <Typography variant="body2">
                    Cache Hit Rate: {performanceData.cache_hit_rate?.toFixed(1) || 0}%
                  </Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={performanceData.cache_hit_rate || 0}
                    color="secondary"
                    sx={{ mt: 1, mb: 2 }} 
                  />
                  
                  <Typography variant="body2">
                    Optimization: {performanceData.optimization_effectiveness?.toFixed(0) || 0}%
                  </Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={performanceData.optimization_effectiveness || 0}
                    color="info"
                    sx={{ mt: 1 }} 
                  />
                </>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  Loading performance data...
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12}>
          <Card elevation={3}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                🚀 Quick Actions
              </Typography>
              
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                <Button 
                  variant="contained" 
                  startIcon={<ChatIcon />}
                  onClick={() => setCurrentView('chat')}
                  size="large"
                >
                  Start Chat
                </Button>
                
                <Button 
                  variant="outlined" 
                  startIcon={<Analytics />}
                  onClick={() => setCurrentView('performance')}
                  size="large"
                >
                  View Analytics
                </Button>
                
                <Button 
                  variant="text" 
                  startIcon={isDarkMode ? <Brightness7 /> : <Brightness4 />}
                  onClick={toggleTheme}
                  size="large"
                >
                  Toggle Theme
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );

  // Render Chat View
  const renderChat = () => (
    <Box sx={{ p: 3, height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Typography variant="h4" gutterBottom>
        💬 Chat with LEX
      </Typography>
      
      {/* Messages Area */}
      <Paper 
        elevation={2} 
        sx={{ 
          flex: 1, 
          p: 2, 
          mb: 2, 
          overflow: 'auto',
          maxHeight: 'calc(100vh - 250px)'
        }}
      >
        {messages.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="h6" color="text.secondary">
              👋 Welcome to LEX
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Start a conversation with your AI assistant
            </Typography>
          </Box>
        ) : (
          <>
            {messages.map((msg) => (
              <Slide key={msg.id} direction="up" in={true}>
                <Paper 
                  elevation={1} 
                  sx={{ 
                    p: 2, 
                    mb: 2, 
                    ml: msg.role === 'user' ? 4 : 0,
                    mr: msg.role === 'user' ? 0 : 4,
                    bgcolor: msg.role === 'user' ? 'primary.main' : 'background.paper',
                    color: msg.role === 'user' ? 'primary.contrastText' : 'text.primary'
                  }}
                >
                  <Typography variant="caption" display="block" sx={{ mb: 1 }}>
                    {msg.role === 'user' ? '👤 You' : '🔱 LEX'} • {new Date(msg.timestamp).toLocaleTimeString()}
                  </Typography>
                  <Typography variant="body1">
                    {msg.content}
                  </Typography>
                </Paper>
              </Slide>
            ))}
          </>
        )}
        
        {/* Streaming Response */}
        {streamingResponse && (
          <Fade in={true}>
            <Paper 
              elevation={1} 
              sx={{ 
                p: 2, 
                mr: 4,
                border: '2px solid',
                borderColor: 'secondary.main',
                bgcolor: 'background.paper'
              }}
            >
              <Typography variant="caption" display="block" sx={{ mb: 1 }}>
                🔱 LEX • Streaming...
              </Typography>
              <Typography variant="body1">
                {streamingResponse}
                <span style={{ 
                  animation: 'blink 1s infinite',
                  marginLeft: '2px'
                }}>|</span>
              </Typography>
            </Paper>
          </Fade>
        )}
      </Paper>

      {/* Input Area */}
      <Box sx={{ display: 'flex', gap: 2 }}>
        <TextField
          fullWidth
          multiline
          maxRows={4}
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message to LEX..."
          variant="outlined"
          disabled={!isConnected}
        />
        <IconButton 
          color="primary" 
          onClick={handleSendMessage}
          disabled={!isConnected || !userInput.trim()}
          size="large"
          sx={{ 
            bgcolor: 'primary.main',
            color: 'primary.contrastText',
            '&:hover': {
              bgcolor: 'primary.dark',
            }
          }}
        >
          <Send />
        </IconButton>
      </Box>
    </Box>
  );

  // Render Performance View
  const renderPerformance = () => (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        📊 Performance Analytics
      </Typography>
      
      <Grid container spacing={3}>
        {performanceData ? (
          <>
            <Grid item xs={12} sm={6} md={3}>
              <Card elevation={2}>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="primary">
                    {performanceData.cache_hit_rate?.toFixed(1) || 0}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Cache Hit Rate
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Card elevation={2}>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="secondary">
                    ${performanceData.total_cost_savings_usd?.toFixed(2) || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Cost Saved
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Card elevation={2}>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="info.main">
                    {performanceData.optimization_effectiveness?.toFixed(0) || 0}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Optimization
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <Card elevation={2}>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography variant="h4" color="warning.main">
                    {performanceData.requests_processed || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Requests Processed
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </>
        ) : (
          <Grid item xs={12}>
            <Card elevation={2}>
              <CardContent sx={{ textAlign: 'center', py: 4 }}>
                <Typography variant="h6" color="text.secondary">
                  Loading performance data...
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    </Box>
  );

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        
        {/* Navigation Bar */}
        <Paper elevation={2} sx={{ position: 'sticky', top: 0, zIndex: 1000 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', p: 2, gap: 2 }}>
            <Typography variant="h5" sx={{ flexGrow: 1, fontWeight: 'bold' }}>
              🔱 LEX
            </Typography>
            
            <Button 
              variant={currentView === 'dashboard' ? 'contained' : 'text'}
              startIcon={<DashboardIcon />}
              onClick={() => setCurrentView('dashboard')}
            >
              Dashboard
            </Button>
            
            <Button 
              variant={currentView === 'chat' ? 'contained' : 'text'}
              startIcon={<ChatIcon />}
              onClick={() => setCurrentView('chat')}
            >
              Chat
            </Button>
            
            <Button 
              variant={currentView === 'performance' ? 'contained' : 'text'}
              startIcon={<Analytics />}
              onClick={() => setCurrentView('performance')}
            >
              Analytics
            </Button>
            
            <IconButton onClick={toggleTheme}>
              {isDarkMode ? <Brightness7 /> : <Brightness4 />}
            </IconButton>
          </Box>
        </Paper>

        {/* Main Content */}
        <Container maxWidth="xl" sx={{ minHeight: 'calc(100vh - 80px)' }}>
          {currentView === 'dashboard' && renderDashboard()}
          {currentView === 'chat' && renderChat()}
          {currentView === 'performance' && renderPerformance()}
        </Container>

        {/* Global Toast Notifications */}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: isDarkMode ? '#1e293b' : '#ffffff',
              color: isDarkMode ? '#f1f5f9' : '#0f172a',
              border: `1px solid ${isDarkMode ? '#334155' : '#e2e8f0'}`,
            },
            success: {
              iconTheme: {
                primary: '#10b981',
                secondary: '#ffffff',
              },
            },
            error: {
              iconTheme: {
                primary: '#ef4444',
                secondary: '#ffffff',
              },
            },
          }}
        />

        {/* Custom Styles for animations */}
        <style>{`
          @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0; }
          }
        `}</style>
      </ThemeProvider>
    </QueryClientProvider>
  );
};

export default App;