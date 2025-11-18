/**
 * Ideas Library Page
 *
 * Browse and search video ideas with genre filtering.
 */
'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  FiSearch,
  FiPlus,
  FiFilter,
  FiGrid,
  FiList,
  FiClock,
  FiMusic,
} from 'react-icons/fi';
import { listGenres, listIdeas } from '@/lib/api';
import type { GenreWithStats, VideoIdea } from '@/lib/api';
import { SlidePanel, useSlidePanel } from '@/components/ui';
import { IdeaDetailPanel } from '@/components/ideas/IdeaDetailPanel';
import { CreateIdeaPanel } from '@/components/ideas/CreateIdeaPanel';

export default function IdeasLibraryPage() {
  const [genres, setGenres] = useState<GenreWithStats[]>([]);
  const [ideas, setIdeas] = useState<VideoIdea[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [selectedGenre, setSelectedGenre] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<'created_at' | 'title' | 'times_used'>('created_at');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('list');

  // Slide panel state
  const ideaPanel = useSlidePanel<string>();
  const createPanel = useSlidePanel();

  // Load genres on mount
  useEffect(() => {
    async function loadGenres() {
      try {
        const data = await listGenres({ with_stats: true });
        setGenres(data);
      } catch (err: any) {
        console.error('Failed to load genres:', err);
        setError(err.message || 'Failed to load genres');
      }
    }
    loadGenres();
  }, []);

  // Load ideas when filters change
  useEffect(() => {
    loadIdeas();
  }, [selectedGenre, searchQuery, sortBy]);

  async function loadIdeas() {
    setLoading(true);
    setError(null);
    try {
      const data = await listIdeas({
        genre_id: selectedGenre || undefined,
        search: searchQuery || undefined,
        sort_by: sortBy,
        sort_order: 'desc',
        limit: 100,
      });
      setIdeas(data);
    } catch (err: any) {
      console.error('Failed to load ideas:', err);
      setError(err.message || 'Failed to load ideas');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6 transition-colors duration-200">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">Ideas Library</h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              Browse and select from {ideas.length} video concepts across {genres.length} genres
            </p>
          </div>
          <button
            onClick={() => createPanel.open()}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 dark:bg-blue-700 text-white rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600 transition-colors duration-200"
          >
            <FiPlus className="w-5 h-5" />
            <span>New Idea</span>
          </button>
        </div>

        {/* Search and Controls */}
        <div className="mt-6 flex flex-wrap items-center gap-4">
          {/* Search */}
          <div className="flex-1 min-w-[300px]">
            <div className="relative">
              <FiSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 dark:text-gray-500" />
              <input
                type="text"
                placeholder="Search ideas by title, description, or niche..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors duration-200"
              />
            </div>
          </div>

          {/* Sort */}
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as any)}
            className="px-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors duration-200"
          >
            <option value="created_at">Recent</option>
            <option value="title">Title</option>
            <option value="times_used">Most Used</option>
          </select>

          {/* View Mode Toggle */}
          <div className="flex items-center space-x-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-lg p-1 transition-colors duration-200">
            <button
              onClick={() => setViewMode('grid')}
              className={`p-2 rounded transition-colors duration-200 ${
                viewMode === 'grid' ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400' : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              <FiGrid className="w-5 h-5" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`p-2 rounded transition-colors duration-200 ${
                viewMode === 'list' ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400' : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              <FiList className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Genre Filter Tabs */}
        <div className="mt-6 flex flex-wrap items-center gap-2">
          <button
            onClick={() => setSelectedGenre(null)}
            className={`px-4 py-2 rounded-lg font-medium whitespace-nowrap transition-colors duration-200 ${
              selectedGenre === null
                ? 'bg-blue-600 dark:bg-blue-700 text-white'
                : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 border border-gray-300 dark:border-gray-700'
            }`}
          >
            All Genres ({ideas.length})
          </button>
          {genres.map((genre) => (
            <button
              key={genre.id}
              onClick={() => setSelectedGenre(genre.id)}
              className={`px-4 py-2 rounded-lg font-medium whitespace-nowrap transition-colors duration-200 ${
                selectedGenre === genre.id
                  ? 'text-white'
                  : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 border border-gray-300 dark:border-gray-700'
              }`}
              style={{
                backgroundColor: selectedGenre === genre.id ? genre.color || '#3B82F6' : undefined,
              }}
            >
              {genre.name} ({genre.active_idea_count})
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto">
        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 px-4 py-3 rounded-lg mb-6 transition-colors duration-200">
            {error}
          </div>
        )}

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 dark:border-blue-400"></div>
          </div>
        ) : ideas.length === 0 ? (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 p-12 text-center transition-colors duration-200">
            <p className="text-gray-500 dark:text-gray-400 text-lg">No ideas found matching your filters</p>
            <button
              onClick={() => createPanel.open()}
              className="inline-flex items-center space-x-2 mt-4 px-4 py-2 bg-blue-600 dark:bg-blue-700 text-white rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600 transition-colors duration-200"
            >
              <FiPlus className="w-5 h-5" />
              <span>Create First Idea</span>
            </button>
          </div>
        ) : viewMode === 'grid' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {ideas.map((idea) => (
              <IdeaCard
                key={idea.id}
                idea={idea}
                genres={genres}
                onClick={() => ideaPanel.open(idea.id)}
              />
            ))}
          </div>
        ) : (
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 overflow-hidden transition-colors duration-200">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-900">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Title
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Genre
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Niche
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Duration
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Used
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {ideas.map((idea) => {
                  const genre = genres.find((g) => g.id === idea.genre_id);
                  return (
                    <tr
                      key={idea.id}
                      className="hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors duration-200"
                      onClick={() => ideaPanel.open(idea.id)}
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-blue-600 dark:text-blue-400 hover:underline font-medium">
                          {idea.title}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className="px-2 py-1 rounded text-sm font-medium text-white"
                          style={{ backgroundColor: genre?.color || '#6B7280' }}
                        >
                          {genre?.name || 'Unknown'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">{idea.niche_label}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                        {idea.target_duration_minutes}min
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                        {idea.times_used} {idea.times_used === 1 ? 'time' : 'times'}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Slide-in Panel for Idea Details */}
      <SlidePanel
        isOpen={ideaPanel.isOpen}
        onClose={ideaPanel.close}
        title="Idea Details"
        width="xl"
      >
        {ideaPanel.selectedId && (
          <IdeaDetailPanel ideaId={ideaPanel.selectedId} onClose={ideaPanel.close} />
        )}
      </SlidePanel>

      {/* Slide-in Panel for Create Idea */}
      <SlidePanel
        isOpen={createPanel.isOpen}
        onClose={createPanel.close}
        title="Create New Idea"
        width="lg"
      >
        <CreateIdeaPanel
          onClose={createPanel.close}
          onCreated={(ideaId) => {
            loadIdeas();
            // Optionally open the newly created idea
            ideaPanel.open(ideaId);
          }}
        />
      </SlidePanel>
    </div>
  );
}

/**
 * Idea Card Component (Grid View)
 */
function IdeaCard({
  idea,
  genres,
  onClick,
}: {
  idea: VideoIdea;
  genres: GenreWithStats[];
  onClick: () => void;
}) {
  const genre = genres.find((g) => g.id === idea.genre_id);

  return (
    <motion.div
      whileHover={{ y: -4 }}
      onClick={onClick}
      className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-gray-900/50 hover:shadow-lg dark:hover:shadow-gray-900/70 transition-all duration-200 p-6 h-full flex flex-col cursor-pointer"
    >
        {/* Genre Badge */}
        <div className="flex items-center justify-between mb-3">
          <span
            className="px-3 py-1 rounded-full text-sm font-medium text-white"
            style={{ backgroundColor: genre?.color || '#6B7280' }}
          >
            {genre?.name || 'Unknown'}
          </span>
          {idea.times_used > 0 && (
            <span className="text-sm text-gray-500 dark:text-gray-400">{idea.times_used}x used</span>
          )}
        </div>

        {/* Title */}
        <h3 className="text-lg font-bold text-gray-900 dark:text-gray-100 mb-2">{idea.title}</h3>

        {/* Description */}
        <p className="text-gray-600 dark:text-gray-400 text-sm mb-4 flex-1 line-clamp-3">{idea.description}</p>

        {/* Niche */}
        <div className="text-sm text-gray-500 dark:text-gray-400 mb-3">
          <span className="font-medium">Niche:</span> {idea.niche_label}
        </div>

        {/* Mood Tags */}
        <div className="flex flex-wrap gap-2 mb-4">
          {idea.mood_tags.slice(0, 3).map((tag, index) => (
            <span
              key={index}
              className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded text-xs transition-colors duration-200"
            >
              {tag}
            </span>
          ))}
          {idea.mood_tags.length > 3 && (
            <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded text-xs transition-colors duration-200">
              +{idea.mood_tags.length - 3} more
            </span>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400 pt-4 border-t border-gray-100 dark:border-gray-700 transition-colors duration-200">
          <div className="flex items-center space-x-1">
            <FiClock className="w-4 h-4" />
            <span>{idea.target_duration_minutes}min</span>
          </div>
          <div className="flex items-center space-x-1">
            <FiMusic className="w-4 h-4" />
            <span>{idea.num_tracks} tracks</span>
          </div>
        </div>
    </motion.div>
  );
}
