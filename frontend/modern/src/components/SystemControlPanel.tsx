import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Box,
  Grid,
  Paper,
  CircularProgress,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Alert
} from '@mui/material';
import {
  Terminal,
  Computer,
  PlayArrow,
  Stop,
  Clear,
  History,
  Security,
  Memory,
  Storage
} from '@mui/icons-material';
import { toast } from 'react-hot-toast';

interface SystemControlProps {
  backendUrl: string;
  systemStatus: any;
}

const SystemControlPanel: React.FC<SystemControlProps> = ({ backendUrl, systemStatus }) => {
  const [command, setCommand] = useState('');
  const [output, setOutput] = useState('');
  const [loading, setLoading] = useState(false);
  const [commandHistory, setCommandHistory] = useState<string[]>([]);

  const quickCommands = [
    { name: 'System Info', command: 'uname -a && echo "---" && lscpu | head -5', category: 'info' },
    { name: 'Memory Usage', command: 'free -h && echo "---" && ps aux --sort=-%mem | head -5', category: 'memory' },
    { name: 'Disk Usage', command: 'df -h && echo "---" && du -sh /app/* 2>/dev/null | sort -hr | head -5', category: 'storage' },
    { name: 'Running Processes', command: 'ps aux | grep python | head -10', category: 'processes' },
    { name: 'Network Status', command: 'ss -tuln | head -10', category: 'network' },
    { name: 'System Health', command: 'uptime && echo "---" && top -bn1 | head -10', category: 'health' }
  ];

  const executeCommand = async (cmdToExecute?: string) => {
    const commandToRun = cmdToExecute || command;
    
    if (!commandToRun.trim()) {
      toast.error('Please enter a command');
      return;
    }

    setLoading(true);
    setOutput('');

    try {
      const formData = new FormData();
      formData.append('command', commandToRun);
      formData.append('working_directory', '/app');
      formData.append('timeout', '30');

      const response = await fetch(`${backendUrl}/api/v1/omnipotent/computer`, {
        method: 'POST',
        body: formData
      });

      const data = await response.json();

      if (data.status === 'success') {
        const commandOutput = data.stdout || '';
        const errorOutput = data.stderr || '';
        
        const fullOutput = commandOutput + (errorOutput ? `\nERROR:\n${errorOutput}` : '');
        setOutput(fullOutput);
        
        // Add to history
        if (!cmdToExecute) { // Only add to history if it's from user input
          setCommandHistory(prev => [commandToRun, ...prev.slice(0, 9)]); // Keep last 10
        }
        
        toast.success('✅ Command executed successfully');
      } else {
        throw new Error(data.error || 'Command execution failed');
      }

    } catch (error) {
      console.error('Command execution error:', error);
      setOutput(`Error: ${error}`);
      toast.error(`❌ Command failed: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && event.ctrlKey) {
      executeCommand();
    }
  };

  const clearTerminal = () => {
    setCommand('');
    setOutput('');
  };

  const useQuickCommand = (quickCommand: any) => {
    setCommand(quickCommand.command);
    toast.success(`Command loaded: ${quickCommand.name}`);
  };

  const useHistoryCommand = (historyCommand: string) => {
    setCommand(historyCommand);
  };

  return (
    <Grid container spacing={3}>
      {/* Command Input */}
      <Grid item xs={12} lg={5}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" mb={3}>
              <Terminal color="primary" sx={{ mr: 2 }} />
              <Typography variant="h5">
                💻 System Control Terminal
              </Typography>
            </Box>

            {/* Quick Commands */}
            <Box mb={3}>
              <Typography variant="subtitle2" gutterBottom>
                ⚡ Quick Commands
              </Typography>
              <Box display="flex" gap={1} flexWrap="wrap" mb={2}>
                {quickCommands.slice(0, 6).map((cmd, index) => (
                  <Chip
                    key={index}
                    label={cmd.name}
                    size="small"
                    clickable
                    onClick={() => useQuickCommand(cmd)}
                    color="primary"
                    variant="outlined"
                  />
                ))}
              </Box>
            </Box>

            {/* Command Input */}
            <TextField
              fullWidth
              multiline
              rows={3}
              variant="outlined"
              label="Enter system command..."
              placeholder="Examples:
• ps aux | grep python
• df -h
• free -m
• uptime
• ls -la /app"
              value={command}
              onChange={(e) => setCommand(e.target.value)}
              onKeyPress={handleKeyPress}
              sx={{ 
                mb: 2,
                '& .MuiInputBase-input': {
                  fontFamily: 'monospace'
                }
              }}
              helperText="Ctrl+Enter to execute"
            />

            {/* Action Buttons */}
            <Box display="flex" gap={2} mb={3}>
              <Button
                variant="contained"
                onClick={() => executeCommand()}
                disabled={loading || !command.trim()}
                startIcon={loading ? <CircularProgress size={20} /> : <PlayArrow />}
                sx={{ flexGrow: 1 }}
              >
                {loading ? 'Executing...' : 'Execute Command'}
              </Button>
              
              <Button
                variant="outlined"
                onClick={clearTerminal}
                startIcon={<Clear />}
              >
                Clear
              </Button>
            </Box>

            {/* Command History */}
            {commandHistory.length > 0 && (
              <Box>
                <Typography variant="subtitle2" gutterBottom>
                  📜 Command History
                </Typography>
                <List dense>
                  {commandHistory.slice(0, 5).map((histCmd, index) => (
                    <ListItem 
                      key={index} 
                      button 
                      onClick={() => useHistoryCommand(histCmd)}
                      sx={{ 
                        borderRadius: 1,
                        mb: 0.5,
                        '&:hover': { bgcolor: 'action.hover' }
                      }}
                    >
                      <ListItemIcon>
                        <History fontSize="small" />
                      </ListItemIcon>
                      <ListItemText 
                        primary={histCmd.length > 50 ? histCmd.slice(0, 50) + '...' : histCmd}
                        primaryTypographyProps={{ 
                          fontFamily: 'monospace',
                          fontSize: '0.85rem'
                        }}
                      />
                    </ListItem>
                  ))}
                </List>
              </Box>
            )}
          </CardContent>
        </Card>
      </Grid>

      {/* Command Output */}
      <Grid item xs={12} lg={7}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" mb={2}>
              <Computer color="secondary" sx={{ mr: 2 }} />
              <Typography variant="h6">
                📺 Terminal Output
              </Typography>
              {loading && (
                <Chip 
                  label="EXECUTING" 
                  size="small" 
                  color="primary" 
                  sx={{ ml: 2 }}
                />
              )}
            </Box>

            <Paper
              variant="outlined"
              sx={{
                p: 2,
                bgcolor: '#000',
                color: '#00ff88',
                fontFamily: 'monospace',
                minHeight: '400px',
                maxHeight: '600px',
                overflow: 'auto',
                border: '1px solid #00ff8840'
              }}
            >
              {loading ? (
                <Box display="flex" alignItems="center" py={2}>
                  <CircularProgress size={16} sx={{ mr: 1, color: '#00ff88' }} />
                  <Typography variant="body2" sx={{ color: '#00ff88' }}>
                    Executing command...
                  </Typography>
                </Box>
              ) : output ? (
                <Typography
                  component="pre"
                  sx={{
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word',
                    fontSize: '0.85rem',
                    lineHeight: 1.4,
                    margin: 0
                  }}
                >
                  {output}
                </Typography>
              ) : (
                <Box py={4} textAlign="center">
                  <Terminal sx={{ fontSize: 48, color: '#333', mb: 2 }} />
                  <Typography variant="body2" sx={{ color: '#666' }}>
                    Terminal ready. Enter a command above to see output here.
                  </Typography>
                  <Typography variant="caption" sx={{ color: '#444' }}>
                    Full system access enabled for educational purposes
                  </Typography>
                </Box>
              )}
            </Paper>
          </CardContent>
        </Card>
      </Grid>

      {/* System Status Grid */}
      <Grid item xs={12}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={1}>
                  <Security color="success" sx={{ mr: 1 }} />
                  <Typography variant="subtitle2">System Security</Typography>
                </Box>
                <Typography variant="h6" color="success.main">
                  OMNIPOTENT ACCESS
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Unrestricted system control enabled
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={1}>
                  <Memory color="info" sx={{ mr: 1 }} />
                  <Typography variant="subtitle2">Memory Status</Typography>
                </Box>
                <Typography variant="h6" color="info.main">
                  OPTIMIZED
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Resource management active
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={1}>
                  <Storage color="warning" sx={{ mr: 1 }} />
                  <Typography variant="subtitle2">Storage Access</Typography>
                </Box>
                <Typography variant="h6" color="warning.main">
                  FULL ACCESS
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Complete file system control
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Grid>

      {/* Security Warning */}
      <Grid item xs={12}>
        <Alert 
          severity="error" 
          sx={{ 
            bgcolor: 'rgba(255, 23, 68, 0.1)',
            border: '1px solid #ff1744'
          }}
        >
          <Typography variant="body2">
            <strong>⚠️ OMNIPOTENT SYSTEM CONTROL:</strong> This terminal has unrestricted access to the entire system. 
            Commands are executed with full privileges for educational and research purposes. Use responsibly for legitimate system administration and learning.
          </Typography>
        </Alert>
      </Grid>
    </Grid>
  );
};

export default SystemControlPanel;