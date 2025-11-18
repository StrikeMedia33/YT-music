/**
 * Video Job Detail Page
 *
 * Display comprehensive details about a single video job.
 */
'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { getVideoJob, cancelVideoJob, type VideoJobDetail } from '@/lib/api';
import { Button, Loading, ErrorMessage, StatusBadge, ConfirmDialog, useToast } from '@/components/ui';
import { useJobProgress } from '@/lib/hooks/use-job-progress';
import { ProgressTracker } from '@/components/progress/ProgressTracker';

export default function VideoJobDetailPage() {
  const params = useParams();
  const router = useRouter();
  const toast = useToast();
  const jobId = params.id as string;

  const [job, setJob] = useState<VideoJobDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [canceling, setCanceling] = useState(false);
  const [showCancelConfirm, setShowCancelConfirm] = useState(false);

  // Real-time progress tracking via SSE
  const shouldTrackProgress =
    !!job &&
    !['completed', 'failed', 'cancelled', 'ready_for_export'].includes(job.status);

  const { status, progress, message, isConnected } = useJobProgress({
    jobId,
    enabled: shouldTrackProgress,
    onUpdate: (event) => {
      console.log('Progress update:', event);
      // Optionally reload job data when status changes
      if (event.status !== job?.status) {
        loadJob();
      }
    },
    onComplete: () => {
      // Reload job data when pipeline completes
      loadJob();
    },
  });

  useEffect(() => {
    if (jobId) {
      loadJob();
    }
  }, [jobId]);

  async function loadJob() {
    try {
      setLoading(true);
      setError(null);
      const data = await getVideoJob(jobId);
      setJob(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load video job');
    } finally {
      setLoading(false);
    }
  }

  async function handleCancelJob() {
    try {
      setCanceling(true);
      await cancelVideoJob(jobId);
      toast.success('Job cancelled', 'The video job has been cancelled.');
      setShowCancelConfirm(false);
      // Reload job data to reflect cancelled status
      await loadJob();
    } catch (err: any) {
      toast.error('Failed to cancel job', err.message || 'An error occurred');
      setShowCancelConfirm(false);
    } finally {
      setCanceling(false);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loading size="lg" message="Loading job details..." />
      </div>
    );
  }

  if (error || !job) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <ErrorMessage
            title="Failed to Load Job"
            message={error || 'Job not found'}
            onRetry={loadJob}
          />
          <div className="mt-4">
            <Button onClick={() => router.push('/video-jobs')}>
              ← Back to Jobs
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between mb-6">
            <Button
              variant="secondary"
              onClick={() => router.push('/video-jobs')}
            >
              ← Back to All Jobs
            </Button>
            <div className="flex items-center gap-3">
              <StatusBadge status={job.status} />
              {!['completed', 'failed', 'cancelled'].includes(job.status) && (
                <Button
                  variant="danger"
                  onClick={() => setShowCancelConfirm(true)}
                  disabled={canceling}
                >
                  Cancel Job
                </Button>
              )}
            </div>
          </div>
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Video Job Details
              </h1>
              <p className="mt-1 text-sm text-gray-500 font-mono">
                ID: {job.id}
              </p>
              {isConnected && (
                <p className="mt-1 text-xs text-green-600 flex items-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse" />
                  Live updates enabled
                </p>
              )}
            </div>
          </div>
        </motion.div>

        {/* Progress Tracker */}
        {!['completed', 'failed', 'cancelled'].includes(job.status) && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="mb-6"
          >
            <ProgressTracker
              currentStatus={status || job.status}
              progress={progress}
              message={message}
            />
          </motion.div>
        )}

        {/* Overview Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white shadow rounded-lg p-6 mb-6"
        >
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Job Overview
          </h2>
          <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <dt className="text-sm font-medium text-gray-500">Channel</dt>
              <dd className="mt-1 text-sm text-gray-900">{job.channel.name}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Niche</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {job.channel.brand_niche}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">
                Target Duration
              </dt>
              <dd className="mt-1 text-sm text-gray-900">
                {job.target_duration_minutes} minutes
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Created At</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {new Date(job.created_at).toLocaleString()}
              </dd>
            </div>
            {job.local_video_path && (
              <div className="sm:col-span-2">
                <dt className="text-sm font-medium text-gray-500">
                  Video Output Path
                </dt>
                <dd className="mt-1 text-sm text-gray-900 font-mono bg-gray-50 p-2 rounded">
                  {job.local_video_path}
                </dd>
              </div>
            )}
            {job.error_message && (
              <div className="sm:col-span-2">
                <dt className="text-sm font-medium text-red-500">Error</dt>
                <dd className="mt-1 text-sm text-red-700 bg-red-50 p-2 rounded">
                  {job.error_message}
                </dd>
              </div>
            )}
          </dl>
        </motion.div>

        {/* Prompts Section */}
        {job.prompts_json && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white shadow rounded-lg p-6 mb-6"
          >
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Generated Prompts
            </h2>
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
              {/* Music Prompts */}
              {job.prompts_json.music_prompts && (
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-2">
                    Music Prompts ({job.prompts_json.music_prompts.length})
                  </h3>
                  <div className="bg-gray-50 rounded-lg p-4 max-h-96 overflow-y-auto">
                    <ul className="space-y-2">
                      {job.prompts_json.music_prompts.map(
                        (prompt: string, i: number) => (
                          <li key={i} className="text-sm text-gray-700">
                            <span className="font-medium text-gray-500">
                              {i + 1}.
                            </span>{' '}
                            {prompt}
                          </li>
                        )
                      )}
                    </ul>
                  </div>
                </div>
              )}

              {/* Visual Prompts */}
              {job.prompts_json.visual_prompts && (
                <div>
                  <h3 className="text-sm font-medium text-gray-700 mb-2">
                    Visual Prompts ({job.prompts_json.visual_prompts.length})
                  </h3>
                  <div className="bg-gray-50 rounded-lg p-4 max-h-96 overflow-y-auto">
                    <ul className="space-y-2">
                      {job.prompts_json.visual_prompts.map(
                        (prompt: string, i: number) => (
                          <li key={i} className="text-sm text-gray-700">
                            <span className="font-medium text-gray-500">
                              {i + 1}.
                            </span>{' '}
                            {prompt}
                          </li>
                        )
                      )}
                    </ul>
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        )}

        {/* Audio Tracks Section */}
        {job.audio_tracks && job.audio_tracks.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-white shadow rounded-lg p-6 mb-6"
          >
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Audio Tracks ({job.audio_tracks.length})
            </h2>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">
                      #
                    </th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">
                      Duration
                    </th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">
                      Provider
                    </th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">
                      File Path
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {job.audio_tracks.map((track) => (
                    <tr key={track.id} className="hover:bg-gray-50">
                      <td className="px-4 py-2 text-sm font-medium text-gray-900">
                        {track.order_index}
                      </td>
                      <td className="px-4 py-2 text-sm text-gray-500">
                        {Math.floor(track.duration_seconds / 60)}:
                        {String(Math.floor(track.duration_seconds % 60)).padStart(
                          2,
                          '0'
                        )}
                      </td>
                      <td className="px-4 py-2 text-sm text-gray-500">
                        {track.provider}
                      </td>
                      <td className="px-4 py-2 text-sm text-gray-500 font-mono truncate max-w-md">
                        {track.local_file_path}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </motion.div>
        )}

        {/* Images Section */}
        {job.images && job.images.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="bg-white shadow rounded-lg p-6 mb-6"
          >
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Generated Visuals ({job.images.length})
            </h2>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">
                      #
                    </th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">
                      Provider
                    </th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">
                      File Path
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {job.images.map((image) => (
                    <tr key={image.id} className="hover:bg-gray-50">
                      <td className="px-4 py-2 text-sm font-medium text-gray-900">
                        {image.order_index}
                      </td>
                      <td className="px-4 py-2 text-sm text-gray-500">
                        {image.provider}
                      </td>
                      <td className="px-4 py-2 text-sm text-gray-500 font-mono truncate max-w-md">
                        {image.local_file_path}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </motion.div>
        )}

        {/* Render Task Section */}
        {job.render_task && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="bg-white shadow rounded-lg p-6"
          >
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Render Information
            </h2>
            <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <dt className="text-sm font-medium text-gray-500">
                  Resolution
                </dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {job.render_task.resolution}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Duration</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {Math.floor(job.render_task.duration_seconds / 60)} min{' '}
                  {Math.floor(job.render_task.duration_seconds % 60)} sec
                </dd>
              </div>
              <div className="sm:col-span-2">
                <dt className="text-sm font-medium text-gray-500">
                  Video File Path
                </dt>
                <dd className="mt-1 text-sm text-gray-900 font-mono bg-gray-50 p-2 rounded">
                  {job.render_task.local_video_path}
                </dd>
              </div>
            </dl>
          </motion.div>
        )}
      </div>

      {/* Cancel Confirmation Modal */}
      <ConfirmDialog
        isOpen={showCancelConfirm}
        onClose={() => setShowCancelConfirm(false)}
        onConfirm={handleCancelJob}
        title="Cancel Video Job?"
        description="Are you sure you want to cancel this job? This action cannot be undone."
        confirmText="Cancel Job"
        cancelText="Keep Job"
        variant="danger"
        loading={canceling}
      />
    </div>
  );
}
