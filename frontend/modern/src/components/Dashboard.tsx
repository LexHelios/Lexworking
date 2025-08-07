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
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Speed,
  Memory,
  Storage,
  CloudSync,
  TrendingUp,
  Psychology,
  Cached,
  Timer,
  AttachMoney,
  Refresh
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { motion } from 'framer-motion';

// Types
interface DashboardProps {
  performanceData: any;
  connectionStats: any;
  isLoading: boolean;
}

const Dashboard: React.FC<DashboardProps> = ({
  performanceData,
  connectionStats,
  isLoading
}) => {
  // Mock data for charts (in production, this would come from real metrics)
  const performanceHistory = [
    { time: '12:00', response: 156, cache: 45, db: 12 },
    { time: '12:05', response: 142, cache: 52, db: 8 },
    { time: '12:10', response: 167, cache: 38, db: 15 },
    { time: '12:15', response: 134, cache: 61, db: 9 },
    { time: '12:20', response: 145, cache: 48, db: 11 },
    { time: '12:25', response: 128, cache: 67, db: 7 },
  ];

  const optimizationBreakdown = [
    { name: 'Cache Hits', value: performanceData?.cache_hit_rate || 45, color: '#10b981' },
    { name: 'Fast Models', value: 30, color: '#6366f1' },
    { name: 'DB Pool', value: 20, color: '#8b5cf6' },
    { name: 'Other', value: 5, color: '#64748b' },
  ];

  // Performance metrics cards
  const performanceMetrics = [
    {
      title: 'Response Time',
      value: `${performanceData?.average_db_query_time_ms || 12.9}ms`,
      change: '-23%',
      changeType: 'positive',
      icon: <Timer />,
      color: 'primary',
      description: 'Average API response time'
    },
    {
      title: 'Cache Hit Rate',
      value: `${performanceData?.cache_hit_rate?.toFixed(1) || 0}%`,
      change: '+15%',
      changeType: 'positive',
      icon: <Cached />,
      color: 'success',
      description: 'Requests served from cache'
    },
    {
      title: 'Cost Savings',
      value: `$${performanceData?.total_cost_savings_usd?.toFixed(2) || 0}`,
      change: '+42%',
      changeType: 'positive',
      icon: <AttachMoney />,
      color: 'warning',
      description: 'Total API cost savings'
    },
    {
      title: 'Active Connections',
      value: `${performanceData?.active_connections || 0}`,
      change: '+8%',
      changeType: 'positive',
      icon: <CloudSync />,
      color: 'info',
      description: 'Current WebSocket connections'
    }
  ];

  const systemHealth = [
    {
      name: 'API Performance',
      value: 92,
      color: 'success',
      description: 'Overall API response performance'
    },
    {
      name: 'Cache Efficiency',
      value: performanceData?.cache_hit_rate || 0,
      color: performanceData?.cache_hit_rate > 40 ? 'success' : 'warning',
      description: 'Cache utilization effectiveness'
    },
    {
      name: 'Database Health',
      value: 95,
      color: 'success',
      description: 'Database query performance'
    },
    {
      name: 'Optimization Score',
      value: performanceData?.optimization_effectiveness || 0,
      color: performanceData?.optimization_effectiveness > 70 ? 'success' : 'warning',
      description: 'Overall system optimization'
    }
  ];

  return (
    <Box sx={{ height: '100%', overflow: 'auto' }}>
      {/* Header */}
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 3
        }}
      >
        <Box>
          <Typography variant="h4" component="h1" sx={{ fontWeight: 700, mb: 1 }}>
            🔱 LEX Dashboard
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Real-time system performance and optimization metrics
          </Typography>
        </Box>

        <Tooltip title="Refresh Data">
          <IconButton
            color="primary"
            sx={{ borderRadius: 2 }}
            disabled={isLoading}
          >
            <Refresh className={isLoading ? 'rotating' : ''} />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Performance Metrics Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {performanceMetrics.map((metric, index) => (
          <Grid item xs={12} sm={6} md={3} key={metric.title}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
            >
              <Card
                elevation={2}
                sx={{
                  height: '100%',
                  background: 'linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05))',
                  backdropFilter: 'blur(10px)',
                  borderRadius: 3,
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    transition: 'transform 0.2s ease-in-out'
                  }
                }}
              >
                <CardContent sx={{ p: 3 }}>
                  <Box
                    sx={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      justifyContent: 'space-between',
                      mb: 2
                    }}
                  >
                    <Box
                      sx={{
                        p: 1.5,
                        borderRadius: 2,
                        bgcolor: `${metric.color}.main`,
                        color: `${metric.color}.contrastText`
                      }}
                    >
                      {metric.icon}
                    </Box>

                    <Chip
                      label={metric.change}
                      size="small"
                      color={metric.changeType === 'positive' ? 'success' : 'error'}
                      variant="filled"
                    />
                  </Box>

                  <Typography variant="h5" sx={{ fontWeight: 700, mb: 1 }}>
                    {metric.value}
                  </Typography>

                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    {metric.title}
                  </Typography>

                  <Typography variant="caption" color="text.secondary">
                    {metric.description}
                  </Typography>
                </CardContent>
              </Card>
            </motion.div>
          </Grid>
        ))}
      </Grid>

      {/* Charts Section */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {/* Performance Timeline */}
        <Grid item xs={12} md={8}>
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.4, delay: 0.2 }}
          >
            <Paper
              elevation={2}
              sx={{
                p: 3,
                height: 400,
                borderRadius: 3
              }}
            >
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
                📈 Performance Timeline
              </Typography>

              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={performanceHistory}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.1)" />
                  <XAxis
                    dataKey="time"
                    stroke="rgba(0,0,0,0.6)"
                    fontSize={12}
                  />
                  <YAxis stroke="rgba(0,0,0,0.6)" fontSize={12} />
                  <RechartsTooltip
                    contentStyle={{
                      background: 'rgba(255,255,255,0.95)',
                      border: '1px solid rgba(0,0,0,0.1)',
                      borderRadius: '8px',
                      backdropFilter: 'blur(10px)'
                    }}
                  />
                  <Line
                    type="monotone"
                    dataKey="response"
                    stroke="#6366f1"
                    strokeWidth={2}
                    dot={{ r: 4 }}
                    name="Response Time (ms)"
                  />
                  <Line
                    type="monotone"
                    dataKey="cache"
                    stroke="#10b981"
                    strokeWidth={2}
                    dot={{ r: 4 }}
                    name="Cache Hit Rate (%)"
                  />
                  <Line
                    type="monotone"
                    dataKey="db"
                    stroke="#8b5cf6"
                    strokeWidth={2}
                    dot={{ r: 4 }}
                    name="DB Query Time (ms)"
                  />
                </LineChart>
              </ResponsiveContainer>
            </Paper>
          </motion.div>
        </Grid>

        {/* Optimization Breakdown */}
        <Grid item xs={12} md={4}>
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.4, delay: 0.3 }}
          >
            <Paper
              elevation={2}
              sx={{
                p: 3,
                height: 400,
                borderRadius: 3
              }}
            >
              <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
                🎯 Optimization Breakdown
              </Typography>

              <Box sx={{ height: 250, display: 'flex', justifyContent: 'center' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={optimizationBreakdown}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={90}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {optimizationBreakdown.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <RechartsTooltip
                      formatter={(value) => [`${value}%`, 'Contribution']}
                      contentStyle={{
                        background: 'rgba(255,255,255,0.95)',
                        border: '1px solid rgba(0,0,0,0.1)',
                        borderRadius: '8px'
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </Box>

              {/* Legend */}
              <Box sx={{ mt: 2 }}>
                {optimizationBreakdown.map((item, index) => (
                  <Box
                    key={item.name}
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      mb: 1
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Box
                        sx={{
                          width: 12,
                          height: 12,
                          borderRadius: '50%',
                          bgcolor: item.color
                        }}
                      />
                      <Typography variant="caption">{item.name}</Typography>
                    </Box>
                    <Typography variant="caption" sx={{ fontWeight: 600 }}>
                      {item.value}%
                    </Typography>
                  </Box>
                ))}
              </Box>
            </Paper>
          </motion.div>
        </Grid>
      </Grid>

      {/* System Health */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.4 }}
      >
        <Paper elevation={2} sx={{ p: 3, borderRadius: 3 }}>
          <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
            🏥 System Health
          </Typography>

          <Grid container spacing={3}>
            {systemHealth.map((health, index) => (
              <Grid item xs={12} sm={6} md={3} key={health.name}>
                <Box sx={{ mb: 2 }}>
                  <Box
                    sx={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      mb: 1
                    }}
                  >
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>
                      {health.name}
                    </Typography>
                    <Typography
                      variant="body2"
                      sx={{
                        fontWeight: 700,
                        color: `${health.color}.main`
                      }}
                    >
                      {health.value}%
                    </Typography>
                  </Box>

                  <LinearProgress
                    variant="determinate"
                    value={health.value}
                    color={health.color as any}
                    sx={{
                      height: 6,
                      borderRadius: 3,
                      bgcolor: 'rgba(0,0,0,0.1)',
                      '& .MuiLinearProgress-bar': {
                        borderRadius: 3
                      }
                    }}
                  />

                  <Typography
                    variant="caption"
                    color="text.secondary"
                    sx={{ mt: 0.5, display: 'block' }}
                  >
                    {health.description}
                  </Typography>
                </Box>
              </Grid>
            ))}
          </Grid>
        </Paper>
      </motion.div>

      {/* Global Styles */}
      <style jsx global>{`
        .rotating {
          animation: rotate 1s linear infinite;
        }

        @keyframes rotate {
          from {
            transform: rotate(0deg);
          }
          to {
            transform: rotate(360deg);
          }
        }
      `}</style>
    </Box>
  );
};

export default Dashboard;