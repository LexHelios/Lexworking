/**
 * LexOS Mobile - Enhanced Android App with Native TTS
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
  Alert,
  StatusBar,
  AppState,
  Image,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons } from '@expo/vector-icons';
import * as Haptics from 'expo-haptics';
import * as SplashScreen from 'expo-splash-screen';
import AsyncStorage from '@react-native-async-storage/async-storage';

import LexService from './src/services/LexService';
import { AudioUtils } from './src/utils/AudioUtils';
import { VoiceVisualizer } from './src/components/VoiceVisualizer';

// Keep splash screen visible while loading
SplashScreen.preventAutoHideAsync();

export default function App() {
  // State
  const [isReady, setIsReady] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [conversation, setConversation] = useState([]);
  const [recording, setRecording] = useState(null);
  const [apiKey, setApiKey] = useState('');
  const [serverUrl, setServerUrl] = useState('');
  const [showSettings, setShowSettings] = useState(false);
  const [inputText, setInputText] = useState('');
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [useLocalTTS, setUseLocalTTS] = useState(true);
  const [appState, setAppState] = useState(AppState.currentState);
  
  // Refs
  const scrollViewRef = useRef(null);
  const pulseAnim = useRef(new Animated.Value(1)).current;
  const fadeAnim = useRef(new Animated.Value(0)).current;
  
  // Initialize app
  useEffect(() => {
    initialize();
  }, []);
  
  // Handle app state changes
  useEffect(() => {
    const subscription = AppState.addEventListener('change', nextAppState => {
      if (appState.match(/inactive|background/) && nextAppState === 'active') {
        // App has come to the foreground
        console.log('App has come to the foreground!');
      }
      setAppState(nextAppState);
    });
    
    return () => {
      subscription.remove();
    };
  }, [appState]);
  
  const initialize = async () => {
    try {
      await AudioUtils.setupAudio();
      await LexService.initialize();
      await loadSettings();
      
      setIsReady(true);
      await SplashScreen.hideAsync();
    } catch (error) {
      console.error('Initialization error:', error);
      Alert.alert('Error', 'Failed to initialize app. Please restart.');
    }
  };
  
  const loadSettings = async () => {
    try {
      const savedKey = await AsyncStorage.getItem('ALIBABA_API_KEY');
      const savedServerUrl = await AsyncStorage.getItem('LEX_SERVER_URL');
      const savedVoice = await AsyncStorage.getItem('VOICE_ENABLED');
      const savedTTS = await AsyncStorage.getItem('USE_LOCAL_TTS');
      
      if (savedKey) {
        setApiKey(savedKey);
      } else {
        setShowSettings(true);
      }
      
      if (savedServerUrl) {
        setServerUrl(savedServerUrl);
      }
      
      if (savedVoice !== null) {
        setVoiceEnabled(savedVoice === 'true');
      }
      
      if (savedTTS !== null) {
        setUseLocalTTS(savedTTS === 'true');
      }
    } catch (error) {
      console.error('Error loading settings:', error);
    }
  };
  
  const saveSettings = async () => {
    try {
      await AsyncStorage.setItem('ALIBABA_API_KEY', apiKey);
      await AsyncStorage.setItem('LEX_SERVER_URL', serverUrl);
      await AsyncStorage.setItem('VOICE_ENABLED', voiceEnabled.toString());
      await AsyncStorage.setItem('USE_LOCAL_TTS', useLocalTTS.toString());
      
      await LexService.initialize();
      setShowSettings(false);
    } catch (error) {
      console.error('Error saving settings:', error);
      Alert.alert('Error', 'Failed to save settings');
    }
  };
  
  const startRecording = async () => {
    try {
      await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
      
      const newRecording = await AudioUtils.startRecording();
      setRecording(newRecording);
      setIsRecording(true);
      
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 300,
        useNativeDriver: true,
      }).start();
    } catch (error) {
      console.error('Failed to start recording:', error);
      Alert.alert('Error', 'Failed to start recording. Please check permissions.');
    }
  };
  
  const stopRecording = async () => {
    if (!recording) return;
    
    try {
      await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
      
      setIsRecording(false);
      const audioBase64 = await AudioUtils.stopRecording(recording);
      setRecording(null);
      
      Animated.timing(fadeAnim, {
        toValue: 0,
        duration: 300,
        useNativeDriver: true,
      }).start();
      
      await processAudio(audioBase64);
    } catch (error) {
      console.error('Failed to stop recording:', error);
      Alert.alert('Error', 'Failed to process recording');
    }
  };
  
  const processAudio = async (audioBase64) => {
    setIsProcessing(true);
    
    try {
      const transcript = await LexService.transcribeAudio(audioBase64);
      
      if (!transcript) {
        throw new Error('No transcript received');
      }
      
      await processText(transcript);
    } catch (error) {
      console.error('Processing error:', error);
      addToConversation('System', 'Failed to process audio. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };
  
  const processText = async (text) => {
    try {
      addToConversation('You', text);
      
      const result = await LexService.executeCommand(text);
      
      if (result.type === 'image') {
        addToConversation('LEX', result.text, result.url);
      } else {
        addToConversation('LEX', result.text);
      }
      
      if (voiceEnabled && result.text) {
        await speakText(result.text);
      }
    } catch (error) {
      console.error('Chat error:', error);
      addToConversation('LEX', 'I encountered an error. Please check your connection and try again.');
    }
  };
  
  const speakText = async (text) => {
    setIsSpeaking(true);
    
    try {
      if (useLocalTTS) {
        await LexService.speakText(text);
      } else {
        const audioBlob = await LexService.speakText(text);
        if (audioBlob instanceof Blob) {
          const reader = new FileReader();
          reader.onloadend = async () => {
            const base64 = reader.result.split(',')[1];
            await AudioUtils.playAudioFromBase64(base64);
          };
          reader.readAsDataURL(audioBlob);
        }
      }
    } catch (error) {
      console.error('TTS error:', error);
    } finally {
      setIsSpeaking(false);
    }
  };
  
  const stopSpeaking = async () => {
    try {
      await LexService.stopSpeaking();
      setIsSpeaking(false);
    } catch (error) {
      console.error('Error stopping speech:', error);
    }
  };
  
  const addToConversation = (speaker, text, imageUrl = null) => {
    const newMessage = {
      speaker,
      text,
      imageUrl,
      timestamp: new Date().toISOString(),
    };
    
    setConversation(prev => [...prev, newMessage]);
    
    // Auto-scroll to bottom
    setTimeout(() => {
      scrollViewRef.current?.scrollToEnd({ animated: true });
    }, 100);
  };
  
  const sendTextMessage = async () => {
    if (!inputText.trim()) return;
    
    const text = inputText.trim();
    setInputText('');
    await processText(text);
  };
  
  const clearConversation = () => {
    Alert.alert(
      'Clear Conversation',
      'Are you sure you want to clear the conversation history?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Clear',
          style: 'destructive',
          onPress: async () => {
            setConversation([]);
            await LexService.clearHistory();
          },
        },
      ]
    );
  };
  
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
  
  if (!isReady) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#00ff00" />
      </View>
    );
  }
  
  // Settings Screen
  if (showSettings) {
    return (
      <View style={styles.container}>
        <StatusBar barStyle="light-content" backgroundColor="#000000" />
        <LinearGradient
          colors={['#1a1a1a', '#2d2d2d']}
          style={styles.gradient}
        >
          <ScrollView contentContainerStyle={styles.settingsContainer}>
            <Text style={styles.title}>LexOS Mobile Settings</Text>
            
            <View style={styles.settingGroup}>
              <Text style={styles.label}>Alibaba Cloud API Key:</Text>
              <TextInput
                style={styles.input}
                value={apiKey}
                onChangeText={setApiKey}
                placeholder="sk-..."
                placeholderTextColor="#666"
                secureTextEntry
              />
            </View>
            
            <View style={styles.settingGroup}>
              <Text style={styles.label}>LexOS Server URL (Optional):</Text>
              <TextInput
                style={styles.input}
                value={serverUrl}
                onChangeText={setServerUrl}
                placeholder="http://192.168.1.100:8000"
                placeholderTextColor="#666"
                autoCapitalize="none"
              />
              <Text style={styles.hint}>
                Connect to your local LexOS server for enhanced features
              </Text>
            </View>
            
            <View style={styles.settingGroup}>
              <TouchableOpacity
                style={styles.toggleContainer}
                onPress={() => setVoiceEnabled(!voiceEnabled)}
              >
                <Text style={styles.toggleLabel}>Voice Output</Text>
                <View style={[styles.toggle, voiceEnabled && styles.toggleActive]}>
                  <View style={[styles.toggleBall, voiceEnabled && styles.toggleBallActive]} />
                </View>
              </TouchableOpacity>
            </View>
            
            <View style={styles.settingGroup}>
              <TouchableOpacity
                style={styles.toggleContainer}
                onPress={() => setUseLocalTTS(!useLocalTTS)}
              >
                <Text style={styles.toggleLabel}>Use Native TTS</Text>
                <View style={[styles.toggle, useLocalTTS && styles.toggleActive]}>
                  <View style={[styles.toggleBall, useLocalTTS && styles.toggleBallActive]} />
                </View>
              </TouchableOpacity>
              <Text style={styles.hint}>
                Native TTS works offline, Qwen TTS has better quality
              </Text>
            </View>
            
            <TouchableOpacity
              style={[styles.saveButton, !apiKey && styles.saveButtonDisabled]}
              onPress={saveSettings}
              disabled={!apiKey}
            >
              <Text style={styles.saveButtonText}>Save & Continue</Text>
            </TouchableOpacity>
          </ScrollView>
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
      <StatusBar barStyle="light-content" backgroundColor="#000000" />
      <LinearGradient
        colors={['#0a0a0a', '#1a1a1a']}
        style={styles.gradient}
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>LEX</Text>
          <View style={styles.headerButtons}>
            <TouchableOpacity
              onPress={() => {
                if (isSpeaking) {
                  stopSpeaking();
                } else {
                  setVoiceEnabled(!voiceEnabled);
                }
              }}
              style={styles.headerButton}
            >
              <Ionicons 
                name={isSpeaking ? 'stop' : (voiceEnabled ? 'volume-high' : 'volume-mute')} 
                size={24} 
                color="#00ff00" 
              />
            </TouchableOpacity>
            <TouchableOpacity
              onPress={clearConversation}
              style={styles.headerButton}
            >
              <Ionicons name="trash-outline" size={24} color="#00ff00" />
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
          ref={scrollViewRef}
          style={styles.conversation}
          contentContainerStyle={styles.conversationContent}
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
                Tap and hold the microphone to talk, or type below
              </Text>
              <View style={styles.featuresContainer}>
                <Text style={styles.featureItem}>🧠 Advanced AI reasoning</Text>
                <Text style={styles.featureItem}>🎨 Image generation</Text>
                <Text style={styles.featureItem}>💻 Code assistance</Text>
                <Text style={styles.featureItem}>🔊 Natural voice interaction</Text>
              </View>
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
              {msg.imageUrl && (
                <Image source={{ uri: msg.imageUrl }} style={styles.messageImage} />
              )}
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
              <VoiceVisualizer isActive={true} color="#00ff00" />
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
            multiline
            maxHeight={100}
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
          
          {isRecording && (
            <Animated.View style={{ opacity: fadeAnim }}>
              <VoiceVisualizer isActive={true} color="#ff0000" />
              <Text style={styles.voiceButtonText}>Listening...</Text>
            </Animated.View>
          )}
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
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#000',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: Platform.OS === 'ios' ? 50 : 30,
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
    padding: 5,
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
    textAlign: 'center',
  },
  welcomeSubtext: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    marginBottom: 30,
  },
  featuresContainer: {
    alignItems: 'flex-start',
  },
  featureItem: {
    fontSize: 14,
    color: '#888',
    marginVertical: 5,
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
  messageImage: {
    width: 200,
    height: 200,
    marginTop: 10,
    borderRadius: 10,
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
    alignItems: 'center',
  },
  inputArea: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderTopWidth: 1,
    borderTopColor: '#333',
    alignItems: 'flex-end',
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
    maxHeight: 100,
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
    textAlign: 'center',
  },
  // Settings styles
  settingsContainer: {
    padding: 30,
  },
  settingGroup: {
    marginBottom: 25,
  },
  label: {
    color: '#fff',
    fontSize: 16,
    marginBottom: 10,
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
  toggleContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 10,
  },
  toggleLabel: {
    color: '#fff',
    fontSize: 16,
  },
  toggle: {
    width: 50,
    height: 30,
    borderRadius: 15,
    backgroundColor: '#333',
    padding: 3,
  },
  toggleActive: {
    backgroundColor: '#00ff00',
  },
  toggleBall: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: '#666',
  },
  toggleBallActive: {
    backgroundColor: '#fff',
    transform: [{ translateX: 20 }],
  },
  saveButton: {
    backgroundColor: '#00ff00',
    borderRadius: 10,
    padding: 15,
    alignItems: 'center',
    marginTop: 30,
  },
  saveButtonDisabled: {
    backgroundColor: '#333',
  },
  saveButtonText: {
    color: '#000',
    fontSize: 18,
    fontWeight: 'bold',
  },
  hint: {
    color: '#666',
    fontSize: 12,
    marginTop: 5,
  },
});