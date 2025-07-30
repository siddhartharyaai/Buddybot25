import React, { useState, useRef, useEffect } from 'react';

const TextInput = ({ onSendMessage, isLoading, darkMode }) => {
  const [inputValue, setInputValue] = useState('');
  const inputRef = useRef(null);

  useEffect(() => {
    console.log('✅ TextInput component mounted (should only see this once)');
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []); // Empty deps: only on initial mount

  const handleChange = (e) => {
    console.log('📝 Text input changed:', e.target.value);
    setInputValue(e.target.value);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && inputValue.trim() && !isLoading) {
      e.preventDefault();
      onSendMessage(inputValue.trim());
      setInputValue('');
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputValue.trim() && !isLoading) {
      onSendMessage(inputValue.trim());
      setInputValue('');
    }
  };

  return (
    <div className="flex items-center space-x-3">
      <div className="flex-1 relative">
        <input
          ref={inputRef}
          type="text"
          value={inputValue}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder="Type a message..."
          className={`w-full px-4 py-3 pr-12 rounded-full border transition-colors focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
            darkMode 
              ? 'bg-gray-800 border-gray-600 text-white placeholder-gray-400'
              : 'bg-white border-gray-300 text-gray-900 placeholder-gray-500'
          }`}
          disabled={isLoading}
          autoComplete="off"
          autoCorrect="off"
          spellCheck="false"
          key="stable-text-input" // Stable key to prevent remount in parent
        />
        <button
          type="button"
          onClick={handleSubmit}
          disabled={!inputValue.trim() || isLoading}
          className={`absolute right-2 top-1/2 transform -translate-y-1/2 p-2 rounded-full transition-colors ${
            darkMode 
              ? 'text-blue-400 hover:text-blue-300 disabled:text-gray-600' 
              : 'text-blue-500 hover:text-blue-600 disabled:text-gray-400'
          }`}
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
        </button>
      </div>
    </div>
  );
};

export default TextInput;