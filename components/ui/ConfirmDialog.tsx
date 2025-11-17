'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiAlertTriangle } from 'react-icons/fi';
import { Button } from './Button';

interface ConfirmDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  description: string;
  confirmText?: string;
  cancelText?: string;
  variant?: 'danger' | 'warning' | 'info';
  loading?: boolean;
}

export function ConfirmDialog({
  isOpen,
  onClose,
  onConfirm,
  title,
  description,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  variant = 'warning',
  loading = false,
}: ConfirmDialogProps) {
  if (!isOpen) return null;

  const handleConfirm = () => {
    onConfirm();
    if (!loading) {
      onClose();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      onClose();
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black bg-opacity-50 z-50"
            aria-hidden="true"
          />

          {/* Dialog */}
          <div
            className="fixed inset-0 z-50 flex items-center justify-center p-4"
            onKeyDown={handleKeyDown}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="bg-white rounded-xl shadow-2xl max-w-md w-full p-6"
              role="alertdialog"
              aria-modal="true"
              aria-labelledby="dialog-title"
              aria-describedby="dialog-description"
            >
              <div className="flex items-start mb-4">
                <div className={`
                  flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center
                  ${variant === 'danger' ? 'bg-red-100' : ''}
                  ${variant === 'warning' ? 'bg-yellow-100' : ''}
                  ${variant === 'info' ? 'bg-blue-100' : ''}
                `}>
                  <FiAlertTriangle className={`
                    w-6 h-6
                    ${variant === 'danger' ? 'text-red-600' : ''}
                    ${variant === 'warning' ? 'text-yellow-600' : ''}
                    ${variant === 'info' ? 'text-blue-600' : ''}
                  `} aria-hidden="true" />
                </div>
                <div className="ml-4 flex-1">
                  <h3 id="dialog-title" className="text-lg font-semibold text-gray-900 mb-2">
                    {title}
                  </h3>
                  <p id="dialog-description" className="text-sm text-gray-600">
                    {description}
                  </p>
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <Button
                  variant="secondary"
                  onClick={onClose}
                  className="flex-1"
                  disabled={loading}
                >
                  {cancelText}
                </Button>
                <Button
                  variant={variant === 'danger' ? 'danger' : 'primary'}
                  onClick={handleConfirm}
                  className="flex-1"
                  loading={loading}
                >
                  {confirmText}
                </Button>
              </div>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
}

export type { ConfirmDialogProps };
