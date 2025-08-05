import React, { useState, useEffect, useRef, useCallback } from 'react';
import toast from 'react-hot-toast';

const StoryStreamingComponent = ({ 
  firstChunk, 
  remainingChunks, 
  totalChunks, 
  sessionId, 
  userId, 
  onComplete 
}) => {
  // SIMPLIFIED STATE MANAGEMENT - Single source of truth
  const [state, setState] = useState({
    displayedText: '',
    isPlaying: false,
    isLoading: false,
    currentChunkIndex: 0,
    audioReady: false,
    error: null,
    completed: false
  });
  
  // SINGLE AUDIO CONTROL REF
  const audioRef = useRef(null);
  const audioQueueRef = useRef([]);
  const storyIdRef = useRef(`story_${Date.now()}`);
  const isActiveRef = useRef(true);

  // Initialize story display
  useEffect(() => {
    if (firstChunk && !state.displayedText) {
      // Handle both string and object formats for firstChunk
      const chunkText = typeof firstChunk === 'string' ? firstChunk : firstChunk.text || firstChunk;
      
      setState(prev => ({
        ...prev,
        displayedText: chunkText,
        isLoading: true
      }));
      
      // Start audio generation immediately
      generateAndPlayAudio();
    }
    
    return () => {
      isActiveRef.current = false;
      stopAllAudio();
    };
  }, [firstChunk]);

  const stopAllAudio = useCallback(() => {
    console.log(`🛑 [${storyIdRef.current}] Stopping all audio`);
    
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      audioRef.current = null;
    }
    
    audioQueueRef.current = [];
    setState(prev => ({ ...prev, isPlaying: false, audioReady: false }));
  }, []);

  const generateAndPlayAudio = async () => {
    try {
      if (!isActiveRef.current) return;
      
      console.log(`🎵 [${storyIdRef.current}] Generating audio for story`);
      setState(prev => ({ ...prev, isLoading: true, error: null }));

      // Collect all story text
      let fullStoryText = firstChunk || '';
      if (remainingChunks && remainingChunks.length > 0) {
        fullStoryText += '\n\n' + remainingChunks.join('\n\n');
      }

      if (!fullStoryText.trim()) {
        throw new Error('No story text available');
      }

      console.log(`📝 [${storyIdRef.current}] Generating TTS for ${fullStoryText.length} characters`);

      // Make TTS API call
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/voice/tts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: fullStoryText,
          voice_personality: 'story_narrator',
          session_id: sessionId
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(`TTS API error: ${response.status} - ${errorData.detail || 'Unknown error'}`);
      }

      const audioData = await response.json();
      
      if (!isActiveRef.current) return;

      // Handle both single audio and chunked response
      let audioToPlay = null;
      
      try {
        // Try to parse as JSON (chunked response)
        const parsedData = typeof audioData.audio === 'string' 
          ? JSON.parse(audioData.audio) 
          : audioData.audio;
          
        if (parsedData && parsedData.is_chunked && parsedData.audio_chunks) {
          console.log(`🎵 [${storyIdRef.current}] Received ${parsedData.audio_chunks.length} audio chunks`);
          audioToPlay = parsedData.audio_chunks[0]; // Start with first chunk
          audioQueueRef.current = parsedData.audio_chunks.slice(1); // Queue remaining
        } else {
          audioToPlay = audioData.audio;
        }
      } catch (e) {
        // Not JSON, treat as single audio response
        audioToPlay = audioData.audio;
      }

      if (!audioToPlay) {
        throw new Error('No audio data received from TTS API');
      }

      await playAudio(audioToPlay);

    } catch (error) {
      console.error(`❌ [${storyIdRef.current}] Audio generation error:`, error);
      setState(prev => ({ 
        ...prev, 
        isLoading: false, 
        error: error.message,
        audioReady: false 
      }));
      toast.error(`Audio generation failed: ${error.message}`);
    }
  };

  const playAudio = async (audioBase64) => {
    try {
      if (!isActiveRef.current || !audioBase64) return;

      console.log(`🔊 [${storyIdRef.current}] Playing audio chunk`);
      
      // Create new audio element
      const audio = new Audio(`data:audio/wav;base64,${audioBase64}`);
      audioRef.current = audio;
      
      // Set up event listeners
      audio.onloadeddata = () => {
        if (!isActiveRef.current) return;
        setState(prev => ({ 
          ...prev, 
          audioReady: true, 
          isLoading: false,
          error: null 
        }));
      };

      audio.onplay = () => {
        if (!isActiveRef.current) return;
        setState(prev => ({ ...prev, isPlaying: true }));
      };

      audio.onpause = () => {
        if (!isActiveRef.current) return;
        setState(prev => ({ ...prev, isPlaying: false }));
      };

      audio.onended = () => {
        if (!isActiveRef.current) return;
        console.log(`✅ [${storyIdRef.current}] Audio chunk completed`);
        
        // Play next chunk if available
        if (audioQueueRef.current.length > 0) {
          const nextChunk = audioQueueRef.current.shift();
          setTimeout(() => playAudio(nextChunk), 100); // Small gap between chunks
        } else {
          // Story completed
          setState(prev => ({ 
            ...prev, 
            isPlaying: false, 
            completed: true 
          }));
          console.log(`🎉 [${storyIdRef.current}] Story narration completed`);
          if (onComplete) onComplete();
        }
      };

      audio.onerror = (e) => {
        console.error(`❌ [${storyIdRef.current}] Audio playback error:`, e);
        setState(prev => ({ 
          ...prev, 
          isPlaying: false, 
          error: 'Audio playback failed',
          isLoading: false 
        }));
      };

      // Start playback
      await audio.play();

    } catch (error) {
      console.error(`❌ [${storyIdRef.current}] Play audio error:`, error);
      setState(prev => ({ 
        ...prev, 
        isPlaying: false, 
        error: error.message,
        isLoading: false 
      }));
    }
  };

  const handlePlayPause = () => {
    if (!audioRef.current) {
      // No audio ready, generate it
      generateAndPlayAudio();
      return;
    }

    if (state.isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play().catch(err => {
        console.error(`❌ [${storyIdRef.current}] Resume playback error:`, err);
        setState(prev => ({ ...prev, error: 'Playback resume failed' }));
      });
    }
  };

  const handleRestart = () => {
    stopAllAudio();
    setState(prev => ({
      ...prev,
      currentChunkIndex: 0,
      completed: false,
      error: null
    }));
    setTimeout(() => generateAndPlayAudio(), 100);
  };

  return (
    <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-2xl p-6 shadow-lg">
      {/* Story Header */}
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full flex items-center justify-center">
          <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
        </div>
        <div>
          <h3 className="text-lg font-semibold text-gray-800">Story Time</h3>
          <p className="text-sm text-gray-600">
            {state.completed ? 'Story completed!' : 
             state.isLoading ? 'Preparing audio...' : 
             'Ready to listen'}
          </p>
        </div>
      </div>

      {/* Story Text Display */}
      <div className="bg-white rounded-xl p-4 mb-4 max-h-48 overflow-y-auto">
        <div className="prose prose-sm max-w-none">
          {state.displayedText && (
            <p className="text-gray-700 leading-relaxed whitespace-pre-line">
              {state.displayedText}
            </p>
          )}
          {remainingChunks && remainingChunks.map((chunk, index) => (
            <p key={index} className="text-gray-700 leading-relaxed whitespace-pre-line mt-3">
              {typeof chunk === 'string' ? chunk : chunk.text || chunk}
            </p>
          ))}
        </div>
      </div>

      {/* Error Display */}
      {state.error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
          <p className="text-red-700 text-sm">⚠️ {state.error}</p>
        </div>
      )}

      {/* Audio Controls */}
      <div className="flex items-center justify-center gap-4">
        {/* Play/Pause Button */}
        <button
          onClick={handlePlayPause}
          disabled={state.isLoading}
          className={`w-14 h-14 rounded-full flex items-center justify-center transition-all duration-200 shadow-lg ${
            state.isLoading 
              ? 'bg-gray-300 cursor-not-allowed' 
              : state.isPlaying 
                ? 'bg-orange-500 hover:bg-orange-600 text-white' 
                : 'bg-green-500 hover:bg-green-600 text-white'
          }`}
        >
          {state.isLoading ? (
            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
          ) : state.isPlaying ? (
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 9v6m4-6v6" />
            </svg>
          ) : (
            <svg className="w-6 h-6 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1.5a2.5 2.5 0 015 0H17m-8 4l2 2 4-4m-4-6v6" />
            </svg>
          )}
        </button>

        {/* Restart Button */}
        <button
          onClick={handleRestart}
          disabled={state.isLoading}
          className="w-12 h-12 rounded-full bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 text-white flex items-center justify-center transition-all duration-200 shadow-lg"
          title="Restart story"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        </button>
      </div>

      {/* Progress Indicator */}
      {(state.isLoading || state.isPlaying) && (
        <div className="mt-4">
          <div className="flex items-center justify-center gap-2 text-sm text-gray-600">
            <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
            <span>
              {state.isLoading ? 'Generating audio...' : 'Playing story...'}
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

export default StoryStreamingComponent;