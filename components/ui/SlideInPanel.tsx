/**
 * SlideInPanel Component
 *
 * A reusable slide-in panel component using Framer Motion for smooth animations.
 * Slides in from the right side of the screen as an overlay.
 *
 * Features:
 * - Smooth slide-in/out animations
 * - Backdrop overlay with click-to-close
 * - Escape key to close
 * - Responsive width (full width on mobile, fixed width on desktop)
 * - Scrollable content area
 * - Header with title and close button
 * - Optional footer for actions
 */
'use client';

import React, { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiX } from 'react-icons/fi';

export interface SlideInPanelProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  width?: 'sm' | 'md' | 'lg' | 'xl' | 'full';
}

const widthClasses = {
  sm: 'max-w-md',
  md: 'max-w-2xl',
  lg: 'max-w-4xl',
  xl: 'max-w-6xl',
  full: 'max-w-full',
};

export function SlideInPanel({
  isOpen,
  onClose,
  title,
  children,
  footer,
  width = 'lg',
}: SlideInPanelProps) {
  // Close on escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  // Prevent body scroll when panel is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }

    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 bg-black bg-opacity-50 z-40"
            onClick={onClose}
            aria-hidden="true"
          />

          {/* Panel */}
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 30, stiffness: 300 }}
            className={`fixed right-0 top-0 bottom-0 ${widthClasses[width]} w-full bg-white shadow-2xl z-50 flex flex-col`}
            role="dialog"
            aria-modal="true"
            aria-labelledby={title ? 'slide-panel-title' : undefined}
          >
            {/* Header */}
            {title && (
              <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 bg-gray-50">
                <h2
                  id="slide-panel-title"
                  className="text-xl font-semibold text-gray-900"
                >
                  {title}
                </h2>
                <button
                  onClick={onClose}
                  className="p-2 rounded-lg hover:bg-gray-200 transition-colors"
                  aria-label="Close panel"
                >
                  <FiX className="w-5 h-5 text-gray-600" />
                </button>
              </div>
            )}

            {/* No title but still need close button */}
            {!title && (
              <div className="absolute right-4 top-4 z-10">
                <button
                  onClick={onClose}
                  className="p-2 rounded-lg bg-white hover:bg-gray-100 shadow-sm transition-colors"
                  aria-label="Close panel"
                >
                  <FiX className="w-5 h-5 text-gray-600" />
                </button>
              </div>
            )}

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-6">
              {children}
            </div>

            {/* Footer */}
            {footer && (
              <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
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
 * Hook to manage slide-in panel state
 *
 * @example
 * const { isOpen, open, close } = useSlideInPanel();
 *
 * return (
 *   <>
 *     <button onClick={open}>Open Panel</button>
 *     <SlideInPanel isOpen={isOpen} onClose={close}>
 *       Content here
 *     </SlideInPanel>
 *   </>
 * );
 */
export function useSlideInPanel(initialState = false) {
  const [isOpen, setIsOpen] = React.useState(initialState);

  const open = React.useCallback(() => setIsOpen(true), []);
  const close = React.useCallback(() => setIsOpen(false), []);
  const toggle = React.useCallback(() => setIsOpen((prev) => !prev), []);

  return { isOpen, open, close, toggle };
}
