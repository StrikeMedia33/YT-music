/**
 * Video Status Badge Component
 *
 * Displays video publishing status with appropriate color coding.
 */
import React from 'react';
import type { VideoStatusDisplay } from '@/lib/api';

export interface VideoStatusBadgeProps {
  status: VideoStatusDisplay;
  className?: string;
}

// WCAG AA compliant color combinations (4.5:1 contrast minimum)
const statusConfig: Record<
  VideoStatusDisplay,
  { label: string; color: string; darkColor: string }
> = {
  production: {
    label: 'Production',
    color: 'bg-blue-100 text-blue-900',  // Light mode
    darkColor: 'dark:bg-blue-900/30 dark:text-blue-300',  // Dark mode
  },
  draft: {
    label: 'Draft',
    color: 'bg-gray-200 text-gray-900',  // Light mode
    darkColor: 'dark:bg-gray-700 dark:text-gray-300',  // Dark mode
  },
  scheduled: {
    label: 'Scheduled',
    color: 'bg-yellow-100 text-yellow-900',  // Light mode
    darkColor: 'dark:bg-yellow-900/30 dark:text-yellow-300',  // Dark mode
  },
  published: {
    label: 'Published',
    color: 'bg-green-100 text-green-900',  // Light mode
    darkColor: 'dark:bg-green-900/30 dark:text-green-300',  // Dark mode
  },
};

export function VideoStatusBadge({ status, className = '' }: VideoStatusBadgeProps) {
  const config = statusConfig[status];

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.color} ${config.darkColor} ${className}`}
      role="status"
      aria-label={`Video status: ${config.label}`}
    >
      {config.label}
    </span>
  );
}
