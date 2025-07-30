import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { 
  ShieldCheckIcon, 
  ClockIcon, 
  EyeIcon,
  XMarkIcon,
  BellIcon,
  LockClosedIcon
} from '@heroicons/react/24/outline';

const ParentalControls = ({ isOpen, onClose, userId, controls, onSave }) => {
  const [activeTab, setActiveTab] = useState('time');
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const { register, handleSubmit, formState: { errors }, watch, setValue } = useForm({
    defaultValues: controls || {
      time_limits: {
        monday: 60,
        tuesday: 60,
        wednesday: 60,
        thursday: 60,
        friday: 60,
        saturday: 90,
        sunday: 90
      },
      content_restrictions: [],
      allowed_content_types: ['story', 'song', 'rhyme', 'educational'],
      quiet_hours: {
        start: '20:00',
        end: '07:00'
      },
      monitoring_enabled: true,
      notification_preferences: {
        activity_summary: true,
        safety_alerts: true,
        time_warnings: true
      }
    }
  });

  const days = [
    { key: 'monday', label: 'Monday' },
    { key: 'tuesday', label: 'Tuesday' },
    { key: 'wednesday', label: 'Wednesday' },
    { key: 'thursday', label: 'Thursday' },
    { key: 'friday', label: 'Friday' },
    { key: 'saturday', label: 'Saturday' },
    { key: 'sunday', label: 'Sunday' }
  ];

  const contentTypes = [
    { id: 'story', name: 'Stories', description: 'Fairy tales and narratives' },
    { id: 'song', name: 'Songs', description: 'Music and lullabies' },
    { id: 'rhyme', name: 'Rhymes', description: 'Nursery rhymes and poems' },
    { id: 'educational', name: 'Educational', description: 'Learning content' },
    { id: 'game', name: 'Games', description: 'Interactive activities' }
  ];

  const tabs = [
    { id: 'time', name: 'Time Limits', icon: ClockIcon },
    { id: 'content', name: 'Content', icon: ShieldCheckIcon },
    { id: 'monitoring', name: 'Monitoring', icon: EyeIcon },
    { id: 'notifications', name: 'Notifications', icon: BellIcon }
  ];

  const onSubmit = async (data) => {
    setIsSubmitting(true);
    try {
      await onSave(data);
      toast.success('Parental controls updated successfully!');
      onClose();
    } catch (error) {
      toast.error('Failed to update parental controls');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
      >
        <motion.div
          className="bg-white rounded-3xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden"
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          transition={{ type: 'spring', stiffness: 300, damping: 30 }}
        >
          {/* Header */}
          <div className="p-6 border-b border-gray-100 bg-gradient-to-r from-blue-50 to-purple-50">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
                  <LockClosedIcon className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">Parental Controls</h2>
                  <p className="text-gray-600">Manage your child's experience</p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="p-2 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100 transition-colors"
              >
                <XMarkIcon className="w-6 h-6" />
              </button>
            </div>
          </div>

          {/* Mobile Tabs (Horizontal) - Hidden on desktop */}
          <div className="block md:hidden border-b border-gray-200">
            <nav className="flex overflow-x-auto">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center space-x-2 px-4 py-3 whitespace-nowrap font-medium transition-all duration-200 border-b-2 ${
                      activeTab === tab.id
                        ? 'border-blue-500 text-blue-600 bg-blue-50'
                        : 'border-transparent text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span className="text-sm">{tab.name}</span>
                  </button>
                );
              })}
            </nav>
          </div>

          <div className="flex h-[calc(90vh-120px)] md:h-[calc(90vh-120px)] overflow-hidden">
            {/* Desktop Sidebar - Hidden on mobile */}
            <div className="hidden md:block w-64 bg-gray-50 border-r border-gray-200 p-4">
              <nav className="space-y-2">
                {tabs.map((tab) => {
                  const Icon = tab.icon;
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-200 ${
                        activeTab === tab.id
                          ? 'bg-blue-500 text-white shadow-lg'
                          : 'text-gray-700 hover:bg-gray-100'
                      }`}
                    >
                      <Icon className="w-5 h-5" />
                      <span className="font-medium">{tab.name}</span>
                    </button>
                  );
                })}
              </nav>
            </div>

            {/* Content - Full width on mobile, flexible on desktop */}
            <div className="flex-1 p-4 md:p-6 overflow-y-auto max-h-full">
              <form onSubmit={handleSubmit(onSubmit)}>
                {/* Time Limits Tab */}
                {activeTab === 'time' && (
                  <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="space-y-6"
                  >
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">Daily Time Limits</h3>
                      <div className="space-y-4">
                        {days.map((day) => (
                          <div key={day.key} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                            <span className="font-medium text-gray-900">{day.label}</span>
                            <div className="flex items-center space-x-2">
                              <input
                                {...register(`time_limits.${day.key}`)}
                                type="number"
                                min="0"
                                max="300"
                                className="w-20 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                              />
                              <span className="text-gray-600">minutes</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">Quiet Hours</h3>
                      <div className="bg-gray-50 p-4 rounded-xl">
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Start Time</label>
                            <input
                              {...register('quiet_hours.start')}
                              type="time"
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">End Time</label>
                            <input
                              {...register('quiet_hours.end')}
                              type="time"
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            />
                          </div>
                        </div>
                        <p className="text-sm text-gray-600 mt-2">
                          AI companion will not respond during these hours
                        </p>
                      </div>
                    </div>
                  </motion.div>
                )}

                {/* Content Tab */}
                {activeTab === 'content' && (
                  <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="space-y-6"
                  >
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">Allowed Content Types</h3>
                      <div className="space-y-3">
                        {contentTypes.map((type) => (
                          <label key={type.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                            <div>
                              <h4 className="font-medium text-gray-900">{type.name}</h4>
                              <p className="text-sm text-gray-600">{type.description}</p>
                            </div>
                            <input
                              {...register('allowed_content_types')}
                              type="checkbox"
                              value={type.id}
                              className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                            />
                          </label>
                        ))}
                      </div>
                    </div>

                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">Content Restrictions</h3>
                      <div className="space-y-4">
                        <div className="bg-red-50 border border-red-200 p-4 rounded-xl">
                          <h4 className="font-medium text-red-900 mb-3">Restricted Content Types</h4>
                          <div className="space-y-3">
                            <label className="flex items-center space-x-3">
                              <input
                                {...register('content_restrictions.block_scary')}
                                type="checkbox"
                                className="w-5 h-5 text-red-600 border-gray-300 rounded focus:ring-red-500"
                              />
                              <div>
                                <span className="text-gray-900 font-medium">Block scary content</span>
                                <p className="text-sm text-gray-600">Horror, monsters, frightening themes</p>
                              </div>
                            </label>
                            
                            <label className="flex items-center space-x-3">
                              <input
                                {...register('content_restrictions.block_mature')}
                                type="checkbox"
                                className="w-5 h-5 text-red-600 border-gray-300 rounded focus:ring-red-500"
                              />
                              <div>
                                <span className="text-gray-900 font-medium">Block mature themes</span>
                                <p className="text-sm text-gray-600">Adult topics, complex emotions</p>
                              </div>
                            </label>
                            
                            <label className="flex items-center space-x-3">
                              <input
                                {...register('content_restrictions.block_violence')}
                                type="checkbox"
                                className="w-5 h-5 text-red-600 border-gray-300 rounded focus:ring-red-500"
                              />
                              <div>
                                <span className="text-gray-900 font-medium">Block violent content</span>
                                <p className="text-sm text-gray-600">Fighting, weapons, aggressive behavior</p>
                              </div>
                            </label>
                            
                            <label className="flex items-center space-x-3">
                              <input
                                {...register('content_restrictions.block_inappropriate')}
                                type="checkbox"
                                className="w-5 h-5 text-red-600 border-gray-300 rounded focus:ring-red-500"
                              />
                              <div>
                                <span className="text-gray-900 font-medium">Block inappropriate language</span>
                                <p className="text-sm text-gray-600">Strong language, negative words</p>
                              </div>
                            </label>
                          </div>
                        </div>

                        <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-xl">
                          <h4 className="font-medium text-yellow-900 mb-3">Restricted Keywords</h4>
                          <div className="space-y-3">
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-2">
                                Blocked Words (comma-separated)
                              </label>
                              <textarea
                                {...register('content_restrictions.blocked_keywords')}
                                rows={3}
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                placeholder="Enter words to block, separated by commas"
                              />
                              <p className="text-xs text-gray-500 mt-1">
                                AI Buddy will avoid using these words in conversations
                              </p>
                            </div>
                          </div>
                        </div>

                        <div className="bg-green-50 border border-green-200 p-4 rounded-xl">
                          <h4 className="font-medium text-green-900 mb-3">Allowed Topics</h4>
                          <div className="grid grid-cols-2 gap-3">
                            {[
                              'Animals', 'Nature', 'Science', 'Math', 'Reading',
                              'Art', 'Music', 'Sports', 'Friendship', 'Family'
                            ].map((topic) => (
                              <label key={topic} className="flex items-center space-x-2">
                                <input
                                  {...register('content_restrictions.allowed_topics')}
                                  type="checkbox"
                                  value={topic.toLowerCase()}
                                  className="w-4 h-4 text-green-600 border-gray-300 rounded focus:ring-green-500"
                                />
                                <span className="text-sm text-gray-700">{topic}</span>
                              </label>
                            ))}
                          </div>
                        </div>

                        <div className="bg-blue-50 border border-blue-200 p-4 rounded-xl">
                          <h4 className="font-medium text-blue-900 mb-3">Content Review Settings</h4>
                          <div className="space-y-3">
                            <label className="flex items-center justify-between">
                              <div>
                                <span className="text-gray-900 font-medium">Manual content review</span>
                                <p className="text-sm text-gray-600">Review all AI responses before delivery</p>
                              </div>
                              <input
                                {...register('content_restrictions.manual_review')}
                                type="checkbox"
                                className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                              />
                            </label>
                            
                            <label className="flex items-center justify-between">
                              <div>
                                <span className="text-gray-900 font-medium">Log all conversations</span>
                                <p className="text-sm text-gray-600">Save conversation history for review</p>
                              </div>
                              <input
                                {...register('content_restrictions.log_conversations')}
                                type="checkbox"
                                className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                              />
                            </label>
                          </div>
                        </div>
                      </div>
                    )</div>
                  </motion.div>
                )}

                {/* Monitoring Tab */}
                {activeTab === 'monitoring' && (
                  <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="space-y-6"
                  >
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">Activity Monitoring</h3>
                      <div className="space-y-4">
                        <label className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                          <div>
                            <h4 className="font-medium text-gray-900">Enable Monitoring</h4>
                            <p className="text-sm text-gray-600">Track conversations and activities</p>
                          </div>
                          <input
                            {...register('monitoring_enabled')}
                            type="checkbox"
                            className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                          />
                        </label>
                      </div>
                    </div>

                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">Data Retention</h3>
                      <div className="bg-gray-50 p-4 rounded-xl">
                        <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                          <option value="7">7 days</option>
                          <option value="30">30 days</option>
                          <option value="90">90 days</option>
                        </select>
                        <p className="text-sm text-gray-600 mt-2">
                          How long to keep conversation history
                        </p>
                      </div>
                    </div>
                  </motion.div>
                )}

                {/* Notifications Tab */}
                {activeTab === 'notifications' && (
                  <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="space-y-6"
                  >
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900 mb-4">Notification Preferences</h3>
                      <div className="space-y-4">
                        <label className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                          <div>
                            <h4 className="font-medium text-gray-900">Activity Summary</h4>
                            <p className="text-sm text-gray-600">Daily summary of interactions</p>
                          </div>
                          <input
                            {...register('notification_preferences.activity_summary')}
                            type="checkbox"
                            className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                          />
                        </label>

                        <label className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                          <div>
                            <h4 className="font-medium text-gray-900">Safety Alerts</h4>
                            <p className="text-sm text-gray-600">Notifications for flagged content</p>
                          </div>
                          <input
                            {...register('notification_preferences.safety_alerts')}
                            type="checkbox"
                            className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                          />
                        </label>

                        <label className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                          <div>
                            <h4 className="font-medium text-gray-900">Time Warnings</h4>
                            <p className="text-sm text-gray-600">Alerts when approaching time limits</p>
                          </div>
                          <input
                            {...register('notification_preferences.time_warnings')}
                            type="checkbox"
                            className="w-5 h-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                          />
                        </label>
                      </div>
                    </div>
                  </motion.div>
                )}

                {/* Footer */}
                <div className="flex justify-end space-x-4 mt-8 pt-6 border-t border-gray-100">
                  <button
                    type="button"
                    onClick={onClose}
                    className="px-6 py-3 text-gray-600 hover:text-gray-800 font-medium transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl font-medium hover:from-blue-600 hover:to-purple-700 transition-all duration-200 shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isSubmitting ? 'Saving...' : 'Save Changes'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default ParentalControls;