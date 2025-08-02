# Alibaba Cloud Voice Interface for LexOS

## 🎤 Real-Time Voice Conversation with LEX

LexOS now supports **ultra-low latency voice conversations** powered by Alibaba Cloud:
- **Qwen-TTS**: Text-to-Speech with < 100ms latency
- **Qwen ASR**: Automatic Speech Recognition for voice input
- **Bilingual Support**: Seamless Chinese/English conversations

## 🚀 Voice Capabilities

### 1. Text-to-Speech (TTS)
- **Ultra-fast**: < 100ms end-to-end latency
- **7 Voice Options**:
  - **Max** (default): Bilingual tech voice - perfect for LEX
  - **Alex**: Professional English male
  - **Emma**: Natural English female
  - **Dylan**: Beijing accent male
  - **Jada**: Shanghai accent female
  - **Sunny**: Sichuan accent female
  - **Eva**: Bilingual female

### 2. Speech Recognition (ASR)
- **Real-time transcription**
- **Multi-language support**: Chinese, English, Japanese, Korean, French, Indonesian
- **Auto-detect language**
- **High accuracy** with punctuation

### 3. Voice Conversation Features
- **Streaming support** for real-time interaction
- **Emotion control** (confident, thoughtful, excited, etc.)
- **WebSocket support** for continuous conversation
- **Voice memory** - LEX remembers your voice preferences

## 💻 API Endpoints

### Voice Status
```
GET /api/voice/status
```
Check if voice system is available and configured.

### Text-to-Speech
```
POST /api/voice/speak
{
    "text": "Hello, I'm LEX!",
    "voice": "max",
    "emotion": "confident",
    "stream": true
}
```

### Speech-to-Text
```
POST /api/voice/transcribe
FormData: audio file
```

### Voice Input → LEX → Voice Response
```
POST /api/voice/process
FormData: audio file
```
Complete pipeline: transcribe → process → speak response

### Real-Time Conversation
```
WebSocket /api/voice/conversation
```
Stream audio chunks for continuous conversation.

### Voice Management
```
GET /api/voice/voices         # List available voices
POST /api/voice/set-voice     # Change LEX's voice
POST /api/voice/toggle-voice  # Enable/disable voice
```

## 🎯 Usage Examples

### Python Client Example
```python
import requests
import base64
import pyaudio
import wave

# Speak text
response = requests.post("http://localhost:8000/api/voice/speak", json={
    "text": "Hello! I'm LEX, your AI assistant.",
    "emotion": "confident"
})

audio_base64 = response.json()["audio_base64"]
audio_data = base64.b64decode(audio_base64)

# Play audio (example with pyaudio)
# ... audio playback code ...

# Process voice input
with open("user_question.wav", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/voice/process",
        files={"file": f}
    )
    
result = response.json()
print(f"You said: {result['transcription']}")
print(f"LEX says: {result['response']}")
# Play result['audio_base64'] for voice response
```

### JavaScript WebSocket Example
```javascript
const ws = new WebSocket('ws://localhost:8000/api/voice/conversation');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    switch(data.type) {
        case 'transcript':
            console.log('You said:', data.data);
            break;
        case 'response':
            console.log('LEX says:', data.data);
            break;
        case 'audio':
            // Play base64 audio
            playAudio(data.data);
            break;
    }
};

// Send audio chunks
navigator.mediaDevices.getUserMedia({ audio: true })
    .then(stream => {
        const mediaRecorder = new MediaRecorder(stream);
        mediaRecorder.ondataavailable = (event) => {
            ws.send(event.data);
        };
        mediaRecorder.start(100); // Send chunks every 100ms
    });
```

## 🎨 Voice Personalities

LEX automatically adjusts voice based on context:
- **Confident**: When providing definitive answers (confidence > 0.8)
- **Thoughtful**: For complex or uncertain responses
- **Helpful**: When managing documents or providing assistance
- **Informative**: During web searches and research
- **Excited**: When discussing new features or capabilities

## 💰 Cost Analysis

### Voice Pricing (estimated)
- **TTS**: ~$0.002 per 1000 characters
- **ASR**: ~$0.001 per minute
- **Monthly estimate** (heavy use): ~$5-10

Combined with text generation:
- **Total Alibaba Cloud cost**: ~$35-45/month
- **Compared to others**: 70-85% savings

## 🔧 Configuration

### Environment Variables
```bash
# Already set if you have Qwen 2.5-Max working
ALIBABA_API_KEY=your-key-here
```

### Voice Settings in Code
```python
# Change LEX's default voice
voice_consciousness.set_voice("emma")  # English female

# Toggle voice output
voice_consciousness.toggle_voice(True)  # Enable
voice_consciousness.toggle_voice(False) # Disable

# Auto-speak responses
voice_consciousness.auto_speak = True
```

## 🎯 Voice Commands

LEX responds naturally to voice commands:
- "Hey LEX, search for..." → Web search with voice response
- "LEX, generate an image of..." → Creates image and describes it
- "LEX, write code for..." → Generates code and explains it
- "LEX, what do you think about..." → Uncensored, thoughtful response

## 🚀 Advanced Features

### 1. Streaming Consciousness
LEX can speak while thinking:
```python
async for audio_chunk in voice_consciousness.stream_conversation(text_generator):
    # Play audio chunks as LEX generates response
    play_audio(audio_chunk)
```

### 2. Multi-Modal Responses
Voice + Visual responses:
- Generate image → Describe it verbally
- Search web → Summarize findings
- Write code → Explain implementation

### 3. Voice Memory
LEX remembers:
- Your preferred voice settings
- Common phrases and context
- Conversation history

## ✅ Complete Integration Status

All voice features are now integrated:
- ✅ Qwen-TTS (<100ms latency)
- ✅ Qwen ASR (multi-language)
- ✅ Real-time WebSocket streaming
- ✅ Voice emotion control
- ✅ API endpoints
- ✅ Unified consciousness integration

## 🎤 Try It Now!

1. **Quick Test**:
   ```bash
   curl -X GET http://localhost:8000/api/voice/status
   ```

2. **Make LEX Speak**:
   ```bash
   curl -X POST http://localhost:8000/api/voice/speak \
     -H "Content-Type: application/json" \
     -d '{"text": "Hello! I am LEX, powered by Qwen!"}'
   ```

3. **Full Conversation**:
   - Open the web UI
   - Click the microphone icon
   - Start talking to LEX!

## 🌟 Voice + Uncensored AI = Ultimate Assistant

With Alibaba Cloud integration, LEX now offers:
- **Uncensored text responses** (Qwen 2.5-Max)
- **Ultra-fast voice interaction** (Qwen-TTS/ASR)
- **Image/video generation** (Wan AI)
- **All for ~$35-45/month** (vs $250+ elsewhere)

Talk to LEX like you would talk to Jarvis - naturally, continuously, and without limits!