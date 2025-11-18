/**
 * Create Idea Panel Component
 *
 * Form for creating new video ideas in a slide panel.
 */
'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { FiCheckCircle } from 'react-icons/fi';
import { createIdea, listGenres } from '@/lib/api';
import type { GenreWithStats, VideoIdeaCreate } from '@/lib/api';
import { useToast } from '@/components/ui';

interface CreateIdeaPanelProps {
  onClose: () => void;
  onCreated?: (ideaId: string) => void;
}

export function CreateIdeaPanel({ onClose, onCreated }: CreateIdeaPanelProps) {
  const router = useRouter();
  const toast = useToast();
  const [genres, setGenres] = useState<GenreWithStats[]>([]);
  const [loading, setLoading] = useState(false);

  const [formData, setFormData] = useState<VideoIdeaCreate>({
    title: '',
    description: '',
    genre_id: '',
    niche_label: '',
    mood_tags: [],
    target_duration_minutes: 70,
    num_tracks: 20,
    is_template: true,
  });

  const [moodTagInput, setMoodTagInput] = useState('');

  // Load genres on mount
  useEffect(() => {
    async function loadGenres() {
      try {
        const data = await listGenres();
        setGenres(data);
        // Auto-select first genre if available
        if (data.length > 0 && !formData.genre_id) {
          setFormData((prev) => ({ ...prev, genre_id: data[0].id }));
        }
      } catch (err: any) {
        console.error('Failed to load genres:', err);
        toast.error('Failed to load genres', err.message);
      }
    }
    loadGenres();
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);

    try {
      const created = await createIdea(formData);
      toast.success('Idea created', `"${formData.title}" has been added to your library.`);
      onCreated?.(created.id);
      onClose();
      router.refresh();
    } catch (err: any) {
      console.error('Failed to create idea:', err);
      toast.error('Failed to create idea', err.message);
      setLoading(false);
    }
  }

  function addMoodTag() {
    if (moodTagInput.trim() && !formData.mood_tags?.includes(moodTagInput.trim())) {
      setFormData({
        ...formData,
        mood_tags: [...(formData.mood_tags || []), moodTagInput.trim()],
      });
      setMoodTagInput('');
    }
  }

  function removeMoodTag(tag: string) {
    setFormData({
      ...formData,
      mood_tags: formData.mood_tags?.filter((t) => t !== tag) || [],
    });
  }

  const isValid =
    formData.title.trim() &&
    formData.genre_id &&
    formData.niche_label.trim() &&
    (formData.target_duration_minutes ?? 0) >= 60 &&
    (formData.target_duration_minutes ?? 0) <= 120 &&
    (formData.num_tracks ?? 0) >= 10 &&
    (formData.num_tracks ?? 0) <= 30;

  return (
    <div className="overflow-y-auto h-full">
      <form onSubmit={handleSubmit} className="space-y-6 p-6">
        {/* Title */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Title <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            placeholder="e.g., Rainy Tokyo Night Beats"
            className="w-full border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-lg px-4 py-2 placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
            required
          />
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
            Choose a descriptive, unique title for your video concept
          </p>
        </div>

        {/* Genre */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Genre <span className="text-red-500">*</span>
          </label>
          <select
            value={formData.genre_id}
            onChange={(e) => setFormData({ ...formData, genre_id: e.target.value })}
            className="w-full border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
            required
          >
            <option value="">Select a genre...</option>
            {genres.map((genre) => (
              <option key={genre.id} value={genre.id}>
                {genre.name} ({genre.active_idea_count} ideas)
              </option>
            ))}
          </select>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
            Choose the music genre for this video concept
          </p>
        </div>

        {/* Niche Label */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Niche Label <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={formData.niche_label}
            onChange={(e) => setFormData({ ...formData, niche_label: e.target.value })}
            placeholder="e.g., Lo-fi Hip Hop - Urban Japan"
            className="w-full border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-lg px-4 py-2 placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
            required
          />
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
            Specific sub-genre or niche within the main genre
          </p>
        </div>

        {/* Description */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Description
          </label>
          <textarea
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            rows={4}
            placeholder="Describe the mood, style, and intended use of this video concept..."
            className="w-full border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-lg px-4 py-2 placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
          />
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
            Provide details to help guide music and visual generation
          </p>
        </div>

        {/* Mood Tags */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Mood Tags
          </label>
          <div className="flex space-x-2 mb-3">
            <input
              type="text"
              value={moodTagInput}
              onChange={(e) => setMoodTagInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  addMoodTag();
                }
              }}
              placeholder="e.g., calm, atmospheric, nostalgic"
              className="flex-1 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-lg px-4 py-2 placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
            />
            <button
              type="button"
              onClick={addMoodTag}
              className="px-4 py-2 bg-blue-600 dark:bg-blue-500 text-white rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600 transition"
            >
              Add
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {formData.mood_tags?.map((tag, index) => (
              <span
                key={index}
                className="px-3 py-1 bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300 rounded-full text-sm flex items-center space-x-2"
              >
                <span>{tag}</span>
                <button
                  type="button"
                  onClick={() => removeMoodTag(tag)}
                  className="text-blue-500 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-200 font-bold"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
            Add keywords that describe the mood and atmosphere
          </p>
        </div>

        {/* Video Settings */}
        <div className="grid grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Target Duration (minutes) <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              value={formData.target_duration_minutes}
              onChange={(e) =>
                setFormData({ ...formData, target_duration_minutes: parseInt(e.target.value) })
              }
              min={60}
              max={120}
              className="w-full border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
              required
            />
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Between 60-120 minutes</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Number of Tracks <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              value={formData.num_tracks}
              onChange={(e) => setFormData({ ...formData, num_tracks: parseInt(e.target.value) })}
              min={10}
              max={30}
              className="w-full border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
              required
            />
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Between 10-30 tracks</p>
          </div>
        </div>

        {/* Template Checkbox */}
        <div className="flex items-center space-x-2">
          <input
            type="checkbox"
            id="is_template"
            checked={formData.is_template}
            onChange={(e) => setFormData({ ...formData, is_template: e.target.checked })}
            className="w-4 h-4 text-blue-600 border-gray-300 dark:border-gray-600 rounded focus:ring-blue-500 bg-white dark:bg-gray-800"
          />
          <label htmlFor="is_template" className="text-sm text-gray-700 dark:text-gray-300">
            Save as reusable template
          </label>
        </div>

        {/* Submit Buttons */}
        <div className="flex items-center justify-end space-x-4 pt-6 border-t border-gray-200 dark:border-gray-700">
          <button
            type="button"
            onClick={onClose}
            className="px-6 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={!isValid || loading}
            className={`flex items-center space-x-2 px-6 py-2 rounded-lg transition ${
              isValid && !loading
                ? 'bg-blue-600 dark:bg-blue-500 text-white hover:bg-blue-700 dark:hover:bg-blue-600'
                : 'bg-gray-300 dark:bg-gray-700 text-gray-500 dark:text-gray-400 cursor-not-allowed'
            }`}
          >
            {loading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>Creating...</span>
              </>
            ) : (
              <>
                <FiCheckCircle className="w-5 h-5" />
                <span>Create Idea</span>
              </>
            )}
          </button>
        </div>

        {/* Info Box */}
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
          <h3 className="font-medium text-blue-900 dark:text-blue-300 mb-2">What's Next?</h3>
          <ul className="text-sm text-blue-800 dark:text-blue-400 space-y-1">
            <li>• After creating, you can generate AI prompts for music and visuals</li>
            <li>• Use this idea as a template for creating video jobs</li>
            <li>• Clone and modify existing ideas to create variations</li>
          </ul>
        </div>
      </form>
    </div>
  );
}
