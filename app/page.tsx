/**
 * Home Page
 *
 * Dashboard overview of the application.
 */
'use client';

import React from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            AI Background Channel Studio
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Automate the creation of high-quality background music videos for
            YouTube using AI-generated music and visuals.
          </p>
          <div className="flex gap-4 justify-center">
            <Link href="/channels">
              <Button size="lg">Get Started</Button>
            </Link>
            <Link href="/video-jobs">
              <Button size="lg" variant="secondary">
                View Jobs
              </Button>
            </Link>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-3 mb-16">
          <FeatureCard
            icon="🎵"
            title="AI Music Generation"
            description="Generate 20 unique music tracks (3-4 minutes each) using advanced AI music providers."
          />
          <FeatureCard
            icon="🎨"
            title="Visual Generation"
            description="Create 20 unique visuals matched to each track for engaging video content."
          />
          <FeatureCard
            icon="🎬"
            title="Video Rendering"
            description="Automatically render professional 1080p videos with crossfades and visual-audio pairing."
          />
          <FeatureCard
            icon="📝"
            title="Metadata Generation"
            description="Generate YouTube titles, descriptions with timestamps, and SEO-optimized tags."
          />
          <FeatureCard
            icon="⚙️"
            title="Background Processing"
            description="Automated pipeline execution with status tracking and error handling."
          />
          <FeatureCard
            icon="📊"
            title="Job Management"
            description="Track and manage all video generation jobs from a centralized dashboard."
          />
        </div>

        {/* Workflow Section */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-16">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
            5-Step Automated Pipeline
          </h2>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-5">
            <WorkflowStep
              number="1"
              title="Prompts"
              description="Generate 20 music + 20 visual prompts"
            />
            <WorkflowStep
              number="2"
              title="Music"
              description="Create 20 unique audio tracks"
            />
            <WorkflowStep
              number="3"
              title="Visuals"
              description="Generate 20 matched visuals"
            />
            <WorkflowStep
              number="4"
              title="Render"
              description="Create final MP4 video"
            />
            <WorkflowStep
              number="5"
              title="Metadata"
              description="Generate YouTube metadata"
            />
          </div>
        </div>

        {/* CTA Section */}
        <div className="bg-blue-600 rounded-xl shadow-lg p-8 text-center text-white">
          <h2 className="text-3xl font-bold mb-4">
            Ready to Create Your First Video?
          </h2>
          <p className="text-lg mb-6 opacity-90">
            Set up your channel and start generating high-quality background
            music videos today.
          </p>
          <Link href="/channels">
            <Button size="lg" className="bg-white text-blue-600 hover:bg-gray-100">
              Create Your First Channel
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: string;
  title: string;
  description: string;
}) {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition">
      <div className="text-4xl mb-3">{icon}</div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-600 text-sm">{description}</p>
    </div>
  );
}

function WorkflowStep({
  number,
  title,
  description,
}: {
  number: string;
  title: string;
  description: string;
}) {
  return (
    <div className="text-center">
      <div className="bg-blue-600 text-white rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-3 text-xl font-bold">
        {number}
      </div>
      <h4 className="font-semibold text-gray-900 mb-1">{title}</h4>
      <p className="text-sm text-gray-600">{description}</p>
    </div>
  );
}
