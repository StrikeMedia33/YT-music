/**
 * Videos Page
 *
 * Display and manage completed videos organized by channel.
 */
'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FiGrid, FiList, FiVideo } from 'react-icons/fi';
import {
  listVideos,
  listChannels,
  type VideoJob,
  type Channel,
  type VideoStatusDisplay,
} from '@/lib/api';
import { Button, Loading, ErrorMessage, StatusBadge } from '@/components/ui';
import { VideoCard } from '@/components/videos/VideoCard';
import { VideoStatusBadge } from '@/components/videos/VideoStatusBadge';

type ViewMode = 'grid' | 'table';

export default function VideosPage() {
  const [videos, setVideos] = useState<VideoJob[]>([]);
  const [channels, setChannels] = useState<Channel[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [channelFilter, setChannelFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<VideoStatusDisplay | 'all'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState<ViewMode>('grid');

  // Load data
  useEffect(() => {
    loadData();
  }, [channelFilter, statusFilter]);

  async function loadData() {
    try {
      setLoading(true);
      setError(null);

      const [videosData, channelsData] = await Promise.all([
        listVideos({
          channel_id: channelFilter !== 'all' ? channelFilter : undefined,
          video_status: statusFilter !== 'all' ? statusFilter : undefined,
        }),
        listChannels(),
      ]);

      setVideos(videosData);
      setChannels(channelsData);
    } catch (err: any) {
      setError(err.message || 'Failed to load videos');
    } finally {
      setLoading(false);
    }
  }

  // Filter videos by search query
  const filteredVideos = videos.filter((video) => {
    const searchLower = searchQuery.toLowerCase();
    return (
      (video.video_title?.toLowerCase().includes(searchLower) ||
        video.niche_label.toLowerCase().includes(searchLower))
    );
  });

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <Loading size="lg" message="Loading videos..." />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">Videos</h1>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Manage your completed videos and publishing workflow.
          </p>
        </div>

        {/* Error Message */}
        {error && <ErrorMessage message={error} onRetry={loadData} className="mb-6" />}

        {/* Filters and View Toggle */}
        <div className="mb-6 grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Channel Filter */}
          <select
            value={channelFilter}
            onChange={(e) => setChannelFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
          >
            <option value="all">All Channels</option>
            {channels.map((channel) => (
              <option key={channel.id} value={channel.id}>
                {channel.name}
              </option>
            ))}
          </select>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as VideoStatusDisplay | 'all')}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
          >
            <option value="all">All Statuses</option>
            <option value="production">Production</option>
            <option value="draft">Draft</option>
            <option value="scheduled">Scheduled</option>
            <option value="published">Published</option>
          </select>

          {/* Search */}
          <input
            type="search"
            placeholder="Search by title or niche..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
          />

          {/* View Toggle */}
          <div className="flex gap-2">
            <Button
              variant={viewMode === 'grid' ? 'primary' : 'secondary'}
              onClick={() => setViewMode('grid')}
              className="flex-1"
            >
              <FiGrid className="w-4 h-4 mr-2" />
              Grid
            </Button>
            <Button
              variant={viewMode === 'table' ? 'primary' : 'secondary'}
              onClick={() => setViewMode('table')}
              className="flex-1"
            >
              <FiList className="w-4 h-4 mr-2" />
              Table
            </Button>
          </div>
        </div>

        {/* Content */}
        {filteredVideos.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-gray-800 dark:to-gray-700 rounded-xl shadow-sm border-2 border-dashed border-blue-200 dark:border-gray-600 p-12 text-center"
          >
            <div className="w-20 h-20 mx-auto mb-6 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center">
              <FiVideo className="w-10 h-10 text-blue-600 dark:text-blue-400" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-3">
              No videos found
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6 max-w-md mx-auto">
              {statusFilter !== 'all' || channelFilter !== 'all'
                ? 'Try adjusting your filters to see more videos.'
                : 'Complete video jobs will appear here once they reach the "ready for export" status.'}
            </p>
          </motion.div>
        ) : viewMode === 'grid' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredVideos.map((video) => (
              <VideoCard
                key={video.id}
                video={video}
                onView={(id) => alert(`View video: ${id}`)}
                onEdit={(id) => alert(`Edit metadata: ${id}`)}
                onSchedule={(id) => alert(`Schedule: ${id}`)}
                onPublish={(id) => alert(`Publish: ${id}`)}
              />
            ))}
          </div>
        ) : (
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-900">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Title
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Channel
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Duration
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Created
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {filteredVideos.map((video) => (
                  <tr
                    key={video.id}
                    onClick={() => alert(`View video: ${video.id}`)}
                    className="hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer"
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
                        {video.video_title || video.niche_label}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {video.niche_label}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {video.video_status && (
                        <VideoStatusBadge status={video.video_status} />
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {video.target_duration_minutes} min
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {new Date(video.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
