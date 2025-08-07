import React from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  Alert,
} from '@mui/material';
import {
  TrendingUp,
  Speed,
  Memory,
  Cloud,
  Psychology,
  Timeline,
} from '@mui/icons-material';
import { motion } from 'framer-motion';

interface DashboardProps {
  performanceData: any;
  connectionStats: any;
  isLoading: boolean;
}

const Dashboard: React.FC<DashboardProps> = ({
  performanceData,
  connectionStats,
  isLoading,
}) => {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        type: 'spring',
        stiffness: 300,
        damping: 24,
      },
    },
  };

  const MetricCard = ({ 
    title, 
    value, 
    subtitle, 
    icon, 
    color = 'primary',
    progress 
  }: any) => (
    <motion.div variants={itemVariants}>
      <Card
        elevation={2}
        sx={{
          height: '100%',
          background: 'linear-gradient(135deg, rgba(129, 140, 248, 0.05) 0%, rgba(16, 185, 129, 0.05) 100%)',
        }}
      >
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Box
              sx={{
                p: 1,
                borderRadius: 2,
                bgcolor: `${color}.main`,
                color: `${color}.contrastText`,
                mr: 2,
              }}
            >
              {icon}
            </Box>
            <Typography variant="h6" component="div">
              {title}
            </Typography>
          </Box>

          <Typography variant="h4" component="div" gutterBottom>
            {isLoading ? '...' : value}
          </Typography>

          {subtitle && (
            <Typography variant="body2" color="text.secondary" gutterBottom>
              {subtitle}
            </Typography>
          )}

          {progress !== undefined && (
            <Box sx={{ mt: 2 }}>
              <LinearProgress
                variant="determinate"
                value={progress}
                sx={{
                  height: 6,
                  borderRadius: 3,
                  bgcolor: 'grey.200',
                  '& .MuiLinearProgress-bar': {
                    borderRadius: 3,
                  },
                }}
              />
              <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
                {progress.toFixed(1)}%
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Typography variant="h4" component="h1" gutterBottom>
          🔱 LEX Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          Real-time performance metrics and system overview
        </Typography>
      </motion.div>

      {/* Status Alert */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        <Alert
          severity={performanceData ? 'success' : 'warning'}
          sx={{ mb: 3 }}
          icon={<Psychology />}
        >
          {performanceData
            ? '🔱 LEX is operating at optimal performance'
            : 'Performance data is loading...'}
        </Alert>
      </motion.div>

      {/* Main Metrics Grid */}
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <Grid container spacing={3}>
          {/* Cache Performance */}
          <Grid item xs={12} sm={6} md={3}>
            <MetricCard
              title="Cache Hit Rate"
              value={`${performanceData?.cache_hit_rate?.toFixed(1) || 0}%`}
              subtitle="Response caching efficiency"
              icon={<Speed />}
              color="success"
              progress={performanceData?.cache_hit_rate || 0}
            />
          </Grid>

          {/* Database Performance */}
          <Grid item xs={12} sm={6} md={3}>
            <MetricCard
              title="DB Query Time"
              value={`${performanceData?.average_db_query_time_ms?.toFixed(1) || 0}ms`}
              subtitle="Average database response"
              icon={<Memory />}
              color="primary"
              progress={Math.max(0, 100 - (performanceData?.average_db_query_time_ms || 0))}
            />
          </Grid>

          {/* Cost Savings */}
          <Grid item xs={12} sm={6} md={3}>
            <MetricCard
              title="Cost Saved"
              value={`$${performanceData?.total_cost_savings_usd?.toFixed(2) || 0}`}
              subtitle="Total optimization savings"
              icon={<TrendingUp />}
              color="success"
            />
          </Grid>

          {/* Optimization Score */}
          <Grid item xs={12} sm={6} md={3}>
            <MetricCard
              title="Optimization"
              value={`${performanceData?.optimization_effectiveness?.toFixed(0) || 0}%`}
              subtitle="Overall system efficiency"
              icon={<Timeline />}
              color="secondary"
              progress={performanceData?.optimization_effectiveness || 0}
            />
          </Grid>

          {/* Connection Stats */}
          <Grid item xs={12} md={6}>
            <motion.div variants={itemVariants}>
              <Paper elevation={2} sx={{ p: 3, height: '100%' }}>
                <Typography variant="h6" gutterBottom>
                  <Cloud sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Connection Statistics
                </Typography>

                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="h4" color="primary">
                        {connectionStats?.activeConnections || 0}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Active Connections
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={6}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="h4" color="success.main">
                        {connectionStats?.totalMessagesSent || 0}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Messages Sent
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>

                {connectionStats?.averageResponseTime && (
                  <Box sx={{ mt: 3 }}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Average Response Time
                    </Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <LinearProgress
                        variant="determinate"
                        value={Math.min(100, 100 - connectionStats.averageResponseTime * 10)}
                        sx={{ flexGrow: 1, height: 8, borderRadius: 4 }}
                      />
                      <Typography variant="body2">
                        {connectionStats.averageResponseTime.toFixed(2)}s
                      </Typography>
                    </Box>
                  </Box>
                )}
              </Paper>
            </motion.div>
          </Grid>

          {/* System Health */}
          <Grid item xs={12} md={6}>
            <motion.div variants={itemVariants}>
              <Paper elevation={2} sx={{ p: 3, height: '100%' }}>
                <Typography variant="h6" gutterBottom>
                  <Psychology sx={{ mr: 1, verticalAlign: 'middle' }} />
                  System Health
                </Typography>

                <Box sx={{ space: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                    <Typography variant="body2">Requests Processed</Typography>
                    <Chip
                      label={performanceData?.requests_processed || 0}
                      size="small"
                      color="primary"
                      variant="outlined"
                    />
                  </Box>

                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                    <Typography variant="body2">Active Connections</Typography>
                    <Chip
                      label={performanceData?.active_connections || 0}
                      size="small"
                      color="success"
                      variant="outlined"
                    />
                  </Box>

                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                    <Typography variant="body2">Stream Time (Avg)</Typography>
                    <Chip
                      label={`${performanceData?.avg_stream_time?.toFixed(2) || 0}s`}
                      size="small"
                      color="info"
                      variant="outlined"
                    />
                  </Box>

                  <Box sx={{ mt: 3 }}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      System Status
                    </Typography>
                    <Chip
                      label={performanceData ? '🔱 Operational' : '⚡ Loading'}
                      color={performanceData ? 'success' : 'warning'}
                      variant="filled"
                      sx={{ fontWeight: 'bold' }}
                    />
                  </Box>
                </Box>
              </Paper>
            </motion.div>
          </Grid>
        </Grid>
      </motion.div>

      {/* Footer Info */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1 }}
      >
        <Box sx={{ mt: 4, textAlign: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            🔱 LEX Modern Dashboard • Real-time Performance Monitoring
          </Typography>
        </Box>
      </motion.div>
    </Box>
  );
};

export default Dashboard;