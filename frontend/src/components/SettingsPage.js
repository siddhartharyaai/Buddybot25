import React from 'react';
import { motion } from 'framer-motion';
import { 
  Cog6ToothIcon,
  UserCircleIcon,
  ShieldCheckIcon,
  SpeakerWaveIcon,
  PaintBrushIcon,
  InformationCircleIcon
} from '@heroicons/react/24/outline';

const SettingsPage = ({ user, onOpenProfile, onOpenParentalControls }) => {
  const settingSections = [
    {
      title: 'Profile',
      description: 'Update your personal information and preferences',
      icon: UserCircleIcon,
      action: onOpenProfile,
      color: 'from-blue-500 to-blue-600',
      items: [
        'Name and age',
        'Voice personality',
        'Learning goals',
        'Interests'
      ]
    },
    {
      title: 'Parental Controls',
      description: 'Manage safety settings and content restrictions',
      icon: ShieldCheckIcon,
      action: onOpenParentalControls,
      color: 'from-green-500 to-green-600',
      items: [
        'Content filtering',
        'Time limits',
        'Activity monitoring',
        'Privacy settings'
      ]
    }
  ];

  const aboutInfo = [
    {
      label: 'App Version',
      value: '1.5.0 (Phase 1.5)'
    },
    {
      label: 'AI Model',
      value: 'Gemini 2.0 Flash'
    },
    {
      label: 'Voice Engine',
      value: 'Deepgram Nova 3 + Aura 2'
    },
    {
      label: 'Supported Languages',
      value: 'English, Hinglish'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ y: -20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="text-center mb-8"
        >
          <div className="flex items-center justify-center mb-4">
            <Cog6ToothIcon className="w-12 h-12 text-gray-600 mr-3" />
            <h1 className="text-4xl font-bold bg-gradient-to-r from-gray-700 to-blue-600 bg-clip-text text-transparent">
              Settings
            </h1>
          </div>
          <p className="text-gray-600 text-lg">
            Customize your AI Buddy experience, {user?.name}! ⚙️
          </p>
        </motion.div>

        {/* User Info Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-2xl shadow-lg p-6 mb-8"
        >
          <div className="flex items-center">
            <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center mr-4">
              <span className="text-2xl text-white">
                {user?.avatar === 'bunny' ? '🐰' :
                 user?.avatar === 'lion' ? '🦁' :
                 user?.avatar === 'puppy' ? '🐶' :
                 user?.avatar === 'robot' ? '🤖' :
                 user?.avatar === 'unicorn' ? '🦄' :
                 user?.avatar === 'dragon' ? '🐉' : '😊'}
              </span>
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold text-gray-900">{user?.name}</h2>
              <p className="text-gray-600">Age {user?.age} • {user?.location}</p>
              <p className="text-sm text-purple-600 font-medium mt-1">
                Voice: {user?.voice_personality?.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </p>
            </div>
          </div>
        </motion.div>

        {/* Settings Sections */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {settingSections.map((section, index) => (
            <motion.div
              key={section.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 + index * 0.1 }}
              className="bg-white rounded-2xl shadow-lg overflow-hidden hover:shadow-xl transition-all duration-200"
            >
              <div className={`h-2 bg-gradient-to-r ${section.color}`}></div>
              <div className="p-6">
                <div className="flex items-center mb-4">
                  <section.icon className="w-8 h-8 text-gray-600 mr-3" />
                  <h3 className="text-xl font-bold text-gray-900">
                    {section.title}
                  </h3>
                </div>
                
                <p className="text-gray-600 mb-4">
                  {section.description}
                </p>

                <ul className="space-y-2 mb-6">
                  {section.items.map((item, idx) => (
                    <li key={idx} className="flex items-center text-sm text-gray-500">
                      <div className="w-1.5 h-1.5 bg-gray-300 rounded-full mr-3"></div>
                      {item}
                    </li>
                  ))}
                </ul>

                <motion.button
                  onClick={section.action}
                  className={`w-full py-3 rounded-xl font-medium text-white bg-gradient-to-r ${section.color} hover:shadow-lg transition-all duration-200`}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  Open {section.title}
                </motion.button>
              </div>
            </motion.div>
          ))}
        </div>

        {/* About Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white rounded-2xl shadow-lg p-6"
        >
          <div className="flex items-center mb-6">
            <InformationCircleIcon className="w-8 h-8 text-gray-600 mr-3" />
            <h3 className="text-xl font-bold text-gray-900">
              About AI Buddy
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {aboutInfo.map((info, index) => (
              <div key={index} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                <span className="font-medium text-gray-700">{info.label}</span>
                <span className="text-gray-600">{info.value}</span>
              </div>
            ))}
          </div>

          <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg">
            <p className="text-sm text-gray-600 leading-relaxed">
              AI Buddy is your smart companion designed to provide safe, educational, and entertaining 
              conversations for children. Built with advanced AI technology and comprehensive safety features 
              to ensure a positive experience for both children and parents.
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default SettingsPage;