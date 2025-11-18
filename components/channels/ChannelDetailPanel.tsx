/**
 * Channel Detail Panel Component
 *
 * Displays detailed channel information in a slide panel with delete functionality.
 */
'use client';

import React, { useState, useEffect } from 'react';
import { FiTrash2, FiExternalLink, FiCalendar, FiTag } from 'react-icons/fi';
import { getChannel, deleteChannel, type Channel } from '@/lib/api';
import { Button, Loading, ErrorMessage, useToast, ConfirmDialog } from '@/components/ui';

export interface ChannelDetailPanelProps {
  channelId: string;
  onClose: () => void;
  onDeleted?: () => void;
}

export function ChannelDetailPanel({
  channelId,
  onClose,
  onDeleted,
}: ChannelDetailPanelProps) {
  const toast = useToast();
  const [channel, setChannel] = useState<Channel | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  useEffect(() => {
    loadChannel();
  }, [channelId]);

  async function loadChannel() {
    try {
      setLoading(true);
      setError(null);
      const data = await getChannel(channelId);
      setChannel(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load channel');
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete() {
    if (!channel) return;

    try {
      setDeleting(true);
      await deleteChannel(channelId);
      toast.success('Channel deleted', `${channel.name} has been permanently deleted.`);
      setShowDeleteConfirm(false);
      onDeleted?.();
      onClose();
    } catch (err: any) {
      toast.error('Failed to delete channel', err.message);
      setError(err.message || 'Failed to delete channel');
      setShowDeleteConfirm(false);
    } finally {
      setDeleting(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loading size="lg" message="Loading channel details..." />
      </div>
    );
  }

  if (error || !channel) {
    return (
      <ErrorMessage
        message={error || 'Channel not found'}
        onRetry={loadChannel}
      />
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="border-b border-gray-200 pb-4 mb-6">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              {channel.name}
            </h2>
            <div className="flex items-center space-x-2">
              <span
                className={`inline-flex px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  channel.is_active
                    ? 'bg-green-100 text-green-800'
                    : 'bg-gray-100 text-gray-800'
                }`}
              >
                {channel.is_active ? 'Active' : 'Inactive'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto space-y-6">
        {/* Channel Info Section */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
            <FiTag className="w-5 h-5 mr-2" />
            Channel Information
          </h3>
          <div className="bg-gray-50 rounded-lg p-4 space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-500 mb-1">
                YouTube Channel ID
              </label>
              <div className="flex items-center space-x-2">
                <code className="text-sm text-gray-900 bg-white px-2 py-1 rounded border border-gray-200">
                  {channel.youtube_channel_id}
                </code>
                <a
                  href={`https://www.youtube.com/channel/${channel.youtube_channel_id}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-700"
                  title="Open on YouTube"
                >
                  <FiExternalLink className="w-4 h-4" />
                </a>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-500 mb-1">
                Brand Niche
              </label>
              <p className="text-sm text-gray-900">{channel.brand_niche}</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-500 mb-1 flex items-center">
                <FiCalendar className="w-4 h-4 mr-1" />
                Created
              </label>
              <p className="text-sm text-gray-900">
                {new Date(channel.created_at).toLocaleString()}
              </p>
            </div>

            {channel.updated_at && (
              <div>
                <label className="block text-sm font-medium text-gray-500 mb-1">
                  Last Updated
                </label>
                <p className="text-sm text-gray-900">
                  {new Date(channel.updated_at).toLocaleString()}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Footer Actions */}
      <div className="border-t border-gray-200 pt-4 mt-6">
        <div className="flex items-center justify-between">
          <Button
            variant="danger"
            onClick={() => setShowDeleteConfirm(true)}
            disabled={deleting}
          >
            <FiTrash2 className="w-4 h-4 mr-2" />
            Delete Channel
          </Button>
          <Button variant="secondary" onClick={onClose}>
            Close
          </Button>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      <ConfirmDialog
        isOpen={showDeleteConfirm}
        onClose={() => setShowDeleteConfirm(false)}
        onConfirm={handleDelete}
        title="Delete Channel?"
        description={`Are you sure you want to delete "${channel?.name}"? This will permanently delete the channel and all associated video jobs. This action cannot be undone.`}
        confirmText="Delete Channel"
        cancelText="Cancel"
        variant="danger"
        loading={deleting}
      />
    </div>
  );
}
