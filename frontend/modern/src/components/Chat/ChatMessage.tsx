import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Chip,
  IconButton,
  Collapse,
  Avatar,
  Card,
  CardMedia,
  CardContent,
  Button,
} from '@mui/material';
import {
  ExpandMore,
  ExpandLess,
  PlayArrow,
  Pause,
  Download,
  Code,
  SmartToy,
  Person,
} from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import remarkGfm from 'remark-gfm';
import { Message } from '../../types/chat.types';

interface ChatMessageProps {
  message: Message;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const [showDetails, setShowDetails] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [expandedMedia, setExpandedMedia] = useState<string | null>(null);

  const isUser = message.sender === 'user';
  const isError = message.isError;

  const handlePlayAudio = (audioUrl: string) => {
    const audio = new Audio(audioUrl);
    audio.play();
    setIsPlaying(true);
    audio.onended = () => setIsPlaying(false);
  };

  const handleDownloadFile = (url: string, filename: string) => {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const renderMediaContent = () => {
    if (!message.mediaContent) return null;

    return (
      <Box sx={{ mt: 2 }}>
        {/* Generated Images */}
        {message.mediaContent.images && message.mediaContent.images.length > 0 && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Generated Images:
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              {message.mediaContent.images.map((image: any, index: number) => (
                <Card key={index} sx={{ maxWidth: 300 }}>
                  <CardMedia
                    component="img"
                    height="200"
                    image={image.url || `data:image/png;base64,${image.data}`}
                    alt={image.description || `Generated image ${index + 1}`}
                    sx={{ cursor: 'pointer' }}
                    onClick={() => setExpandedMedia(expandedMedia === `img-${index}` ? null : `img-${index}`)}
                  />
                  {image.description && (
                    <CardContent sx={{ p: 1 }}>
                      <Typography variant="caption">
                        {image.description}
                      </Typography>
                    </CardContent>
                  )}
                </Card>
              ))}
            </Box>
          </Box>
        )}

        {/* Generated Videos */}
        {message.mediaContent.videos && message.mediaContent.videos.length > 0 && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Generated Videos:
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              {message.mediaContent.videos.map((video: any, index: number) => (
                <Card key={index} sx={{ maxWidth: 400 }}>
                  <video
                    controls
                    width="100%"
                    height="200"
                    src={video.url || `data:video/mp4;base64,${video.data}`}
                  >
                    Your browser does not support the video tag.
                  </video>
                  {video.description && (
                    <CardContent sx={{ p: 1 }}>
                      <Typography variant="caption">
                        {video.description}
                      </Typography>
                    </CardContent>
                  )}
                </Card>
              ))}
            </Box>
          </Box>
        )}

        {/* Generated Audio */}
        {message.mediaContent.audio && message.mediaContent.audio.length > 0 && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Generated Audio:
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              {message.mediaContent.audio.map((audio: any, index: number) => (
                <Paper key={index} sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                  <IconButton
                    onClick={() => handlePlayAudio(audio.url || `data:audio/wav;base64,${audio.data}`)}
                    disabled={isPlaying}
                  >
                    {isPlaying ? <Pause /> : <PlayArrow />}
                  </IconButton>
                  <Typography variant="body2">
                    {audio.description || `Audio ${index + 1}`}
                  </Typography>
                  <IconButton
                    size="small"
                    onClick={() => handleDownloadFile(
                      audio.url || `data:audio/wav;base64,${audio.data}`,
                      `audio_${index + 1}.wav`
                    )}
                  >
                    <Download />
                  </IconButton>
                </Paper>
              ))}
            </Box>
          </Box>
        )}

        {/* Generated Code */}
        {message.mediaContent.code && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Generated Code:
            </Typography>
            <SyntaxHighlighter
              language={message.mediaContent.code.language || 'javascript'}
              style={vscDarkPlus}
              customStyle={{
                borderRadius: '8px',
                fontSize: '14px',
              }}
            >
              {message.mediaContent.code.content}
            </SyntaxHighlighter>
          </Box>
        )}
      </Box>
    );
  };

  const renderUploadedFiles = () => {
    if (!message.mediaFiles || message.mediaFiles.length === 0) return null;

    return (
      <Box sx={{ mt: 1, mb: 1 }}>
        <Typography variant="caption" color="text.secondary" gutterBottom>
          Attached Files:
        </Typography>
        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mt: 0.5 }}>
          {message.mediaFiles.map((file) => (
            <Paper key={file.id} sx={{ p: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
              {file.preview && (
                <img
                  src={file.preview}
                  alt={file.name}
                  style={{ width: 40, height: 40, objectFit: 'cover', borderRadius: 4 }}
                />
              )}
              <Box>
                <Typography variant="caption" display="block">
                  {file.name}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {(file.size / 1024 / 1024).toFixed(1)}MB
                </Typography>
              </Box>
            </Paper>
          ))}
        </Box>
      </Box>
    );
  };

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        mb: 2,
        alignItems: 'flex-start',
        gap: 1,
      }}
      role="log"
      aria-live="polite"
    >
      {/* Avatar */}
      {!isUser && (
        <Avatar sx={{ bgcolor: 'primary.main', width: 32, height: 32 }}>
          <SmartToy fontSize="small" />
        </Avatar>
      )}

      <Paper
        elevation={isError ? 0 : 1}
        sx={{
          p: 2,
          maxWidth: '70%',
          minWidth: '200px',
          backgroundColor: isError 
            ? 'error.dark' 
            : isUser 
              ? 'primary.main' 
              : 'background.paper',
          color: isError
            ? 'error.contrastText'
            : isUser 
              ? 'primary.contrastText' 
              : 'text.primary',
          border: isError ? '1px solid' : 'none',
          borderColor: isError ? 'error.main' : 'transparent',
        }}
        role="article"
        aria-label={`Message from ${isUser ? 'you' : 'LEX'}`}
      >
        {/* Message Header */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <Typography variant="caption" sx={{ fontWeight: 600 }}>
            {isUser ? 'You' : '🔱 LEX'}
          </Typography>
          <Typography variant="caption" sx={{ opacity: 0.7 }}>
            {new Date(message.timestamp).toLocaleTimeString()}
          </Typography>
        </Box>

        {/* Uploaded Files */}
        {renderUploadedFiles()}

        {/* Message Content */}
        <Box component="div">
          {message.content.includes('```') || message.content.includes('**') ? (
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                code({ node, inline, className, children, ...props }) {
                  const match = /language-(\w+)/.exec(className || '');
                  return !inline && match ? (
                    <SyntaxHighlighter
                      style={vscDarkPlus}
                      language={match[1]}
                      PreTag="div"
                      customStyle={{
                        borderRadius: '4px',
                        fontSize: '13px',
                        margin: '8px 0',
                      }}
                      {...props}
                    >
                      {String(children).replace(/\n$/, '')}
                    </SyntaxHighlighter>
                  ) : (
                    <code className={className} {...props}>
                      {children}
                    </code>
                  );
                },
              }}
            >
              {message.content}
            </ReactMarkdown>
          ) : (
            <Typography variant="body1" component="div" sx={{ whiteSpace: 'pre-wrap' }}>
              {message.content}
            </Typography>
          )}
        </Box>

        {/* Media Content */}
        {renderMediaContent()}

        {/* Message Metadata */}
        {message.metadata && !isUser && (
          <Box sx={{ mt: 2 }}>
            <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mb: 1 }}>
              {message.metadata.capabilities?.map((capability) => (
                <Chip
                  key={capability}
                  label={capability}
                  size="small"
                  variant="outlined"
                  sx={{ 
                    fontSize: '0.7rem',
                    height: '20px',
                    color: isUser ? 'primary.contrastText' : 'text.secondary',
                    borderColor: isUser ? 'primary.contrastText' : 'text.secondary',
                  }}
                />
              ))}
            </Box>

            {/* Expandable Details */}
            <Box>
              <Button
                size="small"
                onClick={() => setShowDetails(!showDetails)}
                endIcon={showDetails ? <ExpandLess /> : <ExpandMore />}
                sx={{ 
                  color: isUser ? 'primary.contrastText' : 'text.secondary',
                  fontSize: '0.7rem',
                  p: 0,
                  minWidth: 'auto',
                }}
              >
                Details
              </Button>
              
              <Collapse in={showDetails}>
                <Box sx={{ mt: 1, p: 1, bgcolor: 'rgba(0,0,0,0.1)', borderRadius: 1 }}>
                  <Typography variant="caption" display="block">
                    Action: {message.metadata.actionTaken}
                  </Typography>
                  <Typography variant="caption" display="block">
                    Confidence: {(message.metadata.confidence * 100).toFixed(1)}%
                  </Typography>
                  {message.metadata.processingTime && (
                    <Typography variant="caption" display="block">
                      Processing Time: {message.metadata.processingTime.toFixed(2)}s
                    </Typography>
                  )}
                </Box>
              </Collapse>
            </Box>
          </Box>
        )}
      </Paper>

      {/* User Avatar */}
      {isUser && (
        <Avatar sx={{ bgcolor: 'secondary.main', width: 32, height: 32 }}>
          <Person fontSize="small" />
        </Avatar>
      )}
    </Box>
  );
};