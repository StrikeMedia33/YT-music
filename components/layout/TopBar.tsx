/**
 * Top Bar Component
 *
 * Top navigation bar with breadcrumbs and notifications.
 */
'use client';

import React, { useState, useEffect } from 'react';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { FiBell, FiMenu, FiX } from 'react-icons/fi';
import { useUIStore } from '@/lib/store/ui-store';
import clsx from 'clsx';

export function TopBar() {
  const pathname = usePathname();
  const { toggleSidebar, notifications, removeNotification, clearNotifications } = useUIStore();
  const [showNotifications, setShowNotifications] = useState(false);

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
    <header className="sticky top-0 z-10 bg-white border-b border-gray-200">
      <div className="flex items-center justify-between px-4 py-3">
        {/* Left: Menu button + Breadcrumbs */}
        <div className="flex items-center space-x-4">
          <button
            onClick={toggleSidebar}
            className="lg:hidden p-2 rounded-lg hover:bg-gray-100 transition"
            aria-label="Toggle sidebar navigation"
          >
            <FiMenu className="w-5 h-5" aria-hidden="true" />
          </button>

          {/* Breadcrumbs */}
          <nav className="hidden sm:flex items-center space-x-2 text-sm" aria-label="Breadcrumb">
            {breadcrumbs.map((crumb, index) => (
              <React.Fragment key={crumb.href}>
                {index > 0 && (
                  <span className="text-gray-400" aria-hidden="true">/</span>
                )}
                {index === breadcrumbs.length - 1 ? (
                  <span
                    className="text-gray-900 font-medium"
                    aria-current="page"
                  >
                    {crumb.label}
                  </span>
                ) : (
                  <Link
                    href={crumb.href}
                    className="text-gray-500 hover:text-gray-700 transition-colors"
                  >
                    {crumb.label}
                  </Link>
                )}
              </React.Fragment>
            ))}
          </nav>
        </div>

        {/* Right: Notifications */}
        <div className="flex items-center space-x-2">
          {/* Notifications Bell */}
          <div className="relative">
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              className="p-2 rounded-lg hover:bg-gray-100 transition relative"
              aria-label={"Notifications"}
              aria-haspopup="true"
              aria-expanded={showNotifications}
            >
              <FiBell className="w-5 h-5" aria-hidden="true" />
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
        {showNotifications && notifications.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute right-4 top-16 w-96 bg-white rounded-lg shadow-lg border border-gray-200 overflow-hidden z-50"
            role="dialog"
            aria-label="Notifications"
          >
            <div className="p-3 border-b border-gray-200 flex items-center justify-between">
              <h3 className="font-semibold text-gray-900">
                Notifications ({notifications.length})
              </h3>
              <button
                onClick={() => {
                  clearNotifications();
                  setShowNotifications(false);
                }}
                className="text-xs text-blue-600 hover:text-blue-800 font-medium"
              >
                Clear All
              </button>
            </div>
            <div className="max-h-96 overflow-y-auto">
              {notifications.map((notif) => (
                <motion.div
                  key={notif.id}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  className={clsx(
                    'p-3 border-b border-gray-100 last:border-0 relative group',
                    notif.type === 'error' && 'bg-red-50',
                    notif.type === 'success' && 'bg-green-50',
                    notif.type === 'warning' && 'bg-yellow-50',
                    notif.type === 'info' && 'bg-blue-50'
                  )}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1">
                      <p className="text-sm text-gray-900">{notif.message}</p>
                      <p className="text-xs text-gray-500 mt-1">
                        {new Date(notif.timestamp).toLocaleTimeString()}
                      </p>
                    </div>
                    <button
                      onClick={() => removeNotification(notif.id)}
                      className="p-1 rounded hover:bg-gray-200 transition opacity-0 group-hover:opacity-100"
                      aria-label="Dismiss notification"
                    >
                      <FiX className="w-4 h-4 text-gray-600" />
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}
