import React, { useState, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Chip,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  CloudUpload,
  Delete,
  Visibility,
  FilePresent,
  Image,
  PictureAsPdf,
  Description,
  Code,
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'react-hot-toast';
import { apiEndpoints } from '../services/api';

interface FileUploadProps {
  isConnected: boolean;
  sendMessage: (message: string, options?: any) => void;
}

interface UploadedFile {
  id: string;
  name: string;
  size: number;
  type: string;
  uploadProgress: number;
  status: 'uploading' | 'completed' | 'error';
  url?: string;
  analysis?: string;
}

const FileUpload: React.FC<FileUploadProps> = ({ isConnected, sendMessage }) => {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [selectedFile, setSelectedFile] = useState<UploadedFile | null>(null);
  const [previewOpen, setPreviewOpen] = useState(false);

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      if (!isConnected) {
        toast.error('Please wait for connection before uploading files');
        return;
      }

      for (const file of acceptedFiles) {
        const fileId = `file_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        
        // Add file to state with uploading status
        const uploadFile: UploadedFile = {
          id: fileId,
          name: file.name,
          size: file.size,
          type: file.type,
          uploadProgress: 0,
          status: 'uploading',
        };

        setFiles(prev => [...prev, uploadFile]);

        try {
          // Create FormData for upload
          const formData = new FormData();
          formData.append('file', file);
          formData.append('file_id', fileId);

          // Simulate upload progress (in real implementation, you'd use XMLHttpRequest for progress)
          const progressInterval = setInterval(() => {
            setFiles(prev =>
              prev.map(f =>
                f.id === fileId
                  ? { ...f, uploadProgress: Math.min(f.uploadProgress + 10, 90) }
                  : f
              )
            );
          }, 200);

          // Upload file
          const response = await apiEndpoints.uploadFile(formData);
          
          clearInterval(progressInterval);

          // Update file status
          setFiles(prev =>
            prev.map(f =>
              f.id === fileId
                ? {
                    ...f,
                    uploadProgress: 100,
                    status: 'completed' as const,
                    url: response.data.file_url,
                    analysis: response.data.analysis,
                  }
                : f
            )
          );

          toast.success(`✅ ${file.name} uploaded successfully`);

          // Send file analysis request to LEX
          if (response.data.analysis) {
            const analysisMessage = `📎 File uploaded: ${file.name}\n\nLEX, please analyze this file and provide insights.`;
            sendMessage(analysisMessage, {
              file_context: {
                file_id: fileId,
                file_name: file.name,
                file_type: file.type,
                file_url: response.data.file_url,
                analysis: response.data.analysis,
              },
            });
          }

        } catch (error: any) {
          console.error('Upload error:', error);
          
          setFiles(prev =>
            prev.map(f =>
              f.id === fileId
                ? { ...f, status: 'error' as const, uploadProgress: 0 }
                : f
            )
          );

          toast.error(`❌ Failed to upload ${file.name}`);
        }
      }
    },
    [isConnected, sendMessage]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.webp'],
      'application/pdf': ['.pdf'],
      'text/*': ['.txt', '.md', '.json', '.csv'],
      'application/json': ['.json'],
      'text/csv': ['.csv'],
    },
    maxSize: 10 * 1024 * 1024, // 10MB max
  });

  const removeFile = (fileId: string) => {
    setFiles(prev => prev.filter(f => f.id !== fileId));
    toast.success('File removed');
  };

  const getFileIcon = (type: string) => {
    if (type.startsWith('image/')) return <Image color="primary" />;
    if (type === 'application/pdf') return <PictureAsPdf color="error" />;
    if (type.startsWith('text/') || type === 'application/json') return <Description color="info" />;
    return <FilePresent color="action" />;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'uploading': return 'primary';
      case 'error': return 'error';
      default: return 'default';
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const openPreview = (file: UploadedFile) => {
    setSelectedFile(file);
    setPreviewOpen(true);
  };

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      {/* Header */}
      <Typography variant="h4" component="h1" gutterBottom>
        📎 File Upload & Analysis
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Upload files for LEX to analyze and provide insights
      </Typography>

      {/* Connection Alert */}
      {!isConnected && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          File upload requires an active connection to LEX. Please wait for connection.
        </Alert>
      )}

      {/* Drop Zone */}
      <Paper
        {...getRootProps()}
        elevation={2}
        sx={{
          p: 4,
          mb: 3,
          textAlign: 'center',
          cursor: isConnected ? 'pointer' : 'not-allowed',
          border: isDragActive ? '2px dashed #6366f1' : '2px dashed #e2e8f0',
          bgcolor: isDragActive ? 'rgba(99, 102, 241, 0.05)' : 'background.paper',
          transition: 'all 0.3s ease',
          opacity: isConnected ? 1 : 0.6,
          '&:hover': isConnected ? {
            borderColor: '#6366f1',
            bgcolor: 'rgba(99, 102, 241, 0.05)',
          } : {},
        }}
      >
        <input {...getInputProps()} disabled={!isConnected} />
        
        <CloudUpload
          sx={{
            fontSize: 64,
            color: isDragActive ? 'primary.main' : 'text.secondary',
            mb: 2,
          }}
        />
        
        <Typography variant="h6" gutterBottom>
          {isDragActive
            ? '📎 Drop files here...'
            : '🔱 Drag & drop files or click to select'}
        </Typography>
        
        <Typography variant="body2" color="text.secondary" paragraph>
          Supported formats: Images (PNG, JPG, GIF), PDFs, Text files (TXT, MD, JSON, CSV)
        </Typography>
        
        <Typography variant="caption" color="text.secondary">
          Maximum file size: 10MB per file
        </Typography>
      </Paper>

      {/* Uploaded Files List */}
      {files.length > 0 && (
        <Paper elevation={2} sx={{ mb: 3 }}>
          <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
            <Typography variant="h6">
              📁 Uploaded Files ({files.length})
            </Typography>
          </Box>
          
          <List>
            <AnimatePresence>
              {files.map((file) => (
                <motion.div
                  key={file.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <ListItem>
                    <Box sx={{ mr: 2 }}>
                      {getFileIcon(file.type)}
                    </Box>
                    
                    <ListItemText
                      primary={file.name}
                      secondary={
                        <Box>
                          <Typography variant="caption" display="block">
                            {formatFileSize(file.size)} • {file.type}
                          </Typography>
                          
                          {file.status === 'uploading' && (
                            <Box sx={{ mt: 1 }}>
                              <LinearProgress
                                variant="determinate"
                                value={file.uploadProgress}
                                sx={{ height: 4, borderRadius: 2 }}
                              />
                              <Typography variant="caption" color="text.secondary">
                                Uploading... {file.uploadProgress}%
                              </Typography>
                            </Box>
                          )}
                          
                          {file.analysis && (
                            <Typography
                              variant="caption"
                              color="text.secondary"
                              sx={{ mt: 0.5, display: 'block' }}
                            >
                              📊 Analysis complete
                            </Typography>
                          )}
                        </Box>
                      }
                    />
                    
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mr: 1 }}>
                      <Chip
                        label={file.status}
                        size="small"
                        color={getStatusColor(file.status) as any}
                        variant="outlined"
                      />
                    </Box>
                    
                    <ListItemSecondaryAction>
                      <Box sx={{ display: 'flex' }}>
                        {file.status === 'completed' && (
                          <IconButton
                            edge="end"
                            onClick={() => openPreview(file)}
                            sx={{ mr: 1 }}
                          >
                            <Visibility />
                          </IconButton>
                        )}
                        
                        <IconButton
                          edge="end"
                          onClick={() => removeFile(file.id)}
                          color="error"
                        >
                          <Delete />
                        </IconButton>
                      </Box>
                    </ListItemSecondaryAction>
                  </ListItem>
                </motion.div>
              ))}
            </AnimatePresence>
          </List>
        </Paper>
      )}

      {/* Usage Guide */}
      <Paper elevation={1} sx={{ p: 3, bgcolor: 'background.paper' }}>
        <Typography variant="h6" gutterBottom>
          💡 How to Use File Upload
        </Typography>
        
        <Typography variant="body2" paragraph>
          1. <strong>Upload Files:</strong> Drag and drop or click to select files for analysis
        </Typography>
        
        <Typography variant="body2" paragraph>
          2. <strong>Automatic Analysis:</strong> LEX will automatically analyze uploaded files
        </Typography>
        
        <Typography variant="body2" paragraph>
          3. <strong>Ask Questions:</strong> Reference uploaded files in your conversations with LEX
        </Typography>
        
        <Typography variant="body2">
          4. <strong>File Types:</strong> Images for visual analysis, PDFs for document parsing, 
          text files for content analysis
        </Typography>
      </Paper>

      {/* File Preview Dialog */}
      <Dialog
        open={previewOpen}
        onClose={() => setPreviewOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          File Details: {selectedFile?.name}
        </DialogTitle>
        
        <DialogContent>
          {selectedFile && (
            <Box>
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  Size: {formatFileSize(selectedFile.size)} • 
                  Type: {selectedFile.type}
                </Typography>
              </Box>
              
              {selectedFile.analysis && (
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    📊 Analysis Results:
                  </Typography>
                  <Paper elevation={1} sx={{ p: 2, bgcolor: 'grey.50' }}>
                    <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                      {selectedFile.analysis}
                    </Typography>
                  </Paper>
                </Box>
              )}
            </Box>
          )}
        </DialogContent>
        
        <DialogActions>
          <Button onClick={() => setPreviewOpen(false)}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default FileUpload;