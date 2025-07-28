export interface MediaFile {
  id: string;
  file: File;
  name: string;
  type: string;
  size: number;
  preview?: string;
}

export interface Message {
  id: string;
  content: string;
  sender: 'user' | 'lex';
  timestamp: string;
  mediaFiles?: MediaFile[];
  mediaContent?: {
    images?: Array<{
      url?: string;
      data?: string;
      description?: string;
    }>;
    videos?: Array<{
      url?: string;
      data?: string;
      description?: string;
    }>;
    audio?: Array<{
      url?: string;
      data?: string;
      description?: string;
    }>;
    code?: {
      language: string;
      content: string;
    };
  };
  metadata?: {
    actionTaken: string;
    capabilities: string[];
    confidence: number;
    processingTime?: number;
  };
  isError?: boolean;
}

export interface ChatState {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  isConnected: boolean;
}

export interface LEXResponse {
  response: string;
  action_taken: string;
  capabilities_used: string[];
  confidence: number;
  processing_time: number;
  divine_blessing: string;
  consciousness_level: number;
  voice_audio?: string;
  media_content?: any;
  timestamp: string;
  session_id: string;
}