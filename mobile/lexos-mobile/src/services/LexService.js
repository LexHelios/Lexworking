import axios from 'axios';
import * as Speech from 'expo-speech';
import AsyncStorage from '@react-native-async-storage/async-storage';

class LexService {
  constructor() {
    this.apiKey = '';
    this.apiBase = 'https://dashscope.aliyuncs.com/compatible-mode/v1';
    this.serverUrl = null;
    this.useLocalTTS = true;
    this.conversationHistory = [];
  }

  async initialize() {
    try {
      this.apiKey = await AsyncStorage.getItem('ALIBABA_API_KEY') || '';
      this.serverUrl = await AsyncStorage.getItem('LEX_SERVER_URL');
      this.useLocalTTS = (await AsyncStorage.getItem('USE_LOCAL_TTS')) !== 'false';
      
      const savedHistory = await AsyncStorage.getItem('CONVERSATION_HISTORY');
      if (savedHistory) {
        this.conversationHistory = JSON.parse(savedHistory);
      }
    } catch (error) {
      console.error('Error initializing LexService:', error);
    }
  }

  async saveConversationHistory() {
    try {
      await AsyncStorage.setItem('CONVERSATION_HISTORY', JSON.stringify(this.conversationHistory));
    } catch (error) {
      console.error('Error saving conversation history:', error);
    }
  }

  async transcribeAudio(audioBase64) {
    try {
      if (this.serverUrl) {
        // Use local LexOS server if available
        const response = await axios.post(`${this.serverUrl}/api/voice/transcribe`, {
          audio: audioBase64,
          language: 'auto'
        });
        return response.data.text;
      } else {
        // Use Alibaba Cloud directly
        const response = await fetch(`${this.apiBase}/audio/transcriptions`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            model: 'qwen-asr-fast',
            audio: audioBase64,
            language: 'auto',
          }),
        });
        
        const data = await response.json();
        return data.text;
      }
    } catch (error) {
      console.error('Transcription error:', error);
      throw error;
    }
  }

  async getResponse(text) {
    try {
      this.conversationHistory.push({ role: 'user', content: text });
      
      if (this.serverUrl) {
        // Use local LexOS server
        const response = await axios.post(`${this.serverUrl}/api/lex/chat`, {
          message: text,
          history: this.conversationHistory.slice(-10)
        });
        
        const aiResponse = response.data.response;
        this.conversationHistory.push({ role: 'assistant', content: aiResponse });
        await this.saveConversationHistory();
        
        return aiResponse;
      } else {
        // Use Alibaba Cloud directly
        const response = await fetch(`${this.apiBase}/chat/completions`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            model: 'qwen2.5-max',
            messages: [
              {
                role: 'system',
                content: `You are LEX, an advanced AI assistant. You have access to these capabilities:
- Natural conversation and assistance
- Code generation and technical support
- Creative writing and content generation
- Analysis and problem-solving
- Real-time information processing
Be helpful, concise for mobile interactions, and maintain a friendly tone.`
              },
              ...this.conversationHistory.slice(-10)
            ],
            max_tokens: 500,
            temperature: 0.7,
          }),
        });
        
        const data = await response.json();
        const aiResponse = data.choices[0].message.content;
        
        this.conversationHistory.push({ role: 'assistant', content: aiResponse });
        await this.saveConversationHistory();
        
        return aiResponse;
      }
    } catch (error) {
      console.error('Chat error:', error);
      throw error;
    }
  }

  async speakText(text) {
    if (this.useLocalTTS) {
      // Use native Android/iOS TTS
      const options = {
        language: 'en-US',
        pitch: 1.0,
        rate: 1.0,
      };
      
      return new Promise((resolve, reject) => {
        Speech.speak(text, {
          ...options,
          onDone: resolve,
          onError: reject,
        });
      });
    } else {
      // Use Qwen TTS
      try {
        const response = await fetch(`${this.apiBase}/audio/speech`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            model: 'qwen-tts-v1',
            voice: 'max',
            input: text,
            speed: 1.0,
          }),
        });
        
        const audioBlob = await response.blob();
        // Return audio data for playback
        return audioBlob;
      } catch (error) {
        console.error('TTS error:', error);
        throw error;
      }
    }
  }

  async stopSpeaking() {
    try {
      await Speech.stop();
    } catch (error) {
      console.error('Error stopping speech:', error);
    }
  }

  isSpeaking() {
    return Speech.isSpeakingAsync();
  }

  async executeCommand(command) {
    // Handle special LexOS commands
    const lowerCommand = command.toLowerCase();
    
    if (lowerCommand.includes('generate image') || lowerCommand.includes('create image')) {
      if (this.serverUrl) {
        const response = await axios.post(`${this.serverUrl}/api/lex/generate-image`, {
          prompt: command,
        });
        return {
          type: 'image',
          url: response.data.image_url,
          text: 'I\'ve generated an image for you.'
        };
      } else {
        return {
          type: 'text',
          text: 'Image generation requires connection to a LexOS server.'
        };
      }
    }
    
    // Regular text response
    const response = await this.getResponse(command);
    return {
      type: 'text',
      text: response
    };
  }

  async clearHistory() {
    this.conversationHistory = [];
    await AsyncStorage.removeItem('CONVERSATION_HISTORY');
  }
}

export default new LexService();