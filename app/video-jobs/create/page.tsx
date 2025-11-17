/**
 * Video Job Create Page
 *
 * Redirects to the video jobs list page where users can create jobs.
 * This maintains backward compatibility with any existing links.
 */
'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Loading } from '@/components/ui';

export default function CreateVideoJobPage() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to video jobs list page
    router.replace('/video-jobs');
  }, [router]);

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center">
      <Loading size="lg" message="Redirecting..." />
    </div>
  );
}
