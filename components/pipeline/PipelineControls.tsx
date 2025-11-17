/**
 * Pipeline Controls Component
 *
 * Manual controls for triggering and managing pipeline steps.
 */
'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  FiPlay,
  FiRefreshCw,
  FiSkipForward,
  FiAlertTriangle,
  FiCheckCircle,
} from 'react-icons/fi';
import { Button } from '@/components/ui';
import clsx from 'clsx';

interface PipelineControlsProps {
  jobId: string;
  currentStatus: string;
  onTriggerStep: (step: PipelineStep) => Promise<void>;
  disabled?: boolean;
}

export type PipelineStep =
  | 'generate_prompts'
  | 'generate_music'
  | 'generate_visuals'
  | 'render_video'
  | 'generate_metadata';

interface StepControl {
  id: PipelineStep;
  label: string;
  description: string;
  icon: React.ReactNode;
  allowedStatuses: string[];
  actionLabel: string;
}

const stepControls: StepControl[] = [
  {
    id: 'generate_prompts',
    label: 'Regenerate Prompts',
    description: 'Generate new music and visual prompts using LLM',
    icon: <FiRefreshCw className="w-5 h-5" />,
    allowedStatuses: ['planned', 'failed'],
    actionLabel: 'Regenerate',
  },
  {
    id: 'generate_music',
    label: 'Generate Music',
    description: 'Create 20 unique audio tracks',
    icon: <FiPlay className="w-5 h-5" />,
    allowedStatuses: ['planned', 'generating_music', 'failed'],
    actionLabel: 'Start/Retry',
  },
  {
    id: 'generate_visuals',
    label: 'Generate Visuals',
    description: 'Create 20 unique visuals',
    icon: <FiPlay className="w-5 h-5" />,
    allowedStatuses: ['generating_music', 'generating_image', 'failed'],
    actionLabel: 'Start/Retry',
  },
  {
    id: 'render_video',
    label: 'Render Video',
    description: 'Compile final MP4 with FFmpeg',
    icon: <FiPlay className="w-5 h-5" />,
    allowedStatuses: ['generating_image', 'rendering', 'failed'],
    actionLabel: 'Start/Retry',
  },
  {
    id: 'generate_metadata',
    label: 'Generate Metadata',
    description: 'Create title, description, and tags',
    icon: <FiRefreshCw className="w-5 h-5" />,
    allowedStatuses: ['ready_for_export', 'completed', 'failed'],
    actionLabel: 'Regenerate',
  },
];

export function PipelineControls({
  jobId,
  currentStatus,
  onTriggerStep,
  disabled = false,
}: PipelineControlsProps) {
  const [loading, setLoading] = useState<PipelineStep | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<PipelineStep | null>(null);

  const handleTrigger = async (step: PipelineStep) => {
    try {
      setLoading(step);
      setError(null);
      setSuccess(null);
      await onTriggerStep(step);
      setSuccess(step);
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(err.message || 'Failed to trigger pipeline step');
    } finally {
      setLoading(null);
    }
  };

  const isStepAvailable = (step: StepControl): boolean => {
    return step.allowedStatuses.includes(currentStatus);
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-2">
          Pipeline Controls
        </h2>
        <p className="text-sm text-gray-600">
          Manually trigger or retry pipeline steps
        </p>
      </div>

      {error && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start"
        >
          <FiAlertTriangle className="w-5 h-5 text-red-600 mr-3 mt-0.5" />
          <div className="flex-1">
            <h4 className="text-sm font-medium text-red-900">Error</h4>
            <p className="text-sm text-red-700 mt-1">{error}</p>
          </div>
          <button
            onClick={() => setError(null)}
            className="text-red-600 hover:text-red-800"
          >
            ×
          </button>
        </motion.div>
      )}

      <div className="space-y-3">
        {stepControls.map((step) => {
          const available = isStepAvailable(step);
          const isLoading = loading === step.id;
          const isSuccess = success === step.id;

          return (
            <motion.div
              key={step.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className={clsx(
                'flex items-center justify-between p-4 rounded-lg border-2 transition',
                available
                  ? 'border-gray-200 bg-white hover:border-blue-300'
                  : 'border-gray-100 bg-gray-50 opacity-60'
              )}
            >
              <div className="flex items-start space-x-4 flex-1">
                <div
                  className={clsx(
                    'flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center',
                    available
                      ? 'bg-blue-100 text-blue-600'
                      : 'bg-gray-200 text-gray-400'
                  )}
                >
                  {step.icon}
                </div>
                <div className="flex-1">
                  <h3 className="text-sm font-medium text-gray-900">
                    {step.label}
                  </h3>
                  <p className="text-xs text-gray-600 mt-1">
                    {step.description}
                  </p>
                  {!available && (
                    <p className="text-xs text-gray-500 mt-1 italic">
                      Not available in current status ({currentStatus})
                    </p>
                  )}
                </div>
              </div>

              <div className="ml-4">
                {isSuccess ? (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="flex items-center text-green-600"
                  >
                    <FiCheckCircle className="w-5 h-5 mr-2" />
                    <span className="text-sm font-medium">Triggered</span>
                  </motion.div>
                ) : (
                  <Button
                    variant={available ? 'primary' : 'ghost'}
                    size="sm"
                    onClick={() => handleTrigger(step.id)}
                    disabled={!available || disabled || isLoading}
                  >
                    {isLoading ? (
                      <>
                        <motion.div
                          animate={{ rotate: 360 }}
                          transition={{
                            duration: 1,
                            repeat: Infinity,
                            ease: 'linear',
                          }}
                          className="mr-2"
                        >
                          <FiRefreshCw className="w-4 h-4" />
                        </motion.div>
                        Processing...
                      </>
                    ) : (
                      <>
                        {step.id.includes('generate') ? (
                          <FiRefreshCw className="w-4 h-4 mr-2" />
                        ) : (
                          <FiPlay className="w-4 h-4 mr-2" />
                        )}
                        {step.actionLabel}
                      </>
                    )}
                  </Button>
                )}
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Quick Actions */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <h3 className="text-sm font-medium text-gray-900 mb-3">
          Quick Actions
        </h3>
        <div className="flex flex-wrap gap-2">
          <Button
            variant="secondary"
            size="sm"
            disabled={
              disabled ||
              loading !== null ||
              !['failed'].includes(currentStatus)
            }
            onClick={() => handleTrigger('generate_prompts')}
          >
            <FiRefreshCw className="w-4 h-4 mr-2" />
            Restart from Beginning
          </Button>
          <Button
            variant="secondary"
            size="sm"
            disabled={
              disabled ||
              loading !== null ||
              !['generating_image', 'rendering', 'failed'].includes(
                currentStatus
              )
            }
            onClick={() => handleTrigger('render_video')}
          >
            <FiSkipForward className="w-4 h-4 mr-2" />
            Skip to Rendering
          </Button>
        </div>
      </div>
    </div>
  );
}
