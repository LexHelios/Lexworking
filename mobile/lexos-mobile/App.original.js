/**
 * LexOS Mobile - Your Pocket AI Assistant
 * Powered by Alibaba Cloud (Qwen 2.5-Max + Voice)
 */
import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
  ActivityIndicator,
  Animated,
  Vibration,
  KeyboardAvoidingView,
  Platform,
  TextInput,
  Image,
} from 'react-native';
import { Audio } from 'expo-av';
import * as FileSystem from 'expo-file-system';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';

// Configuration
const CONFIG = {
  API_KEY: '', // Will be loaded from secure storage
  API_BASE: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
  VOICE: 'max', // Bilingual tech voice
};

export default function App() {
  // State
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [conversation, setConversation] = useState([]);
  const [recording, setRecording] = useState(null);
  const [apiKey, setApiKey] = useState('');
  const [showSettings, setShowSettings] = useState(false);
  const [inputText, setInputText] = useState('');
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  
  // Animations
  const pulseAnim = useRef(new Animated.Value(1)).current;
  const fadeAnim = useRef(new Animated.Value(0)).current;
  
  // Load API key on startup
  useEffect(() => {
    loadSettings();
    requestPermissions();
  }, []);
  
  // Pulse animation for recording
  useEffect(() => {
    if (isRecording) {
      Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, {
            toValue: 1.2,
            duration: 500,
            useNativeDriver: true,
          }),
          Animated.timing(pulseAnim, {
            toValue: 1,
            duration: 500,
            useNativeDriver: true,
          }),
        ])
      ).start();
    } else {
      pulseAnim.setValue(1);
    }
  }, [isRecording]);
  
  const loadSettings = async () => {
    try {
      const savedKey = await AsyncStorage.getItem('ALIBABA_API_KEY');
      if (savedKey) {
        setApiKey(savedKey);
        CONFIG.API_KEY = savedKey;
      } else {
        setShowSettings(true);
      }
      
      const savedVoice = await AsyncStorage.getItem('VOICE_ENABLED');
      if (savedVoice !== null) {
        setVoiceEnabled(savedVoice === 'true');
      }
    } catch (error) {
      console.error('Error loading settings:', error);
    }
  };
  
  const saveApiKey = async () => {
    try {
      await AsyncStorage.setItem('ALIBABA_API_KEY', apiKey);
      CONFIG.API_KEY = apiKey;
      setShowSettings(false);
    } catch (error) {
      console.error('Error saving API key:', error);
    }
  };
  
  const requestPermissions = async () => {
    try {
      const { status } = await Audio.requestPermissionsAsync();
      if (status !== 'granted') {
        alert('Audio permissions are required for voice interaction');
      }
      
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
        staysActiveInBackground: true,
      });
    } catch (error) {
      console.error('Permission error:', error);
    }
  };
  
  const startRecording = async () => {
    try {
      // Haptic feedback
      Vibration.vibrate(50);
      
      const { recording } = await Audio.Recording.createAsync(
        Audio.RecordingOptionsPresets.HIGH_QUALITY
      );
      
      setRecording(recording);
      setIsRecording(true);
      
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 300,
        useNativeDriver: true,
      }).start();
      
    } catch (err) {
      console.error('Failed to start recording', err);
      alert('Failed to start recording');
    }
  };
  
  const stopRecording = async () => {
    if (!recording) return;
    
    try {
      // Haptic feedback
      Vibration.vibrate(50);
      
      setIsRecording(false);
      await recording.stopAndUnloadAsync();
      
      const uri = recording.getURI();
      setRecording(null);
      
      Animated.timing(fadeAnim, {
        toValue: 0,
        duration: 300,
        useNativeDriver: true,
      }).start();
      
      // Process the audio
      await processAudio(uri);
      
    } catch (error) {
      console.error('Failed to stop recording', error);
    }
  };
  
  const processAudio = async (audioUri) => {
    setIsProcessing(true);
    
    try {
      // Read audio file
      const audioBase64 = await FileSystem.readAsStringAsync(audioUri, {
        encoding: FileSystem.EncodingType.Base64,
      });
      
      // 1. Transcribe with Qwen ASR
      const transcriptResponse = await fetch(`${CONFIG.API_BASE}/audio/transcriptions`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${CONFIG.API_KEY}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: 'qwen-asr-fast',
          audio: audioBase64,
          language: 'auto',
        }),
      });
      
      const { text: transcript } = await transcriptResponse.json();
      
      if (!transcript) {
        throw new Error('No transcript received');
      }
      
      // Process the transcribed text
      await processText(transcript);
      
    } catch (error) {
      console.error('Processing error:', error);
      addToConversation('Error', 'Failed to process audio. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };
  
  const processText = async (text) => {
    try {
      // Add user message to conversation
      addToConversation('You', text);
      
      // 2. Get response from Qwen 2.5-Max
      const chatResponse = await fetch(`${CONFIG.API_BASE}/chat/completions`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${CONFIG.API_KEY}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: 'qwen2.5-max',
          messages: [
            {
              role: 'system',
              content: 'You are LEX, a helpful AI assistant. Be concise for mobile.'
            },
            ...conversation.slice(-10).map(msg => ({
              role: msg.speaker === 'You' ? 'user' : 'assistant',
              content: msg.text
            })),
            { role: 'user', content: text }
          ],
          max_tokens: 500,
          temperature: 0.7,
        }),
      });
      
      const chatData = await chatResponse.json();
      const lexResponse = chatData.choices[0].message.content;
      
      // Add LEX response to conversation
      addToConversation('LEX', lexResponse);
      
      // 3. Speak the response if voice is enabled
      if (voiceEnabled) {
        await speakText(lexResponse);
      }
      
    } catch (error) {
      console.error('Chat error:', error);
      addToConversation('LEX', 'I encountered an error. Please check your connection.');
    }
  };
  
  const speakText = async (text) => {
    setIsSpeaking(true);
    
    try {
      // Generate speech with Qwen TTS
      const ttsResponse = await fetch(`${CONFIG.API_BASE}/audio/speech`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${CONFIG.API_KEY}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: 'qwen-tts-v1',
          voice: CONFIG.VOICE,
          input: text,
          speed: 1.0,
        }),
      });
      
      const audioBlob = await ttsResponse.blob();
      const audioUri = FileSystem.documentDirectory + 'speech.mp3';
      
      // Save audio to file
      const reader = new FileReader();
      reader.onload = async () => {
        const base64 = reader.result.split(',')[1];
        await FileSystem.writeAsStringAsync(audioUri, base64, {
          encoding: FileSystem.EncodingType.Base64,
        });
        
        // Play audio
        const { sound } = await Audio.Sound.createAsync({ uri: audioUri });
        await sound.playAsync();
        
        sound.setOnPlaybackStatusUpdate((status) => {
          if (status.didJustFinish) {
            setIsSpeaking(false);
            sound.unloadAsync();
          }
        });
      };
      reader.readAsDataURL(audioBlob);
      
    } catch (error) {
      console.error('TTS error:', error);
      setIsSpeaking(false);
    }
  };
  
  const addToConversation = (speaker, text) => {
    setConversation(prev => [
      ...prev,
      {
        speaker,
        text,
        timestamp: new Date().toISOString(),
      }
    ]);
  };
  
  const sendTextMessage = async () => {
    if (!inputText.trim()) return;
    
    const text = inputText.trim();
    setInputText('');
    await processText(text);
  };
  
  // Settings Screen
  if (showSettings) {
    return (
      <View style={styles.container}>
        <LinearGradient
          colors={['#1a1a1a', '#2d2d2d']}
          style={styles.gradient}
        >
          <View style={styles.settingsContainer}>
            <Text style={styles.title}>LexOS Mobile Setup</Text>
            
            <Text style={styles.label}>Alibaba Cloud API Key:</Text>
            <TextInput
              style={styles.input}
              value={apiKey}
              onChangeText={setApiKey}
              placeholder="Enter your API key"
              placeholderTextColor="#666"
              secureTextEntry
            />
            
            <TouchableOpacity
              style={styles.saveButton}
              onPress={saveApiKey}
              disabled={!apiKey}
            >
              <Text style={styles.saveButtonText}>Save & Continue</Text>
            </TouchableOpacity>
            
            <Text style={styles.hint}>
              Get your API key from Alibaba Cloud Console
            </Text>
          </View>
        </LinearGradient>
      </View>
    );
  }
  
  // Main App UI
  return (
    <KeyboardAvoidingView 
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <LinearGradient
        colors={['#0a0a0a', '#1a1a1a']}
        style={styles.gradient}
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>LEX</Text>
          <View style={styles.headerButtons}>
            <TouchableOpacity
              onPress={() => setVoiceEnabled(!voiceEnabled)}
              style={styles.headerButton}
            >
              <Ionicons 
                name={voiceEnabled ? 'volume-high' : 'volume-mute'} 
                size={24} 
                color="#00ff00" 
              />
            </TouchableOpacity>
            <TouchableOpacity
              onPress={() => setShowSettings(true)}
              style={styles.headerButton}
            >
              <Ionicons name="settings" size={24} color="#00ff00" />
            </TouchableOpacity>
          </View>
        </View>
        
        {/* Conversation */}
        <ScrollView 
          style={styles.conversation}
          contentContainerStyle={styles.conversationContent}
          ref={ref => this.scrollView = ref}
          onContentSizeChange={() => this.scrollView?.scrollToEnd({ animated: true })}
        >
          {conversation.length === 0 && (
            <View style={styles.welcomeContainer}>
              <View style={styles.logoPlaceholder}>
                <Text style={styles.logoText}>LEX</Text>
              </View>
              <Text style={styles.welcomeText}>
                Hello! I'm LEX, your AI assistant.
              </Text>
              <Text style={styles.welcomeSubtext}>
                Tap the microphone to talk or type below
              </Text>
            </View>
          )}
          
          {conversation.map((msg, index) => (
            <View
              key={index}
              style={[
                styles.message,
                msg.speaker === 'You' ? styles.userMessage : styles.lexMessage
              ]}
            >
              <Text style={styles.messageSpeaker}>{msg.speaker}</Text>
              <Text style={styles.messageText}>{msg.text}</Text>
            </View>
          ))}
          
          {isProcessing && (
            <View style={styles.processingContainer}>
              <ActivityIndicator size="small" color="#00ff00" />
              <Text style={styles.processingText}>LEX is thinking...</Text>
            </View>
          )}
          
          {isSpeaking && (
            <View style={styles.speakingContainer}>
              <Text style={styles.speakingText}>🔊 Speaking...</Text>
            </View>
          )}
        </ScrollView>
        
        {/* Input Area */}
        <View style={styles.inputArea}>
          <TextInput
            style={styles.textInput}
            value={inputText}
            onChangeText={setInputText}
            placeholder="Type a message..."
            placeholderTextColor="#666"
            onSubmitEditing={sendTextMessage}
            returnKeyType="send"
          />
          
          <TouchableOpacity
            onPress={inputText.trim() ? sendTextMessage : undefined}
            disabled={!inputText.trim() || isProcessing}
            style={[styles.sendButton, (!inputText.trim() || isProcessing) && styles.sendButtonDisabled]}
          >
            <Ionicons name="send" size={20} color="#fff" />
          </TouchableOpacity>
        </View>
        
        {/* Voice Button */}
        <View style={styles.voiceButtonContainer}>
          <TouchableOpacity
            onPressIn={startRecording}
            onPressOut={stopRecording}
            disabled={isProcessing || isSpeaking}
            style={styles.voiceButtonWrapper}
          >
            <Animated.View
              style={[
                styles.voiceButton,
                {
                  transform: [{ scale: pulseAnim }],
                  opacity: isProcessing || isSpeaking ? 0.5 : 1,
                }
              ]}
            >
              <LinearGradient
                colors={isRecording ? ['#ff0000', '#cc0000'] : ['#00ff00', '#00cc00']}
                style={styles.voiceButtonGradient}
              >
                <Ionicons 
                  name={isRecording ? 'mic' : 'mic-outline'} 
                  size={40} 
                  color="#fff" 
                />
              </LinearGradient>
            </Animated.View>
          </TouchableOpacity>
          
          <Animated.Text
            style={[
              styles.voiceButtonText,
              { opacity: fadeAnim }
            ]}
          >
            Listening...
          </Animated.Text>
        </View>
      </LinearGradient>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  gradient: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: 50,
    paddingHorizontal: 20,
    paddingBottom: 10,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#00ff00',
    textShadowColor: '#00ff00',
    textShadowOffset: { width: 0, height: 0 },
    textShadowRadius: 10,
  },
  headerButtons: {
    flexDirection: 'row',
  },
  headerButton: {
    marginLeft: 15,
  },
  conversation: {
    flex: 1,
    paddingHorizontal: 20,
  },
  conversationContent: {
    paddingBottom: 20,
  },
  welcomeContainer: {
    alignItems: 'center',
    marginTop: 50,
  },
  logoPlaceholder: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: '#1a1a1a',
    borderWidth: 2,
    borderColor: '#00ff00',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
  },
  logoText: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#00ff00',
  },
  welcomeText: {
    fontSize: 18,
    color: '#fff',
    marginBottom: 10,
  },
  welcomeSubtext: {
    fontSize: 14,
    color: '#666',
  },
  message: {
    marginVertical: 10,
    padding: 15,
    borderRadius: 15,
    maxWidth: '80%',
  },
  userMessage: {
    alignSelf: 'flex-end',
    backgroundColor: '#1e3a1e',
    borderColor: '#00ff00',
    borderWidth: 1,
  },
  lexMessage: {
    alignSelf: 'flex-start',
    backgroundColor: '#1a1a1a',
    borderColor: '#333',
    borderWidth: 1,
  },
  messageSpeaker: {
    fontSize: 12,
    color: '#00ff00',
    marginBottom: 5,
    fontWeight: 'bold',
  },
  messageText: {
    fontSize: 16,
    color: '#fff',
    lineHeight: 22,
  },
  processingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 10,
  },
  processingText: {
    color: '#00ff00',
    marginLeft: 10,
  },
  speakingContainer: {
    padding: 10,
  },
  speakingText: {
    color: '#00ff00',
  },
  inputArea: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderTopWidth: 1,
    borderTopColor: '#333',
  },
  textInput: {
    flex: 1,
    backgroundColor: '#1a1a1a',
    borderRadius: 25,
    paddingHorizontal: 20,
    paddingVertical: 10,
    color: '#fff',
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#333',
  },
  sendButton: {
    marginLeft: 10,
    backgroundColor: '#00ff00',
    borderRadius: 25,
    width: 45,
    height: 45,
    justifyContent: 'center',
    alignItems: 'center',
  },
  sendButtonDisabled: {
    backgroundColor: '#333',
  },
  voiceButtonContainer: {
    alignItems: 'center',
    paddingBottom: 30,
  },
  voiceButtonWrapper: {
    marginTop: 20,
  },
  voiceButton: {
    width: 80,
    height: 80,
    borderRadius: 40,
    elevation: 5,
    shadowColor: '#00ff00',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.5,
    shadowRadius: 10,
  },
  voiceButtonGradient: {
    width: 80,
    height: 80,
    borderRadius: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  voiceButtonText: {
    color: '#00ff00',
    marginTop: 10,
    fontSize: 16,
  },
  settingsContainer: {
    flex: 1,
    padding: 30,
    justifyContent: 'center',
  },
  label: {
    color: '#fff',
    fontSize: 16,
    marginBottom: 10,
    marginTop: 20,
  },
  input: {
    backgroundColor: '#1a1a1a',
    borderRadius: 10,
    padding: 15,
    color: '#fff',
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#333',
  },
  saveButton: {
    backgroundColor: '#00ff00',
    borderRadius: 10,
    padding: 15,
    alignItems: 'center',
    marginTop: 30,
  },
  saveButtonText: {
    color: '#000',
    fontSize: 18,
    fontWeight: 'bold',
  },
  hint: {
    color: '#666',
    fontSize: 14,
    textAlign: 'center',
    marginTop: 20,
  },
});