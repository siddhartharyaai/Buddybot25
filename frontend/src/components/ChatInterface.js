import React, { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  MicrophoneIcon, 
  StopIcon, 
  PaperAirplaneIcon,
  SpeakerWaveIcon,
  SpeakerXMarkIcon,
  SparklesIcon,
  ChatBubbleLeftEllipsisIcon,
  EyeIcon,
  EyeSlashIcon,
  SunIcon,
  MoonIcon,
  Cog6ToothIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import TextInput from './TextInput';
import VoiceControl from './VoiceControl';

const ChatInterface = ({ user, darkMode, setDarkMode, sessionId, onSendMessage }) => {
  const [isAmbientListening, setIsAmbientListening] = useState(false);
  const [isConversationActive, setIsConversationActive] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [listeningState, setListeningState] = useState('inactive'); // inactive, ambient, active
  const [wakeWordDetected, setWakeWordDetected] = useState(false);
  const [isBotSpeaking, setIsBotSpeaking] = useState(false);
  const [currentTranscript, setCurrentTranscript] = useState('');
  const [botMood, setBotMood] = useState('friendly'); // friendly, excited, calm, thinking
  
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const messagesEndRef = useRef(null);
  const audioRef = useRef(null);
  const ambientRecorderRef = useRef(null);
  const ambientIntervalRef = useRef(null);

  const suggestions = [
    "Tell me a story",
    "Sing a song", 
    "What's a fun fact?",
    "Let's play a game",
    "Help me learn something"
  ];

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    console.log('🎯 ChatInterface component mounted - NOT auto-starting ambient listening');
    
    // Don't auto-start ambient listening - wait for user gesture
    setListeningState('inactive');
    
    // Cleanup on unmount
    return () => {
      stopAmbientListening();
      if (ambientIntervalRef.current) {
        clearInterval(ambientIntervalRef.current);
      }
    };
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const startAmbientListening = async (stream) => {
    try {
      console.log('🎤 Starting ambient listening with provided stream...');
      console.log('User ID:', user?.id);
      console.log('Session ID:', sessionId);
      
      // Start ambient listening on server
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/ambient/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          user_id: user?.id || user?.user_id || 'test_user'
        })
      });

      if (response.ok) {
        setIsAmbientListening(true);
        setListeningState('ambient');
        
        // Start continuous audio processing with the provided stream
        startContinuousAudioProcessing(stream);
        
        toast.success('🎤 Voice activated! Say "Hey Buddy" to start chatting.');
        console.log('✅ Ambient listening started successfully');
        return true; // Return success
      } else {
        const errorData = await response.json();
        console.error('❌ Server error starting ambient listening:', errorData);
        throw new Error(`Failed to start ambient listening: ${errorData.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('❌ Error starting ambient listening:', error);
      setListeningState('inactive');
      toast.error('Failed to start voice features. Please try again.');
      return false; // Return failure
    }
  };

  const stopAmbientListening = async () => {
    try {
      await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/ambient/stop`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId
        })
      });

      setIsAmbientListening(false);
      setIsConversationActive(false);
      setListeningState('inactive');
      
      // Stop audio processing
      if (ambientRecorderRef.current) {
        ambientRecorderRef.current.stop();
      }
      
      if (ambientIntervalRef.current) {
        clearInterval(ambientIntervalRef.current);
      }
    } catch (error) {
      console.error('Error stopping ambient listening:', error);
    }
  };

  // Stop continuous audio processing to prevent re-renders
  const startContinuousAudioProcessing = (stream) => {
    console.log('🎤 Starting continuous audio processing...');
    
    ambientRecorderRef.current = new MediaRecorder(stream, {
      mimeType: 'audio/webm;codecs=opus'
    });

    ambientRecorderRef.current.ondataavailable = (event) => {
      if (event.data.size > 0) {
        // Only process audio if we're still in ambient listening mode
        if (isAmbientListening && listeningState === 'ambient') {
          processAmbientAudio(event.data);
        }
      }
    };

    ambientRecorderRef.current.start(2000); // 2-second chunks
    
    // Set up interval to restart recording (prevent memory issues)
    ambientIntervalRef.current = setInterval(() => {
      if (ambientRecorderRef.current && isAmbientListening) {
        try {
          ambientRecorderRef.current.stop();
          setTimeout(() => {
            if (ambientRecorderRef.current && isAmbientListening) {
              ambientRecorderRef.current.start(2000);
            }
          }, 100);
        } catch (error) {
          console.error('Error restarting recorder:', error);
        }
      }
    }, 10000); // Restart every 10 seconds instead of processing continuously
  };

  const processAmbientAudio = async (audioData) => {
    try {
      let base64Audio;
      
      // Handle different audio data types
      if (typeof audioData === 'string') {
        base64Audio = audioData;
      } else {
        // Convert Blob to base64
        const reader = new FileReader();
        return new Promise((resolve) => {
          reader.onloadend = async () => {
            base64Audio = reader.result.split(',')[1];
            await sendAudioToBackend(base64Audio);
            resolve();
          };
          reader.readAsDataURL(audioData);
        });
      }
      
      await sendAudioToBackend(base64Audio);
    } catch (error) {
      console.error('Error processing ambient audio:', error);
    }
  };
  
  const sendAudioToBackend = async (base64Audio) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/ambient/process`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          audio_base64: base64Audio
        })
      });

      if (response.ok) {
        const data = await response.json();
        handleAmbientResponse(data);
      } else {
        console.warn('Ambient processing request failed:', response.status);
      }
    } catch (error) {
      console.error('Error sending audio to backend:', error);
    }
  };

  const handleAmbientResponse = (data) => {
    const { status, transcript, listening_state, conversation_response, has_response } = data;
    
    // Only update listening state if it has changed
    setListeningState(prevState => {
      if (prevState !== listening_state) {
        return listening_state;
      }
      return prevState;
    });
    
    if (status === 'wake_word_detected') {
      setWakeWordDetected(true);
      setIsConversationActive(true);
      
      // Add wake word message
      const wakeWordMessage = {
        id: Date.now(),
        type: 'system',
        content: `Wake word detected: "${transcript}"`,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, wakeWordMessage]);
      
      // Add AI response if available
      if (has_response && conversation_response) {
        const aiMessage = {
          id: Date.now() + 1,
          type: 'ai',
          content: conversation_response.response_text,
          audioData: conversation_response.response_audio,
          timestamp: new Date()
        };
        
        setMessages(prev => [...prev, aiMessage]);
        
        // Play audio response
        if (conversation_response.response_audio) {
          playAudio(conversation_response.response_audio);
        }
      }
      
      // Clear wake word detection after 3 seconds
      setTimeout(() => setWakeWordDetected(false), 3000);
      
    } else if (status === 'conversation_active' && has_response) {
      // Add user message
      const userMessage = {
        id: Date.now(),
        type: 'user',
        content: transcript,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, userMessage]);
      
      // Add AI response
      const aiMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: conversation_response.response_text,
        audioData: conversation_response.response_audio,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, aiMessage]);
      
      // Play audio response
      if (conversation_response.response_audio) {
        playAudio(conversation_response.response_audio);
      }
      
    } else if (status === 'conversation_ended' || status === 'conversation_timeout') {
      setIsConversationActive(false);
      
      const endMessage = {
        id: Date.now(),
        type: 'system',
        content: status === 'conversation_timeout' ? 'Conversation timed out. Say "Hey Buddy" to start again.' : 'Conversation ended. Say "Hey Buddy" to start again.',
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, endMessage]);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        sendVoiceMessage(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (error) {
      toast.error('Microphone access denied');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const sendVoiceMessage = async (audioBlob) => {
    const reader = new FileReader();
    reader.onloadend = async () => {
      const base64Audio = reader.result.split(',')[1];
      
      const userMessage = {
        id: Date.now(),
        type: 'user',
        content: 'Voice message',
        isVoice: true,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, userMessage]);
      setIsLoading(true);

      try {
        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/conversations/voice`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            session_id: sessionId,
            user_id: user.id,
            audio_base64: base64Audio
          })
        });

        const data = await response.json();
        
        if (response.ok) {
          const aiMessage = {
            id: Date.now() + 1,
            type: 'ai',
            content: data.response_text,
            audioData: data.response_audio,
            contentType: data.content_type,
            metadata: data.metadata,
            timestamp: new Date()
          };

          setMessages(prev => [...prev, aiMessage]);
          
          // Auto-play AI response
          if (data.response_audio) {
            playAudio(data.response_audio);
          }
        } else {
          throw new Error(data.detail || 'Failed to send voice message');
        }
      } catch (error) {
        toast.error('Failed to send voice message');
        console.error('Voice message error:', error);
      } finally {
        setIsLoading(false);
      }
    };
    
    reader.readAsDataURL(audioBlob);
  };

  const sendTextMessage = async (messageText) => {
    if (!messageText || !messageText.trim() || isLoading) return;

    // Store the message content
    const messageContent = messageText.trim();
    
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: messageContent,
      isVoice: false,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/conversations/text`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          user_id: user.id,
          message: messageContent // Use stored message content
        })
      });

      const data = await response.json();
      
      if (response.ok) {
        const aiMessage = {
          id: Date.now() + 1,
          type: 'ai',
          content: data.response_text,
          audioData: data.response_audio,
          contentType: data.content_type,
          metadata: data.metadata,
          timestamp: new Date()
        };

        setMessages(prev => [...prev, aiMessage]);
        
        // Auto-play AI response
        if (data.response_audio) {
          playAudio(data.response_audio);
        }
      } else {
        throw new Error(data.detail || 'Failed to send message');
      }
    } catch (error) {
      toast.error('Failed to send message');
      console.error('Text message error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const playAudio = (base64Audio) => {
    if (audioRef.current) {
      audioRef.current.pause();
    }
    
    const audioBlob = new Blob([Uint8Array.from(atob(base64Audio), c => c.charCodeAt(0))], { type: 'audio/wav' });
    const audioUrl = URL.createObjectURL(audioBlob);
    
    audioRef.current = new Audio(audioUrl);
    audioRef.current.play();
    setIsPlaying(true);
    setIsBotSpeaking(true);
    
    audioRef.current.onended = () => {
      setIsPlaying(false);
      setIsBotSpeaking(false);
      URL.revokeObjectURL(audioUrl);
    };
  };

  const stopAudio = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      setIsPlaying(false);
      setIsBotSpeaking(false);
    }
  };

  const formatTime = (date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const getListeningStateDisplay = () => {
    switch (listeningState) {
      case 'ambient':
        return {
          text: 'Always Listening',
          color: 'text-blue-600',
          bgColor: 'bg-blue-50',
          icon: EyeIcon
        };
      case 'active':
        return {
          text: 'Conversation Active',
          color: 'text-green-600',
          bgColor: 'bg-green-50',
          icon: MicrophoneIcon
        };
      default:
        return {
          text: 'Not Listening',
          color: 'text-gray-600',
          bgColor: 'bg-gray-50',
          icon: EyeSlashIcon
        };
    }
  };

  // Dynamic background based on mood/energy
  const getBackgroundClass = () => {
    const base = darkMode 
      ? 'bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900'
      : 'bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50';
    
    switch(botMood) {
      case 'excited':
        return darkMode 
          ? 'bg-gradient-to-br from-purple-900 via-pink-900 to-orange-900'
          : 'bg-gradient-to-br from-yellow-100 via-orange-100 to-pink-100';
      case 'calm':
        return darkMode 
          ? 'bg-gradient-to-br from-blue-900 via-indigo-900 to-purple-900'
          : 'bg-gradient-to-br from-blue-100 via-indigo-100 to-purple-100';
      case 'thinking':
        return darkMode 
          ? 'bg-gradient-to-br from-gray-800 via-slate-800 to-gray-900'
          : 'bg-gradient-to-br from-gray-100 via-slate-100 to-gray-200';
      default:
        return base;
    }
  };

  // Animated Bot Avatar Component
  const BotAvatar = () => (
    <div className="flex flex-col items-center justify-center h-full p-8">
      {/* Main Avatar Circle */}
      <motion.div
        className={`relative w-48 h-48 rounded-full flex items-center justify-center mb-6 ${
          darkMode ? 'bg-gradient-to-br from-blue-600 to-purple-700' : 'bg-gradient-to-br from-blue-500 to-purple-600'
        }`}
        animate={{
          scale: isBotSpeaking ? [1, 1.05, 1] : [1, 1.02, 1],
          rotate: listeningState === 'active' ? [0, 2, -2, 0] : 0,
        }}
        transition={{
          scale: { duration: 2, repeat: Infinity, ease: "easeInOut" },
          rotate: { duration: 3, repeat: Infinity, ease: "easeInOut" }
        }}
      >
        {/* Inner Glow Effect */}
        <motion.div 
          className="absolute inset-4 rounded-full bg-white/20 backdrop-blur-sm"
          animate={{
            opacity: isBotSpeaking ? [0.3, 0.7, 0.3] : [0.2, 0.4, 0.2]
          }}
          transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
        />
        
        {/* Eyes */}
        <div className="flex space-x-6">
          <motion.div 
            className="w-6 h-12 bg-white rounded-full"
            animate={{
              scaleY: isBotSpeaking ? [1, 0.3, 1] : [1, 0.8, 1]
            }}
            transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
          />
          <motion.div 
            className="w-6 h-12 bg-white rounded-full"
            animate={{
              scaleY: isBotSpeaking ? [1, 0.3, 1] : [1, 0.8, 1]
            }}
            transition={{ duration: 2, repeat: Infinity, ease: "easeInOut", delay: 0.1 }}
          />
        </div>

        {/* Voice Rings */}
        <AnimatePresence>
          {(isBotSpeaking || listeningState === 'active') && (
            <>
              <motion.div
                className="absolute inset-0 rounded-full border-2 border-white/30"
                initial={{ scale: 1, opacity: 0.6 }}
                animate={{ scale: 1.5, opacity: 0 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 1.5, repeat: Infinity, ease: "easeOut" }}
              />
              <motion.div
                className="absolute inset-0 rounded-full border-2 border-white/20"
                initial={{ scale: 1, opacity: 0.4 }}
                animate={{ scale: 2, opacity: 0 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 2, repeat: Infinity, ease: "easeOut", delay: 0.3 }}
              />
            </>
          )}
        </AnimatePresence>
      </motion.div>

      {/* Status Text */}
      <motion.div
        className={`text-center ${darkMode ? 'text-white' : 'text-gray-800'}`}
        animate={{ opacity: [0.7, 1, 0.7] }}
        transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
      >
        <h2 className="text-2xl font-bold mb-2">Hi {user?.name || 'there'}! 👋</h2>
        <p className="text-lg opacity-80">
          {listeningState === 'active' ? 'I\'m listening...' : 
           isBotSpeaking ? 'Speaking...' :
           isAmbientListening ? 'Say "Hey Buddy" to chat!' : 
           'Ready to chat!'}
        </p>
      </motion.div>

      {/* Mood Emojis */}
      <div className="mt-6 text-4xl">
        {botMood === 'excited' && '🤗'}
        {botMood === 'calm' && '😌'}
        {botMood === 'thinking' && '🤔'}
        {botMood === 'friendly' && '😊'}
      </div>
    </div>
  );

  // Live Transcript Component
  const LiveTranscript = () => (
    <div className={`h-full flex flex-col ${darkMode ? 'bg-gray-800 text-white' : 'bg-white text-gray-900'} border-l ${darkMode ? 'border-gray-700' : 'border-gray-200'}`}>
      {/* Transcript Header */}
      <div className={`flex-shrink-0 p-4 border-b ${darkMode ? 'border-gray-700 bg-gray-900' : 'border-gray-200 bg-gray-50'}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <ChatBubbleLeftEllipsisIcon className={`w-6 h-6 ${darkMode ? 'text-blue-400' : 'text-blue-600'}`} />
            <h3 className="text-lg font-semibold">Live Chat</h3>
          </div>
          
          {/* Theme Toggle */}
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

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center py-8">
            <div className="text-6xl mb-4">🎙️</div>
            <h4 className={`text-lg font-semibold mb-2 ${darkMode ? 'text-gray-200' : 'text-gray-800'}`}>
              Start Talking!
            </h4>
            <p className={`${darkMode ? 'text-gray-400' : 'text-gray-600'} mb-6`}>
              Your conversation will appear here in real-time
            </p>
            
            {/* Quick Suggestions */}
            <div className="flex flex-col space-y-2">
              {suggestions.map((suggestion, index) => (
                <motion.button
                  key={index}
                  onClick={() => sendTextMessage(suggestion)}
                  className={`px-4 py-2 rounded-full text-sm transition-colors ${
                    darkMode 
                      ? 'bg-blue-900 text-blue-200 hover:bg-blue-800' 
                      : 'bg-blue-50 text-blue-600 hover:bg-blue-100'
                  }`}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  {suggestion}
                </motion.button>
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
                  {/* Message Bubble */}
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
                  
                  {/* Message Actions */}
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
        
        {/* Current Transcript Preview */}
        {currentTranscript && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex justify-end"
          >
            <div className={`max-w-sm px-4 py-2 rounded-2xl border-2 border-dashed ${
              darkMode 
                ? 'border-blue-500 bg-blue-900/20 text-blue-200' 
                : 'border-blue-300 bg-blue-50 text-blue-800'
            }`}>
              <p className="text-sm italic">{currentTranscript}</p>
            </div>
          </motion.div>
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

      {/* Text Input Area */}
      <div className={`flex-shrink-0 p-4 border-t ${darkMode ? 'border-gray-700 bg-gray-900' : 'border-gray-200 bg-gray-50'}`}>
        <div className="flex items-center justify-between space-x-4">
          {/* Isolated Text Input Component */}
          <div className="flex-1">
            <TextInput 
              onSendMessage={sendTextMessage} 
              isLoading={isLoading}
              darkMode={darkMode}
            />
          </div>
          
          {/* Voice Control Component */}
          <VoiceControl 
            onStartAmbientListening={startAmbientListening}
            onStopAmbientListening={stopAmbientListening}
            darkMode={darkMode}
          />
        </div>
      </div>

    </div>
  );

  return (
    <div className={`h-full ${getBackgroundClass()} transition-all duration-1000`}>
      {/* Modern 2-Panel Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 h-full">
        {/* Left Panel - Animated Bot Avatar */}
        <div className="flex items-center justify-center min-h-96 lg:min-h-full">
          <BotAvatar />
        </div>

        {/* Right Panel - Live Transcript */}
        <div className="h-full min-h-96 lg:min-h-full">
          <LiveTranscript />
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;