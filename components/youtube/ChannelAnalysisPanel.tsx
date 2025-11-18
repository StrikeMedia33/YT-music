/**
 * Channel Analysis Panel Component
 *
 * Slide-in panel for viewing YouTube channel analysis including videos and statistics.
 * Extracted from app/youtube-scraper/[id]/page.tsx for use in slide-in panel.
 */
'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FiExternalLink, FiClock, FiEye, FiThumbsUp, FiMessageSquare, FiTrendingUp } from 'react-icons/fi';
import {
  getScrapedChannel,
  getChannelVideos,
  getChannelAnalysis,
  type ScrapedChannel,
  type ScrapedVideo,
  type VideoAnalysisStats,
} from '@/lib/api';
import { Loading, useToast } from '@/components/ui';

interface ChannelAnalysisPanelProps {
  channelId: number;
  onClose: () => void;
}

export function ChannelAnalysisPanel({ channelId, onClose }: ChannelAnalysisPanelProps) {
  const toast = useToast();
  const [channel, setChannel] = useState<ScrapedChannel | null>(null);
  const [videos, setVideos] = useState<ScrapedVideo[]>([]);
  const [stats, setStats] = useState<VideoAnalysisStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (channelId) {
      loadChannelData();
    }
  }, [channelId]);

  async function loadChannelData() {
    try {
      setLoading(true);
      const [channelData, videosData, statsData] = await Promise.all([
        getScrapedChannel(channelId),
        getChannelVideos(channelId, { limit: 100 }),
        getChannelAnalysis(channelId),
      ]);

      setChannel(channelData);
      setVideos(videosData);
      setStats(statsData);
    } catch (err: any) {
      toast.error('Failed to load channel data', err.message);
    } finally {
      setLoading(false);
    }
  }

  function formatNumber(num?: number) {
    if (!num) return '0';
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  }

  function formatDuration(seconds?: number) {
    if (!seconds) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }

  function formatDate(dateStr?: string) {
    if (!dateStr) return 'Unknown';
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loading size="lg" message="Loading channel analysis..." />
      </div>
    );
  }

  if (!channel) {
    return (
      <div className="p-6 text-center">
        <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-2">Channel not found</h2>
      </div>
    );
  }

  return (
    <div className="overflow-y-auto">
      {/* Channel Header */}
      <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 mb-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100">{channel.channel_name}</h2>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1 line-clamp-2">{channel.description}</p>
            <div className="mt-3 flex items-center gap-3 text-xs text-gray-500 dark:text-gray-400">
              <span className="font-mono truncate">{channel.youtube_channel_id}</span>
              <a
                href={channel.channel_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
              >
                YouTube
                <FiExternalLink className="w-3 h-3" />
              </a>
            </div>
          </div>
          <div className="text-right ml-3">
            <div className="text-xs text-gray-500 dark:text-gray-400">Last scraped</div>
            <div className="text-sm font-semibold text-gray-900 dark:text-gray-100">{formatDate(channel.last_scraped_at)}</div>
          </div>
        </div>
      </div>

      {/* Statistics Cards */}
      {stats && (
        <div className="grid grid-cols-2 gap-3 mb-6">
          <StatCard
            icon={<FiTrendingUp />}
            label="Total Videos"
            value={stats.total_videos.toString()}
            color="blue"
          />
          <StatCard
            icon={<FiEye />}
            label="Avg Views"
            value={formatNumber(stats.avg_view_count)}
            color="green"
          />
          <StatCard
            icon={<FiThumbsUp />}
            label="Avg Likes"
            value={formatNumber(stats.avg_like_count)}
            color="purple"
          />
          <StatCard
            icon={<FiClock />}
            label="Avg Duration"
            value={formatDuration(stats.avg_duration_seconds)}
            color="orange"
          />
        </div>
      )}

      {/* Top Keywords */}
      {stats && stats.most_common_keywords.length > 0 && (
        <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 mb-6">
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-3">Most Common Keywords</h3>
          <div className="flex flex-wrap gap-2">
            {stats.most_common_keywords.map((keyword, index) => (
              <span
                key={index}
                className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-400"
              >
                {keyword}
              </span>
            ))}
          </div>
          <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
            Use these keywords to understand content patterns and generate relevant prompt ideas.
          </p>
        </div>
      )}

      {/* Videos List */}
      <div className="bg-gray-50 dark:bg-gray-800 rounded-lg overflow-hidden">
        <div className="px-4 py-3 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100">
            Scraped Videos ({videos.length})
          </h3>
        </div>

        {videos.length === 0 ? (
          <div className="px-4 py-8 text-center">
            <p className="text-sm text-gray-500 dark:text-gray-400">No videos scraped for this channel.</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200 dark:divide-gray-700 max-h-96 overflow-y-auto">
            {videos.map((video) => (
              <VideoCard key={video.id} video={video} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function StatCard({
  icon,
  label,
  value,
  color,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  color: 'blue' | 'green' | 'purple' | 'orange';
}) {
  const colorClasses = {
    blue: 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400',
    green: 'bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400',
    purple: 'bg-purple-50 dark:bg-purple-900/20 text-purple-600 dark:text-purple-400',
    orange: 'bg-orange-50 dark:bg-orange-900/20 text-orange-600 dark:text-orange-400',
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg p-3 shadow-sm">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-medium text-gray-600 dark:text-gray-400">{label}</p>
          <p className="mt-1 text-lg font-bold text-gray-900 dark:text-gray-100">{value}</p>
        </div>
        <div className={`p-2 rounded-lg ${colorClasses[color]}`}>{icon}</div>
      </div>
    </div>
  );
}

function VideoCard({ video }: { video: ScrapedVideo }) {
  function formatNumber(num?: number) {
    if (!num) return '0';
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  }

  function formatDuration(seconds?: number) {
    if (!seconds) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }

  function formatDate(dateStr?: string) {
    if (!dateStr) return 'Unknown';
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  }

  return (
    <div className="px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 transition bg-white dark:bg-gray-800">
      <div className="flex items-start gap-3">
        {/* Thumbnail */}
        {video.thumbnail_url && (
          <div className="flex-shrink-0">
            <img
              src={video.thumbnail_url}
              alt={video.title}
              className="w-32 h-18 object-cover rounded"
            />
          </div>
        )}

        {/* Content */}
        <div className="flex-1 min-w-0">
          <a
            href={video.video_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-xs font-medium text-gray-900 dark:text-gray-100 hover:text-blue-600 dark:hover:text-blue-400 flex items-start gap-1 line-clamp-2"
          >
            {video.title}
            <FiExternalLink className="w-3 h-3 mt-0.5 flex-shrink-0" />
          </a>

          {/* Metadata */}
          <div className="mt-1 flex items-center gap-3 text-xs text-gray-500 dark:text-gray-400">
            {video.published_at && (
              <span className="flex items-center gap-1">
                <FiClock className="w-3 h-3" />
                {formatDate(video.published_at)}
              </span>
            )}
            {video.duration_seconds && <span>{formatDuration(video.duration_seconds)}</span>}
            {video.view_count !== undefined && (
              <span className="flex items-center gap-1">
                <FiEye className="w-3 h-3" />
                {formatNumber(video.view_count)}
              </span>
            )}
            {video.like_count !== undefined && (
              <span className="flex items-center gap-1">
                <FiThumbsUp className="w-3 h-3" />
                {formatNumber(video.like_count)}
              </span>
            )}
          </div>

          {/* Keywords */}
          {video.title_keywords && video.title_keywords.length > 0 && (
            <div className="mt-1 flex flex-wrap gap-1">
              {video.title_keywords.slice(0, 3).map((keyword, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300"
                >
                  {keyword}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
