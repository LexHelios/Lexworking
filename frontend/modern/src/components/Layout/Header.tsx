import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Box,
  Chip,
} from '@mui/material';
import {
  SmartToy,
  Settings,
  Code,
  Chat,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { RootState } from '../../store/store';

export const Header: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isConnected } = useSelector((state: RootState) => state.chat);

  return (
    <AppBar position="static" elevation={0} sx={{ backgroundColor: 'background.paper', borderBottom: '1px solid', borderColor: 'divider' }}>
      <Toolbar>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <SmartToy sx={{ color: 'primary.main', fontSize: 32 }} />
          <Typography variant="h6" component="div" sx={{ fontWeight: 700 }}>
            🔱 LEX
          </Typography>
          <Typography variant="caption" color="text.secondary">
            v2.0.0
          </Typography>
        </Box>

        <Box sx={{ flexGrow: 1 }} />

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Chip
            label={isConnected ? 'Connected' : 'Disconnected'}
            color={isConnected ? 'success' : 'error'}
            size="small"
            variant="outlined"
          />

          <IconButton
            color={location.pathname === '/chat' || location.pathname === '/' ? 'primary' : 'default'}
            onClick={() => navigate('/chat')}
            title="Chat"
          >
            <Chat />
          </IconButton>

          <IconButton
            color={location.pathname === '/ide' ? 'primary' : 'default'}
            onClick={() => navigate('/ide')}
            title="IDE"
          >
            <Code />
          </IconButton>

          <IconButton
            color={location.pathname === '/settings' ? 'primary' : 'default'}
            onClick={() => navigate('/settings')}
            title="Settings"
          >
            <Settings />
          </IconButton>
        </Box>
      </Toolbar>
    </AppBar>
  );
};