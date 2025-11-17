/**
 * Metadata Editor Component
 *
 * Allows editing of video metadata (title, description, tags).
 */
'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { FiEdit2, FiSave, FiX, FiPlus, FiTag } from 'react-icons/fi';
import { Button } from '@/components/ui';

interface VideoMetadata {
  title: string;
  description: string;
  tags: string[];
}

interface MetadataEditorProps {
  initialMetadata: VideoMetadata;
  onSave: (metadata: VideoMetadata) => Promise<void>;
  readOnly?: boolean;
}

export function MetadataEditor({
  initialMetadata,
  onSave,
  readOnly = false,
}: MetadataEditorProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [metadata, setMetadata] = useState<VideoMetadata>(initialMetadata);
  const [saving, setSaving] = useState(false);
  const [newTag, setNewTag] = useState('');

  const handleSave = async () => {
    try {
      setSaving(true);
      await onSave(metadata);
      setIsEditing(false);
    } catch (error) {
      console.error('Failed to save metadata:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setMetadata(initialMetadata);
    setIsEditing(false);
  };

  const addTag = () => {
    if (newTag.trim() && !metadata.tags.includes(newTag.trim())) {
      setMetadata({
        ...metadata,
        tags: [...metadata.tags, newTag.trim()],
      });
      setNewTag('');
    }
  };

  const removeTag = (tagToRemove: string) => {
    setMetadata({
      ...metadata,
      tags: metadata.tags.filter((tag) => tag !== tagToRemove),
    });
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addTag();
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-gray-900">
          Video Metadata
        </h2>
        {!readOnly && (
          <div className="flex items-center space-x-2">
            {!isEditing ? (
              <Button
                variant="outline"
                size="sm"
                onClick={() => setIsEditing(true)}
              >
                <FiEdit2 className="mr-2 w-4 h-4" />
                Edit Metadata
              </Button>
            ) : (
              <>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleCancel}
                  disabled={saving}
                >
                  <FiX className="mr-2 w-4 h-4" />
                  Cancel
                </Button>
                <Button
                  size="sm"
                  onClick={handleSave}
                  disabled={saving}
                >
                  <FiSave className="mr-2 w-4 h-4" />
                  {saving ? 'Saving...' : 'Save Changes'}
                </Button>
              </>
            )}
          </div>
        )}
      </div>

      <div className="space-y-6">
        {/* Title */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Title
          </label>
          {isEditing ? (
            <input
              type="text"
              value={metadata.title}
              onChange={(e) =>
                setMetadata({ ...metadata, title: e.target.value })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter video title..."
              maxLength={100}
            />
          ) : (
            <div className="bg-gray-50 rounded-lg p-3">
              <p className="text-sm text-gray-900">{metadata.title}</p>
            </div>
          )}
          {isEditing && (
            <p className="text-xs text-gray-500 mt-1">
              {metadata.title.length}/100 characters
            </p>
          )}
        </div>

        {/* Description */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Description
          </label>
          {isEditing ? (
            <textarea
              value={metadata.description}
              onChange={(e) =>
                setMetadata({ ...metadata, description: e.target.value })
              }
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
              rows={8}
              placeholder="Enter video description with timestamps..."
              maxLength={5000}
            />
          ) : (
            <div className="bg-gray-50 rounded-lg p-3 max-h-64 overflow-y-auto">
              <p className="text-sm text-gray-900 whitespace-pre-wrap">
                {metadata.description}
              </p>
            </div>
          )}
          {isEditing && (
            <p className="text-xs text-gray-500 mt-1">
              {metadata.description.length}/5000 characters
            </p>
          )}
        </div>

        {/* Tags */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Tags ({metadata.tags.length})
          </label>

          {/* Tag Input */}
          {isEditing && (
            <div className="flex items-center space-x-2 mb-3">
              <input
                type="text"
                value={newTag}
                onChange={(e) => setNewTag(e.target.value)}
                onKeyPress={handleKeyPress}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Add a tag..."
              />
              <Button
                variant="outline"
                size="sm"
                onClick={addTag}
                disabled={!newTag.trim()}
              >
                <FiPlus className="w-4 h-4 mr-1" />
                Add
              </Button>
            </div>
          )}

          {/* Tag List */}
          <div className="flex flex-wrap gap-2">
            {metadata.tags.length === 0 ? (
              <p className="text-sm text-gray-500 italic">No tags added yet</p>
            ) : (
              metadata.tags.map((tag, index) => (
                <motion.div
                  key={tag}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.8 }}
                  className="inline-flex items-center px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                >
                  <FiTag className="w-3 h-3 mr-1" />
                  {tag}
                  {isEditing && (
                    <button
                      onClick={() => removeTag(tag)}
                      className="ml-2 text-blue-600 hover:text-blue-800"
                    >
                      <FiX className="w-3 h-3" />
                    </button>
                  )}
                </motion.div>
              ))
            )}
          </div>
        </div>

        {/* Helpful Note */}
        {!isEditing && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <p className="text-sm text-yellow-800">
              <strong>Reminder:</strong> When uploading to YouTube, remember to enable the{' '}
              <strong>"Altered or synthetic content"</strong> checkbox in YouTube Studio.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
