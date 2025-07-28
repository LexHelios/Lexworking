import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { LEXResponse, MediaFile } from '../types/chat.types';

const API_BASE_URL = '/api/v1';

export const useLEX = () => {
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Check connection on mount
    checkConnection();
  }, []);

  const checkConnection = async () => {
    try {
      await axios.get(`${API_BASE_URL}/health`);
      setIsConnected(true);
    } catch (error) {
      setIsConnected(false);
    }
  };

  const sendMessage = useCallback(async (
    message: string,
    voiceMode: boolean = false
  ): Promise<LEXResponse> => {
    try {
      const response = await axios.post(`${API_BASE_URL}/lex`, {
        message,
        voice_mode: voiceMode,
        session_id: sessionStorage.getItem('lex_session_id') || undefined,
      });

      // Store session ID for continuity
      if (response.data.session_id) {
        sessionStorage.setItem('lex_session_id', response.data.session_id);
      }

      return response.data;
    } catch (error) {
      console.error('Error sending message to LEX:', error);
      throw error;
    }
  }, []);

  const sendMultimodalMessage = useCallback(async (
    message: string,
    files: MediaFile[],
    mediaType?: string
  ): Promise<LEXResponse> => {
    try {
      const formData = new FormData();
      formData.append('message', message);
      formData.append('voice_mode', 'false');
      
      if (mediaType) {
        formData.append('media_type', mediaType);
      }

      // Add files to form data
      files.forEach((mediaFile, index) => {
        formData.append('files', mediaFile.file);
      });

      const response = await axios.post(`${API_BASE_URL}/lex/multimodal`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 60000, // 60 second timeout for large files
      });

      return {
        ...response.data,
        session_id: response.data.session_id || Date.now().toString(),
      };
    } catch (error) {
      console.error('Error sending multimodal message to LEX:', error);
      throw error;
    }
  }, []);

  const sendVoiceMessage = useCallback(async (
    audioBlob: Blob
  ): Promise<LEXResponse> => {
    try {
      const formData = new FormData();
      formData.append('files', audioBlob, 'voice_recording.wav');
      formData.append('message', '');
      formData.append('media_type', 'voice_transcription');
      formData.append('voice_mode', 'true');

      const response = await axios.post(`${API_BASE_URL}/lex/multimodal`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      return {
        ...response.data,
        session_id: response.data.session_id || Date.now().toString(),
      };
    } catch (error) {
      console.error('Error sending voice message to LEX:', error);
      throw error;
    }
  }, []);

  return {
    isConnected,
    sendMessage,
    sendMultimodalMessage,
    sendVoiceMessage,
    checkConnection,
  };
};