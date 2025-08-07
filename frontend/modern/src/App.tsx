import React, { useState, useEffect } from 'react';
import {
  ThemeProvider,
  createTheme,
  CssBaseline,
  AppBar,
  Toolbar,
  Typography,
  Container,
  Box,
  Paper,
  Grid,
  Card,
  CardContent,
  Button,
  Chip,
  Alert,
  Fade,
  LinearProgress
} from '@mui/material';
import {
  Psychology,
  AutoFixHigh,
  Science,
  Biotech,
  Computer,
  Image,
  Terminal,
  Speed
} from '@mui/icons-material';
import { Toaster, toast } from 'react-hot-toast';

// Import components
import OmnipotentDashboard from './components/OmnipotentDashboard';
import TextGenerationPanel from './components/TextGenerationPanel';
import ImageGenerationPanel from './components/ImageGenerationPanel';
import SystemControlPanel from './components/SystemControlPanel';
import StatusMonitor from './components/StatusMonitor';

// Dark cyberpunk theme
const omnipotentTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#00ff88',
      light: '#4cffb4',
      dark: '#00cc6a',
    },
    secondary: {
      main: '#ff0080',
      light: '#ff4da6',
      dark: '#cc0066',
    },
    background: {
      default: '#000511',
      paper: '#0a0e1a',
    },
    text: {
      primary: '#ffffff',
      secondary: '#b0bec5',
    },
    error: {
      main: '#ff1744',
    },
    warning: {
      main: '#ffa726',
    },
    info: {
      main: '#29b6f6',
    },
    success: {
      main: '#66bb6a',
    },
  },
  typography: {
    fontFamily: '"Fira Code", "Roboto Mono", monospace',
    h1: {
      fontWeight: 700,
      letterSpacing: '0.02em',
    },
    h2: {
      fontWeight: 600,
      letterSpacing: '0.01em',
    },
    h3: {
      fontWeight: 600,
    },
    h4: {
      fontWeight: 500,
    },
    body1: {
      lineHeight: 1.6,
    },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          background: 'linear-gradient(135deg, #0a0e1a 0%, #1a1f2e 100%)',
          border: '1px solid #00ff8820',
          backdropFilter: 'blur(10px)',
          '&:hover': {
            border: '1px solid #00ff88',
            transform: 'translateY(-2px)',
            transition: 'all 0.3s ease',
          },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 600,
          fontFamily: '"Fira Code", monospace',
        },
        contained: {
          background: 'linear-gradient(45deg, #00ff88 30%, #00cc6a 90%)',
          color: '#000',
          '&:hover': {
            background: 'linear-gradient(45deg, #00cc6a 30%, #009952 90%)',
            transform: 'scale(1.05)',
            transition: 'all 0.2s ease',
          },
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          background: 'linear-gradient(135deg, #000511 0%, #0a0e1a 100%)',
          borderBottom: '1px solid #00ff8840',
        },
      },
    },
  },
});

interface SystemStatus {
  status: string;
  omnipotent_mode: boolean;
  unrestricted_models: boolean;
  educational_mode: boolean;
  capabilities: Record<string, boolean>;
  models: {
    text_models_available: string[];
    image_models_available: string[];
  };
}

const App: React.FC = () => {
  const [currentView, setCurrentView] = useState<string>('dashboard');
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [systemReady, setSystemReady] = useState(false);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

  useEffect(() => {
    initializeSystem();
    const interval = setInterval(checkSystemHealth, 10000); // Check every 10s
    return () => clearInterval(interval);
  }, []);

  const initializeSystem = async () => {
    setLoading(true);
    try {
      // Test backend connectivity
      const healthResponse = await fetch(`${backendUrl}/health`);
      
      if (!healthResponse.ok) {
        throw new Error('Backend not responding');
      }

      // Get omnipotent system status
      const statusResponse = await fetch(`${backendUrl}/api/v1/omnipotent/status`);
      
      if (statusResponse.ok) {
        const statusData = await statusResponse.json();
        setSystemStatus(statusData);
        
        if (statusData.status === 'operational' && statusData.omnipotent_mode) {
          setSystemReady(true);
          toast.success('🔱 OMNIPOTENT SYSTEM ONLINE');
        } else {
          toast.error('⚠️ System partially operational');
        }
      } else {
        toast.error('❌ Omnipotent system not responding');
      }
      
    } catch (error) {
      console.error('System initialization failed:', error);
      toast.error('🚨 System initialization failed');
    } finally {
      setLoading(false);
    }
  };

  const checkSystemHealth = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/v1/omnipotent/status`);
      if (response.ok) {
        const data = await response.json();
        setSystemStatus(data);
      }
    } catch (error) {
      console.warn('Health check failed:', error);
    }
  };

  const getSystemStatusColor = () => {
    if (!systemStatus) return 'error';
    if (systemStatus.status === 'operational' && systemStatus.omnipotent_mode) return 'success';
    return 'warning';
  };

  const getCapabilityCount = () => {
    if (!systemStatus?.capabilities) return 0;
    return Object.values(systemStatus.capabilities).filter(Boolean).length;
  };

  const renderCurrentView = () => {
    const commonProps = { backendUrl, systemStatus };
    
    switch (currentView) {
      case 'dashboard':
        return <OmnipotentDashboard {...commonProps} />;
      case 'text':
        return <TextGenerationPanel {...commonProps} />;
      case 'image':
        return <ImageGenerationPanel {...commonProps} />;
      case 'system':
        return <SystemControlPanel {...commonProps} />;
      case 'status':
        return <StatusMonitor {...commonProps} />;
      default:
        return <OmnipotentDashboard {...commonProps} />;
    }
  };

  if (loading) {
    return (
      <ThemeProvider theme={omnipotentTheme}>
        <CssBaseline />
        <Box 
          display="flex" 
          flexDirection="column" 
          justifyContent="center" 
          alignItems="center" 
          minHeight="100vh"
          bgcolor="background.default"
        >
          <Box mb={4}>
            <Psychology sx={{ fontSize: 80, color: 'primary.main', mb: 2 }} />
            <Typography variant="h3" align="center" color="primary">
              🔱 OMNIPOTENT AI SYSTEM 🔱
            </Typography>
            <Typography variant="h6" align="center" color="text.secondary" sx={{ mt: 1 }}>
              Initializing unlimited AI capabilities...
            </Typography>
          </Box>
          
          <Box width="300px" mb={2}>
            <LinearProgress color="primary" />
          </Box>
          
          <Typography variant="body2" color="text.secondary">
            Loading unrestricted models and autonomous agents...
          </Typography>
        </Box>
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider theme={omnipotentTheme}>
      <CssBaseline />
      
      {/* Main App Bar */}
      <AppBar position="static" elevation={0}>
        <Toolbar>
          <Box display="flex" alignItems="center" flexGrow={1}>
            <Psychology sx={{ mr: 2, fontSize: 32, color: 'primary.main' }} />
            <Box>
              <Typography variant="h5" component="div" sx={{ fontWeight: 700 }}>
                🔱 OMNIPOTENT AI SYSTEM 🔱
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Unrestricted Autonomous Intelligence
              </Typography>
            </Box>
          </Box>
          
          {/* System Status Indicators */}
          <Box display="flex" gap={1} alignItems="center">
            <Chip
              label={systemReady ? "OPERATIONAL" : "INITIALIZING"}
              color={systemReady ? "success" : "warning"}
              size="small"
              variant="outlined"
              icon={<AutoFixHigh />}
            />
            
            <Chip
              label="UNRESTRICTED"
              color="error"
              size="small"
              sx={{ 
                fontWeight: 'bold',
                background: 'linear-gradient(45deg, #ff1744, #d50000)',
                color: 'white'
              }}
            />
            
            {systemStatus && (
              <Chip
                label={`${getCapabilityCount()}/10 ACTIVE`}
                color={getSystemStatusColor()}
                size="small"
                variant="outlined"
              />
            )}
          </Box>
        </Toolbar>
      </AppBar>

      {/* Navigation Bar */}
      <Paper 
        elevation={1} 
        sx={{ 
          p: 2, 
          m: 2, 
          background: 'linear-gradient(135deg, #0a0e1a 0%, #1a1f2e 100%)',
          border: '1px solid #00ff8820'
        }}
      >
        <Grid container spacing={1}>
          <Grid item>
            <Button
              variant={currentView === 'dashboard' ? 'contained' : 'outlined'}
              startIcon={<Psychology />}
              onClick={() => setCurrentView('dashboard')}
              size="small"
            >
              Dashboard
            </Button>
          </Grid>
          
          <Grid item>
            <Button
              variant={currentView === 'text' ? 'contained' : 'outlined'}
              startIcon={<Science />}
              onClick={() => setCurrentView('text')}
              size="small"
            >
              Text Generation
            </Button>
          </Grid>
          
          <Grid item>
            <Button
              variant={currentView === 'image' ? 'contained' : 'outlined'}
              startIcon={<Image />}
              onClick={() => setCurrentView('image')}
              size="small"
            >
              Image Generation
            </Button>
          </Grid>
          
          <Grid item>
            <Button
              variant={currentView === 'system' ? 'contained' : 'outlined'}
              startIcon={<Terminal />}
              onClick={() => setCurrentView('system')}
              size="small"
            >
              System Control
            </Button>
          </Grid>
          
          <Grid item>
            <Button
              variant={currentView === 'status' ? 'contained' : 'outlined'}
              startIcon={<Speed />}
              onClick={() => setCurrentView('status')}
              size="small"
            >
              Status Monitor
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Educational Warning */}
      <Container maxWidth="xl" sx={{ mb: 2 }}>
        <Alert 
          severity="info" 
          sx={{ 
            bgcolor: 'rgba(0, 255, 136, 0.1)',
            border: '1px solid #00ff88',
            color: 'text.primary',
            '& .MuiAlert-icon': { color: '#00ff88' }
          }}
          icon={<Biotech />}
        >
          <Typography variant="body2">
            <strong>🎓 EDUCATIONAL MODE:</strong> This system is configured for scientific research and medical education. 
            Unrestricted content generation is enabled for legitimate educational purposes including anatomy training and clinical studies.
          </Typography>
        </Alert>
      </Container>

      {/* Main Content */}
      <Container maxWidth="xl" sx={{ pb: 4 }}>
        <Fade in timeout={500}>
          <Box>
            {renderCurrentView()}
          </Box>
        </Fade>
      </Container>

      {/* Toast Notifications */}
      <Toaster
        position="bottom-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#0a0e1a',
            color: '#ffffff',
            border: '1px solid #00ff88',
            borderRadius: '8px',
            fontFamily: '"Fira Code", monospace',
          },
          success: {
            iconTheme: {
              primary: '#00ff88',
              secondary: '#000',
            },
          },
          error: {
            iconTheme: {
              primary: '#ff1744',
              secondary: '#fff',
            },
          },
        }}
      />
    </ThemeProvider>
  );
};

export default App;