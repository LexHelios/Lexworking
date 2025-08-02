# LexOS Mobile - Android APK Architecture

## 🚀 Overview

LexOS Mobile brings the full power of LEX to your Android phone using:
- **Cloud-first architecture** (no local GPU needed)
- **Native voice interface** using phone's microphone
- **Always-on assistant** in your pocket
- **Offline capabilities** with smart caching

## 📱 Technology Stack

### Option 1: React Native (Recommended)
```
Frontend: React Native + Expo
Voice: Native Android Audio APIs
Backend: Direct Alibaba Cloud APIs
Storage: AsyncStorage + SQLite
```

### Option 2: Flutter
```
Frontend: Flutter + Dart
Voice: flutter_sound package
Backend: Direct API calls
Storage: Hive/SQLite
```

### Option 3: Native Android (Kotlin)
```
Frontend: Jetpack Compose
Voice: Android Speech APIs
Backend: Retrofit + OkHttp
Storage: Room Database
```

## 🏗️ Architecture

```
┌─────────────────────────────────┐
│      LexOS Mobile App           │
├─────────────────────────────────┤
│  Voice Interface Layer          │
│  - Push-to-talk / Always-on     │
│  - Qwen ASR/TTS integration     │
├─────────────────────────────────┤
│  UI Layer                       │
│  - Chat interface               │
│  - Voice visualization          │
│  - Settings & preferences       │
├─────────────────────────────────┤
│  Service Layer                  │
│  - Direct Alibaba Cloud APIs    │
│  - Background processing        │
│  - Notification handling        │
├─────────────────────────────────┤
│  Local Storage                  │
│  - Conversation history         │
│  - Cached responses             │
│  - User preferences            │
└─────────────────────────────────┘
```

## 🔥 Key Features

### 1. Voice-First Interface
- **Wake word**: "Hey LEX" activation
- **Push-to-talk**: Hold button to speak
- **Continuous conversation**: Like phone calls
- **Background listening**: With permission

### 2. Direct Cloud Integration
```javascript
// Direct Alibaba Cloud connection
const lexMobile = {
  qwenAPI: 'https://dashscope.aliyuncs.com/compatible-mode/v1',
  apiKey: process.env.ALIBABA_API_KEY,
  
  async processVoice(audioBlob) {
    // 1. Send to Qwen ASR
    const transcript = await this.transcribe(audioBlob);
    
    // 2. Process with Qwen 2.5-Max
    const response = await this.think(transcript);
    
    // 3. Speak with Qwen TTS
    const audio = await this.speak(response);
    
    return { transcript, response, audio };
  }
};
```

### 3. Mobile-Optimized Features
- **Swipe gestures** for quick actions
- **Widget support** for home screen
- **Share intent** - "Share to LEX"
- **Camera integration** for image analysis
- **Location awareness** for context

### 4. Offline Capabilities
- Cache frequent responses
- Store conversation history
- Work with degraded functionality
- Sync when connected

## 💻 Implementation Plan

### Phase 1: MVP (1-2 weeks)
1. Basic React Native app
2. Voice input/output with Qwen
3. Text chat interface
4. Direct API integration

### Phase 2: Enhanced (2-3 weeks)
1. Background voice processing
2. Notification responses
3. Widget support
4. Image generation display

### Phase 3: Advanced (3-4 weeks)
1. Wake word detection
2. Continuous conversation mode
3. Offline caching
4. Multi-language support

## 🛠️ Quick Start Code

### React Native + Expo Setup
```bash
# Create new Expo app
npx create-expo-app lexos-mobile
cd lexos-mobile

# Install dependencies
npm install axios expo-av expo-permissions @react-native-async-storage/async-storage
```

### Core App Structure
```javascript
// App.js
import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { Audio } from 'expo-av';
import axios from 'axios';

const ALIBABA_API_KEY = 'your-key-here';
const API_BASE = 'https://dashscope.aliyuncs.com/compatible-mode/v1';

export default function App() {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [conversation, setConversation] = useState([]);
  
  const startRecording = async () => {
    try {
      await Audio.requestPermissionsAsync();
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });
      
      const { recording } = await Audio.Recording.createAsync(
        Audio.RECORDING_OPTIONS_PRESET_HIGH_QUALITY
      );
      
      setIsRecording(true);
      // Start recording logic
    } catch (err) {
      console.error('Failed to start recording', err);
    }
  };
  
  const processWithLEX = async (audioUri) => {
    setIsProcessing(true);
    
    try {
      // 1. Transcribe audio
      const formData = new FormData();
      formData.append('audio', {
        uri: audioUri,
        type: 'audio/wav',
        name: 'recording.wav'
      });
      
      // 2. Send to your backend or directly to Alibaba
      const response = await axios.post('/api/voice/process', formData);
      
      // 3. Play response audio
      const { sound } = await Audio.Sound.createAsync({
        uri: response.data.audioUrl
      });
      await sound.playAsync();
      
      // Update conversation
      setConversation([...conversation, {
        user: response.data.transcript,
        lex: response.data.response
      }]);
      
    } catch (error) {
      console.error('Processing error:', error);
    } finally {
      setIsProcessing(false);
    }
  };
  
  return (
    <View style={styles.container}>
      <Text style={styles.title}>LEX Mobile</Text>
      
      <View style={styles.conversation}>
        {conversation.map((turn, i) => (
          <View key={i}>
            <Text style={styles.user}>You: {turn.user}</Text>
            <Text style={styles.lex}>LEX: {turn.lex}</Text>
          </View>
        ))}
      </View>
      
      <TouchableOpacity
        style={[styles.button, isRecording && styles.recording]}
        onPressIn={startRecording}
        onPressOut={stopRecording}
      >
        <Text style={styles.buttonText}>
          {isRecording ? 'Recording...' : 'Hold to Talk'}
        </Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a1a',
    padding: 20,
  },
  title: {
    fontSize: 24,
    color: '#00ff00',
    textAlign: 'center',
    marginBottom: 20,
  },
  conversation: {
    flex: 1,
    marginBottom: 20,
  },
  user: {
    color: '#ffffff',
    marginBottom: 5,
  },
  lex: {
    color: '#00ff00',
    marginBottom: 15,
  },
  button: {
    backgroundColor: '#333',
    padding: 20,
    borderRadius: 50,
    alignItems: 'center',
  },
  recording: {
    backgroundColor: '#ff0000',
  },
  buttonText: {
    color: '#fff',
    fontSize: 18,
  },
});
```

## 🔐 Security Considerations

1. **API Key Storage**:
   - Use Android Keystore
   - Or proxy through your server
   - Never hardcode in APK

2. **Voice Privacy**:
   - Clear permission requests
   - Local audio processing option
   - Delete recordings after use

3. **Data Encryption**:
   - HTTPS for all API calls
   - Encrypt local storage
   - Secure credential handling

## 📦 Building the APK

### With Expo:
```bash
# Build APK
expo build:android -t apk

# Or build AAB for Play Store
expo build:android -t app-bundle
```

### Direct React Native:
```bash
cd android
./gradlew assembleRelease
# APK will be in android/app/build/outputs/apk/release/
```

## 🚀 Deployment Options

1. **Direct APK**: Share the APK file directly
2. **Google Play Store**: Publish for easy updates
3. **Progressive Web App**: Alternative to native
4. **Local server mode**: Connect to home LexOS

## 💡 Advanced Features to Add

1. **Voice Shortcuts**: "Hey LEX, drive mode"
2. **Android Widgets**: Quick actions on home screen
3. **Wear OS Support**: LEX on your watch
4. **Android Auto**: LEX in your car
5. **Smart Home Integration**: Control via voice

## 📱 The Future: LexOS Everywhere

With this mobile app, you'll have:
- **LEX in your pocket** 24/7
- **Voice-first interface** for hands-free use
- **All Alibaba Cloud features** on mobile
- **No GPU needed** - pure cloud power
- **~$35-45/month** for unlimited mobile AI

Your phone becomes your personal Jarvis!