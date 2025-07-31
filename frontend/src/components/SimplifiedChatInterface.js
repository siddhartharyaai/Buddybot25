import React, { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  MicrophoneIcon, 
  StopIcon, 
  SpeakerWaveIcon,
  SpeakerXMarkIcon,
  SparklesIcon,
  ChatBubbleLeftEllipsisIcon,
  SunIcon,
  MoonIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

const SimplifiedChatInterface = ({ user, darkMode, setDarkMode, sessionId, messages, onAddMessage }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isBotSpeaking, setIsBotSpeaking] = useState(false);
  const [currentTranscript, setCurrentTranscript] = useState('');
  const [recordingTimer, setRecordingTimer] = useState(0);
  const [streamReady, setStreamReady] = useState(false);
  const [audioContext, setAudioContext] = useState(null);
  
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const messagesEndRef = useRef(null);
  const audioRef = useRef(null);
  const recordingIntervalRef = useRef(null);
  const streamRef = useRef(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Initialize microphone stream on component mount (Grok's recommendation)
  useEffect(() => {
    const initializeMicrophone = async () => {
      try {
        console.log('🎤 Initializing microphone stream...');
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: {
            sampleRate: 16000,
            channelCount: 1,
            echoCancellation: true,
            noiseSuppression: true
          }
        });
        
        streamRef.current = stream;
        setStreamReady(true);
        console.log('✅ Microphone stream ready');
      } catch (error) {
        console.error('❌ Failed to initialize microphone:', error);
        setStreamReady(false);
      }
    };

    initializeMicrophone();

    // Cleanup on unmount
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
        streamRef.current = null;
      }
    };
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Voice-only suggestions
  const suggestions = [
    "Tell me a story",
    "Sing me a song", 
    "Ask me a riddle",
    "Let's play a game"
  ];

  // Simplified recording based on working GitHub repository
  const startRecording = async () => {
    if (!streamRef.current || isLoading) {
      console.log('⚠️ Stream not ready or loading');
      return;
    }

    // Resume audio context on user gesture (important for mobile)
    await resumeAudioContext();
    
    console.log('🎤 Starting recording...');
    setIsRecording(true);

    // Barge-in feature - stop any playing audio
    if (isBotSpeaking) {
      console.log('🔀 Barge-in: Interrupting bot speech');
      stopAudio();
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.currentTime = 0;
        audioRef.current.src = '';
      }
      setIsBotSpeaking(false);
      setIsPlaying(false);
    }

    try {
      audioChunksRef.current = [];

      // Simple MediaRecorder setup like working repository
      const mediaRecorder = new MediaRecorder(streamRef.current, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
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
          const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
          console.log('🎵 Audio blob created:', audioBlob.size, 'bytes');

          // Process the audio directly without creating temporary message here
          // (temporary message will be created in sendVoiceMessage)
          await sendVoiceMessage(audioBlob);
        }
      };

      // Start recording with timeslice as Grok recommended
      mediaRecorder.start(100);
      console.log('✅ Recording started successfully');

      // Start recording timer
      recordingIntervalRef.current = setInterval(() => {
        setRecordingTimer(prev => prev + 1);
      }, 1000);

    } catch (error) {
      console.error('❌ Failed to start recording:', error);
      setIsRecording(false);
      toast.error('Recording failed. Please try again.');
    }
  };

  const stopRecording = () => {
    console.log('🔇 Stopping recording...');
    setIsRecording(false);
    setRecordingTimer(0);

    // Clear recording timer
    if (recordingIntervalRef.current) {
      clearInterval(recordingIntervalRef.current);
      recordingIntervalRef.current = null;
    }

    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
    }
  };

  const sendVoiceMessage = async (audioBlob) => {
    console.log('🎵 Sending voice message, blob size:', audioBlob.size, 'type:', audioBlob.type);
    
    // Enhanced validation with detailed logging
    if (!audioBlob) {
      console.error('❌ Audio blob is null/undefined');
      toast.error('🎤 Recording failed - no audio captured. Please try again.');
      return;
    }
    
    if (audioBlob.size === 0) {
      console.error('❌ Audio blob size is 0');
      toast.error('🎤 Recording failed - empty audio. Please speak louder and hold the mic button longer.');
      return;
    }

    // More forgiving size threshold for mobile
    const isMobile = /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    const minSize = isMobile ? 500 : 1000; // Lower threshold for mobile
    
    if (audioBlob.size < minSize) {
      console.warn('⚠️ Audio blob very small:', audioBlob.size, 'bytes');
      // Don't block on mobile - try to process anyway
      if (!isMobile) {
        toast.error('Recording too short. Please hold the mic button and speak for at least 1 second.');
        return;
      }
    }
    
    console.log('✅ Audio blob validation passed');
    
    // Create temporary user message for processing
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: '🎤 Processing voice...',
      isVoice: true,
      timestamp: new Date()
    };

    onAddMessage(userMessage);
    setIsLoading(true);

    try {
      // Enhanced mobile-compatible base64 conversion
      console.log('🔄 Converting audio to base64...');
      
      // Method 1: ArrayBuffer conversion (more reliable on mobile)
      let base64Audio;
      try {
        const arrayBuffer = await audioBlob.arrayBuffer();
        console.log('📦 ArrayBuffer size:', arrayBuffer.byteLength);
        
        const uint8Array = new Uint8Array(arrayBuffer);
        base64Audio = btoa(String.fromCharCode(...uint8Array));
        console.log('✅ ArrayBuffer to base64 conversion successful, length:', base64Audio.length);
      } catch (arrayBufferError) {
        console.warn('⚠️ ArrayBuffer method failed, trying FileReader:', arrayBufferError);
        
        // Method 2: FileReader fallback
        try {
          base64Audio = await new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onloadend = () => {
              try {
                const result = reader.result;
                if (!result || typeof result !== 'string') {
                  reject(new Error('FileReader result is not a string'));
                  return;
                }
                const base64 = result.split(',')[1];
                if (!base64 || base64.length === 0) {
                  reject(new Error('Base64 extraction failed'));
                  return;
                }
                resolve(base64);
              } catch (error) {
                reject(error);
              }
            };
            reader.onerror = () => reject(new Error('FileReader error'));
            reader.readAsDataURL(audioBlob);
          });
          console.log('✅ FileReader to base64 conversion successful, length:', base64Audio.length);
        } catch (fileReaderError) {
          console.error('❌ Both conversion methods failed:', fileReaderError);
          throw new Error('Audio conversion failed');
        }
      }
      
      if (!base64Audio || base64Audio.length === 0) {
        throw new Error('Base64 conversion resulted in empty string');
      }
      
      console.log('📡 Sending to backend...');
      
      // Create form data with proper content type
      const formData = new FormData();
      formData.append('session_id', sessionId);
      formData.append('user_id', user.id);
      formData.append('audio_base64', base64Audio);

      console.log('🌐 Making API call to voice endpoint...');
      
      // SMART AUTO-SELECTION: Choose optimal pipeline based on user's voice input
      // Note: We'll let the backend transcript determine this, but we can add frontend intelligence too
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/voice/process_audio`, {
        method: 'POST',
        body: formData
      });

      console.log('📨 Response status:', response.status);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('❌ API error response:', errorText);
        throw new Error(`Server error: ${response.status} - ${errorText}`);
      }
      
      const data = await response.json();
      console.log('✅ Voice processing response:', data);
      
      if (data.status === 'success') {
        // Add AI response
        const aiMessage = {
          id: Date.now() + 1,
          type: 'ai',
          content: data.response_text || 'I heard you!',
          audioData: data.response_audio,
          contentType: data.content_type,
          metadata: data.metadata,
          timestamp: new Date()
        };

        onAddMessage(aiMessage);
        
        // ENHANCED AUDIO HANDLING: Check if 'audio_base64' in msg, convert to Blob, create Audio, play() with catch for errors
        console.log('🎵 FRONTEND AUDIO CHECK: response_audio present:', !!data.response_audio);
        console.log('🎵 FRONTEND AUDIO CHECK: response_audio length:', data.response_audio ? data.response_audio.length : 0);
        
        if (data.response_audio && data.response_audio.length > 0) {
          console.log('🎵 FRONTEND AUDIO: Auto-playing AI response audio');
          try {
            await playAudio(data.response_audio);
          } catch (audioError) {
            console.error('🎵 FRONTEND AUDIO ERROR: Auto-play failed:', audioError);
            // Add fallback button notification
            toast.error('🔊 Audio ready - tap speaker icon to play', {
              duration: 5000,
            });
          }
        } else {
          console.error('🎵 FRONTEND AUDIO ERROR: No audio data in response!');
          console.log('🎵 FRONTEND AUDIO DEBUG: Full response data:', JSON.stringify(data, null, 2));
          toast.error('🔊 No audio: Missing audio data');
        }
        
        toast.success('🎉 Voice message processed!');
      } else {
        throw new Error(data.detail || data.message || 'Voice processing failed');
      }
      
    } catch (error) {
      console.error('💥 Voice message error:', error);
      
      // More specific error messages
      let errorMessage = '🎤 Voice processing failed. ';
      if (error.message.includes('conversion failed')) {
        errorMessage += 'Audio format issue - please try again.';
      } else if (error.message.includes('Server error')) {
        errorMessage += 'Server issue - please check your connection.';
      } else if (error.message.includes('fetch')) {
        errorMessage += 'Network error - please check your internet connection.';
      } else {
        errorMessage += 'Please try speaking louder and holding the mic button longer.';
      }
      
      toast.error(errorMessage);
      
      // Add error message since we can't update existing message
      const errorMsg = {
        id: Date.now() + 1,
        type: 'system',
        content: '❌ Voice processing failed - try again',
        timestamp: new Date()
      };
      onAddMessage(errorMsg);
    } finally {
      setIsLoading(false);
    }
  };

  // Voice-only interface - no text messaging functionality

  // Initialize audio context for better mobile support
  useEffect(() => {
    const initAudioContext = () => {
      try {
        const AudioContextClass = window.AudioContext || window.webkitAudioContext;
        const ctx = new AudioContextClass();
        setAudioContext(ctx);
        console.log('🎵 Audio context initialized');
      } catch (error) {
        console.warn('⚠️ Audio context initialization failed:', error);
      }
    };
    
    initAudioContext();
  }, []);

  // Resume audio context on user gesture
  const resumeAudioContext = async () => {
    if (audioContext && audioContext.state === 'suspended') {
      try {
        await audioContext.resume();
        console.log('🔊 Audio context resumed');
      } catch (error) {
        console.error('❌ Failed to resume audio context:', error);
      }
    }
  };

  const playAudio = async (base64Audio) => {
    if (!base64Audio || base64Audio === "") {
      console.warn('⚠️ No audio data provided for playback');
      toast.error('🔊 No audio: Empty audio data');
      return;
    }
    
    // Resume audio context if suspended (mobile fix)
    await resumeAudioContext();
    
    if (audioRef.current) {
      audioRef.current.pause();
    }
    
    try {
      console.log('🎵 Starting audio playback, audio length:', base64Audio.length);
      
      // Check blob size >0 before proceeding
      if (base64Audio.length === 0) {
        console.error('🎵 CRITICAL: Audio blob size is 0!');
        toast.error('🔊 No audio: Empty blob (size=0)');
        return;
      }
      
      // ENHANCED BLOB CONVERSION: Convert audio_base64 to Blob using atob/Uint8Array, set type='audio/mpeg'
      console.log('🎵 BLOB CONVERSION: Converting base64 to audio blob...');
      
      // Decode base64 to binary
      const binaryString = atob(base64Audio);
      const uint8Array = new Uint8Array(binaryString.length);
      
      // Convert binary string to Uint8Array
      for (let i = 0; i < binaryString.length; i++) {
        uint8Array[i] = binaryString.charCodeAt(i);
      }
      
      // Create blob with proper audio type
      const audioBlob = new Blob([uint8Array], { type: 'audio/mpeg' });
      const audioUrl = URL.createObjectURL(audioBlob);
      
      console.log('🎵 BLOB CONVERSION: Audio blob created, size:', audioBlob.size, 'bytes');
      
      // Log blob size >0 
      if (audioBlob.size === 0) {
        console.error('🎵 CRITICAL: Audio blob created but size is 0 bytes!');
        toast.error('🔊 No audio: Blob conversion failed (size=0)');
        return;
      }
      
      // Create Audio element
      audioRef.current = new Audio(audioUrl);
      
      // ENHANCED ERROR HANDLING: Call play() with catch for 'NotAllowedError'
      console.log('🎵 PLAYBACK: Attempting audio.play()...');
      audioRef.current.play().then(() => {
        console.log('✅ Audio playback started successfully');
        setIsPlaying(true);
        setIsBotSpeaking(true);
      }).catch(err => {
        console.error('❌ Audio playback failed:', err);
        console.log('🎵 AUDIO ERROR TYPE:', err.name);
        console.log('🎵 AUDIO ERROR MESSAGE:', err.message);
        
        // Enhanced error handling for autoplay restrictions
        if (err.name === 'NotAllowedError') {
          console.log('🚫 NotAllowedError: Autoplay blocked - need user gesture');
          toast.error('🔊 Audio ready - tap speaker icon to play', {
            duration: 5000,
          });
          // Store audio for manual playback
          audioRef.current._manualPlayReady = true;
        } else if (err.name === 'NotSupportedError') {
          console.error('🚫 Audio format not supported');
          toast.error('🔊 No audio: Format not supported');
        } else {
          console.error('🚫 General audio error:', err);
          toast.error('🔊 No audio: Playback error - tap speaker icon');
        }
      });
      
      audioRef.current.onended = () => {
        console.log('🎵 Audio playback completed');
        setIsPlaying(false);
        setIsBotSpeaking(false);
        URL.revokeObjectURL(audioUrl);
      };
      
      audioRef.current.onerror = (err) => {
        console.error('❌ Audio error:', err);
        console.log('🎵 AUDIO ELEMENT ERROR:', err);
        setIsPlaying(false);
        setIsBotSpeaking(false);
        URL.revokeObjectURL(audioUrl);
        toast.error('🔊 No audio: Audio element error');
      };
      
    } catch (error) {
      console.error('❌ Audio blob creation failed:', error);
      console.log('🎵 BLOB CREATION ERROR:', error.message);
      toast.error('🔊 No audio: Processing failed');
    }
  };

  const stopAudio = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      setIsPlaying(false);
      setIsBotSpeaking(false);
    }
  };

  const formatTime = (timestamp) => {
    // Ensure timestamp is a Date object
    const date = timestamp instanceof Date ? timestamp : new Date(timestamp);
    // Handle invalid dates
    if (isNaN(date.getTime())) {
      return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  // Unified pointer event handlers (Grok's recommendation)
  const handlePointerDown = (e) => {
    console.log('👆 Pointer down detected');
    e.preventDefault();
    e.stopPropagation();
    
    if (!streamReady || isLoading) {
      console.log('⚠️ Stream not ready or loading');
      return;
    }
    
    if (!isRecording) {
      console.log('▶️ Starting recording via pointer');
      startRecording();
    }
  };

  const handlePointerUp = (e) => {
    console.log('👆 Pointer up detected');
    e.preventDefault();
    e.stopPropagation();
    
    if (isRecording) {
      console.log('🔴 Stopping recording via pointer');
      stopRecording();
    }
  };

  const handlePointerLeave = (e) => {
    console.log('👆 Pointer leave detected');
    
    if (isRecording) {
      console.log('🔴 Stopping recording due to pointer leave');
      stopRecording();
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (recordingIntervalRef.current) {
        clearInterval(recordingIntervalRef.current);
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  // Dynamic background based on bot speaking
  const getBackgroundClass = () => {
    const base = darkMode 
      ? 'bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900'
      : 'bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50';
    
    if (isBotSpeaking) {
      return darkMode 
        ? 'bg-gradient-to-br from-purple-900 via-pink-900 to-orange-900'
        : 'bg-gradient-to-br from-yellow-100 via-orange-100 to-pink-100';
    }
    
    return base;
  };

  return (
    <div className={`h-full ${getBackgroundClass()} transition-all duration-1000`}>
      {/* Full Height Chat Interface - No more split panel layout */}
      <div className="h-full flex flex-col">
        
        {/* Header */}
        <div className={`flex-shrink-0 p-4 border-b ${darkMode ? 'border-gray-700 bg-gray-900' : 'border-gray-200 bg-gray-50'}`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <ChatBubbleLeftEllipsisIcon className={`w-6 h-6 ${darkMode ? 'text-blue-400' : 'text-blue-600'}`} />
              <h3 className="text-lg font-semibold">Chat with Buddy 🤖</h3>
              
              {/* Recording Status Indicator */}
              {isRecording && (
                <motion.div 
                  className="flex items-center space-x-2 text-red-500"
                  animate={{ opacity: [1, 0.5, 1] }}
                  transition={{ duration: 1, repeat: Infinity }}
                >
                  <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                  <span className="text-sm font-medium">Recording {recordingTimer}s</span>
                </motion.div>
              )}
              
              {/* Bot Speaking Indicator */}
              {isBotSpeaking && (
                <motion.div 
                  className="flex items-center space-x-2 text-blue-500"
                  animate={{ opacity: [1, 0.7, 1] }}
                  transition={{ duration: 0.8, repeat: Infinity }}
                >
                  <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                  <span className="text-sm font-medium">Speaking...</span>
                </motion.div>
              )}
            </div>
            
            <button
              onClick={() => setDarkMode(!darkMode)}
              className={`p-2 rounded-full transition-colors ${
                darkMode ? 'bg-gray-700 text-yellow-400 hover:bg-gray-600' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {darkMode ? <SunIcon className="w-5 h-5" /> : <MoonIcon className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {/* Messages Area - Full Height */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="text-center py-12">
              {/* Animated Bot Avatar - Smaller and Centered */}
              <motion.div
                className={`mx-auto w-32 h-32 rounded-full flex items-center justify-center mb-6 ${
                  darkMode ? 'bg-gradient-to-br from-blue-600 to-purple-700' : 'bg-gradient-to-br from-blue-500 to-purple-600'
                }`}
                animate={{
                  scale: isBotSpeaking ? [1, 1.05, 1] : [1, 1.02, 1],
                }}
                transition={{
                  scale: { duration: 2, repeat: Infinity, ease: "easeInOut" },
                }}
              >
                {/* Eyes */}
                <div className="flex space-x-4">
                  <motion.div 
                    className="w-4 h-8 bg-white rounded-full"
                    animate={{
                      scaleY: isBotSpeaking ? [1, 0.3, 1] : [1, 0.8, 1]
                    }}
                    transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                  />
                  <motion.div 
                    className="w-4 h-8 bg-white rounded-full"
                    animate={{
                      scaleY: isBotSpeaking ? [1, 0.3, 1] : [1, 0.8, 1]
                    }}
                    transition={{ duration: 2, repeat: Infinity, ease: "easeInOut", delay: 0.1 }}
                  />
                </div>
              </motion.div>
              
              <h4 className={`text-xl font-semibold mb-2 ${darkMode ? 'text-gray-200' : 'text-gray-800'}`}>
                Hi {user?.name || 'there'}! 👋
              </h4>
              <p className={`${darkMode ? 'text-gray-400' : 'text-gray-600'} mb-6 text-lg`}>
                {isRecording ? `Recording ${recordingTimer}s...` : 
                 isBotSpeaking ? '🔴 Tap mic to interrupt and speak' :
                 'Press and hold the microphone button below to start talking!'}
              </p>
              
              <div className="flex flex-col space-y-2 max-w-md mx-auto">
                <p className={`text-center text-sm mb-3 ${darkMode ? 'text-gray-500' : 'text-gray-500'}`}>
                  Try saying:
                </p>
                {suggestions.map((suggestion, index) => (
                  <div
                    key={index}
                    className={`px-4 py-2 rounded-full text-sm text-center ${
                      darkMode 
                        ? 'bg-blue-900 text-blue-200' 
                        : 'bg-blue-50 text-blue-600'
                    }`}
                  >
                    "{suggestion}"
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <AnimatePresence>
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className="max-w-sm">
                    <div
                      className={`px-4 py-3 rounded-2xl ${
                        message.type === 'user'
                          ? darkMode 
                            ? 'bg-gradient-to-r from-blue-600 to-purple-700 text-white'
                            : 'bg-gradient-to-r from-blue-500 to-purple-600 text-white'
                          : darkMode
                          ? 'bg-gray-700 text-gray-100'
                          : 'bg-gray-100 text-gray-900'
                      }`}
                    >
                      <div className="flex items-start space-x-2">
                        {message.type === 'ai' && (
                          <span className="text-xl">🤖</span>
                        )}
                        {message.type === 'user' && (
                          <span className="text-xl">👶</span>
                        )}
                        <p className="text-sm leading-relaxed">{message.content}</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between mt-1 px-2">
                      <span className={`text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                        {formatTime(message.timestamp)}
                      </span>
                      
                      {message.audioData && (
                        <button
                          onClick={() => playAudio(message.audioData)}
                          className={`p-1 rounded transition-colors ${
                            darkMode 
                              ? 'text-blue-400 hover:text-blue-300 hover:bg-gray-700' 
                              : 'text-blue-500 hover:text-blue-600 hover:bg-blue-50'
                          }`}
                        >
                          <SpeakerWaveIcon className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          )}
          
          {/* Loading Animation */}
          {isLoading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex justify-start"
            >
              <div className={`px-4 py-3 rounded-2xl ${
                darkMode ? 'bg-gray-700' : 'bg-gray-100'
              }`}>
                <div className="flex items-center space-x-2">
                  <span className="text-xl">🤖</span>
                  <div className="flex space-x-1">
                    <div className={`w-2 h-2 rounded-full animate-bounce ${
                      darkMode ? 'bg-blue-400' : 'bg-blue-500'
                    }`}></div>
                    <div className={`w-2 h-2 rounded-full animate-bounce ${
                      darkMode ? 'bg-blue-400' : 'bg-blue-500'
                    }`} style={{ animationDelay: '0.1s' }}></div>
                    <div className={`w-2 h-2 rounded-full animate-bounce ${
                      darkMode ? 'bg-blue-400' : 'bg-blue-500'
                    }`} style={{ animationDelay: '0.2s' }}></div>
                  </div>
                  <span className={`text-sm ${darkMode ? 'text-gray-300' : 'text-gray-600'}`}>
                    Thinking...
                  </span>
                </div>
              </div>
            </motion.div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Bottom Voice-Only Interface - No Text Input */}
        <div className={`flex-shrink-0 border-t ${darkMode ? 'border-gray-700 bg-gray-900' : 'border-gray-200 bg-gray-50'}`}>
          
          {/* Large Centered Microphone Button - Cross-Platform */}
          <div className="px-4 py-8">
            <div className="flex flex-col items-center">
              <motion.button
                // Unified pointer events as Grok recommended
                onPointerDown={handlePointerDown}
                onPointerUp={handlePointerUp}
                onPointerLeave={handlePointerLeave}
                onContextMenu={(e) => e.preventDefault()}
                tabIndex="0"
                className={`relative w-24 h-24 rounded-full transition-all duration-200 select-none shadow-lg flex items-center justify-center ${
                  isRecording 
                    ? 'bg-gradient-to-br from-red-500 to-red-600 text-white scale-110 shadow-red-500/50' 
                    : isBotSpeaking
                    ? 'bg-gradient-to-br from-orange-500 to-orange-600 text-white animate-pulse shadow-orange-500/50'
                    : darkMode
                    ? 'bg-gradient-to-br from-blue-600 to-blue-700 text-white hover:from-blue-500 hover:to-blue-600 shadow-blue-600/30'
                    : 'bg-gradient-to-br from-blue-500 to-blue-600 text-white hover:from-blue-400 hover:to-blue-500 shadow-blue-500/30'
                } ${isLoading ? 'opacity-50' : ''}`}
                disabled={false} // Key insight from working repo
                type="button"
                aria-label="Press and hold to record voice message"
                style={{ 
                  WebkitUserSelect: 'none',
                  WebkitTouchCallout: 'none',
                  WebkitTapHighlightColor: 'transparent',
                  touchAction: 'manipulation', // Grok's recommendation
                  userSelect: 'none',
                  outline: 'none',
                  position: 'relative',
                  zIndex: 50
                }}
                whileHover={{ scale: isLoading ? 1 : 1.05 }}
                whileTap={{ scale: isLoading ? 1 : 0.95 }}
                animate={{
                  boxShadow: isRecording 
                    ? ['0 0 0 0 rgba(239, 68, 68, 0.4)', '0 0 0 30px rgba(239, 68, 68, 0)', '0 0 0 0 rgba(239, 68, 68, 0.4)']
                    : ['0 0 0 0 rgba(59, 130, 246, 0.3)', '0 0 0 15px rgba(59, 130, 246, 0)', '0 0 0 0 rgba(59, 130, 246, 0.3)']
                }}
                transition={{
                  boxShadow: { duration: isRecording ? 1 : 2, repeat: Infinity, ease: "easeOut" }
                }}
              >
                {isRecording ? (
                  <div className="flex flex-col items-center justify-center">
                    <StopIcon className="w-10 h-10 mb-1" />
                    <span className="text-sm font-bold">{recordingTimer}s</span>
                  </div>
                ) : (
                  <MicrophoneIcon className="w-10 h-10" />
                )}
                
                {/* Enhanced Pulsing Animation Ring */}
                <AnimatePresence>
                  {!isLoading && (
                    <motion.div
                      className={`absolute inset-0 rounded-full border-4 ${
                        isRecording ? 'border-red-300' : 'border-blue-300'
                      }`}
                      initial={{ scale: 1, opacity: 0.8 }}
                      animate={{ scale: 2, opacity: 0 }}
                      exit={{ opacity: 0 }}
                      transition={{ 
                        duration: isRecording ? 1 : 2, 
                        repeat: Infinity, 
                        ease: "easeOut" 
                      }}
                    />
                  )}
                </AnimatePresence>
              </motion.button>
              
              {/* Voice-Only Instructions - Simplified */}
              <div className="text-center mt-4">
                <p className={`text-lg font-medium mb-2 ${darkMode ? 'text-gray-200' : 'text-gray-800'}`}>
                  {!streamReady 
                    ? '🎤 Preparing microphone...'
                    : isRecording 
                    ? `🎤 Recording ${recordingTimer}s - Release to send` 
                    : isBotSpeaking
                    ? '🔴 Press to interrupt and speak'
                    : '🎤 Press and hold to speak'}
                </p>
                <p className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-600'}`}>
                  {streamReady && !isRecording && !isBotSpeaking && 
                    'Voice-only AI companion - hold button to talk!'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SimplifiedChatInterface;