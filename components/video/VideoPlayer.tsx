/**
 * Video Player Component
 *
 * Preview and download completed videos.
 */
'use client';

import React, { useRef, useState } from 'react';
import { motion } from 'framer-motion';
import {
  FiDownload,
  FiExternalLink,
  FiCopy,
  FiCheckCircle,
  FiPlay,
  FiPause,
  FiVolume2,
  FiVolumeX,
} from 'react-icons/fi';
import { Button } from '@/components/ui';

interface VideoPlayerProps {
  videoPath: string;
  title: string;
  duration?: number;
  metadata?: {
    title: string;
    description: string;
    tags: string[];
  };
}

export function VideoPlayer({
  videoPath,
  title,
  duration,
  metadata,
}: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [videoDuration, setVideoDuration] = useState(duration || 0);
  const [copied, setCopied] = useState(false);

  const togglePlay = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const toggleMute = () => {
    if (videoRef.current) {
      videoRef.current.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      setCurrentTime(videoRef.current.currentTime);
    }
  };

  const handleLoadedMetadata = () => {
    if (videoRef.current) {
      setVideoDuration(videoRef.current.duration);
    }
  };

  const handleDownload = () => {
    // Create a download link for the video
    const link = document.createElement('a');
    link.href = `/api/video-jobs/download?path=${encodeURIComponent(videoPath)}`;
    link.download = `${title}.mp4`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const copyPath = () => {
    navigator.clipboard.writeText(videoPath);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${String(secs).padStart(2, '0')}`;
  };

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      {/* Video Player */}
      <div className="relative bg-black aspect-video">
        <video
          ref={videoRef}
          className="w-full h-full"
          onTimeUpdate={handleTimeUpdate}
          onLoadedMetadata={handleLoadedMetadata}
          onEnded={() => setIsPlaying(false)}
          poster="/placeholder-video.jpg"
        >
          <source src={`/api/video-jobs/stream?path=${encodeURIComponent(videoPath)}`} type="video/mp4" />
          Your browser does not support the video tag.
        </video>

        {/* Play/Pause Overlay */}
        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
          onClick={togglePlay}
          className="absolute inset-0 flex items-center justify-center bg-black bg-opacity-20 hover:bg-opacity-30 transition"
        >
          {!isPlaying && (
            <div className="w-20 h-20 bg-white bg-opacity-90 rounded-full flex items-center justify-center">
              <FiPlay className="w-10 h-10 text-gray-900 ml-1" />
            </div>
          )}
        </motion.button>

        {/* Controls */}
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black to-transparent p-4">
          <div className="flex items-center space-x-4">
            <button
              onClick={togglePlay}
              className="text-white hover:text-gray-300 transition"
            >
              {isPlaying ? (
                <FiPause className="w-6 h-6" />
              ) : (
                <FiPlay className="w-6 h-6" />
              )}
            </button>

            <button
              onClick={toggleMute}
              className="text-white hover:text-gray-300 transition"
            >
              {isMuted ? (
                <FiVolumeX className="w-6 h-6" />
              ) : (
                <FiVolume2 className="w-6 h-6" />
              )}
            </button>

            <div className="flex-1 flex items-center space-x-3">
              <span className="text-white text-sm font-mono">
                {formatTime(currentTime)}
              </span>
              <div className="flex-1 h-1 bg-gray-600 rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-white"
                  initial={{ width: 0 }}
                  animate={{
                    width: `${(currentTime / videoDuration) * 100}%`,
                  }}
                  transition={{ duration: 0.1 }}
                />
              </div>
              <span className="text-white text-sm font-mono">
                {formatTime(videoDuration)}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Video Info and Actions */}
      <div className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
            {metadata && (
              <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                {metadata.description.split('\n')[0]}
              </p>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap gap-3">
          <Button onClick={handleDownload}>
            <FiDownload className="w-4 h-4 mr-2" />
            Download Video
          </Button>
          <Button variant="outline" onClick={copyPath}>
            {copied ? (
              <>
                <FiCheckCircle className="w-4 h-4 mr-2 text-green-600" />
                Copied!
              </>
            ) : (
              <>
                <FiCopy className="w-4 h-4 mr-2" />
                Copy Path
              </>
            )}
          </Button>
          <Button variant="outline" disabled>
            <FiExternalLink className="w-4 h-4 mr-2" />
            Upload to YouTube
            <span className="ml-2 text-xs bg-gray-200 px-2 py-0.5 rounded">
              Coming Soon
            </span>
          </Button>
        </div>

        {/* File Path */}
        <div className="mt-4 p-3 bg-gray-50 rounded-lg">
          <p className="text-xs text-gray-500 mb-1">Local File Path</p>
          <p className="text-sm text-gray-900 font-mono break-all">
            {videoPath}
          </p>
        </div>

        {/* Metadata Preview */}
        {metadata && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <h4 className="text-sm font-medium text-gray-900 mb-2">
              Generated Metadata
            </h4>
            <div className="space-y-2">
              <div>
                <p className="text-xs text-gray-500">Title</p>
                <p className="text-sm text-gray-900">{metadata.title}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">Tags</p>
                <div className="flex flex-wrap gap-2 mt-1">
                  {metadata.tags.slice(0, 5).map((tag, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs"
                    >
                      {tag}
                    </span>
                  ))}
                  {metadata.tags.length > 5 && (
                    <span className="text-xs text-gray-500">
                      +{metadata.tags.length - 5} more
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
