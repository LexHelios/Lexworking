import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { ChatState, Message } from '../../types/chat.types';

const initialState: ChatState = {
  messages: [],
  isLoading: false,
  error: null,
  isConnected: false,
};

const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    addMessage: (state, action: PayloadAction<Message>) => {
      state.messages.push(action.payload);
      state.error = null;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
      state.isLoading = false;
    },
    setConnected: (state, action: PayloadAction<boolean>) => {
      state.isConnected = action.payload;
    },
    clearMessages: (state) => {
      state.messages = [];
      state.error = null;
    },
    updateMessage: (state, action: PayloadAction<{ id: string; updates: Partial<Message> }>) => {
      const { id, updates } = action.payload;
      const messageIndex = state.messages.findIndex(msg => msg.id === id);
      if (messageIndex !== -1) {
        state.messages[messageIndex] = { ...state.messages[messageIndex], ...updates };
      }
    },
  },
});

export const {
  addMessage,
  setLoading,
  setError,
  setConnected,
  clearMessages,
  updateMessage,
} = chatSlice.actions;

export default chatSlice.reducer;