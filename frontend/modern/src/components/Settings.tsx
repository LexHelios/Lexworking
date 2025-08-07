import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Switch,
  FormControlLabel,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Slider,
  TextField,
  Button,
  Card,
  CardContent,
  CardHeader,
  Divider,
  Alert,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Palette,
  Speed,
  Security,
  Storage,
  Notifications,
  VolumeUp,
  Psychology,
  Tune,
  RestartAlt,
  Save,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import { toast } from 'react-hot-toast';
import { motion } from 'framer-motion';

interface SettingsProps {
  isDarkMode: boolean;
  toggleTheme: () => void;
  performanceData: any;
}

interface UserSettings {
  theme: 'light' | 'dark' | 'auto';
  notifications: boolean;
  soundEnabled: boolean;
  responseSpeed: 'fast' | 'balanced' | 'quality';
  streamingDelay: number;
  autoSave: boolean;
  maxCacheSize: number;
  debugMode: boolean;
  voice: {
    enabled: boolean;
    language: string;
    speed: number;
    pitch: number;
  };
  privacy: {
    storageEnabled: boolean;
    analyticsEnabled: boolean;
    crashReporting: boolean;
  };
}

const Settings: React.FC<SettingsProps> = ({
  isDarkMode,
  toggleTheme,
  performanceData,
}) => {
  const [settings, setSettings] = useState<UserSettings>({
    theme: 'auto',
    notifications: true,
    soundEnabled: true,
    responseSpeed: 'balanced',
    streamingDelay: 30,
    autoSave: true,
    maxCacheSize: 100,
    debugMode: false,
    voice: {
      enabled: false,
      language: 'en-US',
      speed: 1.0,
      pitch: 1.0,
    },
    privacy: {
      storageEnabled: true,
      analyticsEnabled: false,
      crashReporting: true,
    },
  });

  const [hasChanges, setHasChanges] = useState(false);
  const [resetDialogOpen, setResetDialogOpen] = useState(false);

  // Load settings from localStorage
  useEffect(() => {
    const savedSettings = localStorage.getItem('lex_user_settings');
    if (savedSettings) {
      try {
        const parsed = JSON.parse(savedSettings);
        setSettings(prev => ({ ...prev, ...parsed }));
      } catch (error) {
        console.error('Failed to load settings:', error);
      }
    }
  }, []);

  // Update settings and mark as changed
  const updateSetting = (path: string, value: any) => {
    setSettings(prev => {
      const newSettings = { ...prev };
      const keys = path.split('.');
      let current: any = newSettings;
      
      for (let i = 0; i < keys.length - 1; i++) {
        current = current[keys[i]];
      }
      current[keys[keys.length - 1]] = value;
      
      return newSettings;
    });
    setHasChanges(true);
  };

  // Save settings
  const saveSettings = () => {
    try {
      localStorage.setItem('lex_user_settings', JSON.stringify(settings));
      setHasChanges(false);
      toast.success('⚙️ Settings saved successfully');
      
      // Apply theme change if needed
      if (settings.theme !== 'auto') {
        if ((settings.theme === 'dark') !== isDarkMode) {
          toggleTheme();
        }
      }
    } catch (error) {
      console.error('Failed to save settings:', error);
      toast.error('❌ Failed to save settings');
    }
  };

  // Reset settings
  const resetSettings = () => {
    const defaultSettings: UserSettings = {
      theme: 'auto',
      notifications: true,
      soundEnabled: true,
      responseSpeed: 'balanced',
      streamingDelay: 30,
      autoSave: true,
      maxCacheSize: 100,
      debugMode: false,
      voice: {
        enabled: false,
        language: 'en-US',
        speed: 1.0,
        pitch: 1.0,
      },
      privacy: {
        storageEnabled: true,
        analyticsEnabled: false,
        crashReporting: true,
      },
    };
    
    setSettings(defaultSettings);
    setHasChanges(true);
    setResetDialogOpen(false);
    toast.success('⚙️ Settings reset to defaults');
  };

  const SettingCard = ({ title, icon, children }: any) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card elevation={2} sx={{ height: '100%' }}>
        <CardHeader
          avatar={
            <Box
              sx={{
                p: 1,
                borderRadius: 2,
                bgcolor: 'primary.main',
                color: 'primary.contrastText',
              }}
            >
              {icon}
            </Box>
          }
          title={title}
        />
        <CardContent>
          {children}
        </CardContent>
      </Card>
    </motion.div>
  );

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            ⚙️ Settings
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Customize your LEX experience and system preferences
          </Typography>
        </Box>
        
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<RestartAlt />}
            onClick={() => setResetDialogOpen(true)}
            color="error"
          >
            Reset
          </Button>
          <Button
            variant="contained"
            startIcon={<Save />}
            onClick={saveSettings}
            disabled={!hasChanges}
          >
            Save Changes
          </Button>
        </Box>
      </Box>

      {/* Changes Alert */}
      {hasChanges && (
        <Alert severity="info" sx={{ mb: 3 }}>
          You have unsaved changes. Click "Save Changes" to apply them.
        </Alert>
      )}

      {/* Settings Grid */}
      <Grid container spacing={3}>
        {/* Appearance */}
        <Grid item xs={12} md={6}>
          <SettingCard
            title="Appearance"
            icon={<Palette />}
          >
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Theme</InputLabel>
              <Select
                value={settings.theme}
                label="Theme"
                onChange={(e) => updateSetting('theme', e.target.value)}
              >
                <MenuItem value="light">Light</MenuItem>
                <MenuItem value="dark">Dark</MenuItem>
                <MenuItem value="auto">Auto (System)</MenuItem>
              </Select>
            </FormControl>

            <FormControlLabel
              control={
                <Switch
                  checked={settings.notifications}
                  onChange={(e) => updateSetting('notifications', e.target.checked)}
                />
              }
              label="Enable Notifications"
            />

            <FormControlLabel
              control={
                <Switch
                  checked={settings.soundEnabled}
                  onChange={(e) => updateSetting('soundEnabled', e.target.checked)}
                />
              }
              label="Sound Effects"
            />
          </SettingCard>
        </Grid>

        {/* Performance */}
        <Grid item xs={12} md={6}>
          <SettingCard
            title="Performance"
            icon={<Speed />}
          >
            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Response Speed Priority</InputLabel>
              <Select
                value={settings.responseSpeed}
                label="Response Speed Priority"
                onChange={(e) => updateSetting('responseSpeed', e.target.value)}
              >
                <MenuItem value="fast">Fast (Lower Quality)</MenuItem>
                <MenuItem value="balanced">Balanced</MenuItem>
                <MenuItem value="quality">Quality (Slower)</MenuItem>
              </Select>
            </FormControl>

            <Typography gutterBottom>Streaming Delay (ms)</Typography>
            <Slider
              value={settings.streamingDelay}
              onChange={(_, value) => updateSetting('streamingDelay', value)}
              min={10}
              max={100}
              step={10}
              valueLabelDisplay="auto"
              marks={[
                { value: 10, label: 'Fast' },
                { value: 50, label: 'Normal' },
                { value: 100, label: 'Slow' },
              ]}
              sx={{ mb: 2 }}
            />

            <Typography gutterBottom>Max Cache Size (MB)</Typography>
            <Slider
              value={settings.maxCacheSize}
              onChange={(_, value) => updateSetting('maxCacheSize', value)}
              min={50}
              max={500}
              step={50}
              valueLabelDisplay="auto"
              sx={{ mb: 2 }}
            />
          </SettingCard>
        </Grid>

        {/* Voice Settings */}
        <Grid item xs={12} md={6}>
          <SettingCard
            title="Voice & Speech"
            icon={<VolumeUp />}
          >
            <FormControlLabel
              control={
                <Switch
                  checked={settings.voice.enabled}
                  onChange={(e) => updateSetting('voice.enabled', e.target.checked)}
                />
              }
              label="Enable Voice Input/Output"
              sx={{ mb: 2 }}
            />

            {settings.voice.enabled && (
              <>
                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel>Voice Language</InputLabel>
                  <Select
                    value={settings.voice.language}
                    label="Voice Language"
                    onChange={(e) => updateSetting('voice.language', e.target.value)}
                  >
                    <MenuItem value="en-US">English (US)</MenuItem>
                    <MenuItem value="en-GB">English (UK)</MenuItem>
                    <MenuItem value="es-ES">Spanish</MenuItem>
                    <MenuItem value="fr-FR">French</MenuItem>
                    <MenuItem value="de-DE">German</MenuItem>
                  </Select>
                </FormControl>

                <Typography gutterBottom>Speech Speed</Typography>
                <Slider
                  value={settings.voice.speed}
                  onChange={(_, value) => updateSetting('voice.speed', value)}
                  min={0.5}
                  max={2.0}
                  step={0.1}
                  valueLabelDisplay="auto"
                  sx={{ mb: 2 }}
                />

                <Typography gutterBottom>Voice Pitch</Typography>
                <Slider
                  value={settings.voice.pitch}
                  onChange={(_, value) => updateSetting('voice.pitch', value)}
                  min={0.5}
                  max={2.0}
                  step={0.1}
                  valueLabelDisplay="auto"
                />
              </>
            )}
          </SettingCard>
        </Grid>

        {/* Privacy & Data */}
        <Grid item xs={12} md={6}>
          <SettingCard
            title="Privacy & Data"
            icon={<Security />}
          >
            <FormControlLabel
              control={
                <Switch
                  checked={settings.privacy.storageEnabled}
                  onChange={(e) => updateSetting('privacy.storageEnabled', e.target.checked)}
                />
              }
              label="Local Data Storage"
              sx={{ mb: 1 }}
            />
            <Typography variant="caption" color="text.secondary" paragraph>
              Store conversations and settings locally for better experience
            </Typography>

            <FormControlLabel
              control={
                <Switch
                  checked={settings.privacy.analyticsEnabled}
                  onChange={(e) => updateSetting('privacy.analyticsEnabled', e.target.checked)}
                />
              }
              label="Usage Analytics"
              sx={{ mb: 1 }}
            />
            <Typography variant="caption" color="text.secondary" paragraph>
              Help improve LEX by sharing anonymous usage data
            </Typography>

            <FormControlLabel
              control={
                <Switch
                  checked={settings.privacy.crashReporting}
                  onChange={(e) => updateSetting('privacy.crashReporting', e.target.checked)}
                />
              }
              label="Crash Reporting"
              sx={{ mb: 1 }}
            />
            <Typography variant="caption" color="text.secondary">
              Automatically report errors to help fix bugs
            </Typography>
          </SettingCard>
        </Grid>

        {/* Advanced */}
        <Grid item xs={12}>
          <SettingCard
            title="Advanced"
            icon={<Tune />}
          >
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.autoSave}
                      onChange={(e) => updateSetting('autoSave', e.target.checked)}
                    />
                  }
                  label="Auto-save Conversations"
                />
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={settings.debugMode}
                      onChange={(e) => updateSetting('debugMode', e.target.checked)}
                    />
                  }
                  label="Debug Mode"
                />
              </Grid>
            </Grid>

            <Divider sx={{ my: 2 }} />

            <Typography variant="subtitle1" gutterBottom>
              System Information
            </Typography>
            
            <List dense>
              <ListItem>
                <ListItemText primary="LEX Version" />
                <ListItemSecondaryAction>
                  <Chip label="v2.0.0" size="small" color="primary" />
                </ListItemSecondaryAction>
              </ListItem>
              
              <ListItem>
                <ListItemText primary="Performance Score" />
                <ListItemSecondaryAction>
                  <Chip
                    label={`${performanceData?.optimization_effectiveness?.toFixed(0) || 0}%`}
                    size="small"
                    color={
                      (performanceData?.optimization_effectiveness || 0) > 80
                        ? 'success'
                        : (performanceData?.optimization_effectiveness || 0) > 60
                        ? 'warning'
                        : 'error'
                    }
                  />
                </ListItemSecondaryAction>
              </ListItem>
              
              <ListItem>
                <ListItemText primary="Cache Hit Rate" />
                <ListItemSecondaryAction>
                  <Chip
                    label={`${performanceData?.cache_hit_rate?.toFixed(1) || 0}%`}
                    size="small"
                    color="info"
                  />
                </ListItemSecondaryAction>
              </ListItem>
            </List>
          </SettingCard>
        </Grid>
      </Grid>

      {/* Reset Confirmation Dialog */}
      <Dialog
        open={resetDialogOpen}
        onClose={() => setResetDialogOpen(false)}
      >
        <DialogTitle>Reset Settings</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to reset all settings to their default values?
            This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setResetDialogOpen(false)}>
            Cancel
          </Button>
          <Button onClick={resetSettings} color="error" variant="contained">
            Reset All Settings
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Settings;