import { Audio } from 'expo-av';
import * as FileSystem from 'expo-file-system';

export class AudioUtils {
  static async setupAudio() {
    try {
      await Audio.requestPermissionsAsync();
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
        staysActiveInBackground: true,
        shouldDuckAndroid: true,
        playThroughEarpieceAndroid: false,
      });
    } catch (error) {
      console.error('Audio setup error:', error);
      throw error;
    }
  }

  static async startRecording() {
    try {
      const { recording } = await Audio.Recording.createAsync({
        ...Audio.RecordingOptionsPresets.HIGH_QUALITY,
        android: {
          extension: '.wav',
          outputFormat: Audio.RECORDING_OPTION_ANDROID_OUTPUT_FORMAT_DEFAULT,
          audioEncoder: Audio.RECORDING_OPTION_ANDROID_AUDIO_ENCODER_DEFAULT,
          sampleRate: 16000,
          numberOfChannels: 1,
          bitRate: 128000,
        },
        ios: {
          extension: '.wav',
          audioQuality: Audio.RECORDING_OPTION_IOS_AUDIO_QUALITY_HIGH,
          sampleRate: 16000,
          numberOfChannels: 1,
          bitRate: 128000,
          linearPCMBitDepth: 16,
          linearPCMIsBigEndian: false,
          linearPCMIsFloat: false,
        },
      });
      
      return recording;
    } catch (error) {
      console.error('Start recording error:', error);
      throw error;
    }
  }

  static async stopRecording(recording) {
    try {
      await recording.stopAndUnloadAsync();
      const uri = recording.getURI();
      
      // Convert to base64
      const base64 = await FileSystem.readAsStringAsync(uri, {
        encoding: FileSystem.EncodingType.Base64,
      });
      
      // Clean up the file
      await FileSystem.deleteAsync(uri, { idempotent: true });
      
      return base64;
    } catch (error) {
      console.error('Stop recording error:', error);
      throw error;
    }
  }

  static async playAudioFromBase64(base64Audio) {
    try {
      const audioUri = FileSystem.documentDirectory + 'temp_audio.mp3';
      
      await FileSystem.writeAsStringAsync(audioUri, base64Audio, {
        encoding: FileSystem.EncodingType.Base64,
      });
      
      const { sound } = await Audio.Sound.createAsync({ uri: audioUri });
      
      return new Promise((resolve, reject) => {
        sound.setOnPlaybackStatusUpdate((status) => {
          if (status.didJustFinish) {
            sound.unloadAsync();
            FileSystem.deleteAsync(audioUri, { idempotent: true });
            resolve();
          }
          if (status.error) {
            reject(status.error);
          }
        });
        
        sound.playAsync().catch(reject);
      });
    } catch (error) {
      console.error('Play audio error:', error);
      throw error;
    }
  }
}