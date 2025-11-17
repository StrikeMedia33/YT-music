/**
 * Asset Manager Component
 *
 * Manages audio tracks and visual assets with preview capabilities.
 */
'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  FiMusic,
  FiImage,
  FiDownload,
  FiEye,
  FiRefreshCw,
} from 'react-icons/fi';
import { Button } from '@/components/ui';
import clsx from 'clsx';

interface AudioTrack {
  id: string;
  order_index: number;
  duration_seconds: number;
  provider: string;
  local_file_path: string;
}

interface VisualAsset {
  id: string;
  order_index: number;
  provider: string;
  local_file_path: string;
}

interface AssetManagerProps {
  audioTracks: AudioTrack[];
  visualAssets: VisualAsset[];
  onRegenerateAudio?: (trackId: string) => Promise<void>;
  onRegenerateVisual?: (visualId: string) => Promise<void>;
}

export function AssetManager({
  audioTracks,
  visualAssets,
  onRegenerateAudio,
  onRegenerateVisual,
}: AssetManagerProps) {
  const [selectedTab, setSelectedTab] = useState<'audio' | 'visuals'>('audio');
  const [previewTrack, setPreviewTrack] = useState<string | null>(null);
  const [previewVisual, setPreviewVisual] = useState<string | null>(null);

  const formatDuration = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${String(secs).padStart(2, '0')}`;
  };

  return (
    <div className="bg-white rounded-lg shadow">
      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <div className="flex">
          <button
            onClick={() => setSelectedTab('audio')}
            className={clsx(
              'flex-1 px-6 py-4 text-sm font-medium border-b-2 transition',
              selectedTab === 'audio'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            )}
          >
            <FiMusic className="w-4 h-4 inline mr-2" />
            Audio Tracks ({audioTracks.length})
          </button>
          <button
            onClick={() => setSelectedTab('visuals')}
            className={clsx(
              'flex-1 px-6 py-4 text-sm font-medium border-b-2 transition',
              selectedTab === 'visuals'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            )}
          >
            <FiImage className="w-4 h-4 inline mr-2" />
            Visuals ({visualAssets.length})
          </button>
        </div>
      </div>

      {/* Tab Content */}
      <div className="p-6">
        {selectedTab === 'audio' && (
          <motion.div
            key="audio"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
          >
            <div className="space-y-3">
              {audioTracks.length === 0 ? (
                <div className="text-center py-12">
                  <FiMusic className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                  <p className="text-gray-500">No audio tracks generated yet</p>
                </div>
              ) : (
                audioTracks.map((track) => (
                  <motion.div
                    key={track.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition"
                  >
                    <div className="flex items-center space-x-4 flex-1">
                      <div className="flex-shrink-0 w-10 h-10 bg-blue-100 text-blue-600 rounded-lg flex items-center justify-center font-semibold">
                        {track.order_index}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900">
                          Track {track.order_index}
                        </p>
                        <p className="text-xs text-gray-500 truncate font-mono">
                          {track.local_file_path}
                        </p>
                      </div>
                      <div className="flex-shrink-0">
                        <span className="text-sm text-gray-600">
                          {formatDuration(track.duration_seconds)}
                        </span>
                      </div>
                      <div className="flex-shrink-0">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-200 text-gray-800">
                          {track.provider}
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2 ml-4">
                      {onRegenerateAudio && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => onRegenerateAudio(track.id)}
                        >
                          <FiRefreshCw className="w-4 h-4" />
                        </Button>
                      )}
                    </div>
                  </motion.div>
                ))
              )}
            </div>
          </motion.div>
        )}

        {selectedTab === 'visuals' && (
          <motion.div
            key="visuals"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
          >
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {visualAssets.length === 0 ? (
                <div className="col-span-full text-center py-12">
                  <FiImage className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                  <p className="text-gray-500">No visuals generated yet</p>
                </div>
              ) : (
                visualAssets.map((visual) => (
                  <motion.div
                    key={visual.id}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    whileHover={{ scale: 1.02 }}
                    className="bg-gray-50 rounded-lg overflow-hidden border border-gray-200"
                  >
                    {/* Visual Preview Placeholder */}
                    <div className="aspect-video bg-gradient-to-br from-blue-100 to-purple-100 flex items-center justify-center">
                      <div className="text-center">
                        <FiImage className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                        <p className="text-sm text-gray-600">Visual {visual.order_index}</p>
                      </div>
                    </div>

                    {/* Visual Info */}
                    <div className="p-3">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-900">
                          Visual #{visual.order_index}
                        </span>
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-200 text-gray-800">
                          {visual.provider}
                        </span>
                      </div>
                      <p className="text-xs text-gray-500 truncate font-mono mb-3">
                        {visual.local_file_path}
                      </p>
                      <div className="flex items-center space-x-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          className="flex-1"
                          onClick={() => setPreviewVisual(visual.id)}
                        >
                          <FiEye className="w-4 h-4 mr-1" />
                          Preview
                        </Button>
                        {onRegenerateVisual && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => onRegenerateVisual(visual.id)}
                          >
                            <FiRefreshCw className="w-4 h-4" />
                          </Button>
                        )}
                      </div>
                    </div>
                  </motion.div>
                ))
              )}
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
