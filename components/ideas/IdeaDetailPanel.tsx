/**
 * Idea Detail Panel Component
 *
 * Slide-in panel for viewing and editing individual video ideas.
 * Extracted from app/ideas/[id]/page.tsx for use in slide-in panel.
 */
'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
import {
  FiEdit2,
  FiCopy,
  FiTrash2,
  FiClock,
  FiMusic,
  FiTag,
  FiCheckCircle,
  FiXCircle,
} from 'react-icons/fi';
import { getIdea, deleteIdea, cloneIdea, updateIdea, generatePromptsForIdea } from '@/lib/api';
import type { VideoIdeaDetail, VideoIdeaUpdate } from '@/lib/api';
import { ConfirmDialog, useToast } from '@/components/ui';

interface IdeaDetailPanelProps {
  ideaId: string;
  onClose: () => void;
}

export function IdeaDetailPanel({ ideaId, onClose }: IdeaDetailPanelProps) {
  const router = useRouter();
  const toast = useToast();
  const [idea, setIdea] = useState<VideoIdeaDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState<VideoIdeaUpdate>({});
  const [isGenerating, setIsGenerating] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    if (ideaId) {
      loadIdea();
    }
  }, [ideaId]);

  async function loadIdea() {
    setLoading(true);
    setError(null);
    try {
      const data = await getIdea(ideaId);
      setIdea(data);
      setEditData({
        title: data.title,
        description: data.description || undefined,
        niche_label: data.niche_label,
        mood_tags: data.mood_tags,
        target_duration_minutes: data.target_duration_minutes,
        num_tracks: data.num_tracks,
      });
    } catch (err: any) {
      console.error('Failed to load idea:', err);
      setError(err.message || 'Failed to load idea');
    } finally {
      setLoading(false);
    }
  }

  async function handleSave() {
    if (!idea) return;
    try {
      await updateIdea(idea.id, editData);
      setIsEditing(false);
      toast.success('Idea updated', 'Your changes have been saved successfully.');
      loadIdea(); // Reload to get updated data
    } catch (err: any) {
      toast.error('Failed to save', err.message || 'An error occurred while saving');
    }
  }

  async function handleClone() {
    if (!idea) return;
    try {
      const cloned = await cloneIdea(idea.id, `${idea.title} (Copy)`);
      toast.success('Idea cloned', 'A copy of the idea has been created.');
      onClose(); // Close panel
      router.push(`/ideas/${cloned.id}`); // Navigate to cloned idea
    } catch (err: any) {
      toast.error('Failed to clone', err.message || 'An error occurred while cloning');
    }
  }

  async function handleDelete() {
    if (!idea) return;
    try {
      setIsDeleting(true);
      await deleteIdea(idea.id);
      toast.success('Idea deleted', 'The idea has been permanently deleted.');
      setShowDeleteConfirm(false);
      onClose(); // Close panel
      router.refresh(); // Refresh the ideas list
    } catch (err: any) {
      toast.error('Failed to delete', err.message || 'An error occurred while deleting');
      setShowDeleteConfirm(false);
    } finally {
      setIsDeleting(false);
    }
  }

  async function handleGeneratePrompts() {
    if (!idea) return;
    setIsGenerating(true);
    try {
      const result = await generatePromptsForIdea(idea.id);
      toast.success(
        'Prompts generated',
        `Generated ${result.num_music_prompts} music prompts and ${result.num_visual_prompts} visual prompts.`
      );
      loadIdea(); // Reload to show new prompts
    } catch (err: any) {
      toast.error('Failed to generate prompts', err.message || 'An error occurred');
    } finally {
      setIsGenerating(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !idea) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error || 'Idea not found'}
        </div>
      </div>
    );
  }

  return (
    <div className="overflow-y-auto">
      {/* Header Section */}
      <div className="mb-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            {isEditing ? (
              <input
                type="text"
                value={editData.title || ''}
                onChange={(e) => setEditData({ ...editData, title: e.target.value })}
                className="text-2xl font-bold text-gray-900 border-b-2 border-blue-500 focus:outline-none w-full"
              />
            ) : (
              <h1 className="text-2xl font-bold text-gray-900">{idea.title}</h1>
            )}
            <div className="flex items-center space-x-4 mt-2">
              <span
                className="px-3 py-1 rounded-full text-sm font-medium text-white"
                style={{ backgroundColor: idea.genre?.color || '#6B7280' }}
              >
                {idea.genre?.name || 'Unknown'}
              </span>
              {idea.is_template && (
                <span className="px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-700">
                  Template
                </span>
              )}
              {idea.times_used > 0 && (
                <span className="text-sm text-gray-600">
                  Used {idea.times_used} {idea.times_used === 1 ? 'time' : 'times'}
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center space-x-2">
          {isEditing ? (
            <>
              <button
                onClick={handleSave}
                className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
              >
                <FiCheckCircle className="w-4 h-4" />
                <span>Save</span>
              </button>
              <button
                onClick={() => setIsEditing(false)}
                className="flex items-center space-x-2 px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 transition"
              >
                <FiXCircle className="w-4 h-4" />
                <span>Cancel</span>
              </button>
            </>
          ) : (
            <>
              <button
                onClick={() => setIsEditing(true)}
                className="flex items-center space-x-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition text-sm"
              >
                <FiEdit2 className="w-4 h-4" />
                <span>Edit</span>
              </button>
              <button
                onClick={handleClone}
                className="flex items-center space-x-2 px-3 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition text-sm"
              >
                <FiCopy className="w-4 h-4" />
                <span>Clone</span>
              </button>
              <button
                onClick={() => setShowDeleteConfirm(true)}
                className="flex items-center space-x-2 px-3 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition text-sm"
              >
                <FiTrash2 className="w-4 h-4" />
              </button>
            </>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Details */}
        <div className="lg:col-span-2 space-y-6">
          {/* Description */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h2 className="text-lg font-bold text-gray-900 mb-3">Description</h2>
            {isEditing ? (
              <textarea
                value={editData.description || ''}
                onChange={(e) => setEditData({ ...editData, description: e.target.value })}
                rows={4}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter a detailed description..."
              />
            ) : (
              <p className="text-gray-600">{idea.description || 'No description provided'}</p>
            )}
          </div>

          {/* Niche */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h2 className="text-lg font-bold text-gray-900 mb-3">Niche</h2>
            {isEditing ? (
              <input
                type="text"
                value={editData.niche_label || ''}
                onChange={(e) => setEditData({ ...editData, niche_label: e.target.value })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="e.g., Lo-fi Hip Hop - Urban Japan"
              />
            ) : (
              <p className="text-gray-700 font-medium">{idea.niche_label}</p>
            )}
          </div>

          {/* Mood Tags */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h2 className="text-lg font-bold text-gray-900 mb-3 flex items-center">
              <FiTag className="w-5 h-5 mr-2" />
              Mood Tags
            </h2>
            {isEditing ? (
              <div>
                <input
                  type="text"
                  placeholder="Add tags (comma-separated)"
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && e.currentTarget.value.trim()) {
                      const newTags = e.currentTarget.value
                        .split(',')
                        .map((t) => t.trim())
                        .filter(Boolean);
                      setEditData({
                        ...editData,
                        mood_tags: [...(editData.mood_tags || []), ...newTags],
                      });
                      e.currentTarget.value = '';
                    }
                  }}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent mb-3"
                />
                <div className="flex flex-wrap gap-2">
                  {(editData.mood_tags || []).map((tag, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm flex items-center space-x-2"
                    >
                      <span>{tag}</span>
                      <button
                        onClick={() => {
                          const newTags = [...(editData.mood_tags || [])];
                          newTags.splice(index, 1);
                          setEditData({ ...editData, mood_tags: newTags });
                        }}
                        className="text-blue-500 hover:text-blue-700"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>
            ) : (
              <div className="flex flex-wrap gap-2">
                {idea.mood_tags.map((tag, index) => (
                  <span key={index} className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm">
                    {tag}
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Prompts Section */}
          {idea.prompts && (
            <div className="bg-gray-50 rounded-lg p-4">
              <h2 className="text-lg font-bold text-gray-900 mb-3">Generated Prompts</h2>
              <p className="text-sm text-gray-600 mb-4">
                {idea.prompts.music_prompts.length} music prompts and{' '}
                {idea.prompts.visual_prompts.length} visual prompts
              </p>
              <Link
                href={`/ideas/${idea.id}/prompts`}
                onClick={onClose}
                className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
              >
                View & Edit Prompts
              </Link>
            </div>
          )}
        </div>

        {/* Right Column - Metadata */}
        <div className="space-y-6">
          {/* Video Settings */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Video Settings</h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center text-gray-600">
                  <FiClock className="w-4 h-4 mr-2" />
                  <span>Duration</span>
                </div>
                {isEditing ? (
                  <input
                    type="number"
                    value={editData.target_duration_minutes || 70}
                    onChange={(e) =>
                      setEditData({ ...editData, target_duration_minutes: parseInt(e.target.value) })
                    }
                    min={60}
                    max={120}
                    className="w-20 border border-gray-300 rounded px-2 py-1 text-right"
                  />
                ) : (
                  <span className="font-medium">{idea.target_duration_minutes} min</span>
                )}
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center text-gray-600">
                  <FiMusic className="w-4 h-4 mr-2" />
                  <span>Tracks</span>
                </div>
                {isEditing ? (
                  <input
                    type="number"
                    value={editData.num_tracks || 20}
                    onChange={(e) => setEditData({ ...editData, num_tracks: parseInt(e.target.value) })}
                    min={10}
                    max={30}
                    className="w-20 border border-gray-300 rounded px-2 py-1 text-right"
                  />
                ) : (
                  <span className="font-medium">{idea.num_tracks} tracks</span>
                )}
              </div>
            </div>
          </div>

          {/* Timestamps */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Metadata</h2>
            <div className="space-y-3 text-sm">
              <div>
                <span className="text-gray-600">Created:</span>
                <p className="font-medium text-gray-900">
                  {new Date(idea.created_at).toLocaleDateString()} at{' '}
                  {new Date(idea.created_at).toLocaleTimeString()}
                </p>
              </div>
              <div>
                <span className="text-gray-600">Last Updated:</span>
                <p className="font-medium text-gray-900">
                  {new Date(idea.updated_at).toLocaleDateString()} at{' '}
                  {new Date(idea.updated_at).toLocaleTimeString()}
                </p>
              </div>
              <div>
                <span className="text-gray-600">ID:</span>
                <p className="font-mono text-xs text-gray-700 break-all">{idea.id}</p>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Quick Actions</h2>
            <div className="space-y-2">
              <Link
                href={`/video-jobs/create?idea=${idea.id}`}
                onClick={onClose}
                className="block w-full px-4 py-2 bg-green-600 text-white text-center rounded-lg hover:bg-green-700 transition"
              >
                Create Video from This Idea
              </Link>
              <button
                onClick={handleGeneratePrompts}
                disabled={isGenerating}
                className={`block w-full px-4 py-2 text-white text-center rounded-lg transition ${
                  isGenerating ? 'bg-gray-400 cursor-not-allowed' : 'bg-purple-600 hover:bg-purple-700'
                }`}
              >
                {isGenerating ? (
                  <span className="flex items-center justify-center space-x-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>Generating...</span>
                  </span>
                ) : idea.prompts ? (
                  'Regenerate AI Prompts'
                ) : (
                  'Generate AI Prompts'
                )}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      <ConfirmDialog
        isOpen={showDeleteConfirm}
        onClose={() => setShowDeleteConfirm(false)}
        onConfirm={handleDelete}
        title="Delete Idea?"
        description={`Are you sure you want to delete "${idea?.title}"? This action cannot be undone.`}
        confirmText="Delete Idea"
        cancelText="Cancel"
        variant="danger"
        loading={isDeleting}
      />
    </div>
  );
}
