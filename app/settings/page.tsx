/**
 * Settings Page
 *
 * Application settings and AI provider configuration.
 */
'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FiCheck, FiX, FiAlertCircle, FiZap, FiImage, FiMusic } from 'react-icons/fi';
import { Button, Loading, ErrorMessage } from '@/components/ui';
import { useUIStore } from '@/lib/store/ui-store';
import {
  getSettings,
  updateProviderSettings,
  type SettingsResponse,
  type ProviderStatus,
  type MusicProvider,
  type VisualProvider,
} from '@/lib/api';

export default function SettingsPage() {
  const [settings, setSettings] = useState<SettingsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { addNotification } = useUIStore();

  // Local selections
  const [selectedMusicProvider, setSelectedMusicProvider] = useState<MusicProvider | null>(null);
  const [selectedVisualProvider, setSelectedVisualProvider] = useState<VisualProvider | null>(null);

  useEffect(() => {
    loadSettings();
  }, []);

  async function loadSettings() {
    try {
      setLoading(true);
      setError(null);
      const data = await getSettings();
      setSettings(data);
      setSelectedMusicProvider((data.selected_music_provider as MusicProvider) || null);
      setSelectedVisualProvider((data.selected_visual_provider as VisualProvider) || null);
    } catch (err: any) {
      setError(err.message || 'Failed to load settings');
    } finally {
      setLoading(false);
    }
  }

  async function handleSave() {
    if (!selectedMusicProvider && !selectedVisualProvider) {
      addNotification('warning', 'Please select at least one provider');
      return;
    }

    try {
      setSaving(true);
      setError(null);

      await updateProviderSettings({
        music_provider: selectedMusicProvider || undefined,
        visual_provider: selectedVisualProvider || undefined,
      });

      addNotification('success', 'Provider settings saved successfully!');
      await loadSettings(); // Reload to get updated state
    } catch (err: any) {
      setError(err.message || 'Failed to save settings');
      addNotification('error', err.message || 'Failed to save settings');
    } finally {
      setSaving(false);
    }
  }

  const hasChanges =
    selectedMusicProvider !== settings?.selected_music_provider ||
    selectedVisualProvider !== settings?.selected_visual_provider;

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200 flex items-center justify-center">
        <Loading size="lg" message="Loading settings..." />
      </div>
    );
  }

  if (error && !settings) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200 p-8">
        <ErrorMessage
          title="Failed to Load Settings"
          message={error}
          onRetry={loadSettings}
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200 p-8">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">Settings</h1>
            <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
              Configure AI providers for music and visual generation
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <ErrorMessage message={error} className="mb-6" />
          )}

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Music Providers */}
            <div className="bg-white dark:bg-gray-800 transition-colors duration-200 rounded-lg shadow-md p-6">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-3 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
                  <FiMusic className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">Music Providers</h2>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Generate AI music tracks</p>
                </div>
              </div>

              <div className="space-y-4">
                {settings?.music_providers.map((provider) => (
                  <ProviderCard
                    key={provider.provider}
                    provider={provider}
                    selected={selectedMusicProvider === provider.provider}
                    onSelect={() => setSelectedMusicProvider(provider.provider as MusicProvider)}
                  />
                ))}
              </div>
            </div>

            {/* Visual Providers */}
            <div className="bg-white dark:bg-gray-800 transition-colors duration-200 rounded-lg shadow-md p-6">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                  <FiImage className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-gray-900 dark:text-gray-100">Visual Providers</h2>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Generate background visuals</p>
                </div>
              </div>

              <div className="space-y-4">
                {settings?.visual_providers.map((provider) => (
                  <ProviderCard
                    key={provider.provider}
                    provider={provider}
                    selected={selectedVisualProvider === provider.provider}
                    onSelect={() => setSelectedVisualProvider(provider.provider as VisualProvider)}
                  />
                ))}
              </div>
            </div>
          </div>

          {/* Save Button */}
          {hasChanges && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-6 bg-white dark:bg-gray-800 transition-colors duration-200 rounded-lg shadow-md p-6"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-amber-700 dark:text-amber-400">
                  <FiAlertCircle />
                  <span className="text-sm font-medium">You have unsaved changes</span>
                </div>
                <div className="flex gap-3">
                  <Button
                    variant="secondary"
                    onClick={() => {
                      setSelectedMusicProvider((settings?.selected_music_provider as MusicProvider) || null);
                      setSelectedVisualProvider((settings?.selected_visual_provider as VisualProvider) || null);
                    }}
                    disabled={saving}
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={handleSave}
                    loading={saving}
                    disabled={saving}
                  >
                    Save Settings
                  </Button>
                </div>
              </div>
            </motion.div>
          )}

          {/* Info Box */}
          <div className="mt-6 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700 rounded-lg p-6">
            <div className="flex gap-3">
              <FiAlertCircle className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-blue-900 dark:text-blue-300 mb-2">Configuration Notes</h3>
                <ul className="text-sm text-blue-800 dark:text-blue-300 space-y-1">
                  <li>• Providers require API keys to be configured in your <code className="px-1 py-0.5 bg-blue-100 dark:bg-blue-900/30 rounded text-blue-900 dark:text-blue-300">.env</code> file</li>
                  <li>• Only connected providers (with valid API keys) can be selected</li>
                  <li>• Settings are saved to environment variables for the current session</li>
                  <li>• For persistent configuration, update your <code className="px-1 py-0.5 bg-blue-100 dark:bg-blue-900/30 rounded text-blue-900 dark:text-blue-300">.env</code> file directly</li>
                </ul>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}

interface ProviderCardProps {
  provider: ProviderStatus;
  selected: boolean;
  onSelect: () => void;
}

function ProviderCard({ provider, selected, onSelect }: ProviderCardProps) {
  return (
    <motion.div
      whileHover={provider.connected ? { scale: 1.02 } : {}}
      whileTap={provider.connected ? { scale: 0.98 } : {}}
      onClick={provider.connected ? onSelect : undefined}
      className={`
        relative p-4 rounded-lg border-2 transition-all
        ${provider.connected ? 'cursor-pointer' : 'cursor-not-allowed opacity-60'}
        ${selected && provider.connected
          ? 'border-blue-500 dark:border-blue-400 bg-blue-50 dark:bg-blue-900/20'
          : provider.connected
          ? 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500 bg-white dark:bg-gray-800'
          : 'border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700'
        }
      `}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="font-semibold text-gray-900 dark:text-gray-100">{provider.name}</h3>
            {provider.connected ? (
              <div className="flex items-center gap-1 px-2 py-0.5 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 text-xs rounded-full">
                <FiCheck className="w-3 h-3" />
                <span>Connected</span>
              </div>
            ) : (
              <div className="flex items-center gap-1 px-2 py-0.5 bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300 text-xs rounded-full">
                <FiX className="w-3 h-3" />
                <span>Not Connected</span>
              </div>
            )}
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400">{provider.description}</p>
        </div>

        {selected && provider.connected && (
          <div className="ml-3 w-6 h-6 bg-blue-600 dark:bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0">
            <FiCheck className="w-4 h-4 text-white" />
          </div>
        )}
      </div>

      {!provider.connected && (
        <div className="mt-3 text-xs text-gray-500 dark:text-gray-400">
          Add <code className="px-1 py-0.5 bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-gray-300 rounded font-mono">{provider.provider.toUpperCase()}_API_KEY</code> to your .env file
        </div>
      )}
    </motion.div>
  );
}
