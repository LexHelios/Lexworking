import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Box,
  Grid,
  Card,
  CardContent,
  Alert,
  CircularProgress,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Divider
} from '@mui/material';
import {
  Psychology,
  Image,
  Computer,
  Science,
  LocalHospital,
  ExpandMore,
  Warning,
  CheckCircle,
  Error
} from '@mui/icons-material';

interface OmnipotentResult {
  status: string;
  content?: string;
  response?: string;
  image_url?: string;
  error?: string;
  capabilities_used?: string[];
  model_used?: string;
  cost_estimate?: number;
  processing_time?: number;
  omnipotent_mode?: boolean;
  educational_mode?: boolean;
}

interface SystemStatus {
  status: string;
  omnipotent_mode: boolean;
  unrestricted_models: boolean;
  educational_mode: boolean;
  anatomy_training_mode: boolean;
  capabilities: Record<string, boolean>;
  models: {
    text_models_available: string[];
    image_models_available: string[];
  };
}

const OmnipotentInterface: React.FC = () => {
  const [prompt, setPrompt] = useState('');
  const [result, setResult] = useState<OmnipotentResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [requestType, setRequestType] = useState('auto');
  const [imageStyle, setImageStyle] = useState('medical_textbook');
  const [imageModel, setImageModel] = useState('flux-dev-uncensored');
  const [safetyLevel, setSafetyLevel] = useState('unrestricted');
  const [showAdvanced, setShowAdvanced] = useState(false);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

  useEffect(() => {
    fetchSystemStatus();
  }, []);

  const fetchSystemStatus = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/v1/omnipotent/status`);
      const data = await response.json();
      setSystemStatus(data);
    } catch (error) {
      console.error('Failed to fetch system status:', error);
    }
  };

  const handleGenerate = async () => {
    if (!prompt.trim()) return;

    setLoading(true);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('prompt', prompt);
      formData.append('request_type', requestType);
      formData.append('context', JSON.stringify({}));

      const response = await fetch(`${backendUrl}/api/v1/omnipotent/generate`, {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      setResult({
        status: 'error',
        error: `Network error: ${error}`
      });
    } finally {
      setLoading(false);
    }
  };

  const handleImageGenerate = async () => {
    if (!prompt.trim()) return;

    setLoading(true);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('prompt', prompt);
      formData.append('style', imageStyle);
      formData.append('model', imageModel);
      formData.append('safety_level', safetyLevel);

      const response = await fetch(`${backendUrl}/api/v1/omnipotent/image`, {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      setResult({
        status: 'error',
        error: `Network error: ${error}`
      });
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'success';
      case 'error': return 'error';
      default: return 'info';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success': return <CheckCircle />;
      case 'error': return <Error />;
      default: return <Warning />;
    }
  };

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <Paper elevation={3} sx={{ p: 3, mb: 4, background: 'linear-gradient(135deg, #1a1a2e, #16213e)' }}>
        <Box display="flex" alignItems="center" gap={2}>
          <Psychology sx={{ fontSize: 40, color: '#6366f1' }} />
          <Box>
            <Typography variant="h3" component="h1" sx={{ color: '#fff', fontWeight: 'bold' }}>
              🔱 OMNIPOTENT AGENT SYSTEM 🔱
            </Typography>
            <Typography variant="h6" sx={{ color: '#a1a1aa' }}>
              Unrestricted AI for Scientific & Anatomy Education
            </Typography>
          </Box>
        </Box>
      </Paper>

      {/* System Status */}
      {systemStatus && (
        <Paper elevation={2} sx={{ p: 3, mb: 4 }}>
          <Typography variant="h5" gutterBottom>
            🔋 System Status
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={3}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" color={systemStatus.status === 'operational' ? 'success.main' : 'error.main'}>
                    {systemStatus.status === 'operational' ? '✅ Operational' : '❌ Offline'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    System Health
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" color={systemStatus.omnipotent_mode ? 'success.main' : 'warning.main'}>
                    {systemStatus.omnipotent_mode ? '🔱 Omnipotent' : '⚠️ Limited'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Mode Status
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" color={systemStatus.unrestricted_models ? 'success.main' : 'error.main'}>
                    {systemStatus.unrestricted_models ? '🚫 Unrestricted' : '🔒 Restricted'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Content Policy
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={3}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" color={systemStatus.educational_mode ? 'primary.main' : 'text.secondary'}>
                    {systemStatus.educational_mode ? '📚 Educational' : '🚫 General'}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Content Mode
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </Paper>
      )}

      <Grid container spacing={4}>
        {/* Input Panel */}
        <Grid item xs={12} lg={8}>
          <Paper elevation={2} sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>
              🎯 Omnipotent Request Interface
            </Typography>
            
            <TextField
              fullWidth
              multiline
              rows={4}
              variant="outlined"
              label="Enter your unrestricted request..."
              placeholder="Examples:&#10;• Generate a detailed anatomical diagram of human reproductive system&#10;• Create medical textbook illustration of internal organs&#10;• Explain human sexuality for educational purposes&#10;• Generate scientific diagram of physiological processes"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              sx={{ mb: 3 }}
            />

            <Box display="flex" gap={2} mb={3}>
              <Button
                variant="contained"
                size="large"
                onClick={handleGenerate}
                disabled={loading || !prompt.trim()}
                startIcon={loading ? <CircularProgress size={20} /> : <Psychology />}
                sx={{ 
                  background: 'linear-gradient(45deg, #6366f1, #8b5cf6)',
                  '&:hover': {
                    background: 'linear-gradient(45deg, #5b21b6, #7c3aed)'
                  }
                }}
              >
                {loading ? 'Processing...' : 'Generate Text'}
              </Button>

              <Button
                variant="contained"
                size="large"
                onClick={handleImageGenerate}
                disabled={loading || !prompt.trim()}
                startIcon={loading ? <CircularProgress size={20} /> : <Image />}
                sx={{ 
                  background: 'linear-gradient(45deg, #10b981, #059669)',
                  '&:hover': {
                    background: 'linear-gradient(45deg, #047857, #065f46)'
                  }
                }}
              >
                {loading ? 'Generating...' : 'Generate Image'}
              </Button>
            </Box>

            {/* Advanced Options */}
            <Accordion expanded={showAdvanced} onChange={() => setShowAdvanced(!showAdvanced)}>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Typography>⚙️ Advanced Options</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={4}>
                    <FormControl fullWidth>
                      <InputLabel>Request Type</InputLabel>
                      <Select
                        value={requestType}
                        label="Request Type"
                        onChange={(e) => setRequestType(e.target.value)}
                      >
                        <MenuItem value="auto">🤖 Auto-Detect</MenuItem>
                        <MenuItem value="text_generation">📝 Text Only</MenuItem>
                        <MenuItem value="image_generation">🖼️ Image Only</MenuItem>
                        <MenuItem value="computer_control">💻 Computer Control</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>

                  <Grid item xs={12} md={4}>
                    <FormControl fullWidth>
                      <InputLabel>Image Style</InputLabel>
                      <Select
                        value={imageStyle}
                        label="Image Style"
                        onChange={(e) => setImageStyle(e.target.value)}
                      >
                        <MenuItem value="medical_textbook">📖 Medical Textbook</MenuItem>
                        <MenuItem value="anatomy_chart">📊 Anatomy Chart</MenuItem>
                        <MenuItem value="scientific_diagram">🔬 Scientific Diagram</MenuItem>
                        <MenuItem value="clinical_reference">🏥 Clinical Reference</MenuItem>
                        <MenuItem value="anatomical_drawing">✏️ Anatomical Drawing</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>

                  <Grid item xs={12} md={4}>
                    <FormControl fullWidth>
                      <InputLabel>Safety Level</InputLabel>
                      <Select
                        value={safetyLevel}
                        label="Safety Level"
                        onChange={(e) => setSafetyLevel(e.target.value)}
                      >
                        <MenuItem value="unrestricted">🚫 Unrestricted</MenuItem>
                        <MenuItem value="educational">📚 Educational Only</MenuItem>
                        <MenuItem value="medical">⚕️ Medical Context</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                </Grid>
              </AccordionDetails>
            </Accordion>
          </Paper>
        </Grid>

        {/* Capabilities Panel */}
        <Grid item xs={12} lg={4}>
          <Paper elevation={2} sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>
              🔥 Available Capabilities
            </Typography>
            
            <Box display="flex" flexDirection="column" gap={1}>
              <Chip icon={<Science />} label="Unrestricted Text Generation" color="primary" />
              <Chip icon={<LocalHospital />} label="Anatomy Education" color="success" />
              <Chip icon={<Image />} label="Medical Illustration" color="info" />
              <Chip icon={<Computer />} label="System Control" color="warning" />
              <Chip icon={<Psychology />} label="Uncensored Content" color="error" />
            </Box>

            <Divider sx={{ my: 2 }} />

            <Typography variant="h6" gutterBottom>
              📋 Educational Examples
            </Typography>
            
            <Box component="ul" sx={{ pl: 2 }}>
              <Typography component="li" variant="body2" sx={{ mb: 1 }}>
                "Generate anatomical diagram of reproductive system with labels"
              </Typography>
              <Typography component="li" variant="body2" sx={{ mb: 1 }}>
                "Explain physiological processes during human reproduction"
              </Typography>
              <Typography component="li" variant="body2" sx={{ mb: 1 }}>
                "Create medical textbook illustration of internal organs"
              </Typography>
              <Typography component="li" variant="body2" sx={{ mb: 1 }}>
                "Describe human sexuality for educational purposes"
              </Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Results */}
      {result && (
        <Paper elevation={2} sx={{ p: 3, mt: 4 }}>
          <Box display="flex" alignItems="center" gap={2} mb={2}>
            {getStatusIcon(result.status)}
            <Typography variant="h5">
              📊 Result
            </Typography>
            <Chip 
              label={result.status} 
              color={getStatusColor(result.status)} 
              size="small" 
            />
          </Box>

          {result.status === 'success' ? (
            <Box>
              {result.image_url && (
                <Box mb={3}>
                  <Typography variant="h6" gutterBottom>
                    🖼️ Generated Image
                  </Typography>
                  <img 
                    src={result.image_url} 
                    alt="Generated content"
                    style={{ 
                      maxWidth: '100%', 
                      height: 'auto',
                      borderRadius: 8,
                      border: '2px solid #e5e7eb'
                    }}
                  />
                </Box>
              )}

              {(result.content || result.response) && (
                <Box mb={3}>
                  <Typography variant="h6" gutterBottom>
                    📝 Generated Content
                  </Typography>
                  <Paper variant="outlined" sx={{ p: 2, bgcolor: 'grey.50' }}>
                    <Typography variant="body1" style={{ whiteSpace: 'pre-wrap' }}>
                      {result.content || result.response}
                    </Typography>
                  </Paper>
                </Box>
              )}

              {/* Metadata */}
              <Grid container spacing={2}>
                {result.model_used && (
                  <Grid item xs={6} md={3}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Model Used
                    </Typography>
                    <Typography variant="body2">{result.model_used}</Typography>
                  </Grid>
                )}
                
                {result.processing_time && (
                  <Grid item xs={6} md={3}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Processing Time
                    </Typography>
                    <Typography variant="body2">{result.processing_time.toFixed(2)}s</Typography>
                  </Grid>
                )}

                {result.cost_estimate && (
                  <Grid item xs={6} md={3}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Cost Estimate
                    </Typography>
                    <Typography variant="body2">${result.cost_estimate.toFixed(4)}</Typography>
                  </Grid>
                )}

                {result.capabilities_used && (
                  <Grid item xs={12} md={3}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Capabilities Used
                    </Typography>
                    <Box display="flex" gap={1} flexWrap="wrap">
                      {result.capabilities_used.map((capability, index) => (
                        <Chip key={index} label={capability} size="small" />
                      ))}
                    </Box>
                  </Grid>
                )}
              </Grid>
            </Box>
          ) : (
            <Alert severity="error" sx={{ mt: 2 }}>
              <Typography variant="body1">
                <strong>Error:</strong> {result.error}
              </Typography>
            </Alert>
          )}
        </Paper>
      )}
    </Container>
  );
};

export default OmnipotentInterface;