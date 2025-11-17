# Next.js App Router

This directory contains Next.js 14+ App Router pages for the frontend interface.

## Pages

- `page.tsx` - Home page / Dashboard
- `channels/page.tsx` - Channel list page
- `channels/[id]/page.tsx` - Channel detail page
- `video-jobs/page.tsx` - Video jobs list page
- `video-jobs/[id]/page.tsx` - Video job detail page
- `layout.tsx` - Root layout with navigation
- `error.tsx` - Error boundary
- `loading.tsx` - Loading states

## Structure

Each page should:
- Use server components by default
- Handle loading and error states
- Fetch data via API client from `/lib`
- Use shared components from `/components`
