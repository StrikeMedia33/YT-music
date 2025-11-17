/**
 * Video Jobs List Page
 *
 * List all video jobs and create new ones.
 */
'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  listVideoJobs,
  createVideoJob,
  listChannels,
  type VideoJob,
  type VideoJobCreate,
  type Channel,
} from '@/lib/api';
import { Button, Loading, ErrorMessage, StatusBadge, useToast } from '@/components/ui';
import { useUIStore } from '@/lib/store/ui-store';

export default function VideoJobsPage() {
  const router = useRouter();
  const { addNotification } = useUIStore();
  const toast = useToast();
  const [jobs, setJobs] = useState<VideoJob[]>([]);
  const [channels, setChannels] = useState<Channel[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [creating, setCreating] = useState(false);

  // Form state
  const [formData, setFormData] = useState<VideoJobCreate>({
    channel_id: '',
    target_duration_minutes: 70,
  });

  // Load jobs and channels on mount
  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      setLoading(true);
      setError(null);
      const [jobsData, channelsData] = await Promise.all([
        listVideoJobs(),
        listChannels(),
      ]);
      setJobs(jobsData);
      setChannels(channelsData);
    } catch (err: any) {
      setError(err.message || 'Failed to load data');
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateJob(e: React.FormEvent) {
    e.preventDefault();

    try {
      setCreating(true);
      setError(null);
      const newJob = await createVideoJob(formData);

      // Reset form and reload jobs
      setFormData({
        channel_id: '',
        target_duration_minutes: 70,
      });
      setShowCreateForm(false);
      await loadData();

      // Show success toast
      toast.success(
        'Video job created successfully!',
        'The pipeline will begin processing automatically.'
      );

      // Navigate to job detail
      router.push(`/video-jobs/${newJob.id}`);
    } catch (err: any) {
      setError(err.message || 'Failed to create video job');
      toast.error('Failed to create video job', err.message);
    } finally {
      setCreating(false);
    }
  }

  function handleViewJob(jobId: string) {
    router.push(`/video-jobs/${jobId}`);
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loading size="lg" message="Loading video jobs..." />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Video Jobs</h1>
          <p className="mt-2 text-sm text-gray-600">
            Track and manage your video generation jobs.
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <ErrorMessage message={error} onRetry={loadData} className="mb-6" />
        )}

        {/* Create Button */}
        <div className="mb-6">
          <Button
            onClick={() => setShowCreateForm(!showCreateForm)}
            variant={showCreateForm ? 'secondary' : 'primary'}
            disabled={channels.length === 0}
          >
            {showCreateForm ? 'Cancel' : '+ Create Video Job'}
          </Button>
          {channels.length === 0 && (
            <p className="mt-2 text-sm text-gray-500">
              Create a channel first before creating video jobs.
            </p>
          )}
        </div>

        {/* Create Form */}
        {showCreateForm && (
          <div className="bg-white shadow rounded-lg p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Create New Video Job
            </h2>
            <form onSubmit={handleCreateJob}>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <label
                    htmlFor="channel_id"
                    className="block text-sm font-medium text-gray-700 mb-1"
                  >
                    Channel
                  </label>
                  <select
                    id="channel_id"
                    required
                    value={formData.channel_id}
                    onChange={(e) =>
                      setFormData({ ...formData, channel_id: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Select a channel...</option>
                    {channels
                      .filter((c) => c.is_active)
                      .map((channel) => (
                        <option key={channel.id} value={channel.id}>
                          {channel.name} - {channel.brand_niche}
                        </option>
                      ))}
                  </select>
                </div>

                <div>
                  <label
                    htmlFor="target_duration_minutes"
                    className="block text-sm font-medium text-gray-700 mb-1"
                  >
                    Target Duration (minutes)
                  </label>
                  <input
                    type="number"
                    id="target_duration_minutes"
                    required
                    min="60"
                    max="120"
                    value={formData.target_duration_minutes}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        target_duration_minutes: parseInt(e.target.value),
                      })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <p className="mt-1 text-xs text-gray-500">
                    60-120 minutes (20 tracks × 3-6 mins each)
                  </p>
                </div>
              </div>

              <div className="mt-6 flex gap-3">
                <Button type="submit" loading={creating} disabled={creating}>
                  Create Video Job
                </Button>
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => setShowCreateForm(false)}
                >
                  Cancel
                </Button>
              </div>
            </form>
          </div>
        )}

        {/* Jobs Table */}
        <div className="bg-white shadow rounded-lg overflow-hidden">
          {jobs.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500">
                No video jobs yet. Create your first job to get started.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th
                      scope="col"
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      Job ID
                    </th>
                    <th
                      scope="col"
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      Status
                    </th>
                    <th
                      scope="col"
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      Duration
                    </th>
                    <th
                      scope="col"
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      Created
                    </th>
                    <th
                      scope="col"
                      className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {jobs.map((job) => (
                    <tr
                      key={job.id}
                      className="hover:bg-gray-50 cursor-pointer focus-within:ring-2 focus-within:ring-blue-500"
                      onClick={() => handleViewJob(job.id)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                          e.preventDefault();
                          handleViewJob(job.id);
                        }
                      }}
                      tabIndex={0}
                      role="button"
                      aria-label={`View details for job ${job.id.substring(0, 8)}, status: ${job.status}`}
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-mono text-gray-900">
                          {job.id.substring(0, 8)}...
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <StatusBadge status={job.status} />
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {job.target_duration_minutes} min
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(job.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleViewJob(job.id);
                          }}
                        >
                          View Details
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
