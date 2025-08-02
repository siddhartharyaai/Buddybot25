import React, { useState, useEffect, useRef } from 'react';
import toast from 'react-hot-toast';

const StoryStreamingComponent = ({ 
  firstChunk, 
  remainingChunks, 
  totalChunks, 
  sessionId, 
  userId, 
  onComplete 
}) => {
  const [displayedText, setDisplayedText] = useState('');
  const [currentChunkIndex, setCurrentChunkIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [audioQueue, setAudioQueue] = useState([]);
  const [isLoadingNextChunk, setIsLoadingNextChunk] = useState(false);
  const [playedChunkIds, setPlayedChunkIds] = useState(new Set()); // Track played chunks to prevent loops
  const [storySessionId] = useState(() => `story_${Date.now()}_${Math.random()}`); // Unique story session
  
  // ENHANCED AUDIO MANAGEMENT
  const audioRef = useRef(null);
  const audioQueueRef = useRef([]);
  const isProcessingRef = useRef(false);
  const playedChunkIdsRef = useRef(new Set());
  const audioContextRef = useRef(null);
  const isPlayingRef = useRef(false);
  
  // BARGE-IN STATE
  const isInterruptedRef = useRef(false);
  const shouldStopRef = useRef(false);

  // Initialize audio context for better control
  useEffect(() => {
    if (!audioContextRef.current) {
      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
    }
    
    return () => {
      // Cleanup audio context on unmount
      if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
        audioContextRef.current.close();
      }
    };
  }, []);

  // BARGE-IN FUNCTIONALITY: Stop all audio when interrupted
  const stopAllAudio = () => {
    console.log(`🛑 [${storySessionId}] BARGE-IN: Stopping all audio playback`);
    
    // Set interrupt flags
    isInterruptedRef.current = true;
    shouldStopRef.current = true;
    isPlayingRef.current = false;
    
    // Stop current audio
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      audioRef.current.src = '';
    }
    
    // Suspend audio context to prevent any audio
    if (audioContextRef.current && audioContextRef.current.state === 'running') {
      audioContextRef.current.suspend();
    }
    
    // Clear processing state
    isProcessingRef.current = false;
    setIsPlaying(false);
    
    toast.info('🎵 Audio stopped');
  };

  // RESUME AUDIO: Reset barge-in state
  const resumeAudio = () => {
    console.log(`▶️ [${storySessionId}] Resuming audio capability`);
    isInterruptedRef.current = false;
    shouldStopRef.current = false;
    
    // Resume audio context
    if (audioContextRef.current && audioContextRef.current.state === 'suspended') {
      audioContextRef.current.resume();
    }
  };

  // Expose barge-in function globally for voice control
  useEffect(() => {
    window.stopStoryNarration = stopAllAudio;
    window.resumeStoryNarration = resumeAudio;
    
    return () => {
      delete window.stopStoryNarration;
      delete window.resumeStoryNarration;
    };
  }, [storySessionId]);

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
    if (isProcessingRef.current || audioQueueRef.current.length === 0) {
      return;
    }
    
    isProcessingRef.current = true;
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
            if (onComplete) onComplete();
          }
          return;
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
        
        // Create and play audio
        const audio = new Audio(audioUrl);
        audioRef.current = audio;
        
        audio.onended = () => {
          console.log(`✅ [${storySessionId}] Chunk ${uniqueId} audio completed`);
          URL.revokeObjectURL(audioUrl);
          
          // Move to next chunk
          const nextIndex = currentChunkIndex + 1;
          setCurrentChunkIndex(nextIndex);
          
          // Check if more audio to play
          if (nextIndex < audioQueueRef.current.length) {
            setTimeout(() => {
              isProcessingRef.current = false;
              playNextAudio();
            }, 300); // Reduced delay from 500ms to 300ms for smoother flow
          } else {
            // Story audio complete
            console.log(`🎉 [${storySessionId}] Story streaming complete! Played ${playedChunkIdsRef.current.size} chunks`);
            setIsPlaying(false);
            isProcessingRef.current = false;
            
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
          
          if (nextIndex < audioQueueRef.current.length) {
            setTimeout(() => {
              isProcessingRef.current = false;
              playNextAudio();
            }, 100);
          } else {
            setIsPlaying(false);
            isProcessingRef.current = false;
            // Clear state on error completion too
            audioQueueRef.current = [];
            playedChunkIdsRef.current.clear();
          }
        };
        
        // Start playing
        try {
          await audio.play();
        } catch (playError) {
          console.error(`❌ [${storySessionId}] Audio autoplay failed:`, playError);
          // Provide manual play option
          toast.error('🔊 Tap to play story audio', {
            duration: 5000,
            onClick: () => audio.play()
          });
        }
      }
      
    } catch (error) {
      console.error(`❌ [${storySessionId}] Error playing audio:`, error);
      isProcessingRef.current = false;
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