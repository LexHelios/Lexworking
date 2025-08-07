import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Grid,
  LinearProgress,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Avatar,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import {
  Speed,
  Psychology,
  Computer,
  CloudQueue,
  Memory,
  Storage,
  NetworkCheck,
  Timer,
  TrendingUp,
  CheckCircle,
  Warning,
  Error as ErrorIcon
} from '@mui/icons-material';

interface StatusMonitorProps {
  backendUrl: string;
  systemStatus: any;
}

const StatusMonitor: React.FC<StatusMonitorProps> = ({ backendUrl, systemStatus }) => {
  const [performanceData, setPerformanceData] = useState<any>(null);
  const [systemHealth, setSystemHealth] = useState<any>(null);
  const [apiStatus, setApiStatus] = useState<any>(null);

  useEffect(() => {
    fetchPerformanceData();
    fetchSystemHealth();
    fetchApiStatus();
    
    const interval = setInterval(() => {
      fetchPerformanceData();
      fetchSystemHealth();
      fetchApiStatus();
    }, 10000);
    
    return () => clearInterval(interval);
  }, []);

  const fetchPerformanceData = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/v1/performance`);
      if (response.ok) {
        const data = await response.json();
        setPerformanceData(data);
      }
    } catch (error) {
      console.error('Failed to fetch performance data:', error);
    }
  };

  const fetchSystemHealth = async () => {
    try {
      const response = await fetch(`${backendUrl}/health`);
      if (response.ok) {
        const data = await response.json();
        setSystemHealth(data);
      }
    } catch (error) {
      console.error('Failed to fetch system health:', error);
    }
  };

  const fetchApiStatus = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/v1/omnipotent/capabilities`);
      if (response.ok) {
        const data = await response.json();
        setApiStatus(data);
      }
    } catch (error) {
      console.error('Failed to fetch API status:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'operational':
      case 'healthy':
      case 'online':
      case 'active':
        return 'success';
      case 'warning':
      case 'degraded':
        return 'warning';
      case 'error':
      case 'offline':
      case 'failed':
        return 'error';
      default:
        return 'info';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status?.toLowerCase()) {
      case 'operational':
      case 'healthy':
      case 'online':
      case 'active':
        return <CheckCircle color="success" />;
      case 'warning':
      case 'degraded':
        return <Warning color="warning" />;
      case 'error':
      case 'offline':
      case 'failed':
        return <ErrorIcon color="error" />;
      default:
        return <Timer color="info" />;
    }
  };

  const systemMetrics = [
    {
      name: 'System Status',
      value: systemStatus?.status || 'unknown',
      description: 'Overall system health',
      icon: <Psychology />
    },
    {
      name: 'Omnipotent Mode',
      value: systemStatus?.omnipotent_mode ? 'active' : 'inactive',
      description: 'Unrestricted AI capabilities',
      icon: <Speed />
    },
    {
      name: 'Educational Mode',
      value: systemStatus?.educational_mode ? 'enabled' : 'disabled',
      description: 'Educational content generation',
      icon: <Computer />
    },
    {
      name: 'Text Models',
      value: systemStatus?.models?.text_models_available?.length || 0,
      description: 'Available language models',
      icon: <CloudQueue />
    }
  ];

  return (
    <Box>
      {/* System Overview */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {systemMetrics.map((metric, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <Avatar sx={{ bgcolor: 'primary.main', mr: 2, width: 40, height: 40 }}>
                    {metric.icon}
                  </Avatar>
                  <Box>
                    <Typography variant="h6">
                      {typeof metric.value === 'string' ? metric.value.toUpperCase() : metric.value}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {metric.name}
                    </Typography>
                  </Box>
                </Box>
                <Typography variant="caption" color="text.disabled">
                  {metric.description}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Grid container spacing={3}>
        {/* Performance Metrics */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={3}>
                <TrendingUp color="primary" sx={{ mr: 2 }} />
                <Typography variant="h6">🚀 Performance Metrics</Typography>
              </Box>

              {performanceData ? (
                <Box>
                  <Box mb={3}>
                    <Box display="flex" justifyContent="between" alignItems="center" mb={1}>
                      <Typography variant="body2">Cache Hit Rate</Typography>
                      <Typography variant="body2" color="success.main">
                        {performanceData.performance_summary?.cache_hit_rate || 0}%
                      </Typography>
                    </Box>
                    <LinearProgress 
                      variant="determinate" 
                      value={performanceData.performance_summary?.cache_hit_rate || 0}
                      color="success"
                    />
                  </Box>

                  <Box mb={3}>
                    <Box display="flex" justifyContent="between" alignItems="center" mb={1}>
                      <Typography variant="body2">Query Performance</Typography>
                      <Typography variant="body2" color="info.main">
                        {performanceData.performance_summary?.average_db_query_time_ms || 0}ms
                      </Typography>
                    </Box>
                    <LinearProgress 
                      variant="determinate" 
                      value={Math.max(0, 100 - (performanceData.performance_summary?.average_db_query_time_ms || 0))}
                      color="info"
                    />
                  </Box>

                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      Cost Savings: ${performanceData.performance_summary?.total_cost_savings_usd?.toFixed(4) || '0.0000'}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Optimization Score: {performanceData.performance_summary?.optimization_effectiveness || 0}%
                    </Typography>
                  </Box>
                </Box>
              ) : (
                <Typography variant="body2" color="text.disabled">
                  Loading performance data...
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* API Status */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={3}>
                <NetworkCheck color="secondary" sx={{ mr: 2 }} />
                <Typography variant="h6">🔌 API Status</Typography>
              </Box>

              <List dense>
                {apiStatus?.capabilities ? (
                  Object.entries(apiStatus.capabilities).map(([capability, status], index) => (
                    <ListItem key={index} disablePadding>
                      <ListItemIcon sx={{ minWidth: 36 }}>
                        {getStatusIcon(status ? 'active' : 'inactive')}
                      </ListItemIcon>
                      <ListItemText 
                        primary={capability.replace(/_/g, ' ').toUpperCase()}
                        primaryTypographyProps={{ 
                          variant: 'body2',
                          fontFamily: 'monospace'
                        }}
                      />
                      <Chip 
                        label={status ? 'ACTIVE' : 'INACTIVE'} 
                        size="small" 
                        color={status ? 'success' : 'default'}
                      />
                    </ListItem>
                  ))
                ) : (
                  <Typography variant="body2" color="text.disabled">
                    Loading API status...
                  </Typography>
                )}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* System Health Details */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={3}>
                <Memory color="info" sx={{ mr: 2 }} />
                <Typography variant="h6">💾 System Health Details</Typography>
              </Box>

              {systemHealth ? (
                <TableContainer component={Paper} variant="outlined">
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Component</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Value</TableCell>
                        <TableCell>Description</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      <TableRow>
                        <TableCell>System</TableCell>
                        <TableCell>
                          <Chip 
                            label={systemHealth.status?.toUpperCase() || 'UNKNOWN'} 
                            size="small" 
                            color={getStatusColor(systemHealth.status)} 
                          />
                        </TableCell>
                        <TableCell>-</TableCell>
                        <TableCell>Overall system status</TableCell>
                      </TableRow>
                      
                      <TableRow>
                        <TableCell>Database</TableCell>
                        <TableCell>
                          <Chip 
                            label="OPERATIONAL" 
                            size="small" 
                            color="success" 
                          />
                        </TableCell>
                        <TableCell>SQLite</TableCell>
                        <TableCell>Database connectivity</TableCell>
                      </TableRow>
                      
                      <TableRow>
                        <TableCell>Cache</TableCell>
                        <TableCell>
                          <Chip 
                            label="ACTIVE" 
                            size="small" 
                            color="success" 
                          />
                        </TableCell>
                        <TableCell>Redis</TableCell>
                        <TableCell>Response caching system</TableCell>
                      </TableRow>
                      
                      <TableRow>
                        <TableCell>WebSocket</TableCell>
                        <TableCell>
                          <Chip 
                            label="READY" 
                            size="small" 
                            color="info" 
                          />
                        </TableCell>
                        <TableCell>-</TableCell>
                        <TableCell>Real-time communication</TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </TableContainer>
              ) : (
                <Typography variant="body2" color="text.disabled">
                  Loading system health data...
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Stats */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={3}>
                <Storage color="warning" sx={{ mr: 2 }} />
                <Typography variant="h6">📊 Quick Stats</Typography>
              </Box>

              <Box mb={2}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Uptime
                </Typography>
                <Typography variant="h6" color="success.main">
                  {systemHealth?.uptime || 'Unknown'}
                </Typography>
              </Box>

              <Divider sx={{ my: 2 }} />

              <Box mb={2}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Active Connections
                </Typography>
                <Typography variant="h6" color="info.main">
                  {performanceData?.performance_summary?.active_connections || 0}
                </Typography>
              </Box>

              <Divider sx={{ my: 2 }} />

              <Box mb={2}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Total Requests
                </Typography>
                <Typography variant="h6" color="primary.main">
                  {systemStatus?.statistics?.total_requests || 0}
                </Typography>
              </Box>

              <Divider sx={{ my: 2 }} />

              <Box>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  System Mode
                </Typography>
                <Chip 
                  label="OMNIPOTENT" 
                  color="error" 
                  size="small"
                  sx={{ fontWeight: 'bold' }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default StatusMonitor;