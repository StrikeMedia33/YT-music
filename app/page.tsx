/**
 * Dashboard Home Page
 *
 * Overview dashboard with statistics and quick actions.
 */
'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { FiVideo, FiList, FiCheckCircle, FiAlertCircle, FiPlus } from 'react-icons/fi';
import { Button } from '@/components/ui';
import { listVideoJobs, listChannels, type VideoJob, type Channel } from '@/lib/api';

export default function DashboardPage() {
  const [jobs, setJobs] = useState<VideoJob[]>([]);
  const [channels, setChannels] = useState<Channel[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      const [jobsData, channelsData] = await Promise.all([
        listVideoJobs({ limit: 10 }),
        listChannels({ limit: 10 }),
      ]);
      setJobs(jobsData);
      setChannels(channelsData);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  }

  // Calculate statistics
  const stats = {
    total: jobs.length,
    completed: jobs.filter((j) => j.status === 'completed').length,
    inProgress: jobs.filter((j) =>
      ['generating_music', 'generating_image', 'rendering'].includes(j.status)
    ).length,
    failed: jobs.filter((j) => j.status === 'failed').length,
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  };

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center">
        <div className="text-gray-500">Loading dashboard...</div>
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
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-2">
            Welcome to AI Background Channel Studio
          </p>
        </motion.div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <motion.div variants={itemVariants}>
            <StatCard
              icon={<FiVideo className="w-6 h-6" />}
              label="Total Jobs"
              value={stats.total}
              color="blue"
            />
          </motion.div>
          <motion.div variants={itemVariants}>
            <StatCard
              icon={<FiCheckCircle className="w-6 h-6" />}
              label="Completed"
              value={stats.completed}
              color="green"
            />
          </motion.div>
          <motion.div variants={itemVariants}>
            <StatCard
              icon={<FiList className="w-6 h-6" />}
              label="In Progress"
              value={stats.inProgress}
              color="yellow"
            />
          </motion.div>
          <motion.div variants={itemVariants}>
            <StatCard
              icon={<FiAlertCircle className="w-6 h-6" />}
              label="Failed"
              value={stats.failed}
              color="red"
            />
          </motion.div>
        </div>

        {/* Quick Actions */}
        <motion.div variants={itemVariants} className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Link href="/video-jobs">
              <motion.div
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="bg-white rounded-lg shadow-sm border-2 border-dashed border-gray-300 p-6 hover:border-blue-500 transition cursor-pointer"
              >
                <FiPlus className="w-8 h-8 text-blue-600 mb-2" />
                <h3 className="font-semibold text-gray-900">Create Video Job</h3>
                <p className="text-sm text-gray-600 mt-1">
                  Start a new video generation pipeline
                </p>
              </motion.div>
            </Link>

            <Link href="/channels">
              <motion.div
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition cursor-pointer"
              >
                <FiList className="w-8 h-8 text-gray-700 mb-2" />
                <h3 className="font-semibold text-gray-900">Manage Channels</h3>
                <p className="text-sm text-gray-600 mt-1">
                  {channels.length} channel{channels.length !== 1 ? 's' : ''} configured
                </p>
              </motion.div>
            </Link>

            <Link href="/video-jobs">
              <motion.div
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition cursor-pointer"
              >
                <FiVideo className="w-8 h-8 text-gray-700 mb-2" />
                <h3 className="font-semibold text-gray-900">View All Jobs</h3>
                <p className="text-sm text-gray-600 mt-1">
                  Browse and manage video jobs
                </p>
              </motion.div>
            </Link>
          </div>
        </motion.div>

        {/* Recent Jobs */}
        <motion.div variants={itemVariants}>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Recent Jobs</h2>
            <Link href="/video-jobs">
              <Button variant="ghost" size="sm">
                View All
              </Button>
            </Link>
          </div>

          {jobs.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl shadow-sm border-2 border-dashed border-blue-200 p-12 text-center"
            >
              <div className="w-20 h-20 mx-auto mb-6 bg-blue-100 rounded-full flex items-center justify-center">
                <FiVideo className="w-10 h-10 text-blue-600" />
              </div>
              <h3 className="text-heading-md text-gray-900 mb-3">
                Ready to create your first video?
              </h3>
              <p className="text-body-md text-gray-600 mb-6 max-w-md mx-auto">
                Generate professional AI-powered background music videos in minutes.
                Perfect for YouTube channels focused on ambient, lo-fi, and study music.
              </p>
              <Link href="/video-jobs/create">
                <Button size="lg" className="shadow-lg">
                  <FiPlus className="mr-2 w-5 h-5" />
                  Create Your First Video
                </Button>
              </Link>
              <p className="text-caption text-gray-500 mt-4">
                Average generation time: 30-45 minutes
              </p>
            </motion.div>
          ) : (
            <div className="bg-white rounded-lg shadow overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Job ID
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                      Created
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {jobs.slice(0, 5).map((job) => (
                    <tr key={job.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <Link
                          href={`/video-jobs/${job.id}`}
                          className="text-sm font-mono text-blue-600 hover:text-blue-800"
                        >
                          {job.id.substring(0, 8)}...
                        </Link>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm text-gray-900">{job.status}</span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(job.created_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </motion.div>
      </motion.div>
    </div>
  );
}

function StatCard({
  icon,
  label,
  value,
  color,
}: {
  icon: React.ReactNode;
  label: string;
  value: number;
  color: 'blue' | 'green' | 'yellow' | 'red';
}) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    yellow: 'bg-yellow-50 text-yellow-600',
    red: 'bg-red-50 text-red-600',
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
    </motion.div>
  );
}
