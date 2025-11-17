/**
 * Video Creation Wizard
 *
 * Multi-step guided wizard for creating video jobs.
 */
'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { FiArrowLeft, FiArrowRight, FiCheck } from 'react-icons/fi';
import { Button } from '@/components/ui';
import {
  createVideoJob,
  listChannels,
  type Channel,
  type VideoJobCreate,
} from '@/lib/api';

interface WizardStep {
  id: number;
  title: string;
  description: string;
}

const steps: WizardStep[] = [
  {
    id: 1,
    title: 'Video Concept',
    description: 'Define your video idea and mood',
  },
  {
    id: 2,
    title: 'Channel Selection',
    description: 'Choose the target channel',
  },
  {
    id: 3,
    title: 'Customization',
    description: 'Configure video parameters',
  },
  {
    id: 4,
    title: 'Review & Launch',
    description: 'Confirm and create your video',
  },
];

export function VideoCreationWizard() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(1);
  const [channels, setChannels] = useState<Channel[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form data
  const [formData, setFormData] = useState({
    idea: '',
    niche: '',
    mood: [] as string[],
    channelId: '',
    duration: 70,
    numTracks: 20,
    crossfade: 2,
  });

  // Load channels on mount
  React.useEffect(() => {
    loadChannels();
  }, []);

  async function loadChannels() {
    try {
      const data = await listChannels();
      setChannels(data.filter((c) => c.is_active));
    } catch (err: any) {
      setError(err.message || 'Failed to load channels');
    }
  }

  async function handleSubmit() {
    try {
      setLoading(true);
      setError(null);

      const jobData: VideoJobCreate = {
        channel_id: formData.channelId,
        target_duration_minutes: formData.duration,
      };

      const newJob = await createVideoJob(jobData);
      router.push(`/video-jobs/${newJob.id}`);
    } catch (err: any) {
      setError(err.message || 'Failed to create video job');
    } finally {
      setLoading(false);
    }
  }

  const isStepValid = () => {
    switch (currentStep) {
      case 1:
        return formData.niche.length > 0;
      case 2:
        return formData.channelId.length > 0;
      case 3:
        return true;
      case 4:
        return true;
      default:
        return false;
    }
  };

  const selectedChannel = channels.find((c) => c.id === formData.channelId);

  return (
    <div className="max-w-4xl mx-auto">
      {/* Progress Steps */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          {steps.map((step, index) => (
            <React.Fragment key={step.id}>
              <div className="flex flex-col items-center flex-1">
                <motion.div
                  initial={false}
                  animate={{
                    backgroundColor:
                      currentStep >= step.id ? '#3B82F6' : '#E5E7EB',
                    scale: currentStep === step.id ? 1.1 : 1,
                  }}
                  className="w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold mb-2"
                >
                  {currentStep > step.id ? (
                    <FiCheck />
                  ) : (
                    step.id
                  )}
                </motion.div>
                <p
                  className={`text-xs font-medium text-center ${
                    currentStep >= step.id ? 'text-blue-600' : 'text-gray-500'
                  }`}
                >
                  {step.title}
                </p>
              </div>
              {index < steps.length - 1 && (
                <div className="flex-1 h-0.5 mx-2 mt-5 bg-gray-200">
                  <motion.div
                    initial={false}
                    animate={{
                      width: currentStep > step.id ? '100%' : '0%',
                    }}
                    transition={{ duration: 0.3 }}
                    className="h-full bg-blue-600"
                  />
                </div>
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Step Content */}
      <div className="bg-white rounded-lg shadow-lg p-8">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentStep}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
          >
            {/* Step 1: Video Concept */}
            {currentStep === 1 && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-2">
                    {steps[0].title}
                  </h2>
                  <p className="text-gray-600">{steps[0].description}</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Video Idea (Optional)
                  </label>
                  <textarea
                    value={formData.idea}
                    onChange={(e) =>
                      setFormData({ ...formData, idea: e.target.value })
                    }
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    rows={4}
                    placeholder="Describe your video concept... (e.g., 'Calm ambient electronic music for studying and focus')"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Niche / Genre *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.niche}
                    onChange={(e) =>
                      setFormData({ ...formData, niche: e.target.value })
                    }
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="e.g., Ambient Electronic, Lo-Fi Hip Hop, Classical Piano"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Mood Keywords
                  </label>
                  <div className="flex flex-wrap gap-2 mb-3">
                    {['Calm', 'Energetic', 'Focused', 'Relaxing', 'Uplifting', 'Atmospheric'].map(
                      (mood) => (
                        <button
                          key={mood}
                          type="button"
                          onClick={() => {
                            const isSelected = formData.mood.includes(mood);
                            setFormData({
                              ...formData,
                              mood: isSelected
                                ? formData.mood.filter((m) => m !== mood)
                                : [...formData.mood, mood],
                            });
                          }}
                          className={`px-4 py-2 rounded-full text-sm font-medium transition ${
                            formData.mood.includes(mood)
                              ? 'bg-blue-100 text-blue-700 border-2 border-blue-500'
                              : 'bg-gray-100 text-gray-700 border-2 border-transparent hover:border-gray-300'
                          }`}
                        >
                          {mood}
                        </button>
                      )
                    )}
                  </div>
                  <p className="text-xs text-gray-500">
                    Select moods to guide the AI generation
                  </p>
                </div>
              </div>
            )}

            {/* Step 2: Channel Selection */}
            {currentStep === 2 && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-2">
                    {steps[1].title}
                  </h2>
                  <p className="text-gray-600">{steps[1].description}</p>
                </div>

                {channels.length === 0 ? (
                  <div className="text-center py-8 bg-gray-50 rounded-lg">
                    <p className="text-gray-600 mb-4">
                      No active channels found. Create a channel first.
                    </p>
                    <Button
                      onClick={() => router.push('/channels')}
                      variant="primary"
                    >
                      Go to Channels
                    </Button>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 gap-4">
                    {channels.map((channel) => (
                      <motion.div
                        key={channel.id}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() =>
                          setFormData({ ...formData, channelId: channel.id })
                        }
                        className={`p-6 rounded-lg border-2 cursor-pointer transition ${
                          formData.channelId === channel.id
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <h3 className="font-semibold text-gray-900 text-lg">
                              {channel.name}
                            </h3>
                            <p className="text-sm text-gray-600 mt-1">
                              {channel.brand_niche}
                            </p>
                            <p className="text-xs text-gray-500 mt-2">
                              ID: {channel.youtube_channel_id}
                            </p>
                          </div>
                          {formData.channelId === channel.id && (
                            <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                              <FiCheck className="text-white" />
                            </div>
                          )}
                        </div>
                      </motion.div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Step 3: Customization */}
            {currentStep === 3 && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-2">
                    {steps[2].title}
                  </h2>
                  <p className="text-gray-600">{steps[2].description}</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Target Duration: {formData.duration} minutes
                  </label>
                  <input
                    type="range"
                    min="60"
                    max="120"
                    value={formData.duration}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        duration: parseInt(e.target.value),
                      })
                    }
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>60 min</span>
                    <span>90 min</span>
                    <span>120 min</span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Number of Tracks
                    </label>
                    <input
                      type="number"
                      min="10"
                      max="30"
                      value={formData.numTracks}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          numTracks: parseInt(e.target.value),
                        })
                      }
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Default: 20 tracks
                    </p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Crossfade Duration (seconds)
                    </label>
                    <input
                      type="number"
                      min="0"
                      max="5"
                      step="0.5"
                      value={formData.crossfade}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          crossfade: parseFloat(e.target.value),
                        })
                      }
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Default: 2 seconds
                    </p>
                  </div>
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-sm text-blue-800">
                    <strong>Estimated output:</strong> {formData.numTracks} tracks
                    × ~{Math.floor(formData.duration / formData.numTracks)} minutes
                    each = {formData.duration} minutes total video
                  </p>
                </div>
              </div>
            )}

            {/* Step 4: Review & Launch */}
            {currentStep === 4 && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 mb-2">
                    {steps[3].title}
                  </h2>
                  <p className="text-gray-600">{steps[3].description}</p>
                </div>

                <div className="bg-gray-50 rounded-lg p-6 space-y-4">
                  <div>
                    <h3 className="text-sm font-medium text-gray-500">
                      Video Concept
                    </h3>
                    <p className="text-gray-900 mt-1">
                      {formData.idea || 'No description provided'}
                    </p>
                  </div>

                  <div>
                    <h3 className="text-sm font-medium text-gray-500">Niche</h3>
                    <p className="text-gray-900 mt-1">{formData.niche}</p>
                  </div>

                  {formData.mood.length > 0 && (
                    <div>
                      <h3 className="text-sm font-medium text-gray-500">Mood</h3>
                      <div className="flex flex-wrap gap-2 mt-1">
                        {formData.mood.map((mood) => (
                          <span
                            key={mood}
                            className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm"
                          >
                            {mood}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  <div>
                    <h3 className="text-sm font-medium text-gray-500">
                      Channel
                    </h3>
                    <p className="text-gray-900 mt-1">
                      {selectedChannel?.name} ({selectedChannel?.brand_niche})
                    </p>
                  </div>

                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <h3 className="text-sm font-medium text-gray-500">
                        Duration
                      </h3>
                      <p className="text-gray-900 mt-1">
                        {formData.duration} minutes
                      </p>
                    </div>
                    <div>
                      <h3 className="text-sm font-medium text-gray-500">
                        Tracks
                      </h3>
                      <p className="text-gray-900 mt-1">{formData.numTracks}</p>
                    </div>
                    <div>
                      <h3 className="text-sm font-medium text-gray-500">
                        Crossfade
                      </h3>
                      <p className="text-gray-900 mt-1">
                        {formData.crossfade}s
                      </p>
                    </div>
                  </div>
                </div>

                {error && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <p className="text-sm text-red-800">{error}</p>
                  </div>
                )}

                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <p className="text-sm text-yellow-800">
                    <strong>Note:</strong> Once created, the video job will be
                    automatically processed by the background worker. You can
                    monitor progress from the job detail page.
                  </p>
                </div>
              </div>
            )}
          </motion.div>
        </AnimatePresence>

        {/* Navigation Buttons */}
        <div className="flex items-center justify-between mt-8 pt-6 border-t border-gray-200">
          <Button
            variant="ghost"
            onClick={() => setCurrentStep(Math.max(1, currentStep - 1))}
            disabled={currentStep === 1}
          >
            <FiArrowLeft className="mr-2" />
            Previous
          </Button>

          {currentStep < steps.length ? (
            <Button
              onClick={() => setCurrentStep(currentStep + 1)}
              disabled={!isStepValid()}
            >
              Next
              <FiArrowRight className="ml-2" />
            </Button>
          ) : (
            <Button
              onClick={handleSubmit}
              disabled={loading || !isStepValid()}
              loading={loading}
            >
              Create Video Job
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
