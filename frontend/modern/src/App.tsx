import React, { useState } from 'react';
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';
import { motion, AnimatePresence } from 'framer-motion';

// Import components
import ChatInterface from './components/ChatInterface';
import Dashboard from './components/Dashboard';
import PerformanceMonitor from './components/PerformanceMonitor';
import FileUpload from './components/FileUpload';
import Settings from './components/Settings';
import Sidebar from './components/Sidebar';

// Import hooks and utilities
import useWebSocket from './hooks/useWebSocket';
import usePerformanceMetrics from './hooks/usePerformanceMetrics';
import { ThemeContext } from './contexts/ThemeContext';

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
  const [currentPage, setCurrentPage] = useState<string>('chat');
  const [isDarkMode, setIsDarkMode] = useState<boolean>(
    localStorage.getItem('lex-theme') === 'dark' || false
  );
  const [sidebarCollapsed, setSidebarCollapsed] = useState<boolean>(false);

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

  // Page transitions
  const pageVariants = {
    initial: { opacity: 0, y: 20 },
    in: { opacity: 1, y: 0 },
    out: { opacity: 0, y: -20 }
  };

  const pageTransition = {
    type: 'tween',
    ease: 'anticipate',
    duration: 0.3
  };

  // Render current page component
  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'chat':
        return (
          <ChatInterface
            isConnected={isConnected}
            connectionId={connectionId}
            sendMessage={sendMessage}
            messages={messages}
            streamingResponse={streamingResponse}
          />
        );
      case 'dashboard':
        return (
          <Dashboard
            performanceData={performanceData}
            connectionStats={connectionStats}
            isLoading={metricsLoading}
          />
        );
      case 'performance':
        return (
          <PerformanceMonitor
            performanceData={performanceData}
            isLoading={metricsLoading}
          />
        );
      case 'files':
        return (
          <FileUpload
            isConnected={isConnected}
            sendMessage={sendMessage}
          />
        );
      case 'settings':
        return (
          <Settings
            isDarkMode={isDarkMode}
            toggleTheme={toggleTheme}
            performanceData={performanceData}
          />
        );
      default:
        return <Navigate to="/chat" replace />;
    }
  };

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeContext.Provider value={{ isDarkMode, toggleTheme }}>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <div className={`app ${isDarkMode ? 'dark' : 'light'}`}>
            {/* Sidebar */}
            <Sidebar
              currentPage={currentPage}
              onPageChange={setCurrentPage}
              collapsed={sidebarCollapsed}
              onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
              isConnected={isConnected}
              connectionStats={connectionStats}
            />

            {/* Main Content */}
            <main className={`main-content ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
              {/* Connection Status Bar */}
              <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
                <div className="status-content">
                  <div className="status-indicator">
                    <div className={`indicator-dot ${isConnected ? 'connected' : 'disconnected'}`} />
                    <span>
                      {isConnected ? '🔱 LEX Connected' : '🔄 Connecting to LEX...'}
                    </span>
                  </div>
                  
                  {isConnected && connectionStats && (
                    <div className="connection-info">
                      <span>ID: {connectionId?.slice(-8) || 'Unknown'}</span>
                      <span>•</span>
                      <span>Messages: {connectionStats.totalMessagesSent || 0}</span>
                      <span>•</span>
                      <span>Active: {connectionStats.activeConnections || 0}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Page Content with Animation */}
              <div className="page-container">
                <AnimatePresence mode="wait">
                  <motion.div
                    key={currentPage}
                    initial="initial"
                    animate="in"
                    exit="out"
                    variants={pageVariants}
                    transition={pageTransition}
                    className="page-content"
                  >
                    {renderCurrentPage()}
                  </motion.div>
                </AnimatePresence>
              </div>
            </main>

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

            {/* Performance Overlay (Development) */}
            {process.env.NODE_ENV === 'development' && (
              <div className="dev-performance-overlay">
                <div className="performance-stats">
                  <div>🔗 {isConnected ? 'Connected' : 'Disconnected'}</div>
                  <div>📊 {performanceData?.cache_hit_rate?.toFixed(1) || 0}% Cache Hit</div>
                  <div>⚡ {performanceData?.optimization_effectiveness?.toFixed(1) || 0}% Optimized</div>
                </div>
              </div>
            )}
          </div>
        </ThemeProvider>
      </ThemeContext.Provider>
    </QueryClientProvider>
  );
};

export default App;