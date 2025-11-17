/**
 * Video Job Create Page
 *
 * Multi-step wizard for creating new video jobs.
 */
'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { VideoCreationWizard } from '@/components/wizard/VideoCreationWizard';

export default function CreateVideoJobPage() {
  return (
    <div className="p-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="max-w-5xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900">Create Video Job</h1>
            <p className="text-gray-600 mt-2">
              Follow the guided steps to create a new AI-generated video
            </p>
          </div>

          <VideoCreationWizard />
        </div>
      </motion.div>
    </div>
  );
}
