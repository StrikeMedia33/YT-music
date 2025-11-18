/**
 * Video Job Detail Panel Component
 *
 * Slide-in panel for viewing video job details with real-time progress tracking.
 * Extracted from app/video-jobs/[id]/page.tsx for use in slide-in panel.
 */
'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { getVideoJob, cancelVideoJob, type VideoJobDetail } from '@/lib/api';
import { Button, Loading, ErrorMessage, StatusBadge, ConfirmDialog, useToast } from '@/components/ui';
import { useJobProgress } from '@/lib/hooks/use-job-progress';
import { ProgressTracker } from '@/components/progress/ProgressTracker';

interface VideoJobDetailPanelProps {
  jobId: string;
  onClose: () => void;
}

export function VideoJobDetailPanel({ jobId, onClose }: VideoJobDetailPanelProps) {
  const toast = useToast();
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
      <div className="flex items-center justify-center py-20">
        <Loading size="lg" message="Loading job details..." />
      </div>
    );
  }

  if (error || !job) {
    return (
      <div className="p-6">
        <ErrorMessage
          title="Failed to Load Job"
          message={error || 'Job not found'}
          onRetry={loadJob}
        />
      </div>
    );
  }

  return (
    <div className="overflow-y-auto">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <StatusBadge status={job.status} />
            {!['completed', 'failed', 'cancelled'].includes(job.status) && (
              <Button
                variant="danger"
                onClick={() => setShowCancelConfirm(true)}
                disabled={canceling}
                size="sm"
              >
                Cancel Job
              </Button>
            )}
          </div>
        </div>
        <div>
          <h2 className="text-xl font-bold text-gray-900">
            {job.niche_label}
          </h2>
          <p className="mt-1 text-xs text-gray-500 font-mono break-all">
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

      {/* Progress Tracker */}
      {!['completed', 'failed', 'cancelled'].includes(job.status) && (
        <div className="mb-6">
          <ProgressTracker
            currentStatus={status || job.status}
            progress={progress}
            message={message}
          />
        </div>
      )}

      {/* Overview Section */}
      <div className="bg-gray-50 rounded-lg p-4 mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Job Overview
        </h3>
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
              <dd className="mt-1 text-sm text-gray-900 font-mono bg-white p-2 rounded break-all">
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
      </div>

      {/* Prompts Section */}
      {job.prompts_json && (
        <div className="bg-gray-50 rounded-lg p-4 mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Generated Prompts
          </h3>
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            {/* Music Prompts */}
            {job.prompts_json.music_prompts && (
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-2">
                  Music Prompts ({job.prompts_json.music_prompts.length})
                </h4>
                <div className="bg-white rounded-lg p-4 max-h-96 overflow-y-auto">
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
                <h4 className="text-sm font-medium text-gray-700 mb-2">
                  Visual Prompts ({job.prompts_json.visual_prompts.length})
                </h4>
                <div className="bg-white rounded-lg p-4 max-h-96 overflow-y-auto">
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
        </div>
      )}

      {/* Audio Tracks Section */}
      {job.audio_tracks && job.audio_tracks.length > 0 && (
        <div className="bg-gray-50 rounded-lg p-4 mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Audio Tracks ({job.audio_tracks.length})
          </h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-white">
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
              <tbody className="divide-y divide-gray-200 bg-white">
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
        </div>
      )}

      {/* Images Section */}
      {job.images && job.images.length > 0 && (
        <div className="bg-gray-50 rounded-lg p-4 mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Generated Visuals ({job.images.length})
          </h3>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-white">
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
              <tbody className="divide-y divide-gray-200 bg-white">
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
        </div>
      )}

      {/* Render Tasks Section */}
      {job.render_tasks && job.render_tasks.length > 0 && (
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Render Tasks ({job.render_tasks.length})
          </h3>
          <div className="space-y-2">
            {job.render_tasks.map((task) => (
              <div key={task.id} className="bg-white rounded p-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-900">
                    Task #{task.id.slice(0, 8)}
                  </span>
                  <StatusBadge status={task.status} />
                </div>
                {task.output_file_path && (
                  <p className="text-xs text-gray-500 font-mono break-all">
                    {task.output_file_path}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

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
