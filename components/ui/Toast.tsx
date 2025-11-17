'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiCheckCircle, FiXCircle, FiAlertCircle, FiInfo, FiX } from 'react-icons/fi';
import { create } from 'zustand';

type ToastType = 'success' | 'error' | 'warning' | 'info';

interface Toast {
  id: string;
  type: ToastType;
  message: string;
  description?: string;
  duration?: number;
}

interface ToastStore {
  toasts: Toast[];
  addToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
}

export const useToastStore = create<ToastStore>((set) => ({
  toasts: [],
  addToast: (toast) => {
    const id = Math.random().toString(36).substring(2, 9);
    const newToast = { ...toast, id };
    set((state) => ({ toasts: [...state.toasts, newToast] }));

    // Auto-remove after duration
    const duration = toast.duration || 5000;
    setTimeout(() => {
      set((state) => ({ toasts: state.toasts.filter((t) => t.id !== id) }));
    }, duration);
  },
  removeToast: (id) => {
    set((state) => ({ toasts: state.toasts.filter((t) => t.id !== id) }));
  },
}));

const icons = {
  success: FiCheckCircle,
  error: FiXCircle,
  warning: FiAlertCircle,
  info: FiInfo,
};

const styles = {
  success: 'bg-green-50 border-green-200 text-green-900',
  error: 'bg-red-50 border-red-200 text-red-900',
  warning: 'bg-yellow-50 border-yellow-200 text-yellow-900',
  info: 'bg-blue-50 border-blue-200 text-blue-900',
};

const iconStyles = {
  success: 'text-green-500',
  error: 'text-red-500',
  warning: 'text-yellow-500',
  info: 'text-blue-500',
};

export function ToastContainer() {
  const { toasts, removeToast } = useToastStore();

  return (
    <div className="fixed top-4 right-4 z-50 space-y-3 max-w-md">
      <AnimatePresence>
        {toasts.map((toast) => {
          const Icon = icons[toast.type];
          return (
            <motion.div
              key={toast.id}
              initial={{ opacity: 0, y: -20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, x: 100, scale: 0.95 }}
              transition={{ duration: 0.2 }}
              className={`rounded-lg border shadow-lg p-4 pr-10 relative ${styles[toast.type]}`}
              role="alert"
              aria-live="assertive"
            >
              <button
                onClick={() => removeToast(toast.id)}
                className="absolute top-3 right-3 text-gray-400 hover:text-gray-600 transition"
                aria-label="Close notification"
              >
                <FiX className="w-4 h-4" />
              </button>
              <div className="flex items-start">
                <Icon className={`w-5 h-5 mt-0.5 mr-3 flex-shrink-0 ${iconStyles[toast.type]}`} aria-hidden="true" />
                <div>
                  <p className="font-semibold text-sm">{toast.message}</p>
                  {toast.description && (
                    <p className="text-sm mt-1 opacity-90">{toast.description}</p>
                  )}
                </div>
              </div>
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
}

// Usage helper
export function useToast() {
  const { addToast } = useToastStore();

  return {
    success: (message: string, description?: string) =>
      addToast({ type: 'success', message, description }),
    error: (message: string, description?: string) =>
      addToast({ type: 'error', message, description }),
    warning: (message: string, description?: string) =>
      addToast({ type: 'warning', message, description }),
    info: (message: string, description?: string) =>
      addToast({ type: 'info', message, description }),
  };
}
