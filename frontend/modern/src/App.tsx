import React, { useState, useEffect } from 'react';
import {
  Container,
  AppBar,
  Toolbar,
  Typography,
  Box,
  Paper,
  Grid,
  Card,
  CardContent,
  Button,
  Chip,
  Alert
} from '@mui/material';
import {
  Psychology,
  Dashboard,
  Computer,
  Image,
  Science,
  Settings
} from '@mui/icons-material';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Toaster, toast } from 'react-hot-toast';

// Import components
import ChatInterface from './components/ChatInterface';
import OmnipotentInterface from './components/OmnipotentInterface';
import PerformanceMonitor from './components/PerformanceMonitor';
import Settings from './components/Settings';

// Import hooks
import useWebSocket from './hooks/useWebSocket';
import usePerformanceMetrics from './hooks/usePerformanceMetrics';

// Dark theme for the omnipotent system
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#6366f1',
    },
    secondary: {
      main: '#8b5cf6',
    },
    background: {
      default: '#0f0f23',
      paper: '#1a1a2e',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
  },
});

const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<string>('omnipotent');
  const [systemStatus, setSystemStatus] = useState<any>(null);
  
  // WebSocket connection for real-time updates
  const { 
    connectionStatus, 
    sendMessage, 
    lastMessage,
    connectionStats 
  } = useWebSocket();
  
  // Performance monitoring
  const performanceMetrics = usePerformanceMetrics();

  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

  useEffect(() => {
    // Fetch system status on load
    fetchSystemStatus();
    
    // Show connection status
    if (connectionStatus === 'Connected') {
      toast.success('🔱 Connected to OMNIPOTENT System');
    } else if (connectionStatus === 'Disconnected') {
      toast.error('❌ Disconnected from system');
    }
  }, [connectionStatus]);

  const fetchSystemStatus = async () => {
    try {
      const response = await fetch(`${backendUrl}/health`);
      const data = await response.json();
      setSystemStatus(data);
    } catch (error) {
      console.error('Failed to fetch system status:', error);
      toast.error('Failed to fetch system status');
    }
  };

  const renderCurrentView = () => {
    switch (currentView) {
      case 'omnipotent':
        return <OmnipotentInterface />;
      case 'chat':
        return <ChatInterface />;
      case 'performance':
        return <PerformanceMonitor />;
      case 'settings':
        return <Settings />;
      default:
        return <OmnipotentInterface />;
    }
  };

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Box sx={{ flexGrow: 1, minHeight: '100vh', bgcolor: 'background.default' }}>
        <AppBar position="static" elevation={0} sx={{ bgcolor: '#1a1a2e' }}>
          <Toolbar>
            <Psychology sx={{ mr: 2, fontSize: 32, color: '#6366f1' }} />
            <Typography variant="h5" component="div" sx={{ flexGrow: 1, fontWeight: 'bold' }}>
              🔱 LEX OMNIPOTENT SYSTEM 🔱
            </Typography>
            
            {/* System Status Indicators */}
            <Box display="flex" gap={2} alignItems="center">
              <Chip
                label={connectionStatus}
                color={connectionStatus === 'Connected' ? 'success' : 'error'}
                size="small"
                variant="outlined"
              />
              
              {systemStatus && (
                <Chip
                  label={systemStatus.status}
                  color={systemStatus.status === 'operational' ? 'success' : 'warning'}
                  size="small"
                  variant="outlined"
                />
              )}
              
              <Chip
                label="Unrestricted Mode"
                color="error"
                size="small"
                sx={{ fontWeight: 'bold' }}
              />
            </Box>
          </Toolbar>
        </AppBar>

        {/* Navigation Bar */}
        <Paper 
          elevation={1} 
          sx={{ 
            p: 1, 
            m: 2, 
            bgcolor: 'background.paper',
            borderRadius: 2
          }}
        >
          <Box display="flex" gap={1} flexWrap="wrap">
            <Button
              variant={currentView === 'omnipotent' ? 'contained' : 'outlined'}
              startIcon={<Psychology />}
              onClick={() => setCurrentView('omnipotent')}
              sx={{ textTransform: 'none' }}
            >
              🔱 Omnipotent Interface
            </Button>
            
            <Button
              variant={currentView === 'chat' ? 'contained' : 'outlined'}
              startIcon={<Dashboard />}
              onClick={() => setCurrentView('chat')}
              sx={{ textTransform: 'none' }}
            >
              💬 Chat Interface
            </Button>
            
            <Button
              variant={currentView === 'performance' ? 'contained' : 'outlined'}
              startIcon={<Computer />}
              onClick={() => setCurrentView('performance')}
              sx={{ textTransform: 'none' }}
            >
              📊 Performance Monitor
            </Button>
            
            <Button
              variant={currentView === 'settings' ? 'contained' : 'outlined'}
              startIcon={<Settings />}
              onClick={() => setCurrentView('settings')}
              sx={{ textTransform: 'none' }}
            >
              ⚙️ Settings
            </Button>
          </Box>
        </Paper>

        {/* Warning Banner for Educational Use */}
        <Container maxWidth="xl" sx={{ mb: 2 }}>
          <Alert 
            severity="info" 
            sx={{ 
              bgcolor: 'rgba(99, 102, 241, 0.1)',
              border: '1px solid #6366f1',
              '& .MuiAlert-icon': { color: '#6366f1' }
            }}
          >
            <Typography variant="body2">
              <strong>🎓 Educational Mode Active:</strong> This system is configured for scientific and anatomy education. 
              Unrestricted content generation is enabled for legitimate educational purposes including medical training, 
              scientific research, and anatomical studies.
            </Typography>
          </Alert>
        </Container>

        {/* Main Content */}
        {renderCurrentView()}

        {/* System Info Footer */}
        <Paper 
          elevation={1} 
          sx={{ 
            p: 2, 
            m: 2, 
            mt: 4,
            bgcolor: 'background.paper',
            borderRadius: 2
          }}
        >
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={3}>
              <Typography variant="body2" color="text.secondary">
                <strong>System:</strong> LEX Omnipotent v2.0
              </Typography>
            </Grid>
            
            <Grid item xs={12} md={3}>
              <Typography variant="body2" color="text.secondary">
                <strong>Mode:</strong> Educational/Scientific
              </Typography>
            </Grid>
            
            <Grid item xs={12} md={3}>
              <Typography variant="body2" color="text.secondary">
                <strong>Models:</strong> Unrestricted Access
              </Typography>
            </Grid>
            
            <Grid item xs={12} md={3}>
              <Typography variant="body2" color="text.secondary">
                <strong>Safety:</strong> Educational Override
              </Typography>
            </Grid>
          </Grid>
        </Paper>

        {/* Toast Notifications */}
        <Toaster
          position="bottom-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#1a1a2e',
              color: '#fff',
              border: '1px solid #6366f1',
            },
          }}
        />
      </Box>
    </ThemeProvider>
  );
};

export default App;