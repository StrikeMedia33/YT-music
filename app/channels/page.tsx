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
  listGenres,
  listIdeas,
  type Channel,
  type ChannelCreate,
  type GenreWithStats,
  type VideoIdea,
} from '@/lib/api';
import { Button, Loading, ErrorMessage, useToast, SlidePanel, useSlidePanel } from '@/components/ui';
import { ChannelDetailPanel } from '@/components/channels/ChannelDetailPanel';
import { FiChevronDown, FiEdit3 } from 'react-icons/fi';

export default function ChannelsPage() {
  const toast = useToast();
  const [channels, setChannels] = useState<Channel[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [creating, setCreating] = useState(false);

  // Slide panel state
  const channelPanel = useSlidePanel<string>();

  // Form state
  const [formData, setFormData] = useState<ChannelCreate>({
    name: '',
    youtube_channel_id: '',
    brand_niche: '',
    is_active: true,
  });

  // Form validation errors
  const [formErrors, setFormErrors] = useState<{
    name?: string;
    youtube_channel_id?: string;
    brand_niche?: string;
  }>({});

  // Genre and niche selection state
  const [genres, setGenres] = useState<GenreWithStats[]>([]);
  const [ideas, setIdeas] = useState<VideoIdea[]>([]);
  const [selectedGenreId, setSelectedGenreId] = useState<string | null>(null);
  const [nicheInputMode, setNicheInputMode] = useState<'select' | 'custom'>('select');
  const [loadingGenres, setLoadingGenres] = useState(false);

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

  async function loadGenres() {
    try {
      setLoadingGenres(true);
      const data = await listGenres({ with_stats: true });
      setGenres(data);
    } catch (err: any) {
      console.error('Failed to load genres:', err);
      toast.error('Failed to load genres', err.message);
    } finally {
      setLoadingGenres(false);
    }
  }

  async function loadIdeasForGenre(genreId: string) {
    try {
      const data = await listIdeas({ genre_id: genreId, limit: 100 });
      setIdeas(data);
    } catch (err: any) {
      console.error('Failed to load ideas:', err);
      toast.error('Failed to load ideas', err.message);
    }
  }

  // Load genres when create form is shown
  useEffect(() => {
    if (showCreateForm && genres.length === 0) {
      loadGenres();
    }
  }, [showCreateForm]);

  // Load ideas when genre is selected
  useEffect(() => {
    if (selectedGenreId) {
      loadIdeasForGenre(selectedGenreId);
    } else {
      setIdeas([]);
    }
  }, [selectedGenreId]);

  function validateForm(): boolean {
    const errors: typeof formErrors = {};

    if (!formData.name.trim()) {
      errors.name = 'Channel name is required';
    } else if (formData.name.length < 3) {
      errors.name = 'Channel name must be at least 3 characters';
    }

    if (!formData.youtube_channel_id.trim()) {
      errors.youtube_channel_id = 'YouTube Channel ID is required';
    } else if (!formData.youtube_channel_id.startsWith('UC')) {
      errors.youtube_channel_id = 'YouTube Channel ID must start with "UC"';
    }

    if (!formData.brand_niche.trim()) {
      errors.brand_niche = 'Brand niche is required';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  }

  async function handleCreateChannel(e: React.FormEvent) {
    e.preventDefault();

    // Validate form
    if (!validateForm()) {
      return;
    }

    try {
      setCreating(true);
      setError(null);
      const newChannel = await createChannel(formData);

      // Reset form and reload channels
      setFormData({
        name: '',
        youtube_channel_id: '',
        brand_niche: '',
        is_active: true,
      });
      setFormErrors({});
      setSelectedGenreId(null);
      setNicheInputMode('select');
      setShowCreateForm(false);
      await loadChannels();

      // Show success toast
      toast.success('Channel created successfully!', `${formData.name} is now ready for video generation.`);
    } catch (err: any) {
      setError(err.message || 'Failed to create channel');
      toast.error('Failed to create channel', err.message);
    } finally {
      setCreating(false);
    }
  }

  async function handleToggleActive(channelId: string, currentStatus: boolean) {
    try {
      await toggleChannelActive(channelId, !currentStatus);
      await loadChannels();
      toast.success(
        `Channel ${!currentStatus ? 'enabled' : 'disabled'}`,
        `Channel is now ${!currentStatus ? 'active' : 'inactive'}.`
      );
    } catch (err: any) {
      setError(err.message || 'Failed to update channel');
      toast.error('Failed to update channel', err.message);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200 flex items-center justify-center">
        <Loading size="lg" message="Loading channels..." />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">Channels</h1>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
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
            onClick={() => {
              if (showCreateForm) {
                // Reset form when canceling
                setFormData({
                  name: '',
                  youtube_channel_id: '',
                  brand_niche: '',
                  is_active: true,
                });
                setFormErrors({});
                setSelectedGenreId(null);
                setNicheInputMode('select');
              }
              setShowCreateForm(!showCreateForm);
            }}
            variant={showCreateForm ? 'secondary' : 'primary'}
          >
            {showCreateForm ? 'Cancel' : '+ Create Channel'}
          </Button>
        </div>

        {/* Create Form */}
        {showCreateForm && (
          <div className="bg-white dark:bg-gray-800 transition-colors duration-200 shadow dark:shadow-gray-900/50 rounded-lg p-6 mb-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
              Create New Channel
            </h2>
            <form onSubmit={handleCreateChannel}>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <label
                    htmlFor="name"
                    className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
                  >
                    Channel Name <span className="text-red-600 dark:text-red-400" aria-label="required">*</span>
                  </label>
                  <input
                    type="text"
                    id="name"
                    required
                    aria-required="true"
                    aria-invalid={formErrors.name ? 'true' : 'false'}
                    aria-describedby={formErrors.name ? 'name-error' : undefined}
                    value={formData.name}
                    onChange={(e) => {
                      setFormData({ ...formData, name: e.target.value });
                      // Clear error on change
                      if (formErrors.name) {
                        setFormErrors({ ...formErrors, name: undefined });
                      }
                    }}
                    className={`w-full px-3 py-2 border rounded-lg transition bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                      formErrors.name ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
                    }`}
                    placeholder="My Ambient Channel"
                  />
                  {formErrors.name && (
                    <p id="name-error" className="mt-1 text-sm text-red-600 dark:text-red-400" role="alert">
                      {formErrors.name}
                    </p>
                  )}
                </div>

                <div>
                  <label
                    htmlFor="youtube_channel_id"
                    className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
                  >
                    YouTube Channel ID <span className="text-red-600 dark:text-red-400" aria-label="required">*</span>
                  </label>
                  <input
                    type="text"
                    id="youtube_channel_id"
                    required
                    aria-required="true"
                    aria-invalid={formErrors.youtube_channel_id ? 'true' : 'false'}
                    aria-describedby={formErrors.youtube_channel_id ? 'youtube_channel_id-error' : undefined}
                    value={formData.youtube_channel_id}
                    onChange={(e) => {
                      setFormData({
                        ...formData,
                        youtube_channel_id: e.target.value,
                      });
                      // Clear error on change
                      if (formErrors.youtube_channel_id) {
                        setFormErrors({ ...formErrors, youtube_channel_id: undefined });
                      }
                    }}
                    className={`w-full px-3 py-2 border rounded-lg transition bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                      formErrors.youtube_channel_id ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
                    }`}
                    placeholder="UC..."
                  />
                  {formErrors.youtube_channel_id && (
                    <p id="youtube_channel_id-error" className="mt-1 text-sm text-red-600 dark:text-red-400" role="alert">
                      {formErrors.youtube_channel_id}
                    </p>
                  )}
                </div>

                <div className="sm:col-span-2">
                  <div className="flex items-center justify-between mb-1">
                    <label
                      htmlFor="brand_niche"
                      className="block text-sm font-medium text-gray-700 dark:text-gray-300"
                    >
                      Brand Niche <span className="text-red-600 dark:text-red-400" aria-label="required">*</span>
                    </label>
                    <button
                      type="button"
                      onClick={() => setNicheInputMode(nicheInputMode === 'select' ? 'custom' : 'select')}
                      className="text-xs text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 flex items-center gap-1"
                    >
                      <FiEdit3 className="w-3 h-3" />
                      {nicheInputMode === 'select' ? 'Enter custom' : 'Select from library'}
                    </button>
                  </div>

                  {nicheInputMode === 'select' ? (
                    <>
                      {/* Genre Selector */}
                      <div className="mb-3">
                        <label htmlFor="genre_select" className="block text-xs text-gray-600 dark:text-gray-400 mb-1">
                          1. Choose Genre
                        </label>
                        <select
                          id="genre_select"
                          value={selectedGenreId || ''}
                          onChange={(e) => {
                            setSelectedGenreId(e.target.value || null);
                            // Clear niche when genre changes
                            setFormData({ ...formData, brand_niche: '' });
                          }}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        >
                          <option value="">Select a genre...</option>
                          {genres.map((genre) => (
                            <option key={genre.id} value={genre.id}>
                              {genre.name} ({genre.active_idea_count} niches)
                            </option>
                          ))}
                        </select>
                      </div>

                      {/* Niche Selector */}
                      {selectedGenreId && (
                        <div>
                          <label htmlFor="niche_select" className="block text-xs text-gray-600 dark:text-gray-400 mb-1">
                            2. Choose Niche
                          </label>
                          <select
                            id="niche_select"
                            value={formData.brand_niche}
                            onChange={(e) => {
                              setFormData({ ...formData, brand_niche: e.target.value });
                              // Clear error on change
                              if (formErrors.brand_niche) {
                                setFormErrors({ ...formErrors, brand_niche: undefined });
                              }
                            }}
                            className={`w-full px-3 py-2 border rounded-lg transition bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                              formErrors.brand_niche ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
                            }`}
                          >
                            <option value="">Select a niche...</option>
                            {ideas.map((idea) => (
                              <option key={idea.id} value={idea.niche_label}>
                                {idea.niche_label}
                              </option>
                            ))}
                          </select>
                          {ideas.length > 0 && (
                            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                              {ideas.length} niches available in {genres.find(g => g.id === selectedGenreId)?.name}
                            </p>
                          )}
                        </div>
                      )}
                    </>
                  ) : (
                    <input
                      type="text"
                      id="brand_niche"
                      required
                      aria-required="true"
                      aria-invalid={formErrors.brand_niche ? 'true' : 'false'}
                      aria-describedby={formErrors.brand_niche ? 'brand_niche-error' : undefined}
                      value={formData.brand_niche}
                      onChange={(e) => {
                        setFormData({ ...formData, brand_niche: e.target.value });
                        // Clear error on change
                        if (formErrors.brand_niche) {
                          setFormErrors({ ...formErrors, brand_niche: undefined });
                        }
                      }}
                      className={`w-full px-3 py-2 border rounded-lg transition bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                        formErrors.brand_niche ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
                      }`}
                      placeholder="e.g., Ambient Electronic Music, Lo-fi Study Beats"
                    />
                  )}
                  {formErrors.brand_niche && (
                    <p id="brand_niche-error" className="mt-1 text-sm text-red-600 dark:text-red-400" role="alert">
                      {formErrors.brand_niche}
                    </p>
                  )}
                </div>
              </div>

              <div className="mt-6 flex gap-3">
                <Button type="submit" loading={creating} disabled={creating}>
                  Create Channel
                </Button>
                <Button
                  type="button"
                  variant="secondary"
                  onClick={() => {
                    setFormData({
                      name: '',
                      youtube_channel_id: '',
                      brand_niche: '',
                      is_active: true,
                    });
                    setFormErrors({});
                    setSelectedGenreId(null);
                    setNicheInputMode('select');
                    setShowCreateForm(false);
                  }}
                >
                  Cancel
                </Button>
              </div>
            </form>
          </div>
        )}

        {/* Channels Table */}
        <div className="bg-white dark:bg-gray-800 transition-colors duration-200 shadow dark:shadow-gray-900/50 rounded-lg overflow-hidden">
          {channels.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-500 dark:text-gray-400">
                No channels yet. Create your first channel to get started.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className="bg-gray-50 dark:bg-gray-900">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      YouTube ID
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Niche
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Created
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-800 transition-colors duration-200 divide-y divide-gray-200 dark:divide-gray-700">
                  {channels.map((channel) => (
                    <tr
                      key={channel.id}
                      className="hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer"
                      onClick={() => channelPanel.open(channel.id)}
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900 dark:text-gray-100">
                          {channel.name}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-500 dark:text-gray-400">
                          {channel.youtube_channel_id}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-900 dark:text-gray-100">
                          {channel.brand_niche}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                            channel.is_active
                              ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400'
                              : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300'
                          }`}
                        >
                          {channel.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                        {new Date(channel.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleToggleActive(channel.id, channel.is_active);
                          }}
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

      {/* Slide-in Panel for Channel Details */}
      <SlidePanel
        isOpen={channelPanel.isOpen}
        onClose={channelPanel.close}
        title="Channel Details"
        width="lg"
      >
        {channelPanel.selectedId && (
          <ChannelDetailPanel
            channelId={channelPanel.selectedId}
            onClose={channelPanel.close}
            onDeleted={() => {
              loadChannels();
              channelPanel.close();
            }}
          />
        )}
      </SlidePanel>
    </div>
  );
}
