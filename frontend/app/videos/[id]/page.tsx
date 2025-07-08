'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { 
  Calendar, 
  Eye, 
  Share2, 
  Download, 
  Flag, 
  ThumbsUp, 
  Edit,
  Trash2,
  ExternalLink,
  Settings,
  BarChart3,
  ArrowLeft
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { VideoPlayer } from '@/components/video-player';
import { VideoCard } from '@/components/video-card';
import { PublicLinkModal } from '@/components/public-link-modal';
import { useAuthStore, useVideoStore, Video } from '@/lib/store';
import { toast } from 'sonner';

// Mock video data with enhanced details
const mockVideo: Video = {
  id: '1',
  title: 'Company Quarterly Results Presentation',
  description: `Comprehensive overview of Q4 performance and strategic initiatives for the upcoming year. This presentation covers:

• Financial performance and key metrics
• Strategic initiatives and roadmap
• Market expansion opportunities
• Team updates and organizational changes
• Q&A session with leadership

This session was recorded during our all-hands meeting and provides valuable insights into our company's direction and performance.

Key highlights include:
- 25% revenue growth year-over-year
- Expansion into 3 new markets
- Launch of innovative product features
- Team growth and new hires
- Sustainability initiatives

The presentation includes detailed financial charts, market analysis, and forward-looking statements that will help all team members understand our current position and future goals.`,
  duration: 1847, // 30:47
  thumbnail_url: 'https://images.pexels.com/photos/3183150/pexels-photo-3183150.jpeg',
  upload_date: '2024-01-15T10:00:00Z',
  view_count: 1243,
  status: 'ready',
  progress: 45,
  file_size: 856340000,
  metadata: {
    resolution: '1920x1080',
    codec: 'H.264',
    bitrate: 5000
  }
};

const mockRelatedVideos: Video[] = [
  {
    id: '2',
    title: 'Product Demo: New Features Overview',
    description: 'Detailed walkthrough of the latest product updates.',
    duration: 923,
    thumbnail_url: 'https://images.pexels.com/photos/3184306/pexels-photo-3184306.jpeg',
    upload_date: '2024-01-14T14:30:00Z',
    view_count: 856,
    status: 'ready',
    file_size: 445670000,
    metadata: { resolution: '1920x1080', codec: 'H.264', bitrate: 4000 }
  },
  {
    id: '3',
    title: 'Training Session: Security Best Practices',
    description: 'Essential security guidelines for all team members.',
    duration: 1456,
    thumbnail_url: 'https://images.pexels.com/photos/3184639/pexels-photo-3184639.jpeg',
    upload_date: '2024-01-13T09:15:00Z',
    view_count: 2103,
    status: 'ready',
    file_size: 698200000,
    metadata: { resolution: '1920x1080', codec: 'H.264', bitrate: 4500 }
  }
];

const mockAnalytics = {
  totalViews: 1243,
  uniqueViewers: 892,
  averageWatchTime: 1234,
  completionRate: 67.5,
  engagementScore: 8.4,
  viewsByDay: [
    { date: '2024-01-15', views: 234 },
    { date: '2024-01-16', views: 189 },
    { date: '2024-01-17', views: 156 },
    { date: '2024-01-18', views: 203 },
    { date: '2024-01-19', views: 178 },
    { date: '2024-01-20', views: 145 },
    { date: '2024-01-21', views: 138 }
  ]
};

export default function VideoDetailPage() {
  const params = useParams();
  const router = useRouter();
  const { user } = useAuthStore();
  const [video, setVideo] = useState<Video | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [progress, setProgress] = useState(0);
  const [showPublicLinkModal, setShowPublicLinkModal] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    if (!user) {
      router.push('/auth/login');
      return;
    }

    // Simulate loading video data
    setTimeout(() => {
      setVideo(mockVideo);
      setProgress(mockVideo.progress || 0);
      setIsLoading(false);
    }, 1000);
  }, [params.id, user, router]);

  const handleProgressUpdate = (newProgress: number) => {
    setProgress(newProgress);
    // In a real app, you would save this to the backend
    console.log(`Saving progress: ${newProgress}% for video ${params.id}`);
  };

  const handleDeleteVideo = () => {
    if (confirm('Are you sure you want to delete this video? This action cannot be undone.')) {
      // API call to delete video
      toast.success('Video deleted successfully');
      router.push('/admin/videos');
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatFileSize = (bytes: number) => {
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  };

  const formatDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const remainingSeconds = seconds % 60;
    
    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
    }
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  if (!user) {
    return null;
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto px-4 py-8">
          <div className="max-w-6xl mx-auto">
            <div className="aspect-video bg-muted rounded-lg animate-pulse mb-6" />
            <div className="space-y-4">
              <div className="h-8 bg-muted rounded animate-pulse" />
              <div className="h-4 bg-muted rounded w-3/4 animate-pulse" />
              <div className="h-4 bg-muted rounded w-1/2 animate-pulse" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!video) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-2">Video not found</h1>
          <p className="text-muted-foreground">The video you're looking for doesn't exist.</p>
          <Button onClick={() => router.push('/')} className="mt-4">
            Go Back Home
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          {/* Back Navigation */}
          <div className="mb-6">
            <Button variant="outline" onClick={() => router.back()}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
          </div>

          <div className="grid lg:grid-cols-3 gap-8">
            {/* Main Video Content */}
            <div className="lg:col-span-2 space-y-6">
              {/* Video Player */}
              <VideoPlayer
                src="/api/placeholder/video.mp4"
                poster={video.thumbnail_url}
                title={video.title}
                className="aspect-video"
                onProgress={handleProgressUpdate}
                initialProgress={progress}
              />

              {/* Video Info */}
              <div className="space-y-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h1 className="text-2xl font-bold mb-2">{video.title}</h1>
                    <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
                      <span className="flex items-center">
                        <Eye className="h-4 w-4 mr-1" />
                        {video.view_count.toLocaleString()} views
                      </span>
                      <span className="flex items-center">
                        <Calendar className="h-4 w-4 mr-1" />
                        {formatDate(video.upload_date)}
                      </span>
                      <Badge variant="outline">
                        {video.metadata.resolution}
                      </Badge>
                      <Badge variant="outline">
                        {video.metadata.codec}
                      </Badge>
                    </div>
                  </div>

                  {/* Admin Actions */}
                  {user.role === 'admin' && (
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setShowPublicLinkModal(true)}
                      >
                        <ExternalLink className="h-4 w-4 mr-2" />
                        Share
                      </Button>
                      <Link href={`/videos/${video.id}/edit`}>
                        <Button variant="outline" size="sm">
                          <Edit className="h-4 w-4 mr-2" />
                          Edit
                        </Button>
                      </Link>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={handleDeleteVideo}
                        className="text-destructive hover:text-destructive"
                      >
                        <Trash2 className="h-4 w-4 mr-2" />
                        Delete
                      </Button>
                    </div>
                  )}
                </div>

                <Separator />

                {/* Action Buttons */}
                <div className="flex flex-wrap gap-2">
                  <Button variant="outline" size="sm">
                    <ThumbsUp className="h-4 w-4 mr-2" />
                    Like
                  </Button>
                  <Button variant="outline" size="sm">
                    <Share2 className="h-4 w-4 mr-2" />
                    Share
                  </Button>
                  <Button variant="outline" size="sm">
                    <Download className="h-4 w-4 mr-2" />
                    Download
                  </Button>
                  <Button variant="outline" size="sm">
                    <Flag className="h-4 w-4 mr-2" />
                    Report
                  </Button>
                </div>

                <Separator />

                {/* Tabs for different content */}
                <Tabs value={activeTab} onValueChange={setActiveTab}>
                  <TabsList className="grid w-full grid-cols-3">
                    <TabsTrigger value="overview">Overview</TabsTrigger>
                    <TabsTrigger value="details">Details</TabsTrigger>
                    {user.role === 'admin' && (
                      <TabsTrigger value="analytics">Analytics</TabsTrigger>
                    )}
                  </TabsList>

                  <TabsContent value="overview" className="space-y-4">
                    <div>
                      <h3 className="font-semibold mb-3">Description</h3>
                      <div className="bg-muted/50 rounded-lg p-4">
                        <pre className="whitespace-pre-wrap text-sm text-muted-foreground font-sans">
                          {video.description}
                        </pre>
                      </div>
                    </div>
                  </TabsContent>

                  <TabsContent value="details" className="space-y-4">
                    <Card>
                      <CardHeader>
                        <CardTitle>Technical Details</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="grid sm:grid-cols-2 gap-4 text-sm">
                          <div className="space-y-2">
                            <div className="flex justify-between">
                              <span className="text-muted-foreground">Resolution:</span>
                              <span>{video.metadata.resolution}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-muted-foreground">Codec:</span>
                              <span>{video.metadata.codec}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-muted-foreground">Bitrate:</span>
                              <span>{video.metadata.bitrate} kbps</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-muted-foreground">Duration:</span>
                              <span>{formatDuration(video.duration)}</span>
                            </div>
                          </div>
                          <div className="space-y-2">
                            <div className="flex justify-between">
                              <span className="text-muted-foreground">File Size:</span>
                              <span>{formatFileSize(video.file_size)}</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-muted-foreground">Status:</span>
                              <Badge variant={video.status === 'ready' ? 'default' : 'secondary'}>
                                {video.status}
                              </Badge>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-muted-foreground">Progress:</span>
                              <span>{progress.toFixed(1)}%</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-muted-foreground">Upload Date:</span>
                              <span>{formatDate(video.upload_date)}</span>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </TabsContent>

                  {user.role === 'admin' && (
                    <TabsContent value="analytics" className="space-y-4">
                      <div className="grid md:grid-cols-2 gap-4">
                        <Card>
                          <CardHeader>
                            <CardTitle className="flex items-center">
                              <BarChart3 className="h-5 w-5 mr-2" />
                              View Statistics
                            </CardTitle>
                          </CardHeader>
                          <CardContent className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                              <div>
                                <p className="text-2xl font-bold">{mockAnalytics.totalViews}</p>
                                <p className="text-sm text-muted-foreground">Total Views</p>
                              </div>
                              <div>
                                <p className="text-2xl font-bold">{mockAnalytics.uniqueViewers}</p>
                                <p className="text-sm text-muted-foreground">Unique Viewers</p>
                              </div>
                              <div>
                                <p className="text-2xl font-bold">{formatDuration(mockAnalytics.averageWatchTime)}</p>
                                <p className="text-sm text-muted-foreground">Avg Watch Time</p>
                              </div>
                              <div>
                                <p className="text-2xl font-bold">{mockAnalytics.completionRate}%</p>
                                <p className="text-sm text-muted-foreground">Completion Rate</p>
                              </div>
                            </div>
                          </CardContent>
                        </Card>

                        <Card>
                          <CardHeader>
                            <CardTitle>Engagement</CardTitle>
                          </CardHeader>
                          <CardContent>
                            <div className="space-y-4">
                              <div>
                                <p className="text-3xl font-bold text-green-600">{mockAnalytics.engagementScore}</p>
                                <p className="text-sm text-muted-foreground">Engagement Score</p>
                              </div>
                              <div className="space-y-2">
                                <h4 className="font-medium">Recent Views</h4>
                                {mockAnalytics.viewsByDay.slice(-3).map((day) => (
                                  <div key={day.date} className="flex justify-between text-sm">
                                    <span>{new Date(day.date).toLocaleDateString()}</span>
                                    <span>{day.views} views</span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      </div>
                    </TabsContent>
                  )}
                </Tabs>
              </div>
            </div>

            {/* Sidebar - Related Videos */}
            <div className="space-y-6">
              <div>
                <h3 className="font-semibold mb-4">Related Videos</h3>
                <div className="space-y-4">
                  {mockRelatedVideos.map((relatedVideo) => (
                    <VideoCard
                      key={relatedVideo.id}
                      video={relatedVideo}
                      className="border-0 shadow-none bg-muted/30"
                    />
                  ))}
                </div>
              </div>

              {/* Up Next */}
              <Card>
                <CardHeader>
                  <CardTitle>Up Next</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-3">
                    Continue with the next video in the series
                  </p>
                  <VideoCard
                    video={mockRelatedVideos[0]}
                    className="border-0 shadow-none"
                  />
                  <Button className="w-full mt-3" size="sm">
                    Play Next
                  </Button>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>

      {/* Public Link Modal */}
      <PublicLinkModal
        isOpen={showPublicLinkModal}
        onClose={() => setShowPublicLinkModal(false)}
        videoId={video.id}
        videoTitle={video.title}
      />
    </div>
  );
}