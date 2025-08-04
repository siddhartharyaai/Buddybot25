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

  // Initialize with first chunk
  useEffect(() => {
    if (firstChunk) {
      console.log(`🎭 STORY STREAMING [${storySessionId}]: Initializing with first chunk`);
      
      // CLEAR ALL PREVIOUS STATE to prevent looping
      setDisplayedText('');
      setCurrentChunkIndex(0);
      setIsPlaying(false);
      setPlayedChunkIds(new Set());
      playedChunkIdsRef.current = new Set();
      audioQueueRef.current = [];
      isProcessingRef.current = false;
      
      // Set initial text
      setDisplayedText(firstChunk.text);
      
      // Add first chunk audio to queue with unique ID
      if (firstChunk.audio_base64) {
        const uniqueChunkId = `${storySessionId}_chunk_0`;
        const firstAudio = {
          chunk_id: 0,
          unique_id: uniqueChunkId,
          audio_base64: firstChunk.audio_base64,
          text: firstChunk.text
        };
        audioQueueRef.current = [firstAudio];
        setAudioQueue([firstAudio]);
        
        console.log(`🎭 [${storySessionId}] First chunk queued with ID: ${uniqueChunkId}`);
        
        // Start playing first chunk immediately
        playNextAudio();
      }
      
      // Start loading remaining chunks
      if (remainingChunks && remainingChunks.length > 0) {
        loadRemainingChunks();
      }
    }
  }, [firstChunk, remainingChunks, storySessionId]); // Added storySessionId to deps

  const loadRemainingChunks = async () => {
    console.log(`📄 STORY STREAMING [${storySessionId}]: Loading ${remainingChunks.length} remaining chunks`);
    setIsLoadingNextChunk(true);
    
    try {
      // Process remaining chunks sequentially for smooth experience
      for (let i = 0; i < remainingChunks.length; i++) {
        const chunk = remainingChunks[i];
        const uniqueChunkId = `${storySessionId}_chunk_${chunk.chunk_id}`;
        
        console.log(`📄 [${storySessionId}] Loading chunk ${chunk.chunk_id + 1}/${totalChunks} - ID: ${uniqueChunkId}`);
        
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
            story_session_id: storySessionId // Add story session for backend tracking
          })
        });
        
        if (response.ok) {
          const result = await response.json();
          
          if (result.status === 'success') {
            const audioChunk = {
              chunk_id: chunk.chunk_id,
              unique_id: uniqueChunkId,
              audio_base64: result.audio_base64,
              text: chunk.text
            };
            
            // Add to queue only if not already present
            if (!audioQueueRef.current.find(ac => ac.unique_id === uniqueChunkId)) {
              audioQueueRef.current.push(audioChunk);
              setAudioQueue(prev => [...prev, audioChunk]);
              
              console.log(`✅ [${storySessionId}] Chunk ${chunk.chunk_id + 1} audio ready - ID: ${uniqueChunkId}`);
              
              // FIXED: Progressive text reveal - append to SPECIFIC position, not accumulative
              setTimeout(() => {
                setDisplayedText(prev => {
                  // Only add if this chunk text isn't already in the displayed text
                  if (!prev.includes(chunk.text)) {
                    return prev + ' ' + chunk.text;
                  }
                  return prev; // Don't add duplicate text
                });
              }, (i + 1) * 1500); // Reduced delay from 2000ms to 1500ms for better flow
            } else {
              console.log(`⚠️ [${storySessionId}] Chunk ${uniqueChunkId} already in queue, skipping`);
            }
            
          } else {
            console.error(`❌ [${storySessionId}] Failed to generate TTS for chunk ${chunk.chunk_id}`);
          }
        } else {
          console.error(`❌ [${storySessionId}] API error for chunk ${chunk.chunk_id}:`, response.status);
        }
        
        // Small delay between requests to prevent overwhelming the server
        if (i < remainingChunks.length - 1) {
          await new Promise(resolve => setTimeout(resolve, 80)); // Reduced from 100ms to 80ms
        }
      }
      
    } catch (error) {
      console.error(`❌ [${storySessionId}] Error loading remaining chunks:`, error);
      toast.error('⚠️ Some story parts may not have audio');
    } finally {
      setIsLoadingNextChunk(false);
    }
  };

  const playNextAudio = async () => {
    // BARGE-IN CHECK: Stop if interrupted
    if (isInterruptedRef.current || shouldStopRef.current) {
      console.log(`🛑 [${storySessionId}] Playback interrupted, stopping`);
      return;
    }
    
    if (isProcessingRef.current || audioQueueRef.current.length === 0) {
      return;
    }
    
    isProcessingRef.current = true;
    isPlayingRef.current = true;
    setIsPlaying(true);
    
    try {
      const nextAudio = audioQueueRef.current[currentChunkIndex];
      
      if (nextAudio && nextAudio.audio_base64) {
        const uniqueId = nextAudio.unique_id;
        
        // CRITICAL FIX: Check if this chunk has already been played
        if (playedChunkIdsRef.current.has(uniqueId)) {
          console.log(`⚠️ [${storySessionId}] Chunk ${uniqueId} already played, skipping to prevent loop`);
          
          // Move to next chunk instead of replaying
          const nextIndex = currentChunkIndex + 1;
          setCurrentChunkIndex(nextIndex);
          
          if (nextIndex < audioQueueRef.current.length) {
            setTimeout(() => {
              isProcessingRef.current = false;
              playNextAudio();
            }, 100);
          } else {
            setIsPlaying(false);
            isProcessingRef.current = false;
            isPlayingRef.current = false;
            if (onComplete) onComplete();
          }
          return;
        }
        
        // PREVENT OVERLAPS: Stop any existing audio before starting new
        if (audioRef.current) {
          audioRef.current.pause();
          audioRef.current.currentTime = 0;
          audioRef.current.src = '';
        }
        
        // Mark this chunk as being played
        playedChunkIdsRef.current.add(uniqueId);
        setPlayedChunkIds(prev => new Set([...prev, uniqueId]));
        
        console.log(`🎵 [${storySessionId}] Playing chunk ${nextAudio.chunk_id + 1} - ID: ${uniqueId}`);
        
        // Convert base64 to audio blob
        const audioBytes = atob(nextAudio.audio_base64);
        const audioArray = new Uint8Array(audioBytes.length);
        for (let i = 0; i < audioBytes.length; i++) {
          audioArray[i] = audioBytes.charCodeAt(i);
        }
        const audioBlob = new Blob([audioArray], { type: 'audio/wav' });
        const audioUrl = URL.createObjectURL(audioBlob);
        
        // Create and play audio with enhanced controls
        const audio = new Audio(audioUrl);
        audioRef.current = audio;
        
        // Set audio properties for better playback
        audio.preload = 'auto';
        audio.volume = 1.0;
        
        audio.onended = () => {
          console.log(`✅ [${storySessionId}] Chunk ${uniqueId} audio completed`);
          URL.revokeObjectURL(audioUrl);
          
          // BARGE-IN CHECK: Don't continue if interrupted
          if (isInterruptedRef.current || shouldStopRef.current) {
            console.log(`🛑 [${storySessionId}] Stopping due to interruption`);
            isProcessingRef.current = false;
            isPlayingRef.current = false;
            setIsPlaying(false);
            return;
          }
          
          // Move to next chunk
          const nextIndex = currentChunkIndex + 1;
          setCurrentChunkIndex(nextIndex);
          
          // Check if more audio to play
          if (nextIndex < audioQueueRef.current.length) {
            setTimeout(() => {
              isProcessingRef.current = false;
              playNextAudio();
            }, 100); // Reduced delay for smoother continuous playback
          } else {
            // Story audio complete
            console.log(`🎉 [${storySessionId}] Story streaming complete! Played ${playedChunkIdsRef.current.size} chunks`);
            setIsPlaying(false);
            isProcessingRef.current = false;
            isPlayingRef.current = false;
            
            // Clear all state to prevent future loops
            audioQueueRef.current = [];
            playedChunkIdsRef.current.clear();
            
            if (onComplete) {
              onComplete();
            }
            
            toast.success('📚 Story complete!');
          }
        };
        
        audio.onerror = (error) => {
          console.error(`❌ [${storySessionId}] Audio error for chunk ${uniqueId}:`, error);
          URL.revokeObjectURL(audioUrl);
          
          // Skip to next chunk on error
          const nextIndex = currentChunkIndex + 1;
          setCurrentChunkIndex(nextIndex);
          
          if (nextIndex < audioQueueRef.current.length && !isInterruptedRef.current) {
            setTimeout(() => {
              isProcessingRef.current = false;
              playNextAudio();
            }, 100);
          } else {
            setIsPlaying(false);
            isProcessingRef.current = false;
            isPlayingRef.current = false;
            // Clear state on error completion too
            audioQueueRef.current = [];
            playedChunkIdsRef.current.clear();
            
            if (onComplete) onComplete();
          }
        };
        
        // ENHANCED: Wait for audio to be ready before playing
        audio.oncanplaythrough = () => {
          // Final barge-in check before playing
          if (!isInterruptedRef.current && !shouldStopRef.current) {
            audio.play().catch(error => {
              console.error(`❌ [${storySessionId}] Audio play error:`, error);
              // Trigger error handler
              audio.onerror(error);
            });
          } else {
            console.log(`🛑 [${storySessionId}] Skipping play due to interruption`);
            URL.revokeObjectURL(audioUrl);
            isProcessingRef.current = false;
            isPlayingRef.current = false;
            setIsPlaying(false);
          }
        };
        
        // Load the audio (triggers oncanplaythrough when ready)
        audio.load();
        
      } else {
        console.error(`❌ [${storySessionId}] No audio data for current chunk`);
        isProcessingRef.current = false;
        isPlayingRef.current = false;
        setIsPlaying(false);
      }
      
    } catch (error) {
      console.error(`❌ [${storySessionId}] Error in playNextAudio:`, error);
      isProcessingRef.current = false;
      isPlayingRef.current = false;
      setIsPlaying(false);
    }
  };

  const handleManualPlay = () => {
    if (audioRef.current && !isPlaying) {
      audioRef.current.play();
    } else if (!isProcessingRef.current && audioQueueRef.current.length > 0) {
      playNextAudio();
    }
  };

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