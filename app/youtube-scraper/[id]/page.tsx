/**
 * YouTube Channel Analysis Page
 *
 * View detailed analysis of a scraped YouTube channel including videos and statistics.
 */
'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { FiArrowLeft, FiExternalLink, FiClock, FiEye, FiThumbsUp, FiMessageSquare, FiTrendingUp } from 'react-icons/fi';
import {
  getScrapedChannel,
  getChannelVideos,
  getChannelAnalysis,
  type ScrapedChannel,
  type ScrapedVideo,
  type VideoAnalysisStats,
} from '@/lib/api';
import { Loading, useToast } from '@/components/ui';

export default function ChannelAnalysisPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const toast = useToast();
  const channelId = parseInt(params.id);

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
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loading size="lg" message="Loading channel analysis..." />
      </div>
    );
  }

  if (!channel) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Channel not found</h2>
          <Link href="/youtube-scraper" className="text-blue-600 hover:text-blue-800">
            Back to scraper
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Back Button */}
        <Link
          href="/youtube-scraper"
          className="inline-flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900 mb-6"
        >
          <FiArrowLeft className="w-4 h-4" />
          Back to scraper
        </Link>

        {/* Channel Header */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h1 className="text-2xl font-bold text-gray-900">{channel.channel_name}</h1>
              <p className="text-sm text-gray-600 mt-1">{channel.description}</p>
              <div className="mt-4 flex items-center gap-4 text-sm text-gray-500">
                <span>Channel ID: {channel.youtube_channel_id}</span>
                <a
                  href={channel.channel_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-blue-600 hover:text-blue-800"
                >
                  View on YouTube
                  <FiExternalLink className="w-3 h-3" />
                </a>
              </div>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-500">Last scraped</div>
              <div className="text-lg font-semibold text-gray-900">{formatDate(channel.last_scraped_at)}</div>
            </div>
          </div>
        </div>

        {/* Statistics Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
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
          <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Most Common Keywords</h2>
            <div className="flex flex-wrap gap-2">
              {stats.most_common_keywords.map((keyword, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800"
                >
                  {keyword}
                </span>
              ))}
            </div>
            <p className="mt-3 text-xs text-gray-500">
              Use these keywords to understand content patterns and generate relevant prompt ideas.
            </p>
          </div>
        )}

        {/* Videos List */}
        <div className="bg-white rounded-lg shadow-sm">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">
              Scraped Videos ({videos.length})
            </h2>
          </div>

          {videos.length === 0 ? (
            <div className="px-6 py-12 text-center">
              <p className="text-gray-500">No videos scraped for this channel.</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {videos.map((video) => (
                <VideoCard key={video.id} video={video} />
              ))}
            </div>
          )}
        </div>
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
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    purple: 'bg-purple-50 text-purple-600',
    orange: 'bg-orange-50 text-orange-600',
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-lg shadow-sm p-6"
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{label}</p>
          <p className="mt-2 text-3xl font-bold text-gray-900">{value}</p>
        </div>
        <div className={`p-3 rounded-lg ${colorClasses[color]}`}>{icon}</div>
      </div>
    </motion.div>
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
    <div className="px-6 py-4 hover:bg-gray-50 transition">
      <div className="flex items-start gap-4">
        {/* Thumbnail */}
        {video.thumbnail_url && (
          <div className="flex-shrink-0">
            <img
              src={video.thumbnail_url}
              alt={video.title}
              className="w-40 h-24 object-cover rounded-lg"
            />
          </div>
        )}

        {/* Content */}
        <div className="flex-1 min-w-0">
          <a
            href={video.video_url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm font-medium text-gray-900 hover:text-blue-600 flex items-start gap-1"
          >
            {video.title}
            <FiExternalLink className="w-3 h-3 mt-0.5 flex-shrink-0" />
          </a>

          {video.description && (
            <p className="mt-1 text-xs text-gray-600 line-clamp-2">{video.description}</p>
          )}

          {/* Metadata */}
          <div className="mt-2 flex items-center gap-4 text-xs text-gray-500">
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
            {video.comment_count !== undefined && (
              <span className="flex items-center gap-1">
                <FiMessageSquare className="w-3 h-3" />
                {formatNumber(video.comment_count)}
              </span>
            )}
          </div>

          {/* Keywords */}
          {video.title_keywords && video.title_keywords.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-1">
              {video.title_keywords.slice(0, 5).map((keyword, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-700"
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
