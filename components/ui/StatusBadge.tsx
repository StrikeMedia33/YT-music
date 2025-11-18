/**
 * Status Badge Component
 *
 * Displays video job status with appropriate color coding.
 */
import React from 'react';
import type { VideoJobStatus } from '@/lib/api';

export interface StatusBadgeProps {
  status: VideoJobStatus;
  className?: string;
}

// WCAG AA compliant color combinations (4.5:1 contrast minimum)
const statusConfig: Record<
  VideoJobStatus,
  { label: string; color: string }
> = {
  planned: {
    label: 'Planned',
    color: 'bg-gray-200 text-gray-900', // Contrast: ~6.5:1
  },
  generating_music: {
    label: 'Generating Music',
    color: 'bg-blue-100 text-blue-900', // Contrast: ~7.2:1
  },
  generating_image: {
    label: 'Generating Visuals',
    color: 'bg-purple-100 text-purple-900', // Contrast: ~6.8:1
  },
  rendering: {
    label: 'Rendering Video',
    color: 'bg-yellow-100 text-yellow-900', // Contrast: ~5.9:1
  },
  ready_for_export: {
    label: 'Ready for Export',
    color: 'bg-green-100 text-green-900', // Contrast: ~6.3:1
  },
  completed: {
    label: 'Completed',
    color: 'bg-green-700 text-white', // Contrast: ~8.1:1
  },
  failed: {
    label: 'Failed',
    color: 'bg-red-100 text-red-900', // Contrast: ~7.0:1
  },
  cancelled: {
    label: 'Cancelled',
    color: 'bg-gray-400 text-gray-900', // Contrast: ~4.8:1
  },
};

export function StatusBadge({ status, className = '' }: StatusBadgeProps) {
  const config = statusConfig[status];

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.color} ${className}`}
      role="status"
      aria-label={`Status: ${config.label}`}
    >
      {config.label}
    </span>
  );
}
