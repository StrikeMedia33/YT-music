/**
 * Channels Page
 *
 * List all channels and create new ones.
 */
'use client';

import React, { useState, useEffect } from 'react';
import {
  listChannels,
  createChannel,
  toggleChannelActive,
  type Channel,
  type ChannelCreate,
} from '@/lib/api';
import { Button, Loading, ErrorMessage } from '@/components/ui';

export default function ChannelsPage() {
  const [channels, setChannels] = useState<Channel[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [creating, setCreating] = useState(false);

  // Form state
  const [formData, setFormData] = useState<ChannelCreate>({
    name: '',
    youtube_channel_id: '',
    brand_niche: '',
    is_active: true,
  });

  // Load channels on mount
  useEffect(() => {
    loadChannels();
  }, []);

  async function loadChannels() {
    try {
      setLoading(true);
      setError(null);
      const data = await listChannels();
      setChannels(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load channels');
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateChannel(e: React.FormEvent) {
    e.preventDefault();

    try {
      setCreating(true);
      setError(null);
      await createChannel(formData);

      // Reset form and reload channels
      setFormData({
        name: '',
        youtube_channel_id: '',
        brand_niche: '',
        is_active: true,
      });
      setShowCreateForm(false);
      await loadChannels();
    } catch (err: any) {
      setError(err.message || 'Failed to create channel');
    } finally {
      setCreating(false);
    }
  }

  async function handleToggleActive(channelId: string, currentStatus: boolean) {
    try {
      await toggleChannelActive(channelId, !currentStatus);
      await loadChannels();
    } catch (err: any) {
      setError(err.message || 'Failed to update channel');
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loading size="lg" message="Loading channels..." />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Channels</h1>
          <p className="mt-2 text-sm text-gray-600">
            Manage your YouTube channels for automated video generation.
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <ErrorMessage
            message={error}
            onRetry={loadChannels}
            className="mb-6"
          />
        )}

        {/* Create Button */}
        <div className="mb-6">
          <Button
            onClick={() => setShowCreateForm(!showCreateForm)}
            variant={showCreateForm ? 'secondary' : 'primary'}
          >
            {showCreateForm ? 'Cancel' : '+ Create Channel'}
          </Button>
        </div>

        {/* Create Form */}
        {showCreateForm && (
          <div className="bg-white shadow rounded-lg p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Create New Channel
            </h2>
            <form onSubmit={handleCreateChannel}>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <label
                    htmlFor="name"
                    className="block text-sm font-medium text-gray-700 mb-1"
                  >
                    Channel Name
                  </label>
                  <input
                    type="text"
                    id="name"
                    required
                    value={formData.name}
                    onChange={(e) =>
                      setFormData({ ...formData, name: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="My Ambient Channel"
                  />
                </div>

                <div>
                  <label
                    htmlFor="youtube_channel_id"
                    className="block text-sm font-medium text-gray-700 mb-1"
                  >
                    YouTube Channel ID
                  </label>
                  <input
                    type="text"
                    id="youtube_channel_id"
                    required
                    value={formData.youtube_channel_id}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        youtube_channel_id: e.target.value,
                      })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="UC..."
                  />
                </div>

                <div className="sm:col-span-2">
                  <label
                    htmlFor="brand_niche"
                    className="block text-sm font-medium text-gray-700 mb-1"
                  >
                    Brand Niche
                  </label>
                  <input
                    type="text"
                    id="brand_niche"
                    required
                    value={formData.brand_niche}
                    onChange={(e) =>
                      setFormData({ ...formData, brand_niche: e.target.value })
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Ambient Electronic Music"
                  />
                </div>
              </div>

              <div className="mt-6 flex gap-3">
                <Button type="submit" loading={creating} disabled={creating}>
                  Create Channel
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

        {/* Channels Table */}
        <div className="bg-white shadow rounded-lg overflow-hidden">
          {channels.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500">
                No channels yet. Create your first channel to get started.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      YouTube ID
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Niche
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Created
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {channels.map((channel) => (
                    <tr key={channel.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">
                          {channel.name}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-500">
                          {channel.youtube_channel_id}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900">
                          {channel.brand_niche}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            channel.is_active
                              ? 'bg-green-100 text-green-800'
                              : 'bg-gray-100 text-gray-800'
                          }`}
                        >
                          {channel.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(channel.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() =>
                            handleToggleActive(channel.id, channel.is_active)
                          }
                        >
                          {channel.is_active ? 'Disable' : 'Enable'}
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
