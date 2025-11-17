/**
 * Root Layout
 *
 * Main layout with sidebar navigation and top bar.
 */
import React from 'react';
import { Sidebar } from '@/components/layout/Sidebar';
import { TopBar } from '@/components/layout/TopBar';
import { ToastContainer } from '@/components/ui';
import './globals.css';

export const metadata = {
  title: 'AI Background Channel Studio',
  description: 'Automated YouTube background music video generation',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased bg-gray-50">
        <div className="min-h-screen flex">
          {/* Sidebar Navigation */}
          <Sidebar />

          {/* Main Content Area */}
          <div className="flex-1 flex flex-col lg:ml-64">
            {/* Top Bar */}
            <TopBar />

            {/* Page Content */}
            <main className="flex-1 overflow-auto">
              {children}
            </main>
          </div>
        </div>

        {/* Global Toast Notifications */}
        <ToastContainer />
      </body>
    </html>
  );
}
