/**
 * YouTube Channel Scraper Page
 *
 * Discover and scrape YouTube channels for content research and analysis.
 */
'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { FiYoutube, FiSearch, FiDatabase, FiEye, FiTrash2, FiRefreshCw } from 'react-icons/fi';
import {
  listScrapedChannels,
  discoverChannel,
  scrapeChannel,
  deleteScrapedChannel,
  type ScrapedChannel,
  type ChannelDiscoverResponse,
} from '@/lib/api';
import { Button, Loading, useToast } from '@/components/ui';

export default function YouTubeScraperPage() {
  const toast = useToast();
  const [channels, setChannels] = useState<ScrapedChannel[]>([]);
  const [loading, setLoading] = useState(true);
  const [discovering, setDiscovering] = useState(false);
  const [scraping, setScraping] = useState(false);
  const [discoveryResult, setDiscoveryResult] = useState<ChannelDiscoverResponse | null>(null);

  // Form state
  const [channelUrl, setChannelUrl] = useState('');
  const [videoLimit, setVideoLimit] = useState(50);
  const [includeMetadata, setIncludeMetadata] = useState(false);

  useEffect(() => {
    loadChannels();
  }, []);

  async function loadChannels() {
    try {
      setLoading(true);
      const data = await listScrapedChannels({ limit: 100 });
      setChannels(data);
    } catch (err: any) {
      toast.error('Failed to load channels', err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleDiscover(e: React.FormEvent) {
    e.preventDefault();

    if (!channelUrl.trim()) {
      toast.error('URL required', 'Please enter a YouTube channel URL');
      return;
    }

    try {
      setDiscovering(true);
      const result = await discoverChannel({ channel_url: channelUrl });

      if (result.success) {
        setDiscoveryResult(result);
        toast.success('Channel discovered!', `Found: ${result.channel_name}`);
      } else {
        toast.error('Discovery failed', result.error || 'Could not discover channel');
        setDiscoveryResult(null);
      }
    } catch (err: any) {
      toast.error('Discovery failed', err.message);
      setDiscoveryResult(null);
    } finally {
      setDiscovering(false);
    }
  }

  async function handleScrape() {
    if (!discoveryResult || !discoveryResult.success) {
      toast.error('No channel', 'Please discover a channel first');
      return;
    }

    try {
      setScraping(true);
      const result = await scrapeChannel({
        channel_url: channelUrl,
        video_limit: videoLimit,
        include_detailed_metadata: includeMetadata,
      });

      if (result.success) {
        toast.success(
          'Scraping complete!',
          `Scraped ${result.videos_scraped} videos from ${result.channel_name}`
        );
        setChannelUrl('');
        setDiscoveryResult(null);
        await loadChannels();
      } else {
        toast.error('Scraping failed', result.error || 'Unknown error');
      }
    } catch (err: any) {
      toast.error('Scraping failed', err.message);
    } finally {
      setScraping(false);
    }
  }

  async function handleDelete(channelId: number, channelName: string) {
    if (!confirm(`Delete "${channelName}" and all its scraped videos?`)) {
      return;
    }

    try {
      await deleteScrapedChannel(channelId);
      toast.success('Channel deleted', `${channelName} has been removed`);
      await loadChannels();
    } catch (err: any) {
      toast.error('Failed to delete channel', err.message);
    }
  }

  function formatDate(dateStr?: string) {
    if (!dateStr) return 'Never';
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  }

  function getStatusBadge(status: string) {
    const config: Record<string, { label: string; color: string }> = {
      pending: { label: 'Pending', color: 'bg-gray-100 text-gray-800' },
      scraping: { label: 'Scraping...', color: 'bg-blue-100 text-blue-800' },
      completed: { label: 'Completed', color: 'bg-green-100 text-green-800' },
      failed: { label: 'Failed', color: 'bg-red-100 text-red-800' },
    };

    const badge = config[status] || config.pending;
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${badge.color}`}>
        {badge.label}
      </span>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loading size="lg" message="Loading scraped channels..." />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <FiYoutube className="text-red-600" />
            YouTube Channel Analyzer
          </h1>
          <p className="mt-2 text-sm text-gray-600">
            Scrape YouTube channels to analyze content patterns and generate prompt ideas.
          </p>
        </div>

        {/* Scraping Form */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Scrape New Channel</h2>

          <form onSubmit={handleDiscover} className="space-y-4">
            {/* YouTube URL Input */}
            <div>
              <label htmlFor="channel-url" className="block text-sm font-medium text-gray-700 mb-2">
                YouTube Channel URL
              </label>
              <input
                id="channel-url"
                type="text"
                value={channelUrl}
                onChange={(e) => setChannelUrl(e.target.value)}
                placeholder="https://youtube.com/@channelname or https://youtube.com/channel/UCxxxxx"
                className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <p className="mt-1 text-xs text-gray-500">
                Supports @username, /channel/ID, and custom URL formats
              </p>
            </div>

            {/* Discovery Result */}
            {discoveryResult && discoveryResult.success && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-green-50 border border-green-200 rounded-lg p-4"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="text-sm font-semibold text-green-900">{discoveryResult.channel_name}</h3>
                    <p className="text-xs text-green-700 mt-1">{discoveryResult.description}</p>
                    <div className="mt-2 grid grid-cols-2 gap-2 text-xs text-green-700">
                      <div>
                        <span className="font-medium">Channel ID:</span> {discoveryResult.channel_id}
                      </div>
                      <div>
                        <span className="font-medium">URL:</span>{' '}
                        <a
                          href={discoveryResult.channel_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="underline"
                        >
                          View on YouTube
                        </a>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Scraping Options */}
                <div className="mt-4 pt-4 border-t border-green-200 space-y-3">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label htmlFor="video-limit" className="block text-xs font-medium text-green-900 mb-1">
                        Number of videos to scrape
                      </label>
                      <input
                        id="video-limit"
                        type="number"
                        min="1"
                        max="50"
                        value={videoLimit}
                        onChange={(e) => setVideoLimit(parseInt(e.target.value) || 50)}
                        className="w-full px-3 py-2 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-500"
                      />
                      <p className="mt-1 text-xs text-green-600">1-50 videos (RSS feeds limited to ~15)</p>
                    </div>

                    <div className="flex items-center">
                      <input
                        id="include-metadata"
                        type="checkbox"
                        checked={includeMetadata}
                        onChange={(e) => setIncludeMetadata(e.target.checked)}
                        className="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
                      />
                      <label htmlFor="include-metadata" className="ml-2 text-xs font-medium text-green-900">
                        Include detailed metadata
                        <span className="block text-green-600 font-normal mt-0.5">
                          (Slower, includes views/likes)
                        </span>
                      </label>
                    </div>
                  </div>

                  <Button
                    onClick={handleScrape}
                    loading={scraping}
                    variant="primary"
                    className="w-full"
                  >
                    <FiDatabase className="w-4 h-4" />
                    {scraping ? 'Scraping...' : 'Scrape Channel'}
                  </Button>
                </div>
              </motion.div>
            )}

            {/* Discovery Button */}
            {!discoveryResult && (
              <Button type="submit" loading={discovering} variant="primary">
                <FiSearch className="w-4 h-4" />
                {discovering ? 'Discovering...' : 'Discover Channel'}
              </Button>
            )}

            {discoveryResult && !discoveryResult.success && (
              <Button type="submit" loading={discovering} variant="secondary">
                <FiRefreshCw className="w-4 h-4" />
                Try Again
              </Button>
            )}
          </form>
        </div>

        {/* Scraped Channels List */}
        <div className="bg-white rounded-lg shadow-sm">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">
              Scraped Channels ({channels.length})
            </h2>
          </div>

          {channels.length === 0 ? (
            <div className="px-6 py-12 text-center">
              <FiYoutube className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No channels scraped yet</h3>
              <p className="mt-1 text-sm text-gray-500">
                Enter a YouTube channel URL above to get started.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Channel
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Videos
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Last Scraped
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {channels.map((channel) => (
                    <tr key={channel.id} className="hover:bg-gray-50 transition">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div>
                            <div className="text-sm font-medium text-gray-900">{channel.channel_name}</div>
                            <div className="text-sm text-gray-500">{channel.youtube_channel_id}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{channel.video_count_scraped}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {getStatusBadge(channel.scrape_status)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDate(channel.last_scraped_at)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                        <Link
                          href={`/youtube-scraper/${channel.id}`}
                          className="inline-flex items-center gap-1.5 text-blue-600 hover:text-blue-900"
                        >
                          <FiEye className="w-4 h-4" />
                          View
                        </Link>
                        <button
                          onClick={() => handleDelete(channel.id, channel.channel_name)}
                          className="inline-flex items-center gap-1.5 text-red-600 hover:text-red-900"
                        >
                          <FiTrash2 className="w-4 h-4" />
                          Delete
                        </button>
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
