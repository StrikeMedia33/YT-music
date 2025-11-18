/**
 * Activity Monitor Panel Component
 *
 * Displays current video job activity with real-time progress tracking.
 * Shows all active jobs (not completed/failed/cancelled).
 */
'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FiActivity, FiExternalLink } from 'react-icons/fi';
import { listVideoJobs, type VideoJob } from '@/lib/api';
import { useJobProgress } from '@/lib/hooks/use-job-progress';
import { StatusBadge, Loading } from '@/components/ui';

interface ActivityMonitorPanelProps {
  onViewJob?: (jobId: string) => void;
}

export function ActivityMonitorPanel({ onViewJob }: ActivityMonitorPanelProps) {
  const [jobs, setJobs] = useState<VideoJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadActiveJobs();
    // Poll for new jobs every 10 seconds
    const interval = setInterval(loadActiveJobs, 10000);
    return () => clearInterval(interval);
  }, []);

  async function loadActiveJobs() {
    try {
      setError(null);
      const allJobs = await listVideoJobs();
      // Filter to only show active jobs
      const activeJobs = allJobs.filter(
        (job) => !['completed', 'failed', 'cancelled', 'ready_for_export'].includes(job.status)
      );
      setJobs(activeJobs);
    } catch (err: any) {
      console.error('Failed to load active jobs:', err);
      setError(err.message || 'Failed to load active jobs');
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loading size="md" message="Loading active jobs..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 text-center">
        <p className="text-sm text-red-600 mb-3">{error}</p>
        <button
          onClick={loadActiveJobs}
          className="text-sm text-blue-600 hover:text-blue-800 font-medium"
        >
          Retry
        </button>
      </div>
    );
  }

  if (jobs.length === 0) {
    return (
      <div className="p-12 text-center">
        <FiActivity className="w-12 h-12 text-gray-300 mx-auto mb-3" />
        <p className="text-gray-500 text-sm">No active jobs</p>
        <p className="text-gray-400 text-xs mt-1">
          Active jobs will appear here when they are running
        </p>
      </div>
    );
  }

  return (
    <div className="divide-y divide-gray-200">
      {jobs.map((job) => (
        <ActiveJobCard key={job.id} job={job} onViewJob={onViewJob} />
      ))}
    </div>
  );
}

/**
 * Individual job card with real-time progress
 */
function ActiveJobCard({
  job,
  onViewJob,
}: {
  job: VideoJob;
  onViewJob?: (jobId: string) => void;
}) {
  // Real-time progress tracking via SSE
  const { status, progress, message, isConnected } = useJobProgress({
    jobId: job.id,
    enabled: true,
  });

  // Use live status if available, otherwise use job status
  const currentStatus = status || job.status;
  const currentProgress = progress !== null ? progress : null;
  const currentMessage = message || 'Processing...';

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="p-4 hover:bg-gray-50 transition"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          {/* Job title and status */}
          <div className="flex items-center gap-2 mb-2">
            <h4 className="text-sm font-medium text-gray-900 truncate">
              {job.niche_label}
            </h4>
            <StatusBadge status={currentStatus} size="sm" />
          </div>

          {/* Progress bar */}
          {currentProgress !== null && (
            <div className="mb-2">
              <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
                <span>Progress</span>
                <span>{currentProgress}%</span>
              </div>
              <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${currentProgress}%` }}
                  transition={{ duration: 0.5 }}
                  className="h-full bg-blue-600 rounded-full"
                />
              </div>
            </div>
          )}

          {/* Current message */}
          <p className="text-xs text-gray-600 line-clamp-2">{currentMessage}</p>

          {/* Live indicator */}
          {isConnected && (
            <div className="flex items-center gap-1.5 mt-2">
              <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
              <span className="text-xs text-green-600">Live updates</span>
            </div>
          )}
        </div>

        {/* View button */}
        {onViewJob && (
          <button
            onClick={() => onViewJob(job.id)}
            className="flex-shrink-0 p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded transition"
            aria-label="View job details"
          >
            <FiExternalLink className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Job metadata */}
      <div className="mt-3 flex items-center gap-4 text-xs text-gray-500">
        <span>Duration: {job.target_duration_minutes}min</span>
        <span>ID: {job.id.slice(0, 8)}</span>
      </div>
    </motion.div>
  );
}
