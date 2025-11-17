/**
 * Prompts Editor Component
 *
 * Allows editing of generated music and visual prompts.
 */
'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiEdit2, FiSave, FiX, FiPlus, FiTrash2 } from 'react-icons/fi';
import { Button } from '@/components/ui';
import clsx from 'clsx';

interface PromptsEditorProps {
  initialMusicPrompts: string[];
  initialVisualPrompts: string[];
  onSave: (musicPrompts: string[], visualPrompts: string[]) => Promise<void>;
  readOnly?: boolean;
}

export function PromptsEditor({
  initialMusicPrompts,
  initialVisualPrompts,
  onSave,
  readOnly = false,
}: PromptsEditorProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [musicPrompts, setMusicPrompts] = useState<string[]>(
    initialMusicPrompts
  );
  const [visualPrompts, setVisualPrompts] = useState<string[]>(
    initialVisualPrompts
  );
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    try {
      setSaving(true);
      await onSave(musicPrompts, visualPrompts);
      setIsEditing(false);
    } catch (error) {
      console.error('Failed to save prompts:', error);
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    setMusicPrompts(initialMusicPrompts);
    setVisualPrompts(initialVisualPrompts);
    setIsEditing(false);
  };

  const addMusicPrompt = () => {
    setMusicPrompts([...musicPrompts, '']);
  };

  const removeMusicPrompt = (index: number) => {
    setMusicPrompts(musicPrompts.filter((_, i) => i !== index));
  };

  const updateMusicPrompt = (index: number, value: string) => {
    const updated = [...musicPrompts];
    updated[index] = value;
    setMusicPrompts(updated);
  };

  const addVisualPrompt = () => {
    setVisualPrompts([...visualPrompts, '']);
  };

  const removeVisualPrompt = (index: number) => {
    setVisualPrompts(visualPrompts.filter((_, i) => i !== index));
  };

  const updateVisualPrompt = (index: number, value: string) => {
    const updated = [...visualPrompts];
    updated[index] = value;
    setVisualPrompts(updated);
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">
          Generated Prompts
        </h2>
        {!readOnly && (
          <div className="flex items-center space-x-2">
            {!isEditing ? (
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setIsEditing(true)}
              >
                <FiEdit2 className="mr-2 w-4 h-4" />
                Edit Prompts
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

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Music Prompts */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-medium text-gray-700">
              Music Prompts ({musicPrompts.length})
            </h3>
            {isEditing && (
              <Button
                variant="ghost"
                size="sm"
                onClick={addMusicPrompt}
              >
                <FiPlus className="w-4 h-4 mr-1" />
                Add
              </Button>
            )}
          </div>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            <AnimatePresence>
              {musicPrompts.map((prompt, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="relative"
                >
                  {isEditing ? (
                    <div className="flex items-start space-x-2">
                      <div className="flex-1">
                        <textarea
                          value={prompt}
                          onChange={(e) =>
                            updateMusicPrompt(index, e.target.value)
                          }
                          className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                          rows={3}
                          placeholder={`Music prompt ${index + 1}...`}
                        />
                      </div>
                      <button
                        onClick={() => removeMusicPrompt(index)}
                        className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition"
                      >
                        <FiTrash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ) : (
                    <div className="bg-gray-50 rounded-lg p-3">
                      <span className="text-xs font-medium text-gray-500">
                        {index + 1}.
                      </span>{' '}
                      <span className="text-sm text-gray-700">{prompt}</span>
                    </div>
                  )}
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </div>

        {/* Visual Prompts */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-medium text-gray-700">
              Visual Prompts ({visualPrompts.length})
            </h3>
            {isEditing && (
              <Button
                variant="ghost"
                size="sm"
                onClick={addVisualPrompt}
              >
                <FiPlus className="w-4 h-4 mr-1" />
                Add
              </Button>
            )}
          </div>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            <AnimatePresence>
              {visualPrompts.map((prompt, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="relative"
                >
                  {isEditing ? (
                    <div className="flex items-start space-x-2">
                      <div className="flex-1">
                        <textarea
                          value={prompt}
                          onChange={(e) =>
                            updateVisualPrompt(index, e.target.value)
                          }
                          className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                          rows={3}
                          placeholder={`Visual prompt ${index + 1}...`}
                        />
                      </div>
                      <button
                        onClick={() => removeVisualPrompt(index)}
                        className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition"
                      >
                        <FiTrash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ) : (
                    <div className="bg-gray-50 rounded-lg p-3">
                      <span className="text-xs font-medium text-gray-500">
                        {index + 1}.
                      </span>{' '}
                      <span className="text-sm text-gray-700">{prompt}</span>
                    </div>
                  )}
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  );
}
