/**
 * Root Layout
 *
 * Main layout with navigation for the entire application.
 */
import React from 'react';
import Link from 'next/link';
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
      <body className="antialiased">
        <div className="min-h-screen flex flex-col">
          {/* Navigation Header */}
          <header className="bg-white shadow-sm border-b border-gray-200">
            <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between h-16">
                <div className="flex">
                  {/* Logo/Brand */}
                  <Link
                    href="/"
                    className="flex items-center px-2 text-gray-900 font-bold text-lg"
                  >
                    🎵 AI Background Channel Studio
                  </Link>

                  {/* Navigation Links */}
                  <div className="hidden sm:ml-6 sm:flex sm:space-x-4">
                    <Link
                      href="/channels"
                      className="inline-flex items-center px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50 rounded-md transition"
                    >
                      Channels
                    </Link>
                    <Link
                      href="/video-jobs"
                      className="inline-flex items-center px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50 rounded-md transition"
                    >
                      Video Jobs
                    </Link>
                  </div>
                </div>
              </div>
            </nav>
          </header>

          {/* Main Content */}
          <main className="flex-1">{children}</main>

          {/* Footer */}
          <footer className="bg-white border-t border-gray-200 mt-auto">
            <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
              <p className="text-center text-sm text-gray-500">
                AI Background Channel Studio - Powered by Claude Code
              </p>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
