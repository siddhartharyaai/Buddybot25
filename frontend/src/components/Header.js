import React from 'react';
import { motion } from 'framer-motion';
import { 
  SparklesIcon, 
  UserCircleIcon, 
  Cog6ToothIcon,
  ChatBubbleLeftRightIcon,
  ArrowRightOnRectangleIcon,
  SunIcon,
  MoonIcon
} from '@heroicons/react/24/outline';
import { Link, useLocation } from 'react-router-dom';

const Header = ({ user, onOpenProfile, onOpenSettings, onLogout, darkMode, setDarkMode }) => {
  const location = useLocation();
  
  // Function to get avatar emoji based on user's avatar choice
  const getAvatarEmoji = (avatarType) => {
    const avatarMap = {
      'bunny': '🐰',
      'lion': '🦁', 
      'puppy': '🐶',
      'robot': '🤖',
      'unicorn': '🦄',
      'dragon': '🐉'
    };
    return avatarMap[avatarType] || '😊';
  };
  
  const navigation = [
    { name: 'Chat', href: '/chat', icon: ChatBubbleLeftRightIcon },
    { name: 'Profile', href: '/profile', icon: UserCircleIcon },
    { name: 'Settings', href: '/settings', icon: Cog6ToothIcon },
  ];
  
  return (
    <motion.header 
      className={`backdrop-blur-lg border-b sticky top-0 z-50 ${
        darkMode 
          ? 'bg-gray-900/80 border-gray-700' 
          : 'bg-white/80 border-gray-100'
      }`}
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ type: 'spring', stiffness: 300, damping: 30 }}
    >
      <div className="max-w-7xl mx-auto px-3 sm:px-4 lg:px-8">
        <div className="flex justify-between items-center h-12 sm:h-16">
          {/* Logo - More compact on mobile */}
          <Link to="/" className="flex items-center flex-shrink-0">
            <motion.div 
              className="flex items-center space-x-1 sm:space-x-3"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <div className="w-7 h-7 sm:w-10 sm:h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg sm:rounded-xl flex items-center justify-center shadow-md sm:shadow-lg">
                <SparklesIcon className="w-3 h-3 sm:w-6 sm:h-6 text-white" />
              </div>
              <div className="block">
                <h1 className={`text-lg sm:text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent`}>
                  Buddy
                </h1>
                <p className={`text-xs hidden sm:block ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>Your Smart Friend</p>
              </div>
            </motion.div>
          </Link>
          
          {/* Mobile-Optimized Navigation */}
          <nav className="flex items-center space-x-0.5 sm:space-x-1 overflow-x-auto">
            {navigation.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.href;
              
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`relative px-2 py-1.5 sm:px-3 sm:py-2 rounded-lg sm:rounded-xl transition-all duration-200 whitespace-nowrap ${
                    isActive 
                      ? 'bg-blue-50 text-blue-600' 
                      : 'text-gray-600 hover:text-blue-600 hover:bg-blue-50/50'
                  }`}
                >
                  <div className="flex flex-col sm:flex-row items-center space-y-0.5 sm:space-y-0 sm:space-x-1 md:space-x-2">
                    <Icon className="w-4 h-4 sm:w-4 sm:h-4 md:w-5 md:h-5 flex-shrink-0" />
                    <span className="font-medium text-xs sm:text-xs md:text-sm">{item.name}</span>
                  </div>
                  {isActive && (
                    <motion.div
                      className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-600 rounded-full"
                      layoutId="activeTab"
                      initial={false}
                      transition={{ type: 'spring', stiffness: 500, damping: 40 }}
                    />
                  )}
                </Link>
              );
            })}
          </nav>
          
          {/* User Profile - More compact */}
          <div className="flex items-center space-x-2 sm:space-x-4">
            {user && (
              <motion.div 
                className="flex items-center space-x-1 sm:space-x-3 px-2 py-1 sm:px-4 sm:py-2 bg-gradient-to-r from-blue-50 to-purple-50 rounded-full cursor-pointer"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={onOpenProfile}
              >
                <div className="w-6 h-6 sm:w-8 sm:h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                  {user?.avatar ? (
                    <span className="text-sm sm:text-lg">
                      {getAvatarEmoji(user.avatar)}
                    </span>
                  ) : (
                    <span className="text-white font-bold text-xs sm:text-sm">
                      {user.name?.charAt(0).toUpperCase() || 'U'}
                    </span>
                  )}
                </div>
                <div className="hidden sm:block">
                  <p className="text-sm font-medium text-gray-900">{user.name}</p>
                  <p className="text-xs text-gray-500">Age {user.age}</p>
                </div>
              </motion.div>
            )}
            
            {/* Enhanced Dark Mode Toggle - More Prominent */}
            {setDarkMode && (
              <motion.button
                className={`p-2.5 sm:p-3 rounded-xl transition-all duration-200 shadow-lg transform hover:scale-105 ${
                  darkMode 
                    ? 'bg-gradient-to-r from-yellow-400 to-orange-400 text-gray-900 hover:from-yellow-300 hover:to-orange-300' 
                    : 'bg-gradient-to-r from-gray-700 to-gray-800 text-yellow-400 hover:from-gray-600 hover:to-gray-700'
                }`}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={() => setDarkMode(!darkMode)}
                title={darkMode ? "Switch to Light Mode" : "Switch to Dark Mode"}
                aria-label={darkMode ? "Switch to Light Mode" : "Switch to Dark Mode"}
              >
                {darkMode ? (
                  <SunIcon className="w-6 h-6" />
                ) : (
                  <MoonIcon className="w-6 h-6" />
                )}
              </motion.button>
            )}
            
            {/* Logout Button - New addition */}
            {user && onLogout && (
              <motion.button
                className="p-1.5 sm:p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg sm:rounded-xl transition-colors"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={onLogout}
                title="Logout"
              >
                <ArrowRightOnRectangleIcon className="w-5 h-5 sm:w-6 sm:h-6" />
              </motion.button>
            )}
            
            {/* Settings Button - More compact */}
            <motion.button
              className="p-1.5 sm:p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg sm:rounded-xl transition-colors"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={onOpenSettings}
            >
              <Cog6ToothIcon className="w-5 h-5 sm:w-6 sm:h-6" />
            </motion.button>
          </div>
        </div>
      </div>
    </motion.header>
  );
};

export default Header;