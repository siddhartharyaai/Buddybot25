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
  // CENTRALIZED STATE MANAGEMENT - Single source of truth
  const [audioState, setAudioState] = useState({
    displayedText: '',
    currentChunkIndex: 0,
    isPlaying: false,
    isLoading: false,
    isInterrupted: false,
    processedChunks: new Set(),
    pendingRequests: new Map() // Track pending API requests for deduplication
  });
  
  // SINGLE REFS FOR AUDIO CONTROL
  const audioRef = useRef(null);
  const audioQueueRef = useRef([]);
  const storySessionIdRef = useRef(`story_${Date.now()}_${Math.random()}`);
  const audioContextRef = useRef(null);
  const activeRequestsRef = useRef(new Set()); // Track active requests to prevent duplicates

  // Initialize audio context for better control
  useEffect(() => {
    if (!audioContextRef.current) {
      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
    }
    
    return () => {
      // Enhanced cleanup - stop all audio and cancel all requests
      stopAllAudio();
      if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
        audioContextRef.current.close();
      }
      // Cancel any pending API requests
      activeRequestsRef.current.forEach(controller => controller.abort());
      activeRequestsRef.current.clear();
    };
  }, []);

  // CENTRALIZED BARGE-IN FUNCTIONALITY - Enhanced integration
  const stopAllAudio = useCallback(() => {
    console.log(`🛑 [${storySessionIdRef.current}] BARGE-IN: Stopping all audio playback`);
    
    // Update centralized state
    setAudioState(prev => ({ ...prev, isInterrupted: true, isPlaying: false }));
    
    // Stop current audio immediately
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      audioRef.current.src = '';
    }
    
    // Suspend audio context to prevent any audio
    if (audioContextRef.current && audioContextRef.current.state === 'running') {
      audioContextRef.current.suspend();
    }
    
    // Cancel all pending requests
    activeRequestsRef.current.forEach(controller => {
      controller.abort();
      console.log(`🛑 [${storySessionIdRef.current}] Cancelled pending request`);
    });
    activeRequestsRef.current.clear();
    
    // Clear audio queue
    audioQueueRef.current = [];
    
    toast('🎵 Audio stopped', {
      icon: '🛑',
      style: {
        border: '1px solid #3b82f6',
        padding: '16px',
        color: '#1e40af',
      },
    });
  }, []);

  // RESUME AUDIO: Reset barge-in state
  const resumeAudio = useCallback(() => {
    console.log(`▶️ [${storySessionIdRef.current}] Resuming audio capability`);
    
    // Update centralized state
    setAudioState(prev => ({ ...prev, isInterrupted: false }));
    
    // Resume audio context
    if (audioContextRef.current && audioContextRef.current.state === 'suspended') {
      audioContextRef.current.resume();
    }
  }, []);

  // Expose barge-in function globally for voice control
  useEffect(() => {
    window.stopStoryNarration = stopAllAudio;
    window.resumeStoryNarration = resumeAudio;
    
    return () => {
      delete window.stopStoryNarration;
      delete window.resumeStoryNarration;
    };
  }, [stopAllAudio, resumeAudio]);

  // SIMPLIFIED INITIALIZATION - Initialize with first chunk
  useEffect(() => {
    if (firstChunk) {
      console.log(`🎭 STORY STREAMING [${storySessionIdRef.current}]: Initializing with first chunk`);
      
      // RESET ALL STATE to prevent conflicts
      setAudioState({
        displayedText: firstChunk.text || '',
        currentChunkIndex: 0,
        isPlaying: false,
        isLoading: false,
        isInterrupted: false,
        processedChunks: new Set(),
        pendingRequests: new Map()
      });
      
      // Clear audio queue and start fresh
      audioQueueRef.current = [];
      
      // Add first chunk audio to queue with unique ID
      if (firstChunk.audio_base64) {
        const uniqueChunkId = `${storySessionIdRef.current}_chunk_0`;
        const firstAudio = {
          chunk_id: 0,
          unique_id: uniqueChunkId,
          audio_base64: firstChunk.audio_base64,
          text: firstChunk.text
        };
        
        audioQueueRef.current = [firstAudio];
        console.log(`🎭 [${storySessionIdRef.current}] First chunk queued with ID: ${uniqueChunkId}`);
        
        // Start playing first chunk immediately
        playNextAudio();
      }
      
      // Start loading remaining chunks if they exist
      if (remainingChunks && remainingChunks.length > 0) {
        loadRemainingChunks();
      }
    }
  }, [firstChunk, remainingChunks]); // Removed storySessionId dependency
  
  // IMPROVED REQUEST DEDUPLICATION - Prevent duplicate API calls
  const loadRemainingChunks = useCallback(async () => {
    if (!remainingChunks || remainingChunks.length === 0) return;
    
    console.log(`📄 STORY STREAMING [${storySessionIdRef.current}]: Loading ${remainingChunks.length} remaining chunks`);
    setAudioState(prev => ({ ...prev, isLoading: true }));
    
    try {
      // Process chunks with improved deduplication
      for (let i = 0; i < remainingChunks.length; i++) {
        const chunk = remainingChunks[i];
        const uniqueChunkId = `${storySessionIdRef.current}_chunk_${chunk.chunk_id}`;
        
        // Check if already processed or being processed
        if (audioState.processedChunks.has(uniqueChunkId) || 
            audioState.pendingRequests.has(uniqueChunkId)) {
          console.log(`⚠️ [${storySessionIdRef.current}] Chunk ${uniqueChunkId} already processed/pending, skipping`);
          continue;
        }
        
        console.log(`📄 [${storySessionIdRef.current}] Loading chunk ${chunk.chunk_id + 1}/${totalChunks} - ID: ${uniqueChunkId}`);
        
        // Create abort controller for this request
        const controller = new AbortController();
        activeRequestsRef.current.add(controller);
        
        // Track as pending
        setAudioState(prev => ({ 
          ...prev, 
          pendingRequests: new Map(prev.pendingRequests.set(uniqueChunkId, true))
        }));
        
        try {
          // Generate TTS for this chunk
          const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/stories/chunk-tts`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              text: chunk.text,
              chunk_id: chunk.chunk_id,
              user_id: userId,
              story_session_id: storySessionIdRef.current
            }),
            signal: controller.signal
          });
          
          if (response.ok) {
            const result = await response.json();
            
            if (result.status === 'success' && result.audio_base64) {
              const audioChunk = {
                chunk_id: chunk.chunk_id,
                unique_id: uniqueChunkId,
                audio_base64: result.audio_base64,
                text: chunk.text
              };
              
              // Add to queue and update state atomically
              audioQueueRef.current.push(audioChunk);
              setAudioState(prev => ({
                ...prev,
                processedChunks: new Set([...prev.processedChunks, uniqueChunkId]),
                pendingRequests: new Map(
                  [...prev.pendingRequests].filter(([key]) => key !== uniqueChunkId)
                )
              }));
              
              console.log(`✅ [${storySessionIdRef.current}] Chunk ${chunk.chunk_id + 1} audio ready - ID: ${uniqueChunkId}`);
              
              // Progressive text reveal - append at specific position
              setTimeout(() => {
                setAudioState(prev => {
                  const newText = prev.displayedText.includes(chunk.text) 
                    ? prev.displayedText 
                    : prev.displayedText + ' ' + chunk.text;
                  return { ...prev, displayedText: newText };
                });
              }, (i + 1) * 1000); // Reduced delay for better flow
              
            } else {
              console.error(`❌ [${storySessionIdRef.current}] Failed to generate TTS for chunk ${chunk.chunk_id}`);
            }
          } else {
            console.error(`❌ [${storySessionIdRef.current}] API error for chunk ${chunk.chunk_id}:`, response.status);
          }
        } catch (error) {
          if (error.name !== 'AbortError') {
            console.error(`❌ [${storySessionIdRef.current}] Request error for chunk ${chunk.chunk_id}:`, error);
          }
        } finally {
          // Clean up request tracking
          activeRequestsRef.current.delete(controller);
          setAudioState(prev => ({
            ...prev,
            pendingRequests: new Map(
              [...prev.pendingRequests].filter(([key]) => key !== uniqueChunkId)
            )
          }));
        }
        
        // Small delay between requests to prevent server overload
        if (i < remainingChunks.length - 1) {
          await new Promise(resolve => setTimeout(resolve, 50)); // Optimized timing
        }
      }
      
    } catch (error) {
      console.error(`❌ [${storySessionIdRef.current}] Error loading remaining chunks:`, error);
      toast.error('⚠️ Some story parts may not have audio');
    } finally {
      setAudioState(prev => ({ ...prev, isLoading: false }));
    }
  }, [remainingChunks, totalChunks, userId, audioState.processedChunks, audioState.pendingRequests]);

  // SIMPLIFIED AUDIO PLAYBACK - Single sequential player
  const playNextAudio = useCallback(async () => {
    // Check for interruption
    if (audioState.isInterrupted) {
      console.log(`🛑 [${storySessionIdRef.current}] Playback interrupted, stopping`);
      return;
    }
    
    if (audioState.isPlaying || audioQueueRef.current.length === 0) {
      return;
    }
    
    // Get next audio chunk
    const nextAudio = audioQueueRef.current[audioState.currentChunkIndex];
    
    if (!nextAudio || !nextAudio.audio_base64) {
      console.log(`⚠️ [${storySessionIdRef.current}] No audio data for chunk ${audioState.currentChunkIndex}`);
      // Try next chunk or complete
      const nextIndex = audioState.currentChunkIndex + 1;
      if (nextIndex < audioQueueRef.current.length) {
        setAudioState(prev => ({ ...prev, currentChunkIndex: nextIndex }));
        setTimeout(playNextAudio, 100);
      } else {
        completeStory();
      }
      return;
    }
    
    // Check if this chunk has already been played (prevent loops)
    const uniqueId = nextAudio.unique_id;
    if (audioState.processedChunks.has(`played_${uniqueId}`)) {
      console.log(`⚠️ [${storySessionIdRef.current}] Chunk ${uniqueId} already played, moving to next`);
      const nextIndex = audioState.currentChunkIndex + 1;
      setAudioState(prev => ({ ...prev, currentChunkIndex: nextIndex }));
      setTimeout(playNextAudio, 100);
      return;
    }
    
    try {
      // Set playing state
      setAudioState(prev => ({ ...prev, isPlaying: true }));
      
      console.log(`🎵 [${storySessionIdRef.current}] Playing chunk ${nextAudio.chunk_id + 1} - ID: ${uniqueId}`);
      
      // Stop any existing audio
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.currentTime = 0;
        audioRef.current.src = '';
      }
      
      // Convert base64 to audio blob
      const audioBytes = atob(nextAudio.audio_base64);
      const audioArray = new Uint8Array(audioBytes.length);
      for (let i = 0; i < audioBytes.length; i++) {
        audioArray[i] = audioBytes.charCodeAt(i);
      }
      const audioBlob = new Blob([audioArray], { type: 'audio/wav' });
      const audioUrl = URL.createObjectURL(audioBlob);
      
      // Create and setup audio element
      const audio = new Audio(audioUrl);
      audioRef.current = audio;
      audio.preload = 'auto';
      audio.volume = 1.0;
      
      // Mark chunk as played
      setAudioState(prev => ({
        ...prev,
        processedChunks: new Set([...prev.processedChunks, `played_${uniqueId}`])
      }));
      
      audio.onended = () => {
        console.log(`✅ [${storySessionIdRef.current}] Chunk ${uniqueId} audio completed`);
        URL.revokeObjectURL(audioUrl);
        
        // Check for interruption before continuing
        if (audioState.isInterrupted) {
          console.log(`🛑 [${storySessionIdRef.current}] Stopping due to interruption`);
          setAudioState(prev => ({ ...prev, isPlaying: false }));
          return;
        }
        
        // Move to next chunk
        const nextIndex = audioState.currentChunkIndex + 1;
        setAudioState(prev => ({ 
          ...prev, 
          currentChunkIndex: nextIndex,
          isPlaying: false
        }));
        
        // Continue with next chunk or complete
        if (nextIndex < audioQueueRef.current.length) {
          setTimeout(playNextAudio, 50); // Small delay for smooth transition
        } else {
          completeStory();
        }
      };
      
      audio.onerror = (error) => {
        console.error(`❌ [${storySessionIdRef.current}] Audio error for chunk ${uniqueId}:`, error);
        URL.revokeObjectURL(audioUrl);
        
        // Skip to next chunk on error
        const nextIndex = audioState.currentChunkIndex + 1;
        setAudioState(prev => ({ 
          ...prev, 
          currentChunkIndex: nextIndex,
          isPlaying: false
        }));
        
        if (nextIndex < audioQueueRef.current.length) {
          setTimeout(playNextAudio, 100);
        } else {
          completeStory();
        }
      };
      
      // Enhanced: Wait for audio to be ready before playing
      audio.oncanplaythrough = () => {
        // Final interruption check before playing
        if (!audioState.isInterrupted) {
          audio.play().catch(error => {
            console.error(`❌ [${storySessionIdRef.current}] Audio play error:`, error);
            audio.onerror(error);
          });
        } else {
          console.log(`🛑 [${storySessionIdRef.current}] Skipping play due to interruption`);
          URL.revokeObjectURL(audioUrl);
          setAudioState(prev => ({ ...prev, isPlaying: false }));
        }
      };
      
      // Load the audio (triggers oncanplaythrough when ready)
      audio.load();
      
    } catch (error) {
      console.error(`❌ [${storySessionIdRef.current}] Error in playNextAudio:`, error);
      setAudioState(prev => ({ ...prev, isPlaying: false }));
    }
  }, [audioState.isInterrupted, audioState.isPlaying, audioState.currentChunkIndex, audioState.processedChunks]);
  
  // COMPLETE STORY - Clean completion handler
  const completeStory = useCallback(() => {
    console.log(`🎉 [${storySessionIdRef.current}] Story streaming complete!`);
    
    // Reset all state
    setAudioState(prev => ({ 
      ...prev, 
      isPlaying: false,
      isInterrupted: false
    }));
    
    // Clear audio queue
    audioQueueRef.current = [];
    
    if (onComplete) {
      onComplete();
    }
    
    toast.success('📚 Story complete!');
  }, [onComplete]);
  
  // MANUAL PLAY HANDLER - Simplified
  const handleManualPlay = useCallback(() => {
    if (!audioState.isPlaying && audioQueueRef.current.length > 0) {
      playNextAudio();
    }
  }, [audioState.isPlaying, playNextAudio]);

  const formatStoryText = (text) => {
    // Add paragraph breaks and formatting for better display
    return text.split('. ').map((sentence, index) => (
      <span key={index}>
        {sentence}{index < text.split('. ').length - 1 ? '. ' : ''}
        {index % 3 === 2 && index < text.split('. ').length - 1 ? <br /> : ''}
      </span>
    ));
  };

  return (
    <div className="story-streaming-container">
      <div className="story-header flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <span className="text-2xl">📚</span>
          <span className="text-lg font-semibold text-purple-700">Story Time</span>
        </div>
        
        <div className="story-progress">
          <span className="text-sm text-gray-500">
            {isLoadingNextChunk ? 'Loading...' : `${currentChunkIndex + 1} / ${totalChunks} chunks`}
          </span>
        </div>
      </div>
      
      <div className="story-content bg-gradient-to-br from-purple-50 to-pink-50 p-6 rounded-lg shadow-lg border border-purple-200">
        <div className="story-text text-gray-800 leading-relaxed text-lg">
          {formatStoryText(displayedText)}
        </div>
        
        {isLoadingNextChunk && (
          <div className="loading-indicator mt-4 flex items-center space-x-2">
            <div className="animate-spin w-4 h-4 border-2 border-purple-500 border-t-transparent rounded-full"></div>
            <span className="text-sm text-purple-600">Loading more story...</span>
          </div>
        )}
      </div>
      
      <div className="story-controls mt-4 flex items-center justify-center space-x-4">
        {!isPlaying && !isProcessingRef.current && (
          <button
            onClick={handleManualPlay}
            className="flex items-center space-x-2 bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            <span className="text-xl">🔊</span>
            <span>Play Story Audio</span>
          </button>
        )}
        
        {isPlaying && (
          <div className="flex items-center space-x-2 text-purple-600">
            <div className="animate-pulse w-3 h-3 bg-purple-500 rounded-full"></div>
            <span>Playing story...</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default StoryStreamingComponent;