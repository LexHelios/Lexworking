
/**
 * Production API Service for LexOS Mobile
 * Optimized for H100 backend communication
 */
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-netinfo/netinfo';
import { ProductionConfig } from '../config/production';

export interface ApiResponse<T = any> {
  data: T;
  success: boolean;
  message?: string;
  error?: string;
}

export interface StreamResponse {
  id: string;
  content: string;
  finished: boolean;
  metadata?: any;
}

class ApiService {
  private client: AxiosInstance;
  private wsConnection: WebSocket | null = null;
  private requestQueue: Array<() => Promise<any>> = [];
  private isOnline: boolean = true;
  private authToken: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: ProductionConfig.api.baseUrl,
      timeout: ProductionConfig.api.timeout,
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'LexOS-Mobile/2.0.0',
        'X-Client-Version': '2.0.0',
        'X-Platform': 'mobile',
      },
    });

    this.setupInterceptors();
    this.setupNetworkMonitoring();
    this.loadAuthToken();
  }

  private setupInterceptors(): void {
    // Request interceptor
    this.client.interceptors.request.use(
      async (config) => {
        // Add auth token
        if (this.authToken) {
          config.headers.Authorization = `Bearer ${this.authToken}`;
        }

        // Add request ID for tracing
        config.headers['X-Request-ID'] = this.generateRequestId();

        // Add device info
        config.headers['X-Device-Info'] = await this.getDeviceInfo();

        return config;
      },
      (error) => {
        console.error('Request interceptor error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        return response;
      },
      async (error) => {
        const originalRequest = error.config;

        // Handle 401 errors (token refresh)
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          
          try {
            await this.refreshToken();
            return this.client(originalRequest);
          } catch (refreshError) {
            await this.logout();
            throw refreshError;
          }
        }

        // Handle network errors with retry
        if (!error.response && originalRequest._retryCount < ProductionConfig.api.retryAttempts) {
          originalRequest._retryCount = (originalRequest._retryCount || 0) + 1;
          
          await this.delay(ProductionConfig.api.retryDelay * originalRequest._retryCount);
          return this.client(originalRequest);
        }

        return Promise.reject(error);
      }
    );
  }

  private setupNetworkMonitoring(): void {
    NetInfo.addEventListener((state) => {
      const wasOnline = this.isOnline;
      this.isOnline = state.isConnected ?? false;

      if (!wasOnline && this.isOnline) {
        // Back online - process queued requests
        this.processRequestQueue();
      }
    });
  }

  private async loadAuthToken(): Promise<void> {
    try {
      this.authToken = await AsyncStorage.getItem(ProductionConfig.auth.tokenStorageKey);
    } catch (error) {
      console.error('Failed to load auth token:', error);
    }
  }

  private generateRequestId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  private async getDeviceInfo(): Promise<string> {
    // Return basic device info for backend optimization
    return JSON.stringify({
      platform: 'mobile',
      version: '2.0.0',
      timestamp: Date.now(),
    });
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  private async processRequestQueue(): Promise<void> {
    while (this.requestQueue.length > 0 && this.isOnline) {
      const request = this.requestQueue.shift();
      if (request) {
        try {
          await request();
        } catch (error) {
          console.error('Queued request failed:', error);
        }
      }
    }
  }

  // Authentication methods
  async login(credentials: { email: string; password: string }): Promise<ApiResponse<{ token: string; refreshToken: string; user: any }>> {
    try {
      const response = await this.client.post('/auth/login', credentials);
      
      if (response.data.success) {
        this.authToken = response.data.data.token;
        await AsyncStorage.setItem(ProductionConfig.auth.tokenStorageKey, this.authToken);
        await AsyncStorage.setItem(ProductionConfig.auth.refreshTokenKey, response.data.data.refreshToken);
      }

      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async refreshToken(): Promise<void> {
    try {
      const refreshToken = await AsyncStorage.getItem(ProductionConfig.auth.refreshTokenKey);
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }

      const response = await this.client.post('/auth/refresh', { refreshToken });
      
      if (response.data.success) {
        this.authToken = response.data.data.token;
        await AsyncStorage.setItem(ProductionConfig.auth.tokenStorageKey, this.authToken);
      }
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async logout(): Promise<void> {
    try {
      if (this.authToken) {
        await this.client.post('/auth/logout');
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      this.authToken = null;
      await AsyncStorage.removeItem(ProductionConfig.auth.tokenStorageKey);
      await AsyncStorage.removeItem(ProductionConfig.auth.refreshTokenKey);
      this.disconnectWebSocket();
    }
  }

  // AI Chat methods
  async sendMessage(message: string, conversationId?: string): Promise<ApiResponse<{ response: string; conversationId: string }>> {
    try {
      const response = await this.client.post('/ai/chat', {
        message,
        conversationId,
        stream: false,
        maxTokens: ProductionConfig.ai.maxContextLength,
      });

      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Streaming chat
  async streamMessage(
    message: string,
    onChunk: (chunk: StreamResponse) => void,
    conversationId?: string
  ): Promise<void> {
    return new Promise((resolve, reject) => {
      if (!this.isOnline) {
        reject(new Error('No internet connection'));
        return;
      }

      const ws = new WebSocket(ProductionConfig.api.wsUrl);
      
      ws.onopen = () => {
        ws.send(JSON.stringify({
          type: 'chat',
          message,
          conversationId,
          maxTokens: ProductionConfig.ai.maxContextLength,
        }));
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          onChunk(data);
          
          if (data.finished) {
            ws.close();
            resolve();
          }
        } catch (error) {
          reject(error);
        }
      };

      ws.onerror = (error) => {
        reject(error);
      };

      ws.onclose = () => {
        resolve();
      };
    });
  }

  // Image analysis
  async analyzeImage(imageUri: string, prompt?: string): Promise<ApiResponse<{ analysis: string; metadata: any }>> {
    try {
      const formData = new FormData();
      formData.append('image', {
        uri: imageUri,
        type: 'image/jpeg',
        name: 'image.jpg',
      } as any);
      
      if (prompt) {
        formData.append('prompt', prompt);
      }

      const response = await this.client.post('/ai/vision', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 60000, // Longer timeout for image processing
      });

      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Voice processing
  async processVoice(audioUri: string): Promise<ApiResponse<{ transcript: string; response: string }>> {
    try {
      const formData = new FormData();
      formData.append('audio', {
        uri: audioUri,
        type: 'audio/m4a',
        name: 'audio.m4a',
      } as any);

      const response = await this.client.post('/ai/voice', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 60000, // Longer timeout for voice processing
      });

      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Document processing
  async processDocument(documentUri: string): Promise<ApiResponse<{ content: string; summary: string; metadata: any }>> {
    try {
      const formData = new FormData();
      formData.append('document', {
        uri: documentUri,
        type: 'application/pdf',
        name: 'document.pdf',
      } as any);

      const response = await this.client.post('/ai/document', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 120000, // Longer timeout for document processing
      });

      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Health check
  async healthCheck(): Promise<ApiResponse<{ status: string; version: string; uptime: number }>> {
    try {
      const response = await this.client.get('/health');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // WebSocket connection management
  connectWebSocket(): void {
    if (this.wsConnection?.readyState === WebSocket.OPEN) {
      return;
    }

    this.wsConnection = new WebSocket(ProductionConfig.api.wsUrl);
    
    this.wsConnection.onopen = () => {
      console.log('WebSocket connected');
      
      // Send auth token
      if (this.authToken) {
        this.wsConnection?.send(JSON.stringify({
          type: 'auth',
          token: this.authToken,
        }));
      }
    };

    this.wsConnection.onclose = () => {
      console.log('WebSocket disconnected');
      
      // Reconnect after delay if online
      if (this.isOnline) {
        setTimeout(() => this.connectWebSocket(), 5000);
      }
    };

    this.wsConnection.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  disconnectWebSocket(): void {
    if (this.wsConnection) {
      this.wsConnection.close();
      this.wsConnection = null;
    }
  }

  private handleError(error: any): Error {
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.message || error.response.data?.error || 'Server error';
      return new Error(message);
    } else if (error.request) {
      // Network error
      return new Error('Network error - please check your connection');
    } else {
      // Other error
      return new Error(error.message || 'Unknown error occurred');
    }
  }
}

export const apiService = new ApiService();
export default apiService;
