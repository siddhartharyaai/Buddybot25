import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import toast from 'react-hot-toast';
import { v4 as uuidv4 } from 'uuid';

import Layout from './components/Layout';
import Header from './components/Header';
import ProfileSetup from './components/ProfileSetup';
import ParentalControls from './components/ParentalControls';
import SimplifiedChatInterface from './components/SimplifiedChatInterface';
import ProfilePage from './components/ProfilePage';
import SettingsPage from './components/SettingsPage';
import SignUp from './components/SignUp';
import SignIn from './components/SignIn';
import ForgotPassword from './components/ForgotPassword';

import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const App = () => {
  // SIMPLIFIED AUTHENTICATION: Streamlined auth state management
  const [authState, setAuthState] = useState({
    isAuthenticated: false,
    token: null,
    currentView: 'welcome' // welcome, signup, signin, forgotPassword, app
  });

  // SIMPLIFIED STATE MANAGEMENT
  const [user, setUser] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [isProfileSetupOpen, setIsProfileSetupOpen] = useState(false);
  const [isParentalControlsOpen, setIsParentalControlsOpen] = useState(false);
  const [parentalControls, setParentalControls] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('ai_companion_dark_mode');
    return saved ? JSON.parse(saved) : false;
  });
  const [chatMessages, setChatMessages] = useState([]);
  const [chatHistory, setChatHistory] = useState({});
  const [isNewUser, setIsNewUser] = useState(false);

  useEffect(() => {
    const initializeApp = async () => {
      console.log('🚀 Initializing Buddy App...');
      try {
        // Set maximum loading time (safety timeout)
        const loadingTimeout = setTimeout(() => {
          console.warn('⚠️ Loading timeout reached, forcing app to show');
          setIsLoading(false);
        }, 5000); // Maximum 5 seconds loading

        // Initialize all required data
        await Promise.all([
          checkUserProfile(), // This should handle its own loading state
          // Add any other initialization here
        ]);
        
        // Clear timeout if successful
        clearTimeout(loadingTimeout);
        
        console.log('✅ App initialization complete');
        setIsLoading(false);
        
      } catch (error) {
        console.error('❌ App initialization error:', error);
        // Always hide loading screen even on error
        setIsLoading(false);
        toast.error('Failed to initialize app, but you can still use it!');
      }
    };

    initializeApp();
    
  }, []);

  useEffect(() => {
    // Save dark mode preference to localStorage
    localStorage.setItem('ai_companion_dark_mode', JSON.stringify(darkMode));
  }, [darkMode]);

  // Load chat history when session changes
  useEffect(() => {
    if (sessionId && user?.id) {
      loadChatHistory(sessionId);
    }
  }, [sessionId, user?.id]);

  const autoSpeakWelcomeMessage = async (welcomeText) => {
    try {
      if (!welcomeText || !user?.voice_personality) {
        console.log('⚠️ Skipping welcome TTS - missing text or voice personality');
        return;
      }

      console.log('🎵 Auto-speaking welcome message...');
      
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/voice/tts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: welcomeText,
          voice_personality: user.voice_personality || 'friendly_companion'
        })
      });

      if (response.ok) {
        const audioData = await response.json();
        if (audioData.audio) {
          // Create and play audio
          const audio = new Audio(`data:audio/wav;base64,${audioData.audio}`);
          audio.volume = 0.8; // Slightly lower volume for welcome
          await audio.play();
          console.log('✅ Welcome message spoken successfully');
        }
      } else {
        console.log('⚠️ Failed to generate welcome TTS, continuing silently');
      }
    } catch (error) {
      console.log('⚠️ Welcome TTS error (non-critical):', error.message);
      // Don't throw error - this is a nice-to-have feature
    }
  };

  const loadChatHistory = async (currentSessionId) => {
    try {
      // First try to load from localStorage
      const savedHistory = localStorage.getItem(`chat_history_${user?.id}_${currentSessionId}`);
      if (savedHistory) {
        const messages = JSON.parse(savedHistory);
        setChatMessages(messages);
        setChatHistory(prev => ({ ...prev, [currentSessionId]: messages }));
      } else {
        // Generate dynamic welcome message from backend
        await generateWelcomeMessage(currentSessionId);
      }
    } catch (error) {
      console.error('Error loading chat history:', error);
      // Fallback welcome message
      const welcomeMessage = {
        id: Date.now(),
        type: 'bot',
        content: `Hi ${user?.name}! 👋 I'm Buddy, your AI friend. How can I help you today?`,
        timestamp: new Date().toISOString()
      };
      setChatMessages([welcomeMessage]);
    }
  };

  const generateWelcomeMessage = async (currentSessionId) => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/conversations/welcome`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: user?.id,
          session_id: currentSessionId
        })
      });

      if (response.ok) {
        const welcomeData = await response.json();
        const welcomeMessage = {
          id: Date.now(),
          type: 'bot',
          content: welcomeData.message,
          timestamp: new Date().toISOString(),
          metadata: welcomeData.metadata || {}
        };
        setChatMessages([welcomeMessage]);
        setChatHistory(prev => ({ ...prev, [currentSessionId]: [welcomeMessage] }));
        console.log('✅ Generated personalized welcome message');
        
        // Auto-speak welcome message
        setTimeout(() => autoSpeakWelcomeMessage(welcomeMessage.content), 1000);
      } else {
        throw new Error('Failed to generate welcome message');
      }
    } catch (error) {
      console.error('Error generating welcome message:', error);
      // Fallback to static welcome message
      const welcomeMessage = {
        id: Date.now(),
        type: 'bot',
        content: `Hi ${user?.name}! 👋 I'm Buddy, your AI friend. How can I help you today?`,
        timestamp: new Date().toISOString()
      };
      setChatMessages([welcomeMessage]);
      setChatHistory(prev => ({ ...prev, [currentSessionId]: [welcomeMessage] }));
      
      // Auto-speak fallback welcome message  
      setTimeout(() => autoSpeakWelcomeMessage(welcomeMessage.content), 1000);
    }
  };

  const saveChatHistory = (currentSessionId, messages) => {
    try {
      localStorage.setItem(`chat_history_${user?.id}_${currentSessionId}`, JSON.stringify(messages));
      setChatHistory(prev => ({ ...prev, [currentSessionId]: messages }));
    } catch (error) {
      console.error('Error saving chat history:', error);
    }
  };

  const addMessage = (message) => {
    const newMessage = {
      ...message,
      id: Date.now(),
      timestamp: new Date().toISOString()
    };
    
    setChatMessages(prev => {
      const updated = [...prev, newMessage];
      // Save to localStorage
      if (sessionId) {
        saveChatHistory(sessionId, updated);
      }
      return updated;
    });
  };

  const checkUserProfile = async () => {
    console.log('🚀 Starting checkUserProfile...');
    try {
      // First, check for authentication token
      const token = localStorage.getItem('buddy_auth_token');
      const profileId = localStorage.getItem('buddy_profile_id');
      
      if (token && profileId) {
        console.log('🔐 Auth token found, verifying...');
        
        try {
          // Get profile using token
          const response = await fetch(`${API}/auth/profile?token=${token}`, {
            method: 'GET',
            headers: {
              'Content-Type': 'application/json',
            },
          });
          
          if (response.ok) {
            const profile = await response.json();
            console.log('✅ Authenticated user profile loaded');
            setUser(profile);
            setAuthState(prev => ({ ...prev, token, isAuthenticated: true, currentView: 'app' }));
            await createSession(profile.id);
            await loadParentalControls(profile.id);
            return;
          } else {
            console.log('❌ Token invalid, clearing auth data');
            // Clear invalid token and show welcome page
            localStorage.removeItem('buddy_auth_token');
            localStorage.removeItem('buddy_user_id');
            localStorage.removeItem('buddy_profile_id');
            setAuthState(prev => ({ ...prev, currentView: 'welcome' }));
          }
        } catch (error) {
          console.error('Auth verification error:', error);
          // Clear potentially corrupted auth data and show welcome page
          localStorage.removeItem('buddy_auth_token');
          localStorage.removeItem('buddy_user_id');
          localStorage.removeItem('buddy_profile_id');
          setAuthState(prev => ({ ...prev, currentView: 'welcome' }));
        }
      }
      
      // Check if user profile exists in localStorage (legacy support)
      const savedUser = localStorage.getItem('ai_companion_user');
      console.log('💾 Saved user in localStorage:', savedUser ? 'found' : 'not found');
      
      if (!savedUser) {
        // No saved user - show welcome page
        console.log('👤 No saved user found, showing welcome page');
        setAuthState(prev => ({ ...prev, currentView: 'welcome' }));
        return;
      }
      
      console.log('📝 User exists in localStorage, verifying with backend...');
      // User exists in localStorage, verify it exists in backend
      const userData = JSON.parse(savedUser);
      
      try {
        // Verify user exists in backend database
        const response = await fetch(`${API}/users/profile/${userData.id}`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });
        
        if (response.ok) {
          // User exists in backend, proceed normally and skip welcome
          const backendUser = await response.json();
          setUser(backendUser);
          setAuthState(prev => ({ ...prev, isAuthenticated: true, currentView: 'app' }));
          await createSession(backendUser.id);
          await loadParentalControls(backendUser.id);
        } else {
          // User doesn't exist in backend, show welcome page
          console.log('🎯 User not found in backend, showing welcome page');
          localStorage.removeItem('ai_companion_user');
          setAuthState(prev => ({ ...prev, currentView: 'welcome' }));
        }
      } catch (error) {
        console.error('Error verifying user profile with backend:', error);
        // Network error, show welcome page
        console.log('🎯 Network error, showing welcome page');
        localStorage.removeItem('ai_companion_user');
        setAuthState(prev => ({ ...prev, currentView: 'welcome' }));
      }
    } catch (error) {
      console.error('Error checking user profile:', error);
      // Show welcome page as fallback
      setAuthState(prev => ({ ...prev, currentView: 'welcome' }));
    }
  };

  const createSession = async (userId) => {
    try {
      const response = await fetch(`${API}/conversations/session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: userId,
          session_name: 'Chat Session'
        })
      });

      const data = await response.json();
      if (response.ok) {
        setSessionId(data.id);
      } else {
        throw new Error(data.detail || 'Failed to create session');
      }
    } catch (error) {
      console.error('Error creating session:', error);
      toast.error('Failed to create chat session');
      // Don't fail the entire loading process for session creation
    }
  };

  const loadParentalControls = async (userId) => {
    try {
      const response = await fetch(`${API}/users/${userId}/parental-controls`);
      const data = await response.json();
      
      if (response.ok) {
        setParentalControls(data);
      }
    } catch (error) {
      console.error('Error loading parental controls:', error);
      // Don't fail the entire loading process for parental controls
    }
  };

  const updateUserProfile = async (profileData) => {
    try {
      if (!user?.id) {
        throw new Error('No user profile to update');
      }

      // Filter profile data to only include fields that backend accepts
      const backendProfileData = {
        name: profileData.name,
        age: profileData.age,
        location: profileData.location,
        timezone: profileData.timezone || 'UTC',
        language: profileData.language || 'english',
        voice_personality: profileData.voice_personality || 'friendly_companion',
        interests: profileData.interests || [],
        learning_goals: profileData.learning_goals || [],
        parent_email: profileData.parent_email || null,
        // Add the missing fields from ProfileSetup
        gender: profileData.gender || 'prefer_not_to_say',
        avatar: profileData.avatar || 'bunny',
        speech_speed: profileData.speech_speed || 'normal',
        energy_level: profileData.energy_level || 'balanced'
      };

      console.log('Updating profile data for user:', user.id, backendProfileData);

      const response = await fetch(`${API}/users/profile/${user.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(backendProfileData)
      });

      const data = await response.json();
      console.log('Profile update response:', { status: response.status, data });

      if (response.ok) {
        setUser(data);
        localStorage.setItem('ai_companion_user', JSON.stringify(data));
        
        // Check if this is part of new user onboarding
        if (isNewUser) {
          console.log('🎯 New user profile completed, triggering parental controls');
          setIsProfileSetupOpen(false);
          // Trigger parental controls popup after profile completion for new users
          setTimeout(() => {
            setIsParentalControlsOpen(true);
            toast.success('Profile updated! Please complete parental controls for safety.');
          }, 500);
        } else {
          setIsProfileSetupOpen(false);
          toast.success('Profile updated successfully!');
        }
      } else {
        console.error('Profile update failed:', response.status, data);
        throw new Error(data.detail || `Failed to update profile (HTTP ${response.status})`);
      }
    } catch (error) {
      console.error('Error updating profile:', error);
      toast.error(`Failed to update profile: ${error.message}`);
      throw error;
    }
  };

  const deleteUserProfile = async () => {
    try {
      if (!user?.id) {
        throw new Error('No user profile to delete');
      }

      const response = await fetch(`${API}/users/profile/${user.id}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        // Clear user data and redirect to setup
        setUser(null);
        setSessionId(null);
        localStorage.removeItem('ai_companion_user');
        setIsProfileSetupOpen(true);
        toast.success('Profile deleted successfully!');
      } else {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to delete profile');
      }
    } catch (error) {
      console.error('Error deleting profile:', error);
      toast.error('Failed to delete profile');
      throw error;
    }
  };

  const saveParentalControls = async (controlsData) => {
    try {
      const response = await fetch(`${API}/users/${user.id}/parental-controls`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(controlsData)
      });

      const data = await response.json();
      if (response.ok) {
        setParentalControls(data);
        
        // Check if this is part of new user onboarding
        if (isNewUser) {
          console.log('🎉 New user onboarding completed!');
          setIsNewUser(false); // Reset new user flag
          setIsParentalControlsOpen(false);
          toast.success('Welcome to Buddy! Your account is all set up. Let\'s start chatting!');
        } else {
          setIsParentalControlsOpen(false);
          toast.success('Parental controls updated successfully!');
        }
      } else {
        throw new Error(data.detail || 'Failed to update parental controls');
      }
    } catch (error) {
      console.error('Error updating parental controls:', error);
      throw error;
    }
  };

  const saveUserProfile = async (profileData) => {
    try {
      console.log('Creating new user profile:', profileData);
      
      // Create new user profile
      const response = await fetch(`${API}/users/profile`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(profileData)
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        if (response.status === 400 && errorData.detail === "Name taken, try another") {
          toast.error('Name taken, try another');
          throw new Error('Name taken, try another');
        }
        throw new Error('Failed to create user profile');
      }

      const newUser = await response.json();
      
      // Check if name was modified due to duplicates
      if (newUser.name !== profileData.name) {
        toast(`Name "${profileData.name}" was taken, using "${newUser.name}" instead`, {
          icon: '👤',
          style: {
            border: '1px solid #3b82f6',
            padding: '16px',
            color: '#1e40af',
          },
        });
      }
      
      // Save to state and localStorage
      setUser(newUser);
      localStorage.setItem('ai_companion_user', JSON.stringify(newUser));
      
      // Create session for new user
      await createSession(newUser.id);
      await loadParentalControls(newUser.id);
      
      // Close profile setup
      setIsProfileSetupOpen(false);
      
      toast.success('Profile created successfully!');
      
    } catch (error) {
      console.error('Error creating user profile:', error);
      if (error.message === 'Name taken, try another') {
        // Don't close the modal, let user try another name
        return;
      }
      toast.error('Failed to create profile. Please try again.');
    }
  };

  // Authentication handlers
  const handleAuthSuccess = async (tokenData) => {
    try {
      setAuthState(prev => ({ 
        ...prev, 
        token: tokenData.access_token, 
        isAuthenticated: true, 
        currentView: 'app' 
      }));
      
      // Store auth data
      localStorage.setItem('buddy_auth_token', tokenData.access_token);
      localStorage.setItem('buddy_user_id', tokenData.user_id);
      localStorage.setItem('buddy_profile_id', tokenData.profile_id);
      
      // Get user profile
      const response = await fetch(`${API}/auth/profile?token=${tokenData.access_token}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const profile = await response.json();
        setUser(profile);
        
        // Create session
        await createSession(profile.id);
        await loadParentalControls(profile.id);
        
        // Check if this is a new user (based on tokenData.is_new_user flag from signup)
        if (tokenData.is_new_user) {
          console.log('🆕 New user detected, starting onboarding flow');
          setIsNewUser(true);
          // Trigger profile setup popup for new users
          setIsProfileSetupOpen(true);
          toast.success(`Welcome ${profile.name}! Let's set up your profile.`);
        } else {
          console.log('👤 Existing user, going directly to chat');
          toast.success(`Welcome back ${profile.name}!`);
        }
      }
    } catch (error) {
      console.error('Error handling auth success:', error);
      toast.error('Failed to load profile');
    }
  };

  const handleSwitchToSignUp = () => {
    setAuthState(prev => ({ ...prev, currentView: 'signup' }));
  };

  const handleSwitchToSignIn = () => {
    setAuthState(prev => ({ ...prev, currentView: 'signin' }));
  };

  const handleSwitchToForgotPassword = () => {
    setAuthState(prev => ({ ...prev, currentView: 'forgotPassword' }));
  };

  const handleBackToSignIn = () => {
    setAuthState(prev => ({ ...prev, currentView: 'signin' }));
  };

  // Logout handler - clears all session data and returns to welcome page
  const handleLogout = async () => {
    try {
      console.log('🚪 Logging out user...');
      
      // Call backend logout endpoint if it exists (optional)
      const token = localStorage.getItem('buddy_auth_token');
      if (token) {
        try {
          await fetch(`${API}/auth/logout`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`
            }
          });
        } catch (error) {
          // Backend logout is optional - continue with client-side logout
          console.log('Backend logout endpoint not available or failed, continuing with client-side logout');
        }
      }
      
      // Clear all authentication data from localStorage
      localStorage.removeItem('buddy_auth_token');
      localStorage.removeItem('buddy_user_id');
      localStorage.removeItem('buddy_profile_id');
      localStorage.removeItem('ai_companion_user'); // Legacy support
      
      // Reset all application state
      setUser(null);
      setAuthState({ isAuthenticated: false, token: null, currentView: 'welcome' });
      setSessionId(null);
      setParentalControls({});
      setChatMessages([]);
      setChatHistory({});
      setIsNewUser(false);
      
      // Close any open modals
      setIsProfileSetupOpen(false);
      setIsParentalControlsOpen(false);
      
      console.log('✅ Logout completed successfully');
      toast.success('Logged out successfully!');
      
    } catch (error) {
      console.error('Error during logout:', error);
      toast.error('Error during logout, but session has been cleared');
      
      // Force clear everything even if there was an error
      localStorage.clear();
      setUser(null);
      setAuthState({ isAuthenticated: false, token: null, currentView: 'welcome' });
    }
  };

  const handleGetStarted = () => {
    // Always route to authentication for new users
    console.log('🚀 Get Started clicked, showing authentication');
    setAuthState(prev => ({ ...prev, currentView: 'signup' })); // Default to signup for new users
  };

  const WelcomeScreen = () => (
    <div className="min-h-screen flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="max-w-4xl mx-auto text-center"
      >
        {/* Hero Section */}
        <div className="mb-12">
          <motion.div
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="w-24 h-24 bg-gradient-to-br from-blue-500 to-purple-600 rounded-3xl flex items-center justify-center mx-auto mb-6 shadow-2xl"
          >
            <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </motion.div>
          
          <motion.h1
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="text-4xl md:text-6xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-4"
          >
            Meet Your AI Buddy
          </motion.h1>
          
          <motion.p
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="text-xl text-gray-600 max-w-2xl mx-auto mb-8"
          >
            Your smart friend for stories, songs, learning, and fun conversations. 
            Safe, educational, and designed just for you!
          </motion.p>
        </div>

        {/* Features */}
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12"
        >
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-gray-100">
            <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mx-auto mb-4">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 016 0v6a3 3 0 01-3 3z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Voice Chat</h3>
            <p className="text-gray-600">Talk naturally with your AI friend using voice messages and responses.</p>
          </div>

          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-gray-100">
            <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center mx-auto mb-4">
              <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Stories & Songs</h3>
            <p className="text-gray-600">Enjoy bedtime stories, nursery rhymes, and educational content.</p>
          </div>

          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl border border-gray-100">
            <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center mx-auto mb-4">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Safe & Secure</h3>
            <p className="text-gray-600">Built with child safety in mind, with parental controls and monitoring.</p>
          </div>
        </motion.div>

        {/* CTA Button */}
        <motion.button
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.6 }}
          onClick={handleGetStarted}
          className="px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-2xl text-lg font-semibold hover:from-blue-600 hover:to-purple-700 transition-all duration-200 shadow-xl hover:shadow-2xl transform hover:scale-105"
        >
          Get Started
        </motion.button>
      </motion.div>
    </div>
  );

  const ChatPage = () => (
    <div className="h-screen flex flex-col">
      <Header 
        user={user} 
        onOpenProfile={() => setIsProfileSetupOpen(true)}
        onOpenSettings={() => setIsParentalControlsOpen(true)}
        onLogout={handleLogout}
        darkMode={darkMode}
        setDarkMode={setDarkMode}
      />
      <div className="flex-1 overflow-hidden">
        <SimplifiedChatInterface 
          user={user} 
          sessionId={sessionId}
          darkMode={darkMode}
          setDarkMode={setDarkMode}
          messages={chatMessages}
          onAddMessage={addMessage}
        />
      </div>
    </div>
  );

  const ProfilePageWrapper = () => (
    <div className="h-screen flex flex-col">
      <Header 
        user={user} 
        onOpenProfile={() => setIsProfileSetupOpen(true)}
        onOpenSettings={() => setIsParentalControlsOpen(true)}
        onLogout={handleLogout}
        darkMode={darkMode}
        setDarkMode={setDarkMode}
      />
      <div className="flex-1 overflow-auto">
        <ProfilePage 
          user={user} 
          onOpenProfileSetup={() => setIsProfileSetupOpen(true)}
        />
      </div>
    </div>
  );

  const SettingsPageWrapper = () => (
    <div className="h-screen flex flex-col">
      <Header 
        user={user} 
        onOpenProfile={() => setIsProfileSetupOpen(true)}
        onOpenSettings={() => setIsParentalControlsOpen(true)}
        onLogout={handleLogout}
        darkMode={darkMode}
        setDarkMode={setDarkMode}
      />
      <div className="flex-1 overflow-auto">
        <SettingsPage 
          user={user} 
          onOpenProfile={() => setIsProfileSetupOpen(true)}
          onOpenParentalControls={() => setIsParentalControlsOpen(true)}
        />
      </div>
    </div>
  );

  const ParentalControlsPageWrapper = () => (
    <div className="h-screen flex flex-col">
      <Header 
        user={user} 
        onOpenProfile={() => setIsProfileSetupOpen(true)}
        onOpenSettings={() => setIsParentalControlsOpen(true)}
        onLogout={handleLogout}
        darkMode={darkMode}
        setDarkMode={setDarkMode}
      />
      <div className="flex-1 overflow-auto">
        <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 p-4">
          <div className="max-w-4xl mx-auto">
            <ParentalControls
              isOpen={true}
              onClose={() => window.history.back()}
              userId={user?.id}
              controls={parentalControls}
              onSave={saveParentalControls}
              isModal={false}
            />
          </div>
        </div>
      </div>
    </div>
  );

  if (isLoading) {
    return (
      <Layout>
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-gray-600">Loading your AI companion...</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      {/* Show welcome page first, then auth, then app */}
      {authState.currentView === 'welcome' && (
        <WelcomeScreen />
      )}
      
      {/* Authentication screens */}
      {authState.currentView === 'signup' && (
        <SignUp 
          onSuccess={handleAuthSuccess}
          onSwitchToSignIn={handleSwitchToSignIn}
        />
      )}
      
      {authState.currentView === 'signin' && (
        <SignIn 
          onSuccess={handleAuthSuccess}
          onSwitchToSignUp={handleSwitchToSignUp}
          onForgotPassword={handleSwitchToForgotPassword}
        />
      )}
      
      {authState.currentView === 'forgotPassword' && (
        <ForgotPassword onBackToSignIn={handleBackToSignIn} />
      )}
      
      {/* Main app - only show when authenticated and not showing welcome/auth */}
      {authState.currentView === 'app' && authState.isAuthenticated && user && (
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Navigate to="/chat" />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/profile" element={<ProfilePageWrapper />} />
            <Route path="/settings" element={<SettingsPageWrapper />} />
            <Route path="/parental-controls" element={<ParentalControlsPageWrapper />} />
          </Routes>
        </BrowserRouter>
      )}

      {/* Modals */}
      <ProfileSetup
        isOpen={isProfileSetupOpen}
        onClose={() => {
          setIsProfileSetupOpen(false);
          // If this is a new user and they close without completing, show welcome page
          if (isNewUser) {
            setAuthState({ isAuthenticated: false, token: null, currentView: 'welcome' });
            setUser(null);
          }
        }}
        onSave={user ? updateUserProfile : saveUserProfile}
        onDelete={user ? deleteUserProfile : null}
        initialData={user}
      />

      <ParentalControls
        isOpen={isParentalControlsOpen}
        onClose={() => {
          setIsParentalControlsOpen(false);
          // If this is a new user and they close parental controls, complete onboarding anyway
          if (isNewUser) {
            setIsNewUser(false);
            toast('You can set up parental controls later in Settings.', {
              icon: '👨‍👩‍👧‍👦',
              style: {
                border: '1px solid #3b82f6',
                padding: '16px',
                color: '#1e40af',
              },
            });
          }
        }}
        userId={user?.id}
        controls={parentalControls}
        onSave={saveParentalControls}
      />
    </Layout>
  );
};

export default App;