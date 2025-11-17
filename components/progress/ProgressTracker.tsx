/**
 * Progress Tracker Component
 *
 * Visual representation of video job pipeline progress with real-time updates.
 */
'use client';

import React from 'react';
import { motion } from 'framer-motion';
import {
  FiFileText,
  FiMusic,
  FiImage,
  FiVideo,
  FiCheckCircle,
  FiAlertCircle,
  FiLoader,
} from 'react-icons/fi';
import clsx from 'clsx';

export interface PipelineStep {
  id: string;
  label: string;
  description: string;
  icon: React.ReactNode;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  progress?: number;
  message?: string;
}

interface ProgressTrackerProps {
  currentStatus: string;
  progress?: number;
  message?: string;
  compact?: boolean;
}

// Map job status to pipeline steps
const getPipelineSteps = (
  currentStatus: string,
  message?: string
): PipelineStep[] => {
  const statusHierarchy = [
    'planned',
    'generating_music',
    'generating_image',
    'rendering',
    'ready_for_export',
    'completed',
  ];

  const currentIndex = statusHierarchy.indexOf(currentStatus);
  const isFailed = currentStatus === 'failed';

  return [
    {
      id: 'planned',
      label: 'Prompt Generation',
      description: 'Generating music and visual prompts',
      icon: <FiFileText className="w-5 h-5" />,
      status:
        currentIndex > 0
          ? 'completed'
          : currentIndex === 0
          ? 'in_progress'
          : 'pending',
      message: currentIndex === 0 ? message : undefined,
    },
    {
      id: 'generating_music',
      label: 'Music Generation',
      description: 'Creating 20 unique audio tracks',
      icon: <FiMusic className="w-5 h-5" />,
      status:
        currentIndex > 1
          ? 'completed'
          : currentIndex === 1
          ? isFailed
            ? 'failed'
            : 'in_progress'
          : 'pending',
      message: currentIndex === 1 ? message : undefined,
    },
    {
      id: 'generating_image',
      label: 'Visual Generation',
      description: 'Creating 20 unique visuals',
      icon: <FiImage className="w-5 h-5" />,
      status:
        currentIndex > 2
          ? 'completed'
          : currentIndex === 2
          ? isFailed
            ? 'failed'
            : 'in_progress'
          : 'pending',
      message: currentIndex === 2 ? message : undefined,
    },
    {
      id: 'rendering',
      label: 'Video Rendering',
      description: 'Compositing final MP4 with FFmpeg',
      icon: <FiVideo className="w-5 h-5" />,
      status:
        currentIndex > 3
          ? 'completed'
          : currentIndex === 3
          ? isFailed
            ? 'failed'
            : 'in_progress'
          : 'pending',
      message: currentIndex === 3 ? message : undefined,
    },
    {
      id: 'ready_for_export',
      label: 'Ready for Export',
      description: 'Video ready for upload',
      icon: <FiCheckCircle className="w-5 h-5" />,
      status:
        currentIndex >= 4
          ? currentStatus === 'completed'
            ? 'completed'
            : 'in_progress'
          : 'pending',
      message: currentIndex >= 4 ? message : undefined,
    },
  ];
};

export function ProgressTracker({
  currentStatus,
  progress = 0,
  message,
  compact = false,
}: ProgressTrackerProps) {
  const steps = getPipelineSteps(currentStatus, message);
  const isFailed = currentStatus === 'failed';

  if (compact) {
    return (
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-medium text-gray-900">Pipeline Progress</h3>
          <span className="text-xs text-gray-500">{Math.round(progress)}%</span>
        </div>
        <motion.div
          className="w-full bg-gray-200 rounded-full h-2 overflow-hidden"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <motion.div
            className={clsx(
              'h-full rounded-full',
              isFailed ? 'bg-red-500' : 'bg-blue-600'
            )}
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
          />
        </motion.div>
        {message && (
          <p className="text-xs text-gray-600 mt-2 truncate">{message}</p>
        )}
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-2">
          Pipeline Progress
        </h2>
        {message && (
          <p className="text-sm text-gray-600">{message}</p>
        )}
      </div>

      {/* Progress Bar */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">
            Overall Progress
          </span>
          <span className="text-sm font-medium text-gray-900">
            {Math.round(progress)}%
          </span>
        </div>
        <motion.div
          className="w-full bg-gray-200 rounded-full h-3 overflow-hidden"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        >
          <motion.div
            className={clsx(
              'h-full rounded-full',
              isFailed ? 'bg-red-500' : 'bg-blue-600'
            )}
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
          />
        </motion.div>
      </div>

      {/* Pipeline Steps */}
      <div className="space-y-4">
        {steps.map((step, index) => (
          <motion.div
            key={step.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="relative"
          >
            <div className="flex items-start">
              {/* Step Icon */}
              <div className="flex-shrink-0">
                <motion.div
                  className={clsx(
                    'w-12 h-12 rounded-full flex items-center justify-center',
                    step.status === 'completed' && 'bg-green-100 text-green-600',
                    step.status === 'in_progress' &&
                      'bg-blue-100 text-blue-600',
                    step.status === 'failed' && 'bg-red-100 text-red-600',
                    step.status === 'pending' && 'bg-gray-100 text-gray-400'
                  )}
                  animate={{
                    scale: step.status === 'in_progress' ? [1, 1.05, 1] : 1,
                  }}
                  transition={{
                    duration: 2,
                    repeat: step.status === 'in_progress' ? Infinity : 0,
                    ease: 'easeInOut',
                  }}
                >
                  {step.status === 'completed' && (
                    <FiCheckCircle className="w-6 h-6" />
                  )}
                  {step.status === 'in_progress' && (
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{
                        duration: 2,
                        repeat: Infinity,
                        ease: 'linear',
                      }}
                    >
                      <FiLoader className="w-6 h-6" />
                    </motion.div>
                  )}
                  {step.status === 'failed' && (
                    <FiAlertCircle className="w-6 h-6" />
                  )}
                  {step.status === 'pending' && step.icon}
                </motion.div>
              </div>

              {/* Step Content */}
              <div className="ml-4 flex-1 min-w-0">
                <h4
                  className={clsx(
                    'text-sm font-medium',
                    step.status === 'completed' && 'text-green-900',
                    step.status === 'in_progress' && 'text-blue-900',
                    step.status === 'failed' && 'text-red-900',
                    step.status === 'pending' && 'text-gray-500'
                  )}
                >
                  {step.label}
                </h4>
                <p className="text-sm text-gray-600 mt-1">{step.description}</p>
                {step.message && (
                  <p className="text-xs text-gray-500 mt-1 italic">
                    {step.message}
                  </p>
                )}
              </div>

              {/* Status Badge */}
              <div className="ml-4 flex-shrink-0">
                {step.status === 'completed' && (
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    Completed
                  </span>
                )}
                {step.status === 'in_progress' && (
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    In Progress
                  </span>
                )}
                {step.status === 'failed' && (
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                    Failed
                  </span>
                )}
                {step.status === 'pending' && (
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
                    Pending
                  </span>
                )}
              </div>
            </div>

            {/* Connector Line */}
            {index < steps.length - 1 && (
              <motion.div
                className={clsx(
                  'absolute left-6 top-12 w-0.5 h-4',
                  step.status === 'completed' ? 'bg-green-300' : 'bg-gray-200'
                )}
                initial={{ height: 0 }}
                animate={{ height: 16 }}
                transition={{ delay: index * 0.1 + 0.2 }}
              />
            )}
          </motion.div>
        ))}
      </div>
    </div>
  );
}
