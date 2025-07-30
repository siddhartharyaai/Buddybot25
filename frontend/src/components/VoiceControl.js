import React, { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { MicrophoneIcon } from '@heroicons/react/24/outline';

const VoiceControl = ({ onStartAmbientListening, onStopAmbientListening, darkMode }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const currentAudioRef = useRef(null);

  const startRecording = async () => {
    try {
      console.log('🎤 Starting recording with proven approach...');
      
      // Request microphone permission using the same config as the working app
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true
        }
      });
      
      console.log('✅ Microphone access granted');
      
      audioChunksRef.current = [];
      
      // Cross-platform audio format detection (copied from working app)
      let mimeType = 'audio/webm;codecs=opus';
      let audioType = 'audio/webm';
      
      if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
        mimeType = 'audio/webm;codecs=opus';
        audioType = 'audio/webm';
      } else if (MediaRecorder.isTypeSupported('audio/mp4')) {
        mimeType = 'audio/mp4';
        audioType = 'audio/mp4';
      } else if (MediaRecorder.isTypeSupported('audio/mpeg')) {
        mimeType = 'audio/mpeg';
        audioType = 'audio/mpeg';
      } else if (MediaRecorder.isTypeSupported('audio/wav')) {
        mimeType = 'audio/wav';
        audioType = 'audio/wav';
      } else {
        // Fallback for older browsers
        mimeType = '';
        audioType = 'audio/wav';
      }
      
      console.log('🎵 Using audio format:', mimeType, 'on', navigator.userAgent.includes('Safari') ? 'Safari' : 'Other browser');
      
      // Create MediaRecorder with the detected format
      const mediaRecorder = new MediaRecorder(stream, mimeType ? { mimeType } : {});
      mediaRecorderRef.current = mediaRecorder;
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
          console.log('📹 Audio chunk recorded:', event.data.size, 'bytes');
        }
      };
      
      mediaRecorder.onstop = async () => {
        console.log('🛑 Recording stopped, processing audio...');
        
        if (audioChunksRef.current.length > 0) {
          const audioBlob = new Blob(audioChunksRef.current, { type: audioType });
          console.log('🎵 Audio blob created:', audioBlob.size, 'bytes, format:', audioType);
          
          // Process the audio using the working approach
          await processVoiceInput(audioBlob);
        }
        
        // Clean up stream
        stream.getTracks().forEach(track => track.stop());
      };
      
      // Start recording with 100ms chunks like the working app
      mediaRecorder.start(100);
      setIsRecording(true);
      
      console.log('✅ Recording started successfully');
      
    } catch (error) {
      console.error('❌ Recording failed:', error);
      alert('Please allow microphone access and try again. Make sure no other app is using your microphone.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      console.log('🎤 Stopping recording...');
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const processVoiceInput = async (audioBlob) => {
    try {
      setIsProcessing(true);
      console.log('🎤 Processing voice input...');
      
      // Validate audio blob (same as working app)
      if (!audioBlob || audioBlob.size === 0) {
        throw new Error('Empty audio data received');
      }
      
      console.log('📱 Audio details:', {
        size: audioBlob.size,
        type: audioBlob.type,
        platform: navigator.userAgent.includes('Mobile') ? 'Mobile' : 'Desktop'
      });
      
      // Check for minimum audio size (same validation as working app)
      if (audioBlob.size < 500) {
        console.warn('⚠️ Audio too small, likely empty recording');
        alert('Recording too short - Please try again');
        return;
      }
      
      // Convert to base64 for transmission (exactly like working app)
      const arrayBuffer = await audioBlob.arrayBuffer();
      const uint8Array = new Uint8Array(arrayBuffer);
      const binaryString = Array.from(uint8Array, byte => String.fromCharCode(byte)).join('');
      const base64Audio = btoa(binaryString);
      
      console.log(`📤 Audio converted: ${base64Audio.length} chars`);
      
      // Call our backend with the same format the working app uses
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/conversations/voice`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: Date.now().toString(),
          user_id: 'test_user',
          audio_base64: base64Audio
        })
      });

      if (response.ok) {
        const data = await response.json();
        console.log('✅ Voice response received:', data.response_text);
        
        // Play TTS audio if available (same as working app)
        if (data.response_audio) {
          playTTSAudio(data.response_audio);
        }
      } else {
        console.error('❌ Voice API error:', response.status);
        const errorText = await response.text();
        console.error('Error details:', errorText);
        alert('Voice processing failed. Please try again.');
      }
      
    } catch (error) {
      console.error('❌ Voice processing error:', error);
      alert('Voice processing failed. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const playTTSAudio = (base64Audio) => {
    try {
      console.log('🔊 Playing TTS audio...');
      
      // Create audio blob - using MP3 format like the working app
      const binaryString = atob(base64Audio);
      const bytes = new Uint8Array(binaryString.length);
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
      }
      
      // Use MP3 type since Deepgram returns MP3 (same as working app)
      const audioBlob = new Blob([bytes], { type: 'audio/mp3' });
      const audioUrl = URL.createObjectURL(audioBlob);
      
      console.log('🎵 Audio Blob created successfully, size:', audioBlob.size, 'bytes');
      
      // Create audio element with mobile-optimized settings (same as working app)
      const audio = new Audio(audioUrl);
      currentAudioRef.current = audio;
      
      // Mobile audio optimization (copied from working app)
      audio.preload = 'auto';
      audio.volume = 1.0;
      
      // iOS requires user interaction for audio context (same as working app)
      if (/iPhone|iPad|iPod|Android/i.test(navigator.userAgent)) {
        console.log('📱 Mobile device detected - enabling audio context');
        if (window.AudioContext || (window as any).webkitAudioContext) {
          try {
            const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
            if (audioContext.state === 'suspended') {
              audioContext.resume();
            }
          } catch (err) {
            console.log('ℹ️ AudioContext not available:', err);
          }
        }
      }
      
      // Promise-based audio playback (same pattern as working app)
      return new Promise((resolve, reject) => {
        audio.addEventListener('ended', () => {
          console.log('✅ Audio playback completed');
          currentAudioRef.current = null;
          URL.revokeObjectURL(audioUrl);
          resolve();
        });
        
        audio.addEventListener('error', (e) => {
          console.error('❌ Audio error:', e, audio.error);
          URL.revokeObjectURL(audioUrl);
          reject(new Error(`Audio playback failed: ${audio.error?.message || 'Unknown error'}`));
        });
        
        // Attempt to play (same as working app)
        console.log('🎵 Attempting to play audio...');
        audio.play().then(() => {
          console.log('✅ Audio playing successfully!');
        }).catch((playError) => {
          console.error('❌ Play failed:', playError);
          if (playError.name === 'NotAllowedError') {
            console.log('🔇 Audio autoplay blocked - will enable on next user interaction');
            
            // Enable audio on next user interaction (same pattern as working app)
            const enableAudio = async () => {
              try {
                await audio.play();
                console.log('✅ Audio playing after user interaction!');
                document.removeEventListener('click', enableAudio);
                document.removeEventListener('touchstart', enableAudio);
              } catch (retryError) {
                console.error('❌ Still failed after user interaction:', retryError);
                URL.revokeObjectURL(audioUrl);
                reject(new Error('Cannot play audio even with user interaction'));
              }
            };
            
            // Listen for ANY user interaction to enable audio
            document.addEventListener('click', enableAudio, { once: true });
            document.addEventListener('touchstart', enableAudio, { once: true });
          } else {
            URL.revokeObjectURL(audioUrl);
            reject(playError);
          }
        });
      });
      
    } catch (error) {
      console.error('❌ TTS playback error:', error);
    }
  };

  const handleClick = () => {
    if (isRecording) {
      stopRecording();
    } else if (!isProcessing) {
      startRecording();
    }
  };

  const getButtonStyle = () => {
    if (isProcessing) {
      return 'bg-yellow-500 text-white shadow-lg shadow-yellow-500/25 animate-pulse';
    } else if (isRecording) {
      return 'bg-red-500 text-white shadow-lg shadow-red-500/25 animate-pulse';
    } else {
      return darkMode 
        ? 'bg-gray-700 text-gray-300 hover:bg-blue-600 hover:text-white' 
        : 'bg-blue-500 text-white hover:bg-blue-600';
    }
  };

  const getStatusText = () => {
    if (isProcessing) return 'Processing...';
    if (isRecording) return 'Recording - Click to stop';
    return 'Click to record';
  };

  return (
    <div className="flex flex-col items-center space-y-2">
      <motion.button
        type="button"
        onClick={handleClick}
        disabled={isProcessing}
        whileHover={{ scale: isProcessing ? 1 : 1.05 }}
        whileTap={{ scale: isProcessing ? 1 : 0.95 }}
        className={`p-4 rounded-full transition-all duration-300 ${getButtonStyle()}`}
        title={getStatusText()}
      >
        <MicrophoneIcon className="w-6 h-6" />
      </motion.button>
      
      <div className={`text-xs px-3 py-1 rounded-full ${
        isRecording 
          ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
          : isProcessing
          ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
          : 'bg-blue-100 text-blue-600 dark:bg-blue-900 dark:text-blue-200'
      }`}>
        {getStatusText()}
      </div>

      <div className={`text-xs text-center max-w-xs ${
        darkMode ? 'text-gray-400' : 'text-gray-500'
      }`}>
        {!isRecording && !isProcessing && 'Click to record your message'}
        {isRecording && 'Speak now, click again to stop'}
        {isProcessing && 'Processing your voice...'}
      </div>
    </div>
  );
};

export default VoiceControl;