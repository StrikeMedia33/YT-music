/**
 * SlidePanel Component
 *
 * Production-ready slide-in panel based on ScaleGrow implementation.
 * Features smooth animations, accessibility, and scroll position preservation.
 *
 * Key Features:
 * - Smooth spring-based animations
 * - Scroll position preservation (not just overflow:hidden)
 * - ESC key and backdrop click to close
 * - Sticky header and footer
 * - Responsive widths
 * - Full ARIA accessibility
 * - Proper z-index layering
 */
'use client';

import React, { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiX } from 'react-icons/fi';
import { springPhysics, slideVariants, backdropVariants, zIndex } from '@/lib/animations';

export interface SlidePanelProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  subtitle?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  width?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
  preventClose?: boolean; // Prevent closing during async operations
  showCloseButton?: boolean;
}

const widthClasses = {
  sm: 'max-w-md',   // 448px
  md: 'max-w-2xl',  // 672px
  lg: 'max-w-4xl',  // 896px
  xl: 'max-w-6xl',  // 1152px
  full: 'max-w-full',
};

export function SlidePanel({
  isOpen,
  onClose,
  title,
  subtitle,
  children,
  footer,
  width = 'lg',
  preventClose = false,
  showCloseButton = true,
}: SlidePanelProps) {
  const scrollPositionRef = useRef(0);
  const [isRendered, setIsRendered] = useState(false);

  // Save and restore scroll position instead of just hiding overflow
  useEffect(() => {
    if (isOpen) {
      // Save current scroll position
      scrollPositionRef.current = window.scrollY;

      // Prevent body scroll
      document.body.style.overflow = 'hidden';
      document.body.style.position = 'fixed';
      document.body.style.top = `-${scrollPositionRef.current}px`;
      document.body.style.width = '100%';

      setIsRendered(true);
    } else {
      // Restore scroll position
      document.body.style.removeProperty('overflow');
      document.body.style.removeProperty('position');
      document.body.style.removeProperty('top');
      document.body.style.removeProperty('width');

      window.scrollTo(0, scrollPositionRef.current);

      setIsRendered(false);
    }

    return () => {
      document.body.style.removeProperty('overflow');
      document.body.style.removeProperty('position');
      document.body.style.removeProperty('top');
      document.body.style.removeProperty('width');
    };
  }, [isOpen]);

  // Handle ESC key - only add listener when panel is open
  useEffect(() => {
    if (!isOpen || preventClose) return;

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, preventClose, onClose]);

  const handleBackdropClick = () => {
    if (!preventClose) {
      onClose();
    }
  };

  const handleCloseClick = () => {
    if (!preventClose) {
      onClose();
    }
  };

  return (
    <AnimatePresence mode="wait">
      {isOpen && (
        <>
          {/* Backdrop Overlay */}
          <motion.div
            variants={backdropVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            transition={{ duration: 0.2 }}
            className="fixed inset-0 bg-black/50 dark:bg-black/70 backdrop-blur-sm transition-colors duration-200"
            style={{ zIndex: zIndex.slidePanel }}
            onClick={handleBackdropClick}
            aria-hidden="true"
          />

          {/* Slide Panel */}
          <motion.div
            variants={slideVariants.fromRight}
            initial="initial"
            animate="animate"
            exit="exit"
            transition={springPhysics.default}
            className={`fixed right-0 top-0 bottom-0 ${widthClasses[width]} w-full bg-white dark:bg-gray-800 shadow-2xl dark:shadow-gray-900/50 flex flex-col transition-colors duration-200`}
            style={{ zIndex: zIndex.slidePanel + 1 }}
            role="dialog"
            aria-modal="true"
            aria-labelledby={title ? 'slide-panel-title' : undefined}
            aria-describedby={subtitle ? 'slide-panel-subtitle' : undefined}
          >
            {/* Sticky Header */}
            {(title || subtitle) && (
              <div className="sticky top-0 z-10 flex items-start justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 transition-colors duration-200">
                <div className="flex-1 min-w-0">
                  {title && (
                    <h2
                      id="slide-panel-title"
                      className="text-xl font-semibold text-gray-900 dark:text-gray-100 truncate"
                    >
                      {title}
                    </h2>
                  )}
                  {subtitle && (
                    <p
                      id="slide-panel-subtitle"
                      className="mt-1 text-sm text-gray-600 dark:text-gray-400"
                    >
                      {subtitle}
                    </p>
                  )}
                </div>
                {showCloseButton && (
                  <button
                    onClick={handleCloseClick}
                    disabled={preventClose}
                    className="ml-4 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0"
                    aria-label="Close panel"
                  >
                    <FiX className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                  </button>
                )}
              </div>
            )}

            {/* Close button when no header */}
            {!title && !subtitle && showCloseButton && (
              <div className="absolute right-4 top-4 z-10">
                <button
                  onClick={handleCloseClick}
                  disabled={preventClose}
                  className="p-2 rounded-lg bg-white dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 shadow-sm transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                  aria-label="Close panel"
                >
                  <FiX className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                </button>
              </div>
            )}

            {/* Scrollable Content */}
            <div className="flex-1 overflow-y-auto">
              <div className="p-6">
                {children}
              </div>
            </div>

            {/* Sticky Footer */}
            {footer && (
              <div className="sticky bottom-0 z-10 px-6 py-4 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 transition-colors duration-200">
                {footer}
              </div>
            )}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

/**
 * Hook to manage slide panel state
 * Uses the ScaleGrow pattern of tracking both open state and selected ID
 *
 * @example
 * const panel = useSlidePanel<string>();
 *
 * // Open panel with an ID
 * panel.open('job-123');
 *
 * // Check which ID is selected
 * if (panel.selectedId) {
 *   // Load data for panel.selectedId
 * }
 *
 * // Close panel
 * panel.close();
 */
export function useSlidePanel<T = string | number>(initialState = false) {
  const [isOpen, setIsOpen] = useState(initialState);
  const [selectedId, setSelectedId] = useState<T | null>(null);

  const open = (id?: T) => {
    if (id !== undefined) {
      setSelectedId(id);
    }
    setIsOpen(true);
  };

  const close = () => {
    setIsOpen(false);
    // Delay clearing selectedId to allow exit animation to complete
    setTimeout(() => setSelectedId(null), 300);
  };

  const toggle = (id?: T) => {
    if (isOpen) {
      close();
    } else {
      open(id);
    }
  };

  return {
    isOpen,
    selectedId,
    open,
    close,
    toggle,
    setSelectedId, // For manual control if needed
  };
}
