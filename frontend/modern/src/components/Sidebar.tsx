import React from 'react';
import {
  Box,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
  IconButton,
  Divider,
  Chip,
  Tooltip,
  Collapse
} from '@mui/material';
import {
  Chat,
  Dashboard,
  Speed,
  Upload,
  Settings,
  ChevronLeft,
  ChevronRight,
  Psychology,
  Memory,
  Analytics,
  CloudSync
} from '@mui/icons-material';
import { motion } from 'framer-motion';

// Types
interface SidebarProps {
  currentPage: string;
  onPageChange: (page: string) => void;
  collapsed: boolean;
  onToggleCollapse: () => void;
  isConnected: boolean;
  connectionStats: any;
}

interface NavigationItem {
  id: string;
  label: string;
  icon: React.ReactNode;
  badge?: string | number;
  color?: string;
  description?: string;
}

const Sidebar: React.FC<SidebarProps> = ({
  currentPage,
  onPageChange,
  collapsed,
  onToggleCollapse,
  isConnected,
  connectionStats
}) => {
  const sidebarWidth = collapsed ? 80 : 280;

  // Navigation items
  const navigationItems: NavigationItem[] = [
    {
      id: 'chat',
      label: 'Chat Interface',
      icon: <Chat />,
      badge: connectionStats?.totalMessagesSent || undefined,
      description: 'Real-time conversation with LEX'
    },
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: <Dashboard />,
      description: 'System overview and metrics'
    },
    {
      id: 'performance',
      label: 'Performance',
      icon: <Speed />,
      color: isConnected ? 'success' : 'error',
      description: 'Real-time performance monitoring'
    },
    {
      id: 'files',
      label: 'File Upload',
      icon: <Upload />,
      description: 'Upload and analyze documents'
    },
    {
      id: 'settings',
      label: 'Settings',
      icon: <Settings />,
      description: 'Configuration and preferences'
    }
  ];

  const systemStats = [
    {
      label: 'Memory',
      value: '2.4GB',
      icon: <Memory fontSize="small" />,
      color: 'primary'
    },
    {
      label: 'Active',
      value: connectionStats?.activeConnections || 0,
      icon: <CloudSync fontSize="small" />,
      color: 'success'
    },
    {
      label: 'Analytics',
      value: '99.2%',
      icon: <Analytics fontSize="small" />,
      color: 'info'
    }
  ];

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: sidebarWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: sidebarWidth,
          boxSizing: 'border-box',
          background: 'linear-gradient(180deg, #1e293b 0%, #0f172a 100%)',
          borderRight: '1px solid rgba(255, 255, 255, 0.12)',
          transition: 'width 0.3s ease-in-out',
          overflow: 'hidden'
        },
      }}
    >
      <Box
        sx={{
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          color: 'white'
        }}
      >
        {/* Header */}
        <Box
          sx={{
            p: 2,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            minHeight: 64,
            borderBottom: '1px solid rgba(255, 255, 255, 0.12)'
          }}
        >
          {!collapsed && (
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.2 }}
            >
              <Typography
                variant="h6"
                sx={{
                  fontWeight: 700,
                  background: 'linear-gradient(45deg, #6366f1, #8b5cf6)',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  color: 'transparent',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1
                }}
              >
                <Psychology sx={{ color: '#6366f1' }} />
                LEX AI
              </Typography>
              <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                Performance Optimized
              </Typography>
            </motion.div>
          )}

          <IconButton
            onClick={onToggleCollapse}
            sx={{
              color: 'rgba(255, 255, 255, 0.7)',
              '&:hover': {
                color: 'white',
                backgroundColor: 'rgba(255, 255, 255, 0.1)'
              }
            }}
          >
            {collapsed ? <ChevronRight /> : <ChevronLeft />}
          </IconButton>
        </Box>

        {/* Connection Status */}
        <Box sx={{ p: 2 }}>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 1,
              p: 1.5,
              borderRadius: 2,
              background: isConnected
                ? 'linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(5, 150, 105, 0.2))'
                : 'linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(220, 38, 38, 0.2))',
              border: `1px solid ${isConnected ? 'rgba(16, 185, 129, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`
            }}
          >
            <Box
              sx={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                backgroundColor: isConnected ? '#10b981' : '#ef4444',
                animation: isConnected ? 'pulse 2s infinite' : 'blink 1s infinite'
              }}
            />
            {!collapsed && (
              <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.9)' }}>
                {isConnected ? 'LEX Connected' : 'Connecting...'}
              </Typography>
            )}
          </Box>
        </Box>

        {/* Navigation */}
        <List sx={{ flex: 1, px: 1 }}>
          {navigationItems.map((item) => (
            <ListItem key={item.id} disablePadding sx={{ mb: 0.5 }}>
              <Tooltip
                title={collapsed ? `${item.label} - ${item.description}` : ''}
                placement="right"
                arrow
              >
                <ListItemButton
                  selected={currentPage === item.id}
                  onClick={() => onPageChange(item.id)}
                  sx={{
                    borderRadius: 2,
                    py: 1.5,
                    px: 2,
                    color: 'rgba(255, 255, 255, 0.8)',
                    '&:hover': {
                      backgroundColor: 'rgba(255, 255, 255, 0.1)',
                      color: 'white'
                    },
                    '&.Mui-selected': {
                      backgroundColor: 'rgba(99, 102, 241, 0.2)',
                      color: '#818cf8',
                      '&:hover': {
                        backgroundColor: 'rgba(99, 102, 241, 0.3)'
                      }
                    },
                    transition: 'all 0.2s ease-in-out'
                  }}
                >
                  <ListItemIcon
                    sx={{
                      minWidth: collapsed ? 0 : 40,
                      color: 'inherit',
                      justifyContent: 'center'
                    }}
                  >
                    {item.icon}
                  </ListItemIcon>

                  {!collapsed && (
                    <motion.div
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -10 }}
                      transition={{ duration: 0.2, delay: 0.1 }}
                      style={{ display: 'flex', alignItems: 'center', width: '100%' }}
                    >
                      <ListItemText
                        primary={item.label}
                        secondary={item.description}
                        primaryTypographyProps={{
                          variant: 'body2',
                          fontWeight: currentPage === item.id ? 600 : 400
                        }}
                        secondaryTypographyProps={{
                          variant: 'caption',
                          sx: { color: 'rgba(255, 255, 255, 0.6)' }
                        }}
                      />

                      {item.badge && (
                        <Chip
                          label={item.badge}
                          size="small"
                          sx={{
                            height: 20,
                            fontSize: '0.75rem',
                            backgroundColor: 'rgba(99, 102, 241, 0.3)',
                            color: '#818cf8'
                          }}
                        />
                      )}
                    </motion.div>
                  )}
                </ListItemButton>
              </Tooltip>
            </ListItem>
          ))}
        </List>

        {/* System Stats */}
        {!collapsed && (
          <Box sx={{ p: 2 }}>
            <Divider sx={{ mb: 2, borderColor: 'rgba(255, 255, 255, 0.12)' }} />
            
            <Typography
              variant="caption"
              sx={{
                color: 'rgba(255, 255, 255, 0.6)',
                fontWeight: 600,
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
                mb: 1,
                display: 'block'
              }}
            >
              System Status
            </Typography>

            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              {systemStats.map((stat, index) => (
                <motion.div
                  key={stat.label}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.2, delay: index * 0.05 }}
                >
                  <Box
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      p: 1,
                      borderRadius: 1,
                      backgroundColor: 'rgba(255, 255, 255, 0.05)',
                      '&:hover': {
                        backgroundColor: 'rgba(255, 255, 255, 0.1)'
                      },
                      transition: 'background-color 0.2s ease-in-out'
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {stat.icon}
                      <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                        {stat.label}
                      </Typography>
                    </Box>
                    <Typography
                      variant="caption"
                      sx={{
                        fontWeight: 600,
                        color: `${stat.color}.main`
                      }}
                    >
                      {stat.value}
                    </Typography>
                  </Box>
                </motion.div>
              ))}
            </Box>
          </Box>
        )}

        {/* Footer */}
        <Box
          sx={{
            p: 2,
            borderTop: '1px solid rgba(255, 255, 255, 0.12)',
            textAlign: collapsed ? 'center' : 'left'
          }}
        >
          {!collapsed ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.3, delay: 0.2 }}
            >
              <Typography
                variant="caption"
                sx={{
                  color: 'rgba(255, 255, 255, 0.6)',
                  display: 'block',
                  mb: 0.5
                }}
              >
                🔱 JAI MAHAKAAL!
              </Typography>
              <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.4)' }}>
                Version 2.0 - Performance Optimized
              </Typography>
            </motion.div>
          ) : (
            <Tooltip title="🔱 JAI MAHAKAAL!" placement="right" arrow>
              <Psychology sx={{ color: 'rgba(255, 255, 255, 0.6)' }} />
            </Tooltip>
          )}
        </Box>
      </Box>

      {/* Global Styles for Animations */}
      <style jsx global>{`
        @keyframes pulse {
          0%, 100% {
            opacity: 1;
          }
          50% {
            opacity: 0.7;
          }
        }

        @keyframes blink {
          0%, 50% {
            opacity: 1;
          }
          51%, 100% {
            opacity: 0.3;
          }
        }
      `}</style>
    </Drawer>
  );
};

export default Sidebar;