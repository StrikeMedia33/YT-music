# Notification System

The notification system provides a comprehensive way to display real-time updates about video jobs, background tasks, and other system events to users.

## Features

- **Rich Notifications**: Support for different types (success, error, info, warning, progress)
- **Job Integration**: Special handling for video job notifications with job IDs and types
- **Progress Tracking**: Real-time progress bars for long-running tasks
- **Action Buttons**: Clickable actions that can navigate or trigger callbacks
- **Auto-dismissal**: Success notifications automatically dismiss after 5 seconds
- **Non-dismissible**: Important notifications can be marked as non-dismissible
- **Job Type Icons**: Visual indicators for music, image, video, and render jobs
- **Dark Mode Support**: All notifications work in both light and dark themes

## Usage

### Basic Notifications

```tsx
import { useNotifications } from '@/lib/hooks/useNotifications';

function MyComponent() {
  const { notifySuccess, notifyError, notifyInfo, notifyWarning } = useNotifications();

  const handleSuccess = () => {
    notifySuccess('Operation completed successfully!');
  };

  const handleError = () => {
    notifyError('Something went wrong!');
  };

  return (
    <button onClick={handleSuccess}>Complete Task</button>
  );
}
```

### Job Notifications

```tsx
import { useNotifications } from '@/lib/hooks/useNotifications';

function VideoJobComponent() {
  const { notifyJobComplete, notifyJobError, notifyJobProgress } = useNotifications();

  // Job completed
  const handleJobComplete = (jobId: string) => {
    notifyJobComplete(jobId, 'video', 'Video rendering completed!');
  };

  // Job error
  const handleJobError = (jobId: string) => {
    notifyJobError(jobId, 'video', 'Failed to render video');
  };

  // Job progress with progress bar
  const handleJobProgress = (jobId: string) => {
    notifyJobProgress(jobId, 'music', 'Generating music tracks...', 45);
  };
}
```

### Background Task Notifications

```tsx
import { useNotifications } from '@/lib/hooks/useNotifications';

function BackgroundTaskComponent() {
  const { notifyBackgroundTask } = useNotifications();

  const startBackgroundJob = () => {
    notifyBackgroundTask('Audio Processing', 'Processing 20 audio tracks in the background');
  };
}
```

### Advanced Usage with Actions

```tsx
import { useUIStore } from '@/lib/store/ui-store';

function AdvancedNotifications() {
  const { addNotification } = useUIStore();

  const notifyWithAction = () => {
    addNotification('success', 'Video is ready!', {
      jobId: 'job-123',
      jobType: 'video',
      action: {
        label: 'View Video',
        href: '/video-jobs/job-123',
      },
    });
  };

  const notifyWithCallback = () => {
    addNotification('info', 'Update available', {
      action: {
        label: 'Install Now',
        onClick: () => {
          console.log('Installing update...');
        },
      },
    });
  };
}
```

### Progress Updates

```tsx
import { useNotifications } from '@/lib/hooks/useNotifications';

function ProgressComponent() {
  const { notifyJobProgress, updateJobProgress } = useNotifications();

  const handleLongRunningTask = async () => {
    // Create initial progress notification
    const notificationId = notifyJobProgress(
      'job-123',
      'render',
      'Starting render...',
      0
    );

    // Simulate progress updates
    for (let i = 10; i <= 100; i += 10) {
      await new Promise(resolve => setTimeout(resolve, 1000));
      updateJobProgress(notificationId, i, `Rendering: ${i}% complete`);
    }
  };
}
```

### Video Job Polling Integration

The system includes a complete polling integration example:

```tsx
import { useState, useEffect } from 'react';
import { useVideoJobPolling } from '@/lib/hooks/useVideoJobPolling';
import { listVideoJobs, VideoJob } from '@/lib/api';

function VideoJobsPage() {
  const [jobs, setJobs] = useState<VideoJob[]>([]);

  // Fetch jobs
  useEffect(() => {
    async function loadJobs() {
      const data = await listVideoJobs();
      setJobs(data);
    }
    loadJobs();
  }, []);

  // Enable polling with notifications
  const { activeJobs, hasActiveJobs } = useVideoJobPolling(jobs, {
    interval: 5000, // Poll every 5 seconds
    enabled: true,
    onStatusChange: (change) => {
      console.log('Job status changed:', change);
      // Refresh jobs when status changes
      loadJobs();
    },
  });

  return (
    <div>
      {hasActiveJobs && (
        <p>Processing {activeJobs.length} jobs in the background</p>
      )}
      {/* Rest of your component */}
    </div>
  );
}
```

## Notification Types

- **`success`**: Green background, used for successful operations
- **`error`**: Red background, used for failures and errors
- **`warning`**: Yellow background, used for warnings and cautions
- **`info`**: Blue background, used for informational messages
- **`progress`**: Purple background, used for ongoing operations with progress

## Job Types

- **`video`**: Video generation jobs (🎥 icon)
- **`music`**: Music generation jobs (🎵 icon)
- **`image`**: Image/visual generation jobs (🖼️ icon)
- **`render`**: Video rendering jobs (🎬 icon)

## API Reference

### `useNotifications()` Hook

Returns an object with the following methods:

#### Job Notifications
- `notifyJobComplete(jobId, jobType, message?)` - Notify job completion
- `notifyJobError(jobId, jobType, error)` - Notify job error
- `notifyJobProgress(jobId, jobType, message, progress)` - Notify job progress (returns notification ID)
- `updateJobProgress(notificationId, progress, message?)` - Update progress notification

#### Background Tasks
- `notifyBackgroundTask(taskName, message?)` - Notify about background task

#### Generic Notifications
- `notifySuccess(message)` - Show success notification
- `notifyError(message)` - Show error notification
- `notifyInfo(message)` - Show info notification
- `notifyWarning(message)` - Show warning notification

#### Advanced
- `addNotification(type, message, options)` - Add custom notification with full options
- `updateNotification(id, updates)` - Update existing notification
- `removeNotification(id)` - Remove notification by ID

### `useVideoJobPolling()` Hook

Poll video jobs and automatically trigger notifications on status changes.

**Parameters:**
- `jobs: VideoJob[]` - Array of video jobs to monitor
- `options?: UseVideoJobPollingOptions`
  - `interval?: number` - Polling interval in ms (default: 5000)
  - `enabled?: boolean` - Enable/disable polling (default: true)
  - `onStatusChange?: (change) => void` - Callback on status change

**Returns:**
- `activeJobs: VideoJob[]` - List of jobs currently processing
- `hasActiveJobs: boolean` - Whether there are active jobs

## Store Access

For advanced usage, you can access the notification store directly:

```tsx
import { useUIStore } from '@/lib/store/ui-store';

function AdvancedComponent() {
  const {
    notifications,
    addNotification,
    updateNotification,
    removeNotification,
    clearNotifications
  } = useUIStore();

  // Direct access to all notifications
  console.log('Total notifications:', notifications.length);

  // Clear all notifications
  const handleClearAll = () => {
    clearNotifications();
  };
}
```

## Best Practices

1. **Use Specific Methods**: Prefer `notifyJobComplete()` over `addNotification()` for common patterns
2. **Progress Updates**: Use non-dismissible progress notifications for long tasks
3. **Error Details**: Include helpful error messages and provide "View Details" actions
4. **Background Tasks**: Notify users when tasks are running in the background
5. **Auto-dismiss**: Let success notifications auto-dismiss to avoid clutter
6. **Action Buttons**: Provide relevant actions (View Job, Retry, etc.) when appropriate
7. **Polling Intervals**: Use 5-10 second intervals for background job polling to balance responsiveness and API load

## Examples in the Codebase

- **TopBar Component** (`components/layout/TopBar.tsx`): Notification dropdown UI
- **Notification Hook** (`lib/hooks/useNotifications.ts`): Convenient notification methods
- **Video Job Polling** (`lib/hooks/useVideoJobPolling.ts`): Complete polling integration example
- **UI Store** (`lib/store/ui-store.ts`): Notification state management

## Future Enhancements

- [ ] Notification persistence (save to localStorage)
- [ ] Notification history view
- [ ] Sound/vibration for important notifications
- [ ] Desktop notifications (browser Notification API)
- [ ] Notification grouping by job
- [ ] Undo actions for certain notifications
