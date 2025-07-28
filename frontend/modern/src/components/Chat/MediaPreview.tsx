import React from 'react';
import {
  Box,
  Paper,
  Typography,
  IconButton,
  Card,
  CardMedia,
  CardContent,
  Chip,
} from '@mui/material';
import {
  Close,
  Image as ImageIcon,
  VideoFile,
  AudioFile,
  Description,
  Visibility,
} from '@mui/icons-material';
import { MediaFile } from '../../types/chat.types';

interface MediaPreviewProps {
  files: MediaFile[];
  onRemoveFile: (fileId: string) => void;
  onClose: () => void;
}

export const MediaPreview: React.FC<MediaPreviewProps> = ({
  files,
  onRemoveFile,
  onClose,
}) => {
  const getFileIcon = (type: string) => {
    if (type.startsWith('image/')) return <ImageIcon />;
    if (type.startsWith('video/')) return <VideoFile />;
    if (type.startsWith('audio/')) return <AudioFile />;
    return <Description />;
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <Paper elevation={2} sx={{ p: 2, mb: 1, backgroundColor: 'background.paper' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="subtitle2" color="text.secondary">
          Attached Files ({files.length})
        </Typography>
        <IconButton size="small" onClick={onClose}>
          <Close />
        </IconButton>
      </Box>

      <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', maxHeight: 200, overflow: 'auto' }}>
        {files.map((file) => (
          <Card key={file.id} sx={{ width: 200, position: 'relative' }}>
            {/* Remove button */}
            <IconButton
              size="small"
              onClick={() => onRemoveFile(file.id)}
              sx={{
                position: 'absolute',
                top: 4,
                right: 4,
                backgroundColor: 'rgba(0,0,0,0.7)',
                color: 'white',
                zIndex: 1,
                '&:hover': {
                  backgroundColor: 'rgba(0,0,0,0.9)',
                },
              }}
            >
              <Close fontSize="small" />
            </IconButton>

            {/* File preview */}
            {file.type.startsWith('image/') && file.preview ? (
              <CardMedia
                component="img"
                height="120"
                image={file.preview}
                alt={file.name}
                sx={{ objectFit: 'cover' }}
              />
            ) : file.type.startsWith('video/') ? (
              <Box
                sx={{
                  height: 120,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  backgroundColor: 'grey.800',
                }}
              >
                <VideoFile sx={{ fontSize: 40, color: 'grey.400' }} />
              </Box>
            ) : file.type.startsWith('audio/') ? (
              <Box
                sx={{
                  height: 120,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  backgroundColor: 'grey.800',
                }}
              >
                <AudioFile sx={{ fontSize: 40, color: 'grey.400' }} />
              </Box>
            ) : (
              <Box
                sx={{
                  height: 120,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  backgroundColor: 'grey.800',
                }}
              >
                <Description sx={{ fontSize: 40, color: 'grey.400' }} />
              </Box>
            )}

            {/* File info */}
            <CardContent sx={{ p: 1 }}>
              <Typography variant="caption" display="block" noWrap title={file.name}>
                {file.name}
              </Typography>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 0.5 }}>
                <Chip
                  icon={getFileIcon(file.type)}
                  label={file.type.split('/')[1]?.toUpperCase() || 'FILE'}
                  size="small"
                  variant="outlined"
                  sx={{ fontSize: '0.6rem', height: 20 }}
                />
                <Typography variant="caption" color="text.secondary">
                  {formatFileSize(file.size)}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        ))}
      </Box>
    </Paper>
  );
};