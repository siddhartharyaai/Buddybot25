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
import StoriesPage from './components/StoriesPage';
import ProfilePage from './components/ProfilePage';
import SettingsPage from './components/SettingsPage';

import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const App = () => {
  const [user, setUser] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [isProfileSetupOpen, setIsProfileSetupOpen] = useState(false);
  const [isParentalControlsOpen, setIsParentalControlsOpen] = useState(false);
  const [parentalControls, setParentalControls] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [darkMode, setDarkMode] = useState(() => {
    // Check localStorage for dark mode preference
    const saved = localStorage.getItem('ai_companion_dark_mode');
    return saved ? JSON.parse(saved) : false;
  });
  const [chatMessages, setChatMessages] = useState([]);
  const [chatHistory, setChatHistory] = useState({});

  useEffect(() => {
    checkUserProfile();
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

  const loadChatHistory = async (currentSessionId) => {
    try {
      // First try to load from localStorage
      const savedHistory = localStorage.getItem(`chat_history_${user?.id}_${currentSessionId}`);
      if (savedHistory) {
        const messages = JSON.parse(savedHistory);
        setChatMessages(messages);
        setChatHistory(prev => ({ ...prev, [currentSessionId]: messages }));
      } else {
        // Initialize with welcome message if no history exists
        const welcomeMessage = {
          id: Date.now(),
          type: 'bot',
          content: `Hi ${user?.name}! 👋 I'm Buddy, your AI companion. How can I help you today?`,
          timestamp: new Date().toISOString()
        };
        setChatMessages([welcomeMessage]);
        setChatHistory(prev => ({ ...prev, [currentSessionId]: [welcomeMessage] }));
      }
    } catch (error) {
      console.error('Error loading chat history:', error);
      // Fallback welcome message
      const welcomeMessage = {
        id: Date.now(),
        type: 'bot',
        content: `Hi ${user?.name}! 👋 I'm Buddy, your AI companion. How can I help you today?`,
        timestamp: new Date().toISOString()
      };
      setChatMessages([welcomeMessage]);
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
    try {
      // Check if user profile exists in localStorage
      const savedUser = localStorage.getItem('ai_companion_user');
      
      if (!savedUser) {
        // Create a guest/demo user for immediate access to voice functionality
        console.log('🎯 No user profile found, creating guest demo user for immediate access...');
        const guestUser = await createGuestUser();
        if (guestUser) {
          setUser(guestUser);
          await createSession(guestUser.id);
          await loadParentalControls(guestUser.id);
          setIsLoading(false);
          return;
        } else {
          // Fallback to profile setup if guest creation fails
          setIsProfileSetupOpen(true);
          setIsLoading(false);
          return;
        }
      }
      
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
          // User exists in backend, proceed normally
          const backendUser = await response.json();
          setUser(backendUser);
          await createSession(backendUser.id);
          await loadParentalControls(backendUser.id);
        } else {
          // User doesn't exist in backend, create guest user instead of clearing
          console.log('🎯 User not found in backend, creating guest demo user...');
          localStorage.removeItem('ai_companion_user');
          const guestUser = await createGuestUser();
          if (guestUser) {
            setUser(guestUser);
            await createSession(guestUser.id);
            await loadParentalControls(guestUser.id);
          } else {
            setIsProfileSetupOpen(true);
          }
        }
      } catch (error) {
        console.error('Error verifying user profile with backend:', error);
        // Network error, create guest user instead of profile setup
        console.log('🎯 Network error, creating guest demo user...');
        localStorage.removeItem('ai_companion_user');
        const guestUser = await createGuestUser();
        if (guestUser) {
          setUser(guestUser);
          await createSession(guestUser.id);
          await loadParentalControls(guestUser.id);
        } else {
          setIsProfileSetupOpen(true);
        }
      }
    } catch (error) {
      console.error('Error checking user profile:', error);
      // Create guest user as fallback
      const guestUser = await createGuestUser();
      if (guestUser) {
        setUser(guestUser);
        await createSession(guestUser.id);
        await loadParentalControls(guestUser.id);
      } else {
        setIsProfileSetupOpen(true);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const createGuestUser = async () => {
    try {
      console.log('👤 Creating guest demo user for immediate voice access...');
      
      const guestProfileData = {
        name: "Demo Kid",
        age: 7,
        location: "Demo City",
        timezone: "America/New_York",
        language: "english",
        voice_personality: "friendly_companion",
        interests: ["stories", "games", "music"],
        learning_goals: ["reading", "math"],
        parent_email: "demo@example.com",
        avatar: "bunny",
        gender: "child",
        speech_speed: "normal",
        is_guest: true  // Flag this as a guest user
      };

      const response = await fetch(`${API}/users/profile`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(guestProfileData),
      });

      if (response.ok) {
        const userData = await response.json();
        console.log('✅ Guest demo user created successfully:', userData.id);
        
        // Save to localStorage but mark as guest
        localStorage.setItem('ai_companion_user', JSON.stringify({
          ...userData,
          is_guest: true
        }));
        
        return userData;
      } else {
        console.error('❌ Failed to create guest user:', response.status);
        return null;
      }
    } catch (error) {
      console.error('❌ Error creating guest user:', error);
      return null;
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
    }
  };

  const saveUserProfile = async (profileData) => {
    try {
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
        parent_email: profileData.parent_email || null
      };

      console.log('Saving profile data:', backendProfileData);

      const response = await fetch(`${API}/users/profile`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(backendProfileData)
      });

      const data = await response.json();
      console.log('Profile save response:', { status: response.status, data });

      if (response.ok) {
        setUser(data);
        localStorage.setItem('ai_companion_user', JSON.stringify(data));
        await createSession(data.id);
        await loadParentalControls(data.id);
        toast.success('Profile created successfully!');
      } else {
        console.error('Profile save failed:', response.status, data);
        throw new Error(data.detail || `Failed to create profile (HTTP ${response.status})`);
      }
    } catch (error) {
      console.error('Error saving profile:', error);
      toast.error(`Failed to save profile: ${error.message}`);
      throw error;
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
        parent_email: profileData.parent_email || null
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
        toast.success('Profile updated successfully!');
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
        toast.success('Parental controls updated successfully!');
      } else {
        throw new Error(data.detail || 'Failed to update parental controls');
      }
    } catch (error) {
      console.error('Error updating parental controls:', error);
      throw error;
    }
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
            Your smart companion for stories, songs, learning, and fun conversations. 
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
            <p className="text-gray-600">Talk naturally with your AI companion using voice messages and responses.</p>
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
          onClick={() => setIsProfileSetupOpen(true)}
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

  const StoriesPageWrapper = () => (
    <div className="h-screen flex flex-col">
      <Header 
        user={user} 
        onOpenProfile={() => setIsProfileSetupOpen(true)}
        onOpenSettings={() => setIsParentalControlsOpen(true)}
      />
      <div className="flex-1 overflow-auto">
        <StoriesPage 
          user={user} 
          sessionId={sessionId}
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
      <BrowserRouter>
        <Routes>
          <Route path="/" element={user ? <Navigate to="/chat" /> : <WelcomeScreen />} />
          <Route path="/chat" element={user ? <ChatPage /> : <Navigate to="/" />} />
          <Route path="/stories" element={user ? <StoriesPageWrapper /> : <Navigate to="/" />} />
          <Route path="/profile" element={user ? <ProfilePageWrapper /> : <Navigate to="/" />} />
          <Route path="/settings" element={user ? <SettingsPageWrapper /> : <Navigate to="/" />} />
        </Routes>
      </BrowserRouter>

      {/* Modals */}
      <ProfileSetup
        isOpen={isProfileSetupOpen}
        onClose={() => setIsProfileSetupOpen(false)}
        onSave={user ? updateUserProfile : saveUserProfile}
        onDelete={user ? deleteUserProfile : null}
        initialData={user}
      />

      <ParentalControls
        isOpen={isParentalControlsOpen}
        onClose={() => setIsParentalControlsOpen(false)}
        userId={user?.id}
        controls={parentalControls}
        onSave={saveParentalControls}
      />
    </Layout>
  );
};

export default App;
