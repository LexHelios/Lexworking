import axios from 'axios';

// Get backend URL from environment variables
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

// Create axios instance with defaults
const api = axios.create({
  baseURL: BACKEND_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Request interceptor for adding auth tokens if needed
api.interceptors.request.use(
  (config) => {
    // Add authentication token if available
    const token = localStorage.getItem('lex_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized errors
      localStorage.removeItem('lex_token');
      // Could redirect to login if needed
    }
    return Promise.reject(error);
  }
);

// API endpoints
export const apiEndpoints = {
  // Health and status
  health: () => api.get('/health'),
  status: () => api.get('/api/v1/status'),

  // Performance metrics
  performance: () => api.get('/api/v1/performance'),
  
  // LEX AI endpoints
  chat: (data: { prompt: string; context?: any }) => 
    api.post('/api/v1/lex', data),
  
  streamChat: (data: { prompt: string; context?: any }) =>
    api.post('/api/v1/lex/stream', data, {
      responseType: 'stream'
    }),

  // File operations
  uploadFile: (file: FormData) => 
    api.post('/api/v1/files/upload', file, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }),

  // Memory and conversation
  getConversations: () => api.get('/api/v1/conversations'),
  getConversation: (id: string) => api.get(`/api/v1/conversations/${id}`),
  deleteConversation: (id: string) => api.delete(`/api/v1/conversations/${id}`),

  // Voice/Speech
  speechToText: (audioBlob: Blob) => {
    const formData = new FormData();
    formData.append('audio', audioBlob, 'speech.webm');
    return api.post('/api/v1/speech/transcribe', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  textToSpeech: (text: string, voice?: string) =>
    api.post('/api/v1/speech/synthesize', { text, voice }, {
      responseType: 'blob'
    }),

  // Settings
  getUserSettings: () => api.get('/api/v1/user/settings'),
  updateUserSettings: (settings: any) => api.put('/api/v1/user/settings', settings),
};

export default api;