# LexOS Mobile - Android App

## 🚀 Overview

LexOS Mobile brings the full power of LEX AI to your Android device with:
- 🎙️ **Native voice interaction** with Text-to-Speech (TTS) support
- 💬 **Real-time chat interface** with Qwen 2.5-Max
- 🔊 **Offline TTS** using Android's native speech engine
- ☁️ **Cloud TTS** option with Qwen's premium voices
- 🏠 **Local server support** for enhanced features
- 📱 **Optimized for mobile** with responsive UI

## 📲 Features

### Core Functionality
- **Voice Input**: Push-to-talk recording with visual feedback
- **Text Input**: Full keyboard support with multiline messages
- **TTS Output**: Choose between native Android TTS (offline) or Qwen TTS (premium quality)
- **Conversation History**: Persistent chat history with auto-save
- **Dark Theme**: Eye-friendly interface optimized for OLED screens

### Advanced Features
- **Local Server Connection**: Connect to your home LexOS instance
- **Image Generation**: Request AI-generated images (requires server)
- **Voice Controls**: Stop speaking, toggle voice output
- **Haptic Feedback**: Touch feedback for better UX
- **Background Processing**: Continues working when minimized

## 🛠️ Setup Instructions

### Prerequisites
- Node.js 16+ installed
- Android device or emulator
- Alibaba Cloud API key for Qwen services

### Quick Start

1. **Install dependencies**:
```bash
cd lexos-mobile
npm install
```

2. **Run on Android**:
```bash
# Start Metro bundler
npm start

# In another terminal, run on Android
npm run android
```

3. **Configure API Key**:
   - Launch the app
   - Enter your Alibaba Cloud API key in settings
   - Optionally add your LexOS server URL

### Building APK

**Windows**:
```batch
build-android.bat
```

**macOS/Linux**:
```bash
chmod +x build-android.sh
./build-android.sh
```

Choose from:
1. Development APK (for testing)
2. Production APK (optimized)
3. AAB for Play Store

## 🔧 Configuration

### API Settings
- **Alibaba Cloud API Key**: Required for AI features
- **LexOS Server URL**: Optional, for local server features

### Voice Settings
- **Voice Output**: Toggle voice responses on/off
- **Native TTS**: Use Android's built-in TTS (works offline)
- **Qwen TTS**: Premium voice quality (requires internet)

## 📁 Project Structure

```
lexos-mobile/
├── App.js                 # Main app component
├── App.enhanced.js        # Enhanced version with all features
├── src/
│   ├── services/
│   │   └── LexService.js  # Core AI service
│   ├── utils/
│   │   └── AudioUtils.js  # Audio recording/playback
│   └── components/
│       └── VoiceVisualizer.js  # Voice UI component
├── assets/               # App icons and splash screens
├── app.json             # Expo configuration
├── eas.json             # Build configuration
└── package.json         # Dependencies
```

## 🎯 Usage Tips

### Voice Interaction
1. **Hold to talk**: Press and hold the microphone button
2. **Release to send**: Let go to process your message
3. **Visual feedback**: Watch for the pulsing animation
4. **Stop speaking**: Tap the speaker icon while LEX is talking

### Text Input
- Type messages in the input field
- Press Enter or tap Send
- Supports multiline messages
- Auto-scrolls to latest message

### Performance Tips
- Use Native TTS for offline capability
- Connect to local server for faster responses
- Clear conversation history periodically
- Close other apps for better performance

## 🔐 Security

- API keys stored securely using AsyncStorage
- HTTPS connections for all API calls
- No data collection or tracking
- Conversation history stored locally only

## 🐛 Troubleshooting

### Common Issues

**"Failed to start recording"**
- Check microphone permissions in Android settings
- Restart the app

**"No response from LEX"**
- Verify API key is correct
- Check internet connection
- Try toggling between cloud/local server

**"TTS not working"**
- Enable TTS in Android accessibility settings
- Download language packs for offline TTS
- Switch between Native/Qwen TTS

### Debug Mode
Add to App.js for verbose logging:
```javascript
global.__DEV__ = true;
```

## 🚀 Future Enhancements

- [ ] Wake word detection ("Hey LEX")
- [ ] Widget support for quick access
- [ ] Android Auto integration
- [ ] Wear OS companion app
- [ ] Share intent support
- [ ] Camera integration for image analysis
- [ ] Offline mode with cached responses

## 📄 License

This project is part of LexOS and follows the same licensing terms.

## 🤝 Contributing

Contributions are welcome! Please submit issues and pull requests.

## 📞 Support

For help and support:
- Check the [LexOS documentation](https://github.com/lexos)
- Join our community Discord
- Submit issues on GitHub