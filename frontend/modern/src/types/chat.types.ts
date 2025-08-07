// Chat types for LEX Modern Frontend

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: number;
  metadata?: any;
  streaming?: boolean;
  tokens?: string[];
}

export interface ChatState {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
}

export interface ChatContextType {
  messages: Message[];
  sendMessage: (content: string, options?: any) => void;
  isConnected: boolean;
  clearMessages: () => void;
}