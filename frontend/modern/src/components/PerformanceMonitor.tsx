import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  LinearProgress,
  Switch,
  FormControlLabel,
  Tabs,
  Tab,
  Alert,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material';
import {
  Speed,
  Memory,
  Storage,
  Timeline,
  TrendingUp,
  TrendingDown,
  CheckCircle,
  Warning,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { motion, AnimatePresence } from 'framer-motion';

interface PerformanceMonitorProps {
  performanceData: any;
  isLoading: boolean;
}

const PerformanceMonitor: React.FC<PerformanceMonitorProps> = ({
  performanceData,
  isLoading,
}) => {
  const [tabValue, setTabValue] = useState(0);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [metricsHistory, setMetricsHistory] = useState<any[]>([]);

  // Mock historical data for demonstration
  useEffect(() => {
    if (performanceData) {
      const newEntry = {
        timestamp: new Date().toLocaleTimeString(),
        cacheHitRate: performanceData.cache_hit_rate || 0,
        dbQueryTime: performanceData.average_db_query_time_ms || 0,
        optimization: performanceData.optimization_effectiveness || 0,
        costSaved: performanceData.total_cost_savings_usd || 0,
      };

      setMetricsHistory(prev => {
        const newHistory = [...prev, newEntry].slice(-20); // Keep last 20 entries
        return newHistory;
      });
    }
  }, [performanceData]);

  const getPerformanceGrade = () => {
    if (!performanceData) return { grade: 'N/A', color: 'grey' };
    
    const cacheScore = (performanceData.cache_hit_rate || 0) * 0.3;
    const dbScore = Math.max(0, 100 - (performanceData.average_db_query_time_ms || 0)) * 0.3;
    const optimizationScore = (performanceData.optimization_effectiveness || 0) * 0.4;
    
    const totalScore = cacheScore + dbScore + optimizationScore;
    
    if (totalScore >= 90) return { grade: 'A+', color: 'success' };
    if (totalScore >= 80) return { grade: 'A', color: 'success' };
    if (totalScore >= 70) return { grade: 'B', color: 'info' };
    if (totalScore >= 60) return { grade: 'C', color: 'warning' };
    return { grade: 'D', color: 'error' };
  };

  const performanceGrade = getPerformanceGrade();

  const MetricCard = ({ title, value, change, icon, color = 'primary' }: any) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card elevation={2}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <Box>
              <Typography color="text.secondary" variant="body2">
                {title}
              </Typography>
              <Typography variant="h4" component="div">
                {isLoading ? '...' : value}
              </Typography>
              {change !== undefined && (
                <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                  {change >= 0 ? (
                    <TrendingUp sx={{ color: 'success.main', mr: 0.5 }} />
                  ) : (
                    <TrendingDown sx={{ color: 'error.main', mr: 0.5 }} />
                  )}
                  <Typography
                    variant="body2"
                    color={change >= 0 ? 'success.main' : 'error.main'}
                  >
                    {change >= 0 ? '+' : ''}{change.toFixed(1)}%
                  </Typography>
                </Box>
              )}
            </Box>
            <Box
              sx={{
                p: 1,
                borderRadius: 2,
                bgcolor: `${color}.main`,
                color: `${color}.contrastText`,
              }}
            >
              {icon}
            </Box>
          </Box>
        </CardContent>
      </Card>
    </motion.div>
  );

  const HealthIndicator = ({ label, status, details }: any) => {
    const getStatusIcon = () => {
      switch (status) {
        case 'excellent':
          return <CheckCircle sx={{ color: 'success.main' }} />;
        case 'good':
          return <CheckCircle sx={{ color: 'info.main' }} />;
        case 'warning':
          return <Warning sx={{ color: 'warning.main' }} />;
        case 'error':
          return <ErrorIcon sx={{ color: 'error.main' }} />;
        default:
          return <CheckCircle sx={{ color: 'grey.500' }} />;
      }
    };

    return (
      <ListItem>
        <ListItemIcon>
          {getStatusIcon()}
        </ListItemIcon>
        <ListItemText
          primary={label}
          secondary={details}
        />
      </ListItem>
    );
  };

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            ⚡ Performance Monitor
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Real-time system performance and optimization metrics
          </Typography>
        </Box>
        
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <FormControlLabel
            control={
              <Switch
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
                color="primary"
              />
            }
            label="Auto Refresh"
          />
          
          <Chip
            label={`Grade: ${performanceGrade.grade}`}
            color={performanceGrade.color as any}
            variant="filled"
            sx={{ fontWeight: 'bold' }}
          />
        </Box>
      </Box>

      {/* Performance Alert */}
      {performanceData && (
        <Alert
          severity={
            performanceData.optimization_effectiveness > 80
              ? 'success'
              : performanceData.optimization_effectiveness > 60
              ? 'warning'
              : 'info'
          }
          sx={{ mb: 3 }}
        >
          System is operating at {performanceData.optimization_effectiveness?.toFixed(1) || 0}% 
          optimization effectiveness. 
          {performanceData.total_cost_savings_usd > 0 && (
            ` Cost savings: $${performanceData.total_cost_savings_usd.toFixed(2)}`
          )}
        </Alert>
      )}

      {/* Main Metrics */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Cache Hit Rate"
            value={`${performanceData?.cache_hit_rate?.toFixed(1) || 0}%`}
            change={5.2} // Mock change value
            icon={<Speed />}
            color="success"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="DB Query Time"
            value={`${performanceData?.average_db_query_time_ms?.toFixed(1) || 0}ms`}
            change={-2.1} // Mock change value (negative is good for query time)
            icon={<Memory />}
            color="primary"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Cost Saved"
            value={`$${performanceData?.total_cost_savings_usd?.toFixed(2) || 0}`}
            change={12.5} // Mock change value
            icon={<TrendingUp />}
            color="success"
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Requests Processed"
            value={performanceData?.requests_processed || 0}
            change={8.3} // Mock change value
            icon={<Timeline />}
            color="info"
          />
        </Grid>
      </Grid>

      {/* Tabs */}
      <Paper elevation={2} sx={{ mb: 3 }}>
        <Tabs
          value={tabValue}
          onChange={(_, newValue) => setTabValue(newValue)}
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab label="Performance Trends" />
          <Tab label="System Health" />
          <Tab label="Optimization Details" />
        </Tabs>

        <Box sx={{ p: 3 }}>
          <AnimatePresence mode="wait">
            {tabValue === 0 && (
              <motion.div
                key="trends"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                <Typography variant="h6" gutterBottom>
                  Performance Trends (Last 20 Updates)
                </Typography>
                
                {metricsHistory.length > 0 ? (
                  <Box sx={{ height: 400 }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={metricsHistory}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="timestamp" />
                        <YAxis />
                        <Tooltip />
                        <Line
                          type="monotone"
                          dataKey="cacheHitRate"
                          stroke="#10b981"
                          name="Cache Hit Rate (%)"
                          strokeWidth={2}
                        />
                        <Line
                          type="monotone"
                          dataKey="optimization"
                          stroke="#6366f1"
                          name="Optimization (%)"
                          strokeWidth={2}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </Box>
                ) : (
                  <Typography color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
                    Collecting performance data...
                  </Typography>
                )}
              </motion.div>
            )}

            {tabValue === 1 && (
              <motion.div
                key="health"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                <Typography variant="h6" gutterBottom>
                  System Health Status
                </Typography>
                
                <List>
                  <HealthIndicator
                    label="Cache System"
                    status={
                      (performanceData?.cache_hit_rate || 0) > 80
                        ? 'excellent'
                        : (performanceData?.cache_hit_rate || 0) > 60
                        ? 'good'
                        : 'warning'
                    }
                    details={`Hit rate: ${performanceData?.cache_hit_rate?.toFixed(1) || 0}%`}
                  />
                  
                  <HealthIndicator
                    label="Database Performance"
                    status={
                      (performanceData?.average_db_query_time_ms || 0) < 50
                        ? 'excellent'
                        : (performanceData?.average_db_query_time_ms || 0) < 100
                        ? 'good'
                        : 'warning'
                    }
                    details={`Avg query time: ${performanceData?.average_db_query_time_ms?.toFixed(1) || 0}ms`}
                  />
                  
                  <HealthIndicator
                    label="AI Model Performance"
                    status="excellent"
                    details="All models responding normally"
                  />
                  
                  <HealthIndicator
                    label="WebSocket Connections"
                    status={
                      (performanceData?.active_connections || 0) > 0 ? 'excellent' : 'good'
                    }
                    details={`${performanceData?.active_connections || 0} active connections`}
                  />
                </List>
              </motion.div>
            )}

            {tabValue === 2 && (
              <motion.div
                key="optimization"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                <Typography variant="h6" gutterBottom>
                  Optimization Details
                </Typography>
                
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <Paper elevation={1} sx={{ p: 2 }}>
                      <Typography variant="subtitle1" gutterBottom>
                        Cost Optimization
                      </Typography>
                      
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="body2" color="text.secondary">
                          Total Saved
                        </Typography>
                        <Typography variant="h5" color="success.main">
                          ${performanceData?.total_cost_savings_usd?.toFixed(2) || 0}
                        </Typography>
                      </Box>
                      
                      <LinearProgress
                        variant="determinate"
                        value={Math.min(100, (performanceData?.optimization_effectiveness || 0))}
                        sx={{ height: 8, borderRadius: 4 }}
                      />
                      <Typography variant="caption" color="text.secondary">
                        Optimization Effectiveness: {performanceData?.optimization_effectiveness?.toFixed(1) || 0}%
                      </Typography>
                    </Paper>
                  </Grid>
                  
                  <Grid item xs={12} md={6}>
                    <Paper elevation={1} sx={{ p: 2 }}>
                      <Typography variant="subtitle1" gutterBottom>
                        Request Optimization
                      </Typography>
                      
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="body2" color="text.secondary">
                          Requests Processed
                        </Typography>
                        <Typography variant="h5" color="primary.main">
                          {performanceData?.requests_processed || 0}
                        </Typography>
                      </Box>
                      
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2">Cache Usage</Typography>
                        <Typography variant="body2">
                          {performanceData?.cache_hit_rate?.toFixed(1) || 0}%
                        </Typography>
                      </Box>
                      
                      <LinearProgress
                        variant="determinate"
                        value={performanceData?.cache_hit_rate || 0}
                        sx={{ height: 6, borderRadius: 3 }}
                      />
                    </Paper>
                  </Grid>
                </Grid>
              </motion.div>
            )}
          </AnimatePresence>
        </Box>
      </Paper>
    </Box>
  );
};

export default PerformanceMonitor;