import React, { useState } from 'react';
import {
  Box,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  IconButton,
  Typography,
  Chip,
  Divider,
  Tooltip,
  Collapse,
} from '@mui/material';
import {
  Menu,
  MenuOpen,
  Chat,
  Dashboard,
  Speed,
  FileUpload,
  Settings,
  Psychology,
  ExpandLess,
  ExpandMore,
  Circle,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';

interface SidebarProps {
  currentPage: string;
  onPageChange: (page: string) => void;
  collapsed: boolean;
  onToggleCollapse: () => void;
  isConnected: boolean;
  connectionStats: any;
}

const Sidebar: React.FC<SidebarProps> = ({
  currentPage,
  onPageChange,
  collapsed,
  onToggleCollapse,
  isConnected,
  connectionStats,
}) => {
  const [statsExpanded, setStatsExpanded] = useState(false);

  const menuItems = [
    {
      id: 'chat',
      label: 'Chat Interface',
      icon: <Chat />,
      description: 'AI conversation with streaming',
    },
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: <Dashboard />,
      description: 'System overview & metrics',
    },
    {
      id: 'performance',
      label: 'Performance',
      icon: <Speed />,
      description: 'Real-time performance monitoring',
    },
    {
      id: 'files',
      label: 'File Upload',
      icon: <FileUpload />,
      description: 'Upload and analyze files',
    },
    {
      id: 'settings',
      label: 'Settings',
      icon: <Settings />,
      description: 'System configuration',
    },
  ];

  const drawerWidth = collapsed ? 70 : 280;

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: drawerWidth,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: drawerWidth,
          boxSizing: 'border-box',
          transition: 'width 0.3s ease',
          borderRight: 'none',
          background: 'linear-gradient(180deg, #1e293b 0%, #0f172a 100%)',
          color: 'white',
        },
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
        }}
      >
        {!collapsed && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            <Typography variant="h6" sx={{ fontWeight: 'bold', color: '#818cf8' }}>
              🔱 LEX
            </Typography>
            <Typography variant="caption" sx={{ color: '#94a3b8' }}>
              AI Assistant
            </Typography>
          </motion.div>
        )}
        
        <Tooltip title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}>
          <IconButton
            onClick={onToggleCollapse}
            sx={{ color: '#94a3b8', '&:hover': { color: '#818cf8' } }}
          >
            {collapsed ? <Menu /> : <MenuOpen />}
          </IconButton>
        </Tooltip>
      </Box>

      <Divider sx={{ borderColor: '#334155' }} />

      {/* Connection Status */}
      <Box sx={{ p: 2 }}>
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 1,
            mb: collapsed ? 0 : 1,
          }}
        >
          <Circle
            sx={{
              fontSize: 12,
              color: isConnected ? '#10b981' : '#ef4444',
              animation: isConnected ? 'none' : 'pulse 2s infinite',
            }}
          />
          {!collapsed && (
            <Typography variant="body2" sx={{ color: '#cbd5e1' }}>
              {isConnected ? 'Connected' : 'Disconnected'}
            </Typography>
          )}
        </Box>

        {!collapsed && connectionStats && (
          <Box>
            <ListItemButton
              onClick={() => setStatsExpanded(!statsExpanded)}
              sx={{
                borderRadius: 1,
                '&:hover': { bgcolor: 'rgba(129, 140, 248, 0.1)' },
              }}
            >
              <ListItemText
                primary={
                  <Typography variant="caption" sx={{ color: '#94a3b8' }}>
                    Connection Stats
                  </Typography>
                }
              />
              {statsExpanded ? <ExpandLess /> : <ExpandMore />}
            </ListItemButton>

            <Collapse in={statsExpanded} timeout="auto" unmountOnExit>
              <Box sx={{ pl: 2, py: 1 }}>
                <Typography variant="caption" sx={{ color: '#64748b' }}>
                  Messages: {connectionStats.totalMessagesSent || 0}
                </Typography>
                <br />
                <Typography variant="caption" sx={{ color: '#64748b' }}>
                  Active: {connectionStats.activeConnections || 0}
                </Typography>
              </Box>
            </Collapse>
          </Box>
        )}
      </Box>

      <Divider sx={{ borderColor: '#334155' }} />

      {/* Menu Items */}
      <List sx={{ flexGrow: 1, px: 1 }}>
        {menuItems.map((item) => (
          <ListItem key={item.id} disablePadding sx={{ mb: 0.5 }}>
            <Tooltip
              title={collapsed ? `${item.label}: ${item.description}` : ''}
              placement="right"
            >
              <ListItemButton
                selected={currentPage === item.id}
                onClick={() => onPageChange(item.id)}
                sx={{
                  borderRadius: 2,
                  '&.Mui-selected': {
                    bgcolor: 'rgba(129, 140, 248, 0.15)',
                    '&:hover': {
                      bgcolor: 'rgba(129, 140, 248, 0.2)',
                    },
                  },
                  '&:hover': {
                    bgcolor: 'rgba(129, 140, 248, 0.1)',
                  },
                }}
              >
                <ListItemIcon
                  sx={{
                    color: currentPage === item.id ? '#818cf8' : '#94a3b8',
                    minWidth: collapsed ? 'auto' : 40,
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                
                {!collapsed && (
                  <ListItemText
                    primary={
                      <Typography
                        variant="body2"
                        sx={{
                          color: currentPage === item.id ? '#f1f5f9' : '#cbd5e1',
                          fontWeight: currentPage === item.id ? 600 : 400,
                        }}
                      >
                        {item.label}
                      </Typography>
                    }
                    secondary={
                      <Typography
                        variant="caption"
                        sx={{ color: '#64748b' }}
                      >
                        {item.description}
                      </Typography>
                    }
                  />
                )}
              </ListItemButton>
            </Tooltip>
          </ListItem>
        ))}
      </List>

      {/* Footer */}
      {!collapsed && (
        <Box sx={{ p: 2, mt: 'auto' }}>
          <Divider sx={{ borderColor: '#334155', mb: 2 }} />
          
          <Box sx={{ textAlign: 'center' }}>
            <Typography variant="caption" sx={{ color: '#64748b' }}>
              LEX Modern Dashboard
            </Typography>
            <br />
            <Typography variant="caption" sx={{ color: '#475569' }}>
              v2.0.0 • Production Ready
            </Typography>
          </Box>
        </Box>
      )}

      {/* Global Styles */}
      <style jsx global>{`
        @keyframes pulse {
          0%, 100% {
            opacity: 1;
          }
          50% {
            opacity: 0.5;
          }
        }
      `}</style>
    </Drawer>
  );
};

export default Sidebar;