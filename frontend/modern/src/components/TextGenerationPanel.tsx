import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Box,
  Grid,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Paper,
  CircularProgress,
  Alert,
  Slider,
  Switch,
  FormControlLabel,
  Divider
} from '@mui/material';
import {
  Science,
  Biotech,
  Psychology,
  ExpandMore,
  Send,
  Clear,
  FileCopy,
  Download,
  Tune
} from '@mui/icons-material';
import { toast } from 'react-hot-toast';

interface TextGenerationProps {
  backendUrl: string;
  systemStatus: any;
}

const TextGenerationPanel: React.FC<TextGenerationProps> = ({ backendUrl, systemStatus }) => {
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [model, setModel] = useState('llama-3.1-405b');
  const [temperature, setTemperature] = useState(0.7);
  const [maxTokens, setMaxTokens] = useState(2000);
  const [requestType, setRequestType] = useState('educational_anatomy');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [streamMode, setStreamMode] = useState(false);
  const [cost, setCost] = useState(0);

  const educationalTemplates = [
    {
      name: 'Human Anatomy',
      prompt: 'Generate comprehensive educational content about human anatomy for medical students, including detailed anatomical structures and physiological processes.',
      category: 'anatomy'
    },
    {
      name: 'Reproductive System',
      prompt: 'Explain the human reproductive system anatomy and physiology for medical education, including both male and female reproductive organs and their functions.',
      category: 'anatomy'
    },
    {
      name: 'Cardiovascular System',
      prompt: 'Describe the cardiovascular system anatomy and physiology for medical students, including heart structure, blood vessels, and circulation.',
      category: 'physiology'
    },
    {
      name: 'Nervous System',
      prompt: 'Provide detailed educational content about the nervous system for medical training, including brain anatomy, spinal cord, and neural pathways.',
      category: 'neuroscience'
    }
  ];

  const availableModels = [
    { id: 'llama-3.1-405b', name: 'Llama 3.1 405B (OpenRouter)', cost: 0.0024 },
    { id: 'claude-3-opus', name: 'Claude 3 Opus (OpenRouter)', cost: 0.075 },
    { id: 'llama-3.1-70b', name: 'Llama 3.1 70B (OpenRouter)', cost: 0.0008 },
    { id: 'mixtral-8x7b', name: 'Mixtral 8x7B (OpenRouter)', cost: 0.0006 }
  ];

  const generateContent = async () => {
    if (!prompt.trim()) {
      toast.error('Please enter a prompt');
      return;
    }

    setLoading(true);
    setResponse('');
    setCost(0);

    try {
      const formData = new FormData();
      formData.append('prompt', prompt);
      formData.append('request_type', requestType);
      formData.append('model_preference', model);
      formData.append('max_tokens', maxTokens.toString());
      formData.append('temperature', temperature.toString());

      const response = await fetch(`${backendUrl}/api/v1/omnipotent/generate`, {
        method: 'POST',
        body: formData
      });

      const data = await response.json();

      if (data.status === 'success') {
        const content = data.content || data.response || '';
        setResponse(content);
        setCost(data.cost_estimate || 0);
        
        toast.success(`✅ Generated ${content.length} characters`);
        
        if (data.model_used) {
          toast.success(`Model: ${data.model_used}`, { duration: 2000 });
        }
      } else {
        throw new Error(data.error || 'Generation failed');
      }

    } catch (error) {
      console.error('Generation error:', error);
      toast.error(`❌ Generation failed: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  const loadTemplate = (template: any) => {
    setPrompt(template.prompt);
    toast.success(`Template loaded: ${template.name}`);
  };

  const clearAll = () => {
    setPrompt('');
    setResponse('');
    setCost(0);
  };

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(response);
      toast.success('Content copied to clipboard');
    } catch (error) {
      toast.error('Failed to copy content');
    }
  };

  const downloadContent = () => {
    const blob = new Blob([response], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `omnipotent-content-${Date.now()}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success('Content downloaded');
  };

  return (
    <Grid container spacing={3}>
      {/* Input Panel */}
      <Grid item xs={12} lg={6}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" mb={3}>
              <Science color="primary" sx={{ mr: 2 }} />
              <Typography variant="h5">
                🧠 Text Generation Console
              </Typography>
            </Box>

            {/* Educational Templates */}
            <Box mb={3}>
              <Typography variant="subtitle2" gutterBottom>
                📚 Educational Templates
              </Typography>
              <Box display="flex" gap={1} flexWrap="wrap" mb={2}>
                {educationalTemplates.map((template, index) => (
                  <Chip
                    key={index}
                    label={template.name}
                    size="small"
                    clickable
                    onClick={() => loadTemplate(template)}
                    color="primary"
                    variant="outlined"
                  />
                ))}
              </Box>
            </Box>

            {/* Main Input */}
            <TextField
              fullWidth
              multiline
              rows={6}
              variant="outlined"
              label="Enter your educational prompt..."
              placeholder={`Examples:
• Generate detailed anatomical explanation of human reproductive system
• Create comprehensive content about cardiovascular physiology
• Explain nervous system anatomy for medical students
• Provide educational content about human biology and physiology`}
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              sx={{ mb: 3 }}
            />

            {/* Model Selection */}
            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>AI Model</InputLabel>
                  <Select
                    value={model}
                    label="AI Model"
                    onChange={(e) => setModel(e.target.value)}
                  >
                    {availableModels.map((m) => (
                      <MenuItem key={m.id} value={m.id}>
                        {m.name} (${m.cost}/1K tokens)
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Request Type</InputLabel>
                  <Select
                    value={requestType}
                    label="Request Type"
                    onChange={(e) => setRequestType(e.target.value)}
                  >
                    <MenuItem value="educational_anatomy">🫁 Educational Anatomy</MenuItem>
                    <MenuItem value="medical_physiology">❤️ Medical Physiology</MenuItem>
                    <MenuItem value="scientific_research">🔬 Scientific Research</MenuItem>
                    <MenuItem value="clinical_education">🏥 Clinical Education</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>

            {/* Advanced Settings */}
            <Accordion expanded={showAdvanced} onChange={() => setShowAdvanced(!showAdvanced)}>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Box display="flex" alignItems="center">
                  <Tune sx={{ mr: 1 }} />
                  <Typography>Advanced Settings</Typography>
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <Typography gutterBottom>Temperature: {temperature}</Typography>
                    <Slider
                      value={temperature}
                      onChange={(_, value) => setTemperature(value as number)}
                      min={0.1}
                      max={1.0}
                      step={0.1}
                      marks
                      valueLabelDisplay="auto"
                    />
                  </Grid>
                  
                  <Grid item xs={12}>
                    <Typography gutterBottom>Max Tokens: {maxTokens}</Typography>
                    <Slider
                      value={maxTokens}
                      onChange={(_, value) => setMaxTokens(value as number)}
                      min={500}
                      max={4000}
                      step={100}
                      marks
                      valueLabelDisplay="auto"
                    />
                  </Grid>
                  
                  <Grid item xs={12}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={streamMode}
                          onChange={(e) => setStreamMode(e.target.checked)}
                        />
                      }
                      label="Stream Mode (Real-time generation)"
                    />
                  </Grid>
                </Grid>
              </AccordionDetails>
            </Accordion>

            {/* Action Buttons */}
            <Box display="flex" gap={2} mt={3}>
              <Button
                variant="contained"
                size="large"
                onClick={generateContent}
                disabled={loading || !prompt.trim()}
                startIcon={loading ? <CircularProgress size={20} /> : <Send />}
                sx={{ flexGrow: 1 }}
              >
                {loading ? 'Generating...' : 'Generate Content'}
              </Button>
              
              <Button
                variant="outlined"
                onClick={clearAll}
                startIcon={<Clear />}
              >
                Clear
              </Button>
            </Box>

            {/* Cost Estimate */}
            {cost > 0 && (
              <Alert severity="info" sx={{ mt: 2 }}>
                <Typography variant="body2">
                  Estimated cost: ${cost.toFixed(4)} | Model: {model}
                </Typography>
              </Alert>
            )}
          </CardContent>
        </Card>
      </Grid>

      {/* Output Panel */}
      <Grid item xs={12} lg={6}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" justifyContent="between" mb={2}>
              <Box display="flex" alignItems="center">
                <Psychology color="secondary" sx={{ mr: 2 }} />
                <Typography variant="h6">
                  📝 Generated Content
                </Typography>
              </Box>
              
              {response && (
                <Box display="flex" gap={1}>
                  <Button
                    size="small"
                    startIcon={<FileCopy />}
                    onClick={copyToClipboard}
                  >
                    Copy
                  </Button>
                  <Button
                    size="small"
                    startIcon={<Download />}
                    onClick={downloadContent}
                  >
                    Download
                  </Button>
                </Box>
              )}
            </Box>

            {loading && (
              <Box display="flex" flexDirection="column" alignItems="center" py={4}>
                <CircularProgress color="primary" sx={{ mb: 2 }} />
                <Typography variant="body2" color="text.secondary">
                  Generating unrestricted educational content...
                </Typography>
              </Box>
            )}

            {response ? (
              <Paper
                variant="outlined"
                sx={{
                  p: 2,
                  bgcolor: 'background.default',
                  minHeight: '400px',
                  maxHeight: '600px',
                  overflow: 'auto',
                  fontFamily: 'monospace'
                }}
              >
                <Typography
                  component="pre"
                  sx={{
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word',
                    fontSize: '0.9rem',
                    lineHeight: 1.6
                  }}
                >
                  {response}
                </Typography>
              </Paper>
            ) : !loading && (
              <Paper
                variant="outlined"
                sx={{
                  p: 4,
                  textAlign: 'center',
                  bgcolor: 'background.default',
                  minHeight: '400px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                <Box>
                  <Biotech sx={{ fontSize: 48, color: 'text.disabled', mb: 2 }} />
                  <Typography variant="h6" color="text.secondary" gutterBottom>
                    Ready for Content Generation
                  </Typography>
                  <Typography variant="body2" color="text.disabled">
                    Enter a prompt above to generate unrestricted educational content
                  </Typography>
                </Box>
              </Paper>
            )}
          </CardContent>
        </Card>
      </Grid>

      {/* System Status */}
      <Grid item xs={12}>
        <Alert 
          severity="success" 
          sx={{ 
            bgcolor: 'rgba(0, 255, 136, 0.1)',
            border: '1px solid #00ff88'
          }}
        >
          <Typography variant="body2">
            <strong>🔓 UNRESTRICTED MODE:</strong> This system can generate educational content without content restrictions for scientific and medical training purposes. 
            All content is optimized for legitimate educational use including anatomy, physiology, and clinical studies.
          </Typography>
        </Alert>
      </Grid>
    </Grid>
  );
};

export default TextGenerationPanel;