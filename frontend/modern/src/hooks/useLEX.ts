import { useState, useCallback } from 'react';
import { toast } from 'react-hot-toast';
import { apiEndpoints } from '../services/api';

interface LEXResponse {
  response: string;
  model_used?: string;
  confidence?: number;
  cache_hit?: boolean;
  performance_score?: number;
  metadata?: any;
}

interface UseLEXOptions {
  autoErrorToast?: boolean;
  defaultContext?: any;
}

interface UseLEXReturn {
  sendMessage: (prompt: string, context?: any) => Promise<LEXResponse | null>;
  isLoading: boolean;
  error: string | null;
  lastResponse: LEXResponse | null;
  clearError: () => void;
}

export const useLEX = (options: UseLEXOptions = {}): UseLEXReturn => {
  const { autoErrorToast = true, defaultContext = {} } = options;
  
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastResponse, setLastResponse] = useState<LEXResponse | null>(null);

  const sendMessage = useCallback(async (
    prompt: string, 
    context: any = {}
  ): Promise<LEXResponse | null> => {
    if (!prompt.trim()) {
      const errorMsg = 'Prompt cannot be empty';
      setError(errorMsg);
      if (autoErrorToast) {
        toast.error(errorMsg);
      }
      return null;
    }

    setIsLoading(true);
    setError(null);

    try {
      const requestData = {
        prompt: prompt.trim(),
        context: {
          ...defaultContext,
          ...context,
          timestamp: Date.now(),
        },
      };

      const response = await apiEndpoints.chat(requestData);
      
      if (response.data) {
        setLastResponse(response.data);
        return response.data;
      } else {
        throw new Error('No response data received');
      }

    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 
                          err.response?.data?.message || 
                          err.message || 
                          'Failed to get response from LEX';
      
      setError(errorMessage);
      setLastResponse(null);
      
      if (autoErrorToast) {
        toast.error(`❌ ${errorMessage}`);
      }
      
      console.error('LEX API Error:', err);
      return null;

    } finally {
      setIsLoading(false);
    }
  }, [autoErrorToast, defaultContext]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    sendMessage,
    isLoading,
    error,
    lastResponse,
    clearError,
  };
};

export default useLEX;