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

const statusConfig: Record<
  VideoJobStatus,
  { label: string; color: string }
> = {
  planned: {
    label: 'Planned',
    color: 'bg-gray-100 text-gray-800',
  },
  generating_music: {
    label: 'Generating Music',
    color: 'bg-blue-100 text-blue-800',
  },
  generating_image: {
    label: 'Generating Visuals',
    color: 'bg-purple-100 text-purple-800',
  },
  rendering: {
    label: 'Rendering Video',
    color: 'bg-yellow-100 text-yellow-800',
  },
  ready_for_export: {
    label: 'Ready for Export',
    color: 'bg-green-100 text-green-800',
  },
  completed: {
    label: 'Completed',
    color: 'bg-green-600 text-white',
  },
  failed: {
    label: 'Failed',
    color: 'bg-red-100 text-red-800',
  },
};

export function StatusBadge({ status, className = '' }: StatusBadgeProps) {
  const config = statusConfig[status];

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.color} ${className}`}
    >
      {config.label}
    </span>
  );
}
