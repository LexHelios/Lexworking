import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  Chip,
  LinearProgress,
  Avatar,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Psychology,
  AutoFixHigh,
  Science,
  Biotech,
  Computer,
  Image,
  Terminal,
  Speed,
  Security,
  CloudQueue,
  Memory,
  StorageRounded,
  PlayArrow,
  Stop,
  Refresh
} from '@mui/icons-material';
import { toast } from 'react-hot-toast';

interface DashboardProps {
  backendUrl: string;
  systemStatus: any;
}

const OmnipotentDashboard: React.FC<DashboardProps> = ({ backendUrl, systemStatus }) => {
  const [systemMetrics, setSystemMetrics] = useState<any>(null);
  const [recentActivity, setRecentActivity] = useState<any[]>([]);
  const [autonomousMode, setAutonomousMode] = useState(false);

  useEffect(() => {
    fetchSystemMetrics();
    fetchRecentActivity();
    const interval = setInterval(fetchSystemMetrics, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchSystemMetrics = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/v1/omnipotent/status`);
      if (response.ok) {
        const data = await response.json();
        setSystemMetrics(data);
      }
    } catch (error) {
      console.error('Failed to fetch system metrics:', error);
    }
  };

  const fetchRecentActivity = async () => {
    // Mock recent activity - in production this would come from the backend
    setRecentActivity([
      { id: 1, type: 'text_generation', description: 'Generated anatomical content', timestamp: new Date() },
      { id: 2, type: 'image_generation', description: 'Created medical illustration', timestamp: new Date() },
      { id: 3, type: 'system_control', description: 'Executed system command', timestamp: new Date() },
    ]);
  };

  const toggleAutonomousMode = async () => {
    try {
      // This would connect to the autonomous system
      setAutonomousMode(!autonomousMode);
      toast.success(autonomousMode ? '🛑 Autonomous mode disabled' : '🚀 Autonomous mode enabled');
    } catch (error) {
      toast.error('Failed to toggle autonomous mode');
    }
  };

  const quickAction = async (action: string) => {
    toast.loading('Executing action...', { id: action });
    
    try {
      let response;
      
      switch (action) {
        case 'anatomy':
          response = await fetch(`${backendUrl}/api/v1/omnipotent/generate`, {
            method: 'POST',
            body: new URLSearchParams({
              prompt: 'Generate educational content about human anatomy for medical students',
              request_type: 'educational_anatomy'
            })
          });
          break;
          
        case 'medical_image':
          response = await fetch(`${backendUrl}/api/v1/omnipotent/image`, {
            method: 'POST',
            body: new URLSearchParams({
              prompt: 'Medical textbook illustration of human anatomy',
              style: 'medical_textbook',
              model: 'flux-dev-uncensored'
            })
          });
          break;
          
        case 'system_check':
          response = await fetch(`${backendUrl}/api/v1/omnipotent/computer`, {
            method: 'POST',
            body: new URLSearchParams({
              command: 'echo "System health check completed at $(date)"'
            })
          });
          break;
          
        default:
          throw new Error('Unknown action');
      }
      
      if (response?.ok) {
        const data = await response.json();
        toast.success(`✅ ${action.replace('_', ' ')} completed`, { id: action });
      } else {
        throw new Error('Action failed');
      }
      
    } catch (error) {
      toast.error(`❌ ${action.replace('_', ' ')} failed`, { id: action });
    }
  };

  const capabilities = systemStatus?.capabilities || {};
  const activeCapabilities = Object.entries(capabilities).filter(([_, active]) => active);
  const inactiveCapabilities = Object.entries(capabilities).filter(([_, active]) => !active);

  return (
    <Box>
      {/* System Overview Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
                  <Psychology />
                </Avatar>
                <Typography variant="h6">System Status</Typography>
              </Box>
              <Typography variant="h4" color="primary" gutterBottom>
                {systemStatus?.status === 'operational' ? 'ONLINE' : 'OFFLINE'}
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={systemStatus?.status === 'operational' ? 100 : 0}
                color="primary"
                sx={{ mt: 1 }}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <Avatar sx={{ bgcolor: 'success.main', mr: 2 }}>
                  <AutoFixHigh />
                </Avatar>
                <Typography variant="h6">Capabilities</Typography>
              </Box>
              <Typography variant="h4" color="success.main" gutterBottom>
                {activeCapabilities.length}/10
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Active omnipotent capabilities
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <Avatar sx={{ bgcolor: 'info.main', mr: 2 }}>
                  <CloudQueue />
                </Avatar>
                <Typography variant="h6">API Models</Typography>
              </Box>
              <Typography variant="h4" color="info.main" gutterBottom>
                {(systemMetrics?.models?.text_models_available?.length || 0) + 
                 (systemMetrics?.models?.image_models_available?.length || 0)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Available AI models
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <Avatar sx={{ bgcolor: 'warning.main', mr: 2 }}>
                  <Memory />
                </Avatar>
                <Typography variant="h6">Autonomous</Typography>
              </Box>
              <Box display="flex" alignItems="center" gap={1}>
                <Chip
                  label={autonomousMode ? 'ACTIVE' : 'STANDBY'}
                  color={autonomousMode ? 'success' : 'default'}
                  size="small"
                />
                <IconButton 
                  size="small" 
                  onClick={toggleAutonomousMode}
                  color={autonomousMode ? 'error' : 'success'}
                >
                  {autonomousMode ? <Stop /> : <PlayArrow />}
                </IconButton>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Main Dashboard Content */}
      <Grid container spacing={3}>
        {/* Quick Actions */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                🚀 Quick Actions
              </Typography>
              
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Button
                    fullWidth
                    variant="contained"
                    startIcon={<Biotech />}
                    onClick={() => quickAction('anatomy')}
                    sx={{ mb: 1 }}
                  >
                    Generate Anatomy Content
                  </Button>
                </Grid>
                
                <Grid item xs={12}>
                  <Button
                    fullWidth
                    variant="outlined"
                    startIcon={<Image />}
                    onClick={() => quickAction('medical_image')}
                    sx={{ mb: 1 }}
                  >
                    Create Medical Illustration
                  </Button>
                </Grid>
                
                <Grid item xs={12}>
                  <Button
                    fullWidth
                    variant="outlined"
                    startIcon={<Terminal />}
                    onClick={() => quickAction('system_check')}
                  >
                    Run System Health Check
                  </Button>
                </Grid>
              </Grid>
              
              <Divider sx={{ my: 2 }} />
              
              <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                Educational Templates
              </Typography>
              
              <Box display="flex" gap={1} flexWrap="wrap">
                <Chip 
                  label="Human Anatomy" 
                  size="small" 
                  clickable 
                  onClick={() => quickAction('anatomy')}
                />
                <Chip 
                  label="Physiology" 
                  size="small" 
                  clickable 
                />
                <Chip 
                  label="Medical Diagrams" 
                  size="small" 
                  clickable 
                  onClick={() => quickAction('medical_image')}
                />
                <Chip 
                  label="Clinical Studies" 
                  size="small" 
                  clickable 
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Active Capabilities */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="between" mb={2}>
                <Typography variant="h6">
                  🔥 Active Capabilities
                </Typography>
                <Tooltip title="Refresh capabilities">
                  <IconButton size="small" onClick={fetchSystemMetrics}>
                    <Refresh />
                  </IconButton>
                </Tooltip>
              </Box>
              
              <List dense>
                {activeCapabilities.map(([capability, _], index) => (
                  <ListItem key={index} disablePadding>
                    <ListItemIcon>
                      <Box 
                        sx={{
                          width: 8,
                          height: 8,
                          borderRadius: '50%',
                          bgcolor: 'success.main'
                        }}
                      />
                    </ListItemIcon>
                    <ListItemText 
                      primary={capability.replace(/_/g, ' ').toUpperCase()}
                      primaryTypographyProps={{ variant: 'body2', fontFamily: 'monospace' }}
                    />
                  </ListItem>
                ))}
              </List>
              
              {inactiveCapabilities.length > 0 && (
                <>
                  <Divider sx={{ my: 1 }} />
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Inactive Capabilities
                  </Typography>
                  <List dense>
                    {inactiveCapabilities.slice(0, 3).map(([capability, _], index) => (
                      <ListItem key={index} disablePadding>
                        <ListItemIcon>
                          <Box 
                            sx={{
                              width: 8,
                              height: 8,
                              borderRadius: '50%',
                              bgcolor: 'text.disabled'
                            }}
                          />
                        </ListItemIcon>
                        <ListItemText 
                          primary={capability.replace(/_/g, ' ').toUpperCase()}
                          primaryTypographyProps={{ 
                            variant: 'body2', 
                            fontFamily: 'monospace',
                            color: 'text.disabled'
                          }}
                        />
                      </ListItem>
                    ))}
                  </List>
                </>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                📊 Recent Activity
              </Typography>
              
              <List>
                {recentActivity.map((activity, index) => (
                  <React.Fragment key={activity.id}>
                    <ListItem>
                      <ListItemIcon>
                        {activity.type === 'text_generation' && <Science color="primary" />}
                        {activity.type === 'image_generation' && <Image color="secondary" />}
                        {activity.type === 'system_control' && <Terminal color="info" />}
                      </ListItemIcon>
                      <ListItemText
                        primary={activity.description}
                        secondary={activity.timestamp.toLocaleTimeString()}
                      />
                      <Chip 
                        label={activity.type.replace('_', ' ').toUpperCase()} 
                        size="small" 
                        variant="outlined" 
                      />
                    </ListItem>
                    {index < recentActivity.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
              
              {recentActivity.length === 0 && (
                <Typography variant="body2" color="text.secondary" textAlign="center" py={2}>
                  No recent activity. Start by running a quick action above.
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default OmnipotentDashboard;