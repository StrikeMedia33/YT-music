/**
 * Sidebar Navigation Component
 *
 * Main navigation sidebar with icons and labels.
 */
'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion } from 'framer-motion';
import {
  FiHome,
  FiVideo,
  FiList,
  FiSettings,
  FiBarChart2,
  FiMenu,
  FiX,
} from 'react-icons/fi';
import { useUIStore } from '@/lib/store/ui-store';
import clsx from 'clsx';

interface NavItem {
  label: string;
  href: string;
  icon: React.ReactNode;
}

const navItems: NavItem[] = [
  {
    label: 'Dashboard',
    href: '/',
    icon: <FiHome className="w-5 h-5" />,
  },
  {
    label: 'Video Jobs',
    href: '/video-jobs',
    icon: <FiVideo className="w-5 h-5" />,
  },
  {
    label: 'Channels',
    href: '/channels',
    icon: <FiList className="w-5 h-5" />,
  },
  {
    label: 'Analytics',
    href: '/analytics',
    icon: <FiBarChart2 className="w-5 h-5" />,
  },
  {
    label: 'Settings',
    href: '/settings',
    icon: <FiSettings className="w-5 h-5" />,
  },
];

export function Sidebar() {
  const pathname = usePathname();
  const { sidebarOpen, toggleSidebar } = useUIStore();

  return (
    <>
      {/* Mobile overlay */}
      {sidebarOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={toggleSidebar}
          className="fixed inset-0 bg-black bg-opacity-50 z-20 lg:hidden"
        />
      )}

      {/* Sidebar */}
      <motion.aside
        initial={false}
        animate={{
          x: sidebarOpen ? 0 : -280,
        }}
        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
        className={clsx(
          'fixed left-0 top-0 bottom-0 w-64 bg-white border-r border-gray-200 z-30',
          'flex flex-col',
          'lg:translate-x-0'
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <Link href="/" className="flex items-center space-x-2">
            <span className="text-2xl">🎵</span>
            <span className="font-bold text-gray-900 text-lg">
              AI Studio
            </span>
          </Link>
          <button
            onClick={toggleSidebar}
            className="lg:hidden p-2 rounded-lg hover:bg-gray-100 transition"
          >
            <FiX className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-1">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link key={item.href} href={item.href}>
                <motion.div
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className={clsx(
                    'flex items-center space-x-3 px-4 py-3 rounded-lg transition',
                    isActive
                      ? 'bg-blue-50 text-blue-600'
                      : 'text-gray-700 hover:bg-gray-100'
                  )}
                >
                  {item.icon}
                  <span className="font-medium">{item.label}</span>
                </motion.div>
              </Link>
            );
          })}
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200">
          <p className="text-xs text-gray-500 text-center">
            Powered by Claude Code
          </p>
        </div>
      </motion.aside>

      {/* Toggle button for mobile */}
      {!sidebarOpen && (
        <motion.button
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          onClick={toggleSidebar}
          className="fixed top-4 left-4 z-20 lg:hidden p-2 bg-white rounded-lg shadow-lg border border-gray-200"
        >
          <FiMenu className="w-6 h-6" />
        </motion.button>
      )}
    </>
  );
}
