import React from 'react';
import { motion } from 'framer-motion';
import { 
  UserCircleIcon,
  PencilIcon,
  HeartIcon,
  AcademicCapIcon,
  MapPinIcon,
  CalendarIcon,
  MicrophoneIcon,
  LanguageIcon,
  SparklesIcon
} from '@heroicons/react/24/outline';

const ProfilePage = ({ user, onOpenProfileSetup }) => {
  const getAvatarEmoji = (avatar) => {
    const avatarMap = {
      'bunny': '🐰',
      'lion': '🦁', 
      'puppy': '🐶',
      'robot': '🤖',
      'unicorn': '🦄',
      'dragon': '🐉'
    };
    return avatarMap[avatar] || '😊';
  };

  const formatVoicePersonality = (personality) => {
    return personality?.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) || 'Friendly Companion';
  };

  const formatInterests = (interests) => {
    const interestEmojis = {
      'animals': '🐾',
      'stories': '📚',
      'music': '🎵',
      'science': '🔬',
      'art': '🎨',
      'sports': '⚽',
      'games': '🎮',
      'nature': '🌱',
      'space': '🚀',
      'dinosaurs': '🦕',
      'cooking': '👨‍🍳',
      'dancing': '💃'
    };

    return interests?.map(interest => ({
      name: interest.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      emoji: interestEmojis[interest] || '✨'
    })) || [];
  };

  const formatLearningGoals = (goals) => {
    const goalEmojis = {
      'reading': '📖',
      'math': '🔢',
      'daily_habits': '🗓️',
      'social_skills': '👥',
      'manners': '🤝',
      'emotional_learning': '❤️',
      'creativity': '🎨',
      'problem_solving': '🧩'
    };

    return goals?.map(goal => ({
      name: goal.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      emoji: goalEmojis[goal] || '🎯'
    })) || [];
  };

  const profileStats = [
    {
      label: 'Conversations',
      value: '47',
      icon: '💬',
      color: 'from-blue-500 to-blue-600'
    },
    {
      label: 'Stories Heard',
      value: '12',
      icon: '📚',
      color: 'from-purple-500 to-purple-600'
    },
    {
      label: 'Games Played',
      value: '8',
      icon: '🎮',
      color: 'from-green-500 to-green-600'
    },
    {
      label: 'Learning Streak',
      value: '5 days',
      icon: '🔥',
      color: 'from-orange-500 to-orange-600'
    }
  ];

  const formattedInterests = formatInterests(user?.interests);
  const formattedGoals = formatLearningGoals(user?.learning_goals);

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 p-2 sm:p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header - Mobile optimized */}
        <motion.div
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="text-center mb-6 sm:mb-8"
        >
          <div className="flex items-center justify-center mb-3 sm:mb-4">
            <UserCircleIcon className="w-8 h-8 sm:w-12 sm:h-12 text-purple-600 mr-2 sm:mr-3" />
            <h1 className="text-2xl sm:text-4xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
              My Profile
            </h1>
          </div>
          <p className="text-gray-600 text-base sm:text-lg px-4">
            Here's everything about you, {user?.name}! 👤✨
          </p>
        </motion.div>

        {/* Profile Card - Mobile optimized */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-3xl shadow-xl p-4 sm:p-8 mb-6 sm:mb-8 relative overflow-hidden"
        >
          {/* Background Pattern */}
          <div className="absolute top-0 right-0 w-20 h-20 sm:w-32 sm:h-32 bg-gradient-to-br from-purple-100 to-pink-100 rounded-full opacity-50 -mr-10 sm:-mr-16 -mt-10 sm:-mt-16"></div>
          
          <div className="relative">
            <div className="flex flex-col items-center">
              {/* Avatar - Mobile sized */}
              <div className="w-20 h-20 sm:w-32 sm:h-32 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-3xl sm:text-6xl mb-4 sm:mb-6 shadow-lg">
                {getAvatarEmoji(user?.avatar)}
              </div>

              {/* Basic Info - Mobile centered */}
              <div className="flex-1 text-center w-full">
                <div className="flex items-center justify-center mb-2 sm:mb-2">
                  <h2 className="text-xl sm:text-3xl font-bold text-gray-900 mr-2 sm:mr-3">{user?.name}</h2>
                  <motion.button
                    onClick={onOpenProfileSetup}
                    className="p-1.5 sm:p-2 rounded-full hover:bg-gray-100 transition-colors"
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                  >
                    <PencilIcon className="w-4 h-4 sm:w-5 sm:h-5 text-gray-500" />
                  </motion.button>
                </div>
                
                <div className="flex flex-wrap justify-center gap-2 sm:gap-4 text-gray-600 mb-3 sm:mb-4 text-sm sm:text-base">
                  <div className="flex items-center">
                    <CalendarIcon className="w-3 h-3 sm:w-4 sm:h-4 mr-1 sm:mr-2" />
                    <span className="text-xs sm:text-sm">{user?.age} years old</span>
                  </div>
                  <div className="flex items-center">
                    <MapPinIcon className="w-3 h-3 sm:w-4 sm:h-4 mr-1 sm:mr-2" />
                    <span className="text-xs sm:text-sm">{user?.location}</span>
                  </div>
                  <div className="flex items-center">
                    <MicrophoneIcon className="w-3 h-3 sm:w-4 sm:h-4 mr-1 sm:mr-2" />
                    <span className="text-xs sm:text-sm">{formatVoicePersonality(user?.voice_personality)}</span>
                  </div>
                </div>

                <div className="flex flex-wrap justify-center gap-1.5 sm:gap-2">
                  <span className="px-2 py-1 sm:px-3 sm:py-1 bg-purple-100 text-purple-700 rounded-full text-xs sm:text-sm font-medium">
                    {user?.gender?.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) || 'Not specified'}
                  </span>
                  <span className="px-2 py-1 sm:px-3 sm:py-1 bg-blue-100 text-blue-700 rounded-full text-xs sm:text-sm font-medium">
                    {user?.language?.replace(/\b\w/g, l => l.toUpperCase()) || 'English'}
                  </span>
                  <span className="px-2 py-1 sm:px-3 sm:py-1 bg-green-100 text-green-700 rounded-full text-xs sm:text-sm font-medium">
                    {user?.speech_speed?.replace(/\b\w/g, l => l.toUpperCase()) || 'Normal'} Speed
                  </span>
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {profileStats.map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 + index * 0.1 }}
              className="bg-white rounded-2xl shadow-lg p-6 text-center"
            >
              <div className="text-3xl mb-2">{stat.icon}</div>
              <div className={`text-2xl font-bold bg-gradient-to-r ${stat.color} bg-clip-text text-transparent mb-1`}>
                {stat.value}
              </div>
              <div className="text-sm text-gray-600">{stat.label}</div>
            </motion.div>
          ))}
        </div>

        {/* Interests & Goals */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Interests */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-white rounded-2xl shadow-lg p-6"
          >
            <div className="flex items-center mb-6">
              <HeartIcon className="w-8 h-8 text-pink-600 mr-3" />
              <h3 className="text-2xl font-bold text-gray-900">My Interests</h3>
            </div>

            {formattedInterests.length > 0 ? (
              <div className="grid grid-cols-2 gap-3">
                {formattedInterests.map((interest, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.5 + index * 0.1 }}
                    className="flex items-center p-3 bg-pink-50 rounded-xl"
                  >
                    <span className="text-2xl mr-3">{interest.emoji}</span>
                    <span className="font-medium text-gray-700">{interest.name}</span>
                  </motion.div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <SparklesIcon className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>No interests set yet. Update your profile to add some!</p>
              </div>
            )}
          </motion.div>

          {/* Learning Goals */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5 }}
            className="bg-white rounded-2xl shadow-lg p-6"
          >
            <div className="flex items-center mb-6">
              <AcademicCapIcon className="w-8 h-8 text-blue-600 mr-3" />
              <h3 className="text-2xl font-bold text-gray-900">Learning Goals</h3>
            </div>

            {formattedGoals.length > 0 ? (
              <div className="grid grid-cols-1 gap-3">
                {formattedGoals.map((goal, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.6 + index * 0.1 }}
                    className="flex items-center p-3 bg-blue-50 rounded-xl"
                  >
                    <span className="text-2xl mr-3">{goal.emoji}</span>
                    <span className="font-medium text-gray-700">{goal.name}</span>
                  </motion.div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <AcademicCapIcon className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>No learning goals set yet. Update your profile to add some!</p>
              </div>
            )}
          </motion.div>
        </div>

        {/* Edit Profile Button */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="text-center mt-8"
        >
          <motion.button
            onClick={onOpenProfileSetup}
            className="px-8 py-4 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-2xl font-semibold hover:from-purple-700 hover:to-blue-700 transition-all duration-200 shadow-lg hover:shadow-xl"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <PencilIcon className="w-5 h-5 mr-2 inline" />
            Edit Profile
          </motion.button>
        </motion.div>
      </div>
    </div>
  );
};

export default ProfilePage;