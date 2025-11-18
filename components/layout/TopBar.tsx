/**
 * Top Bar Component
 *
 * Top navigation bar with breadcrumbs and notifications.
 */
'use client';

import React, { useState, useEffect } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FiBell,
  FiMenu,
  FiX,
  FiActivity,
  FiSun,
  FiMoon,
  FiVideo,
  FiMusic,
  FiImage,
  FiFilm,
  FiExternalLink,
  FiLoader
} from 'react-icons/fi';
import { useUIStore, Notification } from '@/lib/store/ui-store';
import { useTheme } from '@/lib/contexts/theme-context';
import { SlidePanel, useSlidePanel } from '@/components/ui';
import { ActivityMonitorPanel } from '@/components/activity/ActivityMonitorPanel';
import { VideoJobDetailPanel } from '@/components/video-jobs/VideoJobDetailPanel';
import clsx from 'clsx';

// Helper function to get job icon
const getJobIcon = (jobType?: Notification['jobType']) => {
  switch (jobType) {
    case 'video':
      return <FiVideo className="w-4 h-4" />;
    case 'music':
      return <FiMusic className="w-4 h-4" />;
    case 'image':
      return <FiImage className="w-4 h-4" />;
    case 'render':
      return <FiFilm className="w-4 h-4" />;
    default:
      return null;
  }
};

export function TopBar() {
  const pathname = usePathname();
  const router = useRouter();
  const { toggleSidebar, notifications, removeNotification, clearNotifications } = useUIStore();
  const { theme, toggleTheme } = useTheme();
  const [showNotifications, setShowNotifications] = useState(false);

  // Slide panel state
  const activityPanel = useSlidePanel();
  const jobPanel = useSlidePanel<string>();

  // Generate breadcrumbs from pathname
  const breadcrumbs = React.useMemo(() => {
    const paths = pathname.split('/').filter(Boolean);
    return [
      { label: 'Home', href: '/' },
      ...paths.map((path, index) => ({
        label: path.charAt(0).toUpperCase() + path.slice(1).replace(/-/g, ' '),
        href: '/' + paths.slice(0, index + 1).join('/'),
      })),
    ];
  }, [pathname]);

  // Auto-dismiss success notifications after 5 seconds
  useEffect(() => {
    const successNotifications = notifications.filter((n) => n.type === 'success');
    if (successNotifications.length > 0) {
      const timers = successNotifications.map((notif) =>
        setTimeout(() => {
          removeNotification(notif.id);
        }, 5000)
      );
      return () => timers.forEach(clearTimeout);
    }
  }, [notifications, removeNotification]);

  return (
    <header className="sticky top-0 z-10 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 transition-colors duration-200">
      <div className="flex items-center justify-between px-4 py-3">
        {/* Left: Menu button + Breadcrumbs */}
        <div className="flex items-center space-x-4">
          <button
            onClick={toggleSidebar}
            className="lg:hidden p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition"
            aria-label="Toggle sidebar navigation"
          >
            <FiMenu className="w-5 h-5 text-gray-700 dark:text-gray-200" aria-hidden="true" />
          </button>

          {/* Breadcrumbs */}
          <nav className="hidden sm:flex items-center space-x-2 text-sm" aria-label="Breadcrumb">
            {breadcrumbs.map((crumb, index) => (
              <React.Fragment key={crumb.href}>
                {index > 0 && (
                  <span className="text-gray-400 dark:text-gray-500" aria-hidden="true">/</span>
                )}
                {index === breadcrumbs.length - 1 ? (
                  <span
                    className="text-gray-900 dark:text-gray-100 font-medium"
                    aria-current="page"
                  >
                    {crumb.label}
                  </span>
                ) : (
                  <Link
                    href={crumb.href}
                    className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors"
                  >
                    {crumb.label}
                  </Link>
                )}
              </React.Fragment>
            ))}
          </nav>
        </div>

        {/* Right: Dark Mode, Activity Monitor & Notifications */}
        <div className="flex items-center space-x-2">
          {/* Dark Mode Toggle */}
          <button
            onClick={toggleTheme}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition relative"
            aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
            title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
          >
            {theme === 'dark' ? (
              <FiSun className="w-5 h-5 text-gray-700 dark:text-gray-200" aria-hidden="true" />
            ) : (
              <FiMoon className="w-5 h-5 text-gray-700 dark:text-gray-200" aria-hidden="true" />
            )}
          </button>

          {/* Activity Monitor */}
          <button
            onClick={() => activityPanel.open()}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition relative"
            aria-label="Activity Monitor"
            title="View active video jobs"
          >
            <FiActivity className="w-5 h-5 text-gray-700 dark:text-gray-200" aria-hidden="true" />
          </button>

          {/* Notifications Bell */}
          <div className="relative">
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition relative"
              aria-label={"Notifications"}
              aria-haspopup="true"
              aria-expanded={showNotifications}
            >
              <FiBell className="w-5 h-5 text-gray-700 dark:text-gray-200" aria-hidden="true" />
              {notifications.length > 0 && (
                <motion.span
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"
                  role="status"
                />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Notifications Dropdown */}
      <AnimatePresence>
        {showNotifications && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute right-4 top-16 w-96 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden z-50"
            role="dialog"
            aria-label="Notifications"
          >
            <div className="p-3 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
              <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                Notifications ({notifications.length})
              </h3>
              {notifications.length > 0 && (
                <button
                  onClick={() => {
                    clearNotifications();
                    setShowNotifications(false);
                  }}
                  className="text-xs text-blue-600 dark:text-white hover:text-blue-800 dark:hover:text-gray-300 font-medium"
                >
                  Clear All
                </button>
              )}
            </div>
            <div className="max-h-96 overflow-y-auto">
              {notifications.length === 0 ? (
                <div className="p-8 text-center">
                  <FiBell className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-3" />
                  <p className="text-sm text-gray-500 dark:text-gray-400 font-medium">
                    No notifications
                  </p>
                  <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                    You'll see updates about video jobs and background tasks here
                  </p>
                </div>
              ) : (
                notifications.map((notif) => (
                  <motion.div
                    key={notif.id}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    className={clsx(
                      'p-3 border-b border-gray-100 dark:border-gray-700 last:border-0 relative group',
                      notif.type === 'error' && 'bg-red-50 dark:bg-red-900/20',
                      notif.type === 'success' && 'bg-green-50 dark:bg-green-900/20',
                      notif.type === 'warning' && 'bg-yellow-50 dark:bg-yellow-900/20',
                      notif.type === 'info' && 'bg-blue-50 dark:bg-blue-900/20',
                      notif.type === 'progress' && 'bg-purple-50 dark:bg-purple-900/20'
                    )}
                  >
                    <div className="flex items-start gap-3">
                      {/* Job Type Icon */}
                      {notif.jobType && (
                        <div className="mt-0.5 text-gray-600 dark:text-gray-400">
                          {getJobIcon(notif.jobType)}
                        </div>
                      )}

                      {/* Progress Spinner for progress type */}
                      {notif.type === 'progress' && !notif.jobType && (
                        <div className="mt-0.5">
                          <FiLoader className="w-4 h-4 text-blue-600 dark:text-blue-400 animate-spin" />
                        </div>
                      )}

                      {/* Content */}
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-gray-900 dark:text-gray-100">{notif.message}</p>

                        {/* Progress Bar */}
                        {notif.progress !== undefined && (
                          <div className="mt-2">
                            <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400 mb-1">
                              <span>Progress</span>
                              <span>{notif.progress}%</span>
                            </div>
                            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
                              <motion.div
                                initial={{ width: 0 }}
                                animate={{ width: `${notif.progress}%` }}
                                transition={{ duration: 0.3 }}
                                className="h-full bg-blue-600 dark:bg-blue-400 rounded-full"
                              />
                            </div>
                          </div>
                        )}

                        {/* Action Button */}
                        {notif.action && (
                          <div className="mt-2">
                            {notif.action.href ? (
                              <Link
                                href={notif.action.href}
                                onClick={() => {
                                  setShowNotifications(false);
                                  if (notif.dismissible !== false) {
                                    removeNotification(notif.id);
                                  }
                                }}
                                className="inline-flex items-center gap-1 text-xs font-medium text-blue-600 dark:text-white hover:text-blue-800 dark:hover:text-gray-300"
                              >
                                {notif.action.label}
                                <FiExternalLink className="w-3 h-3" />
                              </Link>
                            ) : notif.action.onClick ? (
                              <button
                                onClick={() => {
                                  notif.action?.onClick?.();
                                  setShowNotifications(false);
                                  if (notif.dismissible !== false) {
                                    removeNotification(notif.id);
                                  }
                                }}
                                className="inline-flex items-center gap-1 text-xs font-medium text-blue-600 dark:text-white hover:text-blue-800 dark:hover:text-gray-300"
                              >
                                {notif.action.label}
                              </button>
                            ) : null}
                          </div>
                        )}

                        {/* Timestamp */}
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                          {new Date(notif.timestamp).toLocaleTimeString()}
                        </p>
                      </div>

                      {/* Dismiss Button */}
                      {notif.dismissible !== false && (
                        <button
                          onClick={() => removeNotification(notif.id)}
                          className="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-700 transition opacity-0 group-hover:opacity-100"
                          aria-label="Dismiss notification"
                        >
                          <FiX className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                        </button>
                      )}
                    </div>
                  </motion.div>
                ))
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Activity Monitor Panel */}
      <SlidePanel
        isOpen={activityPanel.isOpen}
        onClose={activityPanel.close}
        title="Activity Monitor"
        subtitle="Track active video job progress"
        width="lg"
      >
        <ActivityMonitorPanel
          onViewJob={(jobId) => {
            activityPanel.close();
            jobPanel.open(jobId);
          }}
        />
      </SlidePanel>

      {/* Video Job Detail Panel */}
      <SlidePanel
        isOpen={jobPanel.isOpen}
        onClose={jobPanel.close}
        title="Video Job Details"
        width="xl"
      >
        {jobPanel.selectedId && (
          <VideoJobDetailPanel jobId={jobPanel.selectedId} onClose={jobPanel.close} />
        )}
      </SlidePanel>
    </header>
  );
}
