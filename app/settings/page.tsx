/**
 * Settings Page
 *
 * Application settings and configuration.
 */
'use client';

import React from 'react';
import { motion } from 'framer-motion';

export default function SettingsPage() {
  return (
    <div className="p-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Settings</h1>

        <div className="bg-white rounded-lg shadow p-8 text-center">
          <p className="text-gray-600">
            Settings page coming soon...
          </p>
          <p className="text-sm text-gray-500 mt-2">
            Configure providers, rendering options, and more.
          </p>
        </div>
      </motion.div>
    </div>
  );
}
