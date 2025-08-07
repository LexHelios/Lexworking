import React, { useState } from 'react';
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
  Paper,
  CircularProgress,
  Alert,
  ImageList,
  ImageListItem,
  ImageListItemBar,
  IconButton,
  Dialog,
  DialogContent,
  DialogTitle
} from '@mui/material';
import {
  Image,
  Biotech,
  Send,
  Clear,
  Download,
  Fullscreen,
  Close
} from '@mui/icons-material';
import { toast } from 'react-hot-toast';

interface ImageGenerationProps {
  backendUrl: string;
  systemStatus: any;
}

const ImageGenerationPanel: React.FC<ImageGenerationProps> = ({ backendUrl, systemStatus }) => {
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [generatedImages, setGeneratedImages] = useState<any[]>([]);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [model, setModel] = useState('flux-dev-uncensored');
  const [style, setStyle] = useState('medical_textbook');
  const [safetyLevel, setSafetyLevel] = useState('unrestricted');

  const imageTemplates = [
    {
      name: 'Human Anatomy Diagram',
      prompt: 'Detailed medical textbook illustration of human internal anatomy showing organs and systems for educational purposes',
      category: 'anatomy'
    },
    {
      name: 'Reproductive System',
      prompt: 'Educational anatomical diagram of human reproductive system with labeled structures for medical training',
      category: 'anatomy'
    },
    {
      name: 'Cardiovascular System',
      prompt: 'Medical illustration showing heart anatomy and blood circulation for educational textbook',
      category: 'physiology'
    },
    {
      name: 'Skeletal System',
      prompt: 'Detailed anatomical drawing of human skeleton and bone structure for medical education',
      category: 'anatomy'
    }
  ];

  const availableModels = [
    { id: 'flux-dev-uncensored', name: 'FLUX Dev (Unrestricted)', cost: 0.025 },
    { id: 'flux-pro-uncensored', name: 'FLUX Pro (Unrestricted)', cost: 0.05 },
    { id: 'stable-diffusion-xl-uncensored', name: 'SDXL (Unrestricted)', cost: 0.02 },
    { id: 'playground-v2.5', name: 'Playground v2.5', cost: 0.03 }
  ];

  const imageStyles = [
    { id: 'medical_textbook', name: '📖 Medical Textbook', description: 'Professional medical illustration style' },
    { id: 'anatomy_chart', name: '📊 Anatomy Chart', description: 'Detailed anatomical chart format' },
    { id: 'scientific_diagram', name: '🔬 Scientific Diagram', description: 'Technical scientific illustration' },
    { id: 'clinical_reference', name: '🏥 Clinical Reference', description: 'Clinical reference material style' },
    { id: 'anatomical_drawing', name: '✏️ Anatomical Drawing', description: 'Hand-drawn anatomical style' }
  ];

  const generateImage = async () => {
    if (!prompt.trim()) {
      toast.error('Please enter a prompt');
      return;
    }

    setLoading(true);

    try {
      const formData = new FormData();
      formData.append('prompt', prompt);
      formData.append('style', style);
      formData.append('model', model);
      formData.append('safety_level', safetyLevel);
      formData.append('resolution', '1024x1024');

      const response = await fetch(`${backendUrl}/api/v1/omnipotent/image`, {
        method: 'POST',
        body: formData
      });

      const data = await response.json();

      if (data.status === 'success') {
        const newImage = {
          id: Date.now(),
          url: data.image_url,
          prompt: prompt,
          model: data.model_used,
          style: style,
          cost: data.cost_estimate || 0,
          timestamp: new Date()
        };
        
        setGeneratedImages(prev => [newImage, ...prev]);
        toast.success('✅ Image generated successfully!');
        
      } else {
        throw new Error(data.error || 'Image generation failed');
      }

    } catch (error) {
      console.error('Image generation error:', error);
      toast.error(`❌ Image generation failed: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  const useTemplate = (template: any) => {
    setPrompt(template.prompt);
    toast.success(`Template loaded: ${template.name}`);
  };

  const downloadImage = async (imageUrl: string, filename: string) => {
    try {
      const response = await fetch(imageUrl);
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      toast.success('Image downloaded');
    } catch (error) {
      toast.error('Failed to download image');
    }
  };

  const clearAll = () => {
    setPrompt('');
    setGeneratedImages([]);
  };

  return (
    <Grid container spacing={3}>
      {/* Input Panel */}
      <Grid item xs={12} lg={5}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" mb={3}>
              <Image color="primary" sx={{ mr: 2 }} />
              <Typography variant="h5">
                🎨 Image Generation Studio
              </Typography>
            </Box>

            {/* Educational Templates */}
            <Box mb={3}>
              <Typography variant="subtitle2" gutterBottom>
                🖼️ Medical Templates
              </Typography>
              <Box display="flex" gap={1} flexWrap="wrap" mb={2}>
                {imageTemplates.map((template, index) => (
                  <Chip
                    key={index}
                    label={template.name}
                    size="small"
                    clickable
                    onClick={() => useTemplate(template)}
                    color="secondary"
                    variant="outlined"
                  />
                ))}
              </Box>
            </Box>

            {/* Main Input */}
            <TextField
              fullWidth
              multiline
              rows={4}
              variant="outlined"
              label="Describe your medical illustration..."
              placeholder="Examples:
• Medical textbook illustration of human anatomy
• Anatomical diagram showing organ systems
• Educational chart of physiological processes
• Clinical reference illustration for medical training"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              sx={{ mb: 3 }}
            />

            {/* Configuration */}
            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>AI Model</InputLabel>
                  <Select
                    value={model}
                    label="AI Model"
                    onChange={(e) => setModel(e.target.value)}
                  >
                    {availableModels.map((m) => (
                      <MenuItem key={m.id} value={m.id}>
                        {m.name} (${m.cost}/image)
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Style</InputLabel>
                  <Select
                    value={style}
                    label="Style"
                    onChange={(e) => setStyle(e.target.value)}
                  >
                    {imageStyles.map((s) => (
                      <MenuItem key={s.id} value={s.id}>
                        {s.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12} md={6}>
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

            {/* Action Buttons */}
            <Box display="flex" gap={2}>
              <Button
                variant="contained"
                size="large"
                onClick={generateImage}
                disabled={loading || !prompt.trim()}
                startIcon={loading ? <CircularProgress size={20} /> : <Send />}
                sx={{ flexGrow: 1 }}
              >
                {loading ? 'Generating...' : 'Generate Image'}
              </Button>
              
              <Button
                variant="outlined"
                onClick={clearAll}
                startIcon={<Clear />}
              >
                Clear
              </Button>
            </Box>

            {loading && (
              <Box mt={3} textAlign="center">
                <CircularProgress color="primary" sx={{ mb: 2 }} />
                <Typography variant="body2" color="text.secondary">
                  Generating unrestricted medical illustration...
                </Typography>
                <Typography variant="caption" color="text.disabled">
                  This may take 30-60 seconds
                </Typography>
              </Box>
            )}
          </CardContent>
        </Card>
      </Grid>

      {/* Generated Images */}
      <Grid item xs={12} lg={7}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" mb={3}>
              <Biotech color="secondary" sx={{ mr: 2 }} />
              <Typography variant="h6">
                🖼️ Generated Medical Illustrations
              </Typography>
              <Chip 
                label={`${generatedImages.length} images`} 
                size="small" 
                sx={{ ml: 2 }} 
              />
            </Box>

            {generatedImages.length > 0 ? (
              <ImageList variant="masonry" cols={2} gap={16}>
                {generatedImages.map((image) => (
                  <ImageListItem key={image.id}>
                    <img
                      src={image.url}
                      alt={image.prompt}
                      loading="lazy"
                      style={{ 
                        cursor: 'pointer',
                        borderRadius: '8px',
                        border: '1px solid #00ff8820'
                      }}
                      onClick={() => setSelectedImage(image.url)}
                    />
                    <ImageListItemBar
                      title={image.prompt.slice(0, 50) + '...'}
                      subtitle={
                        <Box>
                          <Typography variant="caption" display="block">
                            {image.model} • ${image.cost.toFixed(3)}
                          </Typography>
                          <Typography variant="caption" color="text.disabled">
                            {image.timestamp.toLocaleTimeString()}
                          </Typography>
                        </Box>
                      }
                      actionIcon={
                        <Box>
                          <IconButton
                            sx={{ color: 'rgba(255, 255, 255, 0.54)' }}
                            onClick={() => setSelectedImage(image.url)}
                          >
                            <Fullscreen />
                          </IconButton>
                          <IconButton
                            sx={{ color: 'rgba(255, 255, 255, 0.54)' }}
                            onClick={() => downloadImage(image.url, `medical-${image.id}.jpg`)}
                          >
                            <Download />
                          </IconButton>
                        </Box>
                      }
                    />
                  </ImageListItem>
                ))}
              </ImageList>
            ) : (
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
                  <Image sx={{ fontSize: 48, color: 'text.disabled', mb: 2 }} />
                  <Typography variant="h6" color="text.secondary" gutterBottom>
                    No Images Generated Yet
                  </Typography>
                  <Typography variant="body2" color="text.disabled">
                    Create your first unrestricted medical illustration above
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
          severity="warning" 
          sx={{ 
            bgcolor: 'rgba(255, 167, 38, 0.1)',
            border: '1px solid #ffa726'
          }}
        >
          <Typography variant="body2">
            <strong>🔓 UNRESTRICTED IMAGING:</strong> This system can generate medical images without content restrictions for educational purposes. 
            All images are created for legitimate scientific, medical, and educational use including anatomical diagrams and clinical illustrations.
          </Typography>
        </Alert>
      </Grid>

      {/* Image Preview Dialog */}
      <Dialog
        open={Boolean(selectedImage)}
        onClose={() => setSelectedImage(null)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center" justifyContent="between">
            <Typography variant="h6">Image Preview</Typography>
            <IconButton onClick={() => setSelectedImage(null)}>
              <Close />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          {selectedImage && (
            <img
              src={selectedImage}
              alt="Generated medical illustration"
              style={{ 
                width: '100%', 
                height: 'auto',
                borderRadius: '8px'
              }}
            />
          )}
        </DialogContent>
      </Dialog>
    </Grid>
  );
};

export default ImageGenerationPanel;