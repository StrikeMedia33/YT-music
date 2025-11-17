/**
 * Analytics Page
 *
 * Analytics dashboard showing job statistics and metrics.
 */
'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  FiVideo,
  FiClock,
  FiCheckCircle,
  FiXCircle,
  FiTrendingUp,
  FiMusic,
  FiImage,
} from 'react-icons/fi';
import { listVideoJobs, type VideoJob } from '@/lib/api';
import clsx from 'clsx';

interface Analytics {
  totalJobs: number;
  completedJobs: number;
  failedJobs: number;
  inProgressJobs: number;
  completionRate: number;
  averageRenderTime: number;
  totalAudioTracks: number;
  totalVisuals: number;
  statusBreakdown: Record<string, number>;
}

export default function AnalyticsPage() {
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [jobs, setJobs] = useState<VideoJob[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, []);

  async function loadAnalytics() {
    try {
      setLoading(true);
      const jobsData = await listVideoJobs({ limit: 100 });
      setJobs(jobsData);

      // Calculate analytics
      const totalJobs = jobsData.length;
      const completedJobs = jobsData.filter(
        (j) => j.status === 'completed'
      ).length;
      const failedJobs = jobsData.filter((j) => j.status === 'failed').length;
      const inProgressJobs = jobsData.filter((j) =>
        ['generating_music', 'generating_image', 'rendering'].includes(
          j.status
        )
      ).length;

      const statusBreakdown = jobsData.reduce((acc, job) => {
        acc[job.status] = (acc[job.status] || 0) + 1;
        return acc;
      }, {} as Record<string, number>);

      setAnalytics({
        totalJobs,
        completedJobs,
        failedJobs,
        inProgressJobs,
        completionRate:
          totalJobs > 0 ? (completedJobs / totalJobs) * 100 : 0,
        averageRenderTime: 0, // TODO: Calculate from actual data
        totalAudioTracks: completedJobs * 20, // Estimate: 20 tracks per job
        totalVisuals: completedJobs * 20, // Estimate: 20 visuals per job
        statusBreakdown,
      });
    } catch (error) {
      console.error('Failed to load analytics:', error);
    } finally {
      setLoading(false);
    }
  }

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.1 },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  };

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center">
        <div className="text-gray-500">Loading analytics...</div>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="p-8">
        <div className="text-center text-gray-500">
          Failed to load analytics
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <motion.div
        initial="hidden"
        animate="visible"
        variants={containerVariants}
      >
        {/* Header */}
        <motion.div variants={itemVariants} className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
          <p className="text-gray-600 mt-2">
            Track performance and insights across all video jobs
          </p>
        </motion.div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <motion.div variants={itemVariants}>
            <MetricCard
              icon={<FiVideo className="w-6 h-6" />}
              label="Total Jobs"
              value={analytics.totalJobs}
              color="blue"
            />
          </motion.div>
          <motion.div variants={itemVariants}>
            <MetricCard
              icon={<FiCheckCircle className="w-6 h-6" />}
              label="Completed"
              value={analytics.completedJobs}
              color="green"
              subtitle={`${analytics.completionRate.toFixed(1)}% completion rate`}
            />
          </motion.div>
          <motion.div variants={itemVariants}>
            <MetricCard
              icon={<FiXCircle className="w-6 h-6" />}
              label="Failed"
              value={analytics.failedJobs}
              color="red"
            />
          </motion.div>
          <motion.div variants={itemVariants}>
            <MetricCard
              icon={<FiTrendingUp className="w-6 h-6" />}
              label="In Progress"
              value={analytics.inProgressJobs}
              color="yellow"
            />
          </motion.div>
        </div>

        {/* Content Generated */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <motion.div variants={itemVariants}>
            <MetricCard
              icon={<FiMusic className="w-6 h-6" />}
              label="Audio Tracks Generated"
              value={analytics.totalAudioTracks}
              color="purple"
              subtitle={`${analytics.completedJobs} completed jobs`}
            />
          </motion.div>
          <motion.div variants={itemVariants}>
            <MetricCard
              icon={<FiImage className="w-6 h-6" />}
              label="Visuals Generated"
              value={analytics.totalVisuals}
              color="indigo"
              subtitle={`${analytics.completedJobs} completed jobs`}
            />
          </motion.div>
        </div>

        {/* Status Breakdown */}
        <motion.div variants={itemVariants} className="mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-6">
              Job Status Breakdown
            </h2>
            <div className="space-y-3">
              {Object.entries(analytics.statusBreakdown).map(
                ([status, count]) => {
                  const percentage =
                    analytics.totalJobs > 0
                      ? (count / analytics.totalJobs) * 100
                      : 0;
                  return (
                    <div key={status}>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-700 capitalize">
                          {status.replace(/_/g, ' ')}
                        </span>
                        <span className="text-sm text-gray-600">
                          {count} ({percentage.toFixed(1)}%)
                        </span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                        <motion.div
                          className={clsx(
                            'h-full',
                            getStatusColor(status)
                          )}
                          initial={{ width: 0 }}
                          animate={{ width: `${percentage}%` }}
                          transition={{ duration: 0.5, delay: 0.2 }}
                        />
                      </div>
                    </div>
                  );
                }
              )}
            </div>
          </div>
        </motion.div>

        {/* Recent Activity */}
        <motion.div variants={itemVariants}>
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Recent Jobs
            </h2>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Job ID
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Status
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Created
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {jobs.slice(0, 10).map((job) => (
                    <tr key={job.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm font-mono text-gray-900">
                        {job.id.substring(0, 8)}...
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className={clsx(
                            'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                            getStatusBadgeColor(job.status)
                          )}
                        >
                          {job.status}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-500">
                        {new Date(job.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
}

function MetricCard({
  icon,
  label,
  value,
  color,
  subtitle,
}: {
  icon: React.ReactNode;
  label: string;
  value: number;
  color: 'blue' | 'green' | 'red' | 'yellow' | 'purple' | 'indigo';
  subtitle?: string;
}) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    red: 'bg-red-50 text-red-600',
    yellow: 'bg-yellow-50 text-yellow-600',
    purple: 'bg-purple-50 text-purple-600',
    indigo: 'bg-indigo-50 text-indigo-600',
  };

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      className="bg-white rounded-lg shadow p-6"
    >
      <div className={`inline-flex p-3 rounded-lg ${colorClasses[color]} mb-4`}>
        {icon}
      </div>
      <p className="text-sm text-gray-600">{label}</p>
      <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
      {subtitle && (
        <p className="text-xs text-gray-500 mt-1">{subtitle}</p>
      )}
    </motion.div>
  );
}

function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    completed: 'bg-green-500',
    failed: 'bg-red-500',
    generating_music: 'bg-blue-500',
    generating_image: 'bg-purple-500',
    rendering: 'bg-yellow-500',
    ready_for_export: 'bg-indigo-500',
    planned: 'bg-gray-400',
  };
  return colors[status] || 'bg-gray-400';
}

function getStatusBadgeColor(status: string): string {
  const colors: Record<string, string> = {
    completed: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800',
    generating_music: 'bg-blue-100 text-blue-800',
    generating_image: 'bg-purple-100 text-purple-800',
    rendering: 'bg-yellow-100 text-yellow-800',
    ready_for_export: 'bg-indigo-100 text-indigo-800',
    planned: 'bg-gray-100 text-gray-800',
  };
  return colors[status] || 'bg-gray-100 text-gray-800';
}
