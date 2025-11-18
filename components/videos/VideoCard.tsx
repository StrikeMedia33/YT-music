/**
 * Video Card Component
 *
 * Card component for displaying video in grid view.
 */
import React from 'react';
import { motion } from 'framer-motion';
import { FiMoreVertical, FiExternalLink, FiEdit, FiCalendar, FiCheckCircle } from 'react-icons/fi';
import type { VideoJob } from '@/lib/api';
import { VideoStatusBadge } from './VideoStatusBadge';

export interface VideoCardProps {
  video: VideoJob;
  onView: (videoId: string) => void;
  onEdit?: (videoId: string) => void;
  onSchedule?: (videoId: string) => void;
  onPublish?: (videoId: string) => void;
}

export function VideoCard({ video, onView, onEdit, onSchedule, onPublish }: VideoCardProps) {
  const [showMenu, setShowMenu] = React.useState(false);

  // Generate thumbnail placeholder (first image or default)
  const thumbnailUrl = video.local_video_path
    ? `/api/videos/${video.id}/thumbnail` // Future: actual thumbnail endpoint
    : null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ scale: 1.02 }}
      className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden cursor-pointer border border-gray-200 dark:border-gray-700"
      onClick={() => onView(video.id)}
    >
      {/* Thumbnail */}
      <div className="relative aspect-video bg-gradient-to-br from-blue-100 to-purple-100 dark:from-gray-700 dark:to-gray-600">
        {thumbnailUrl ? (
          <img
            src={thumbnailUrl}
            alt={video.video_title || video.niche_label}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <span className="text-4xl text-gray-400 dark:text-gray-500">🎵</span>
          </div>
        )}

        {/* Duration badge */}
        <div className="absolute bottom-2 right-2 bg-black/80 text-white text-xs px-2 py-1 rounded">
          {video.target_duration_minutes} min
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        {/* Title */}
        <h3 className="font-semibold text-gray-900 dark:text-gray-100 line-clamp-2 mb-2">
          {video.video_title || video.niche_label}
        </h3>

        {/* Metadata */}
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm text-gray-600 dark:text-gray-400">
            {video.niche_label}
          </span>
          {video.video_status && (
            <VideoStatusBadge status={video.video_status} />
          )}
        </div>

        {/* Actions */}
        <div className="flex items-center justify-between">
          <span className="text-xs text-gray-500 dark:text-gray-400">
            {new Date(video.created_at).toLocaleDateString()}
          </span>

          {/* Quick actions menu */}
          <div className="relative">
            <button
              onClick={(e) => {
                e.stopPropagation();
                setShowMenu(!showMenu);
              }}
              className="p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition"
              aria-label="More actions"
            >
              <FiMoreVertical className="w-4 h-4 text-gray-600 dark:text-gray-400" />
            </button>

            {showMenu && (
              <div className="absolute right-0 bottom-full mb-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-1 z-10">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onView(video.id);
                    setShowMenu(false);
                  }}
                  className="w-full px-4 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2"
                >
                  <FiExternalLink className="w-4 h-4" />
                  View Details
                </button>
                {onEdit && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onEdit(video.id);
                      setShowMenu(false);
                    }}
                    className="w-full px-4 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2"
                  >
                    <FiEdit className="w-4 h-4" />
                    Copy Metadata
                  </button>
                )}
                {onSchedule && !video.youtube_video_id && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onSchedule(video.id);
                      setShowMenu(false);
                    }}
                    className="w-full px-4 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2"
                  >
                    <FiCalendar className="w-4 h-4" />
                    Schedule
                  </button>
                )}
                {onPublish && !video.youtube_video_id && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onPublish(video.id);
                      setShowMenu(false);
                    }}
                    className="w-full px-4 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2"
                  >
                    <FiCheckCircle className="w-4 h-4" />
                    Mark as Published
                  </button>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
}
