# TypeScript Type Definitions

This directory contains TypeScript type definitions and interfaces for the frontend.

## Type Categories

### API Types
- `api.ts` - Generic API response types
- `channels.ts` - Channel-related types
- `video-jobs.ts` - Video job-related types
- `audio-tracks.ts` - Audio track types
- `images.ts` - Image/visual types

### UI Types
- `components.ts` - Component prop types
- `forms.ts` - Form data types
- `tables.ts` - Table configuration types

### Domain Types
```typescript
// Example: Channel type
export interface Channel {
  id: string;
  name: string;
  youtube_channel_id: string;
  brand_niche: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// Example: VideoJob status enum
export type VideoJobStatus =
  | 'planned'
  | 'generating_music'
  | 'generating_image'
  | 'rendering'
  | 'ready_for_export'
  | 'completed'
  | 'failed';
```

## Guidelines

- Match backend schema structures
- Use strict TypeScript mode
- Export all types/interfaces
- Document complex types with comments
- Use enums for fixed value sets
