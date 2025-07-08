'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ArrowLeft, Save, Upload, Trash2, Eye } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useAuthStore, Video } from '@/lib/store';
import { toast } from 'sonner';

const mockVideo: Video = {
  id: '1',
  title: 'Company Quarterly Results Presentation',
  description: `Comprehensive overview of Q4 performance and strategic initiatives for the upcoming year. This presentation covers:

• Financial performance and key metrics
• Strategic initiatives and roadmap
• Market expansion opportunities
• Team updates and organizational changes
• Q&A session with leadership`,
  duration: 1847,
  thumbnail_url: 'https://images.pexels.com/photos/3183150/pexels-photo-3183150.jpeg',
  upload_date: '2024-01-15T10:00:00Z',
  view_count: 1243,
  status: 'ready',
  file_size: 856340000,
  metadata: {
    resolution: '1920x1080',
    codec: 'H.264',
    bitrate: 5000
  }
};

const categories = [
  'Training',
  'Company Updates',
  'Product Demos',
  'Marketing',
  'Technical',
  'HR',
  'Finance',
  'General'
];

const tags = [
  'quarterly-results',
  'presentation',
  'company-update',
  'finance',
  'strategy',
  'leadership',
  'performance',
  'metrics'
];

export default function VideoEditPage() {
  const params = useParams();
  const router = useRouter();
  const { user } = useAuthStore();
  
  const [video, setVideo] = useState<Video | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isUploadingThumbnail, setIsUploadingThumbnail] = useState(false);
  
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: '',
    tags: [] as string[],
    isPublic: false,
    isFeatured: false,
    allowDownloads: true,
    allowComments: true,
    trackAnalytics: true
  });

  useEffect(() => {
    if (!user) {
      router.push('/auth/login');
      return;
    }
    
    if (user.role !== 'admin') {
      router.push('/');
      return;
    }

    // Simulate loading video data
    setTimeout(() => {
      setVideo(mockVideo);
      setFormData({
        title: mockVideo.title,
        description: mockVideo.description,
        category: 'Company Updates',
        tags: ['quarterly-results', 'presentation', 'company-update'],
        isPublic: false,
        isFeatured: true,
        allowDownloads: true,
        allowComments: true,
        trackAnalytics: true
      });
      setIsLoading(false);
    }, 1000);
  }, [params.id, user, router]);

  const handleSave = async () => {
    setIsSaving(true);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      toast.success('Video updated successfully');
      router.push(`/videos/${params.id}`);
    } catch (error) {
      toast.error('Failed to update video');
    } finally {
      setIsSaving(false);
    }
  };

  const handleThumbnailUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsUploadingThumbnail(true);
    
    try {
      // Simulate upload
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Update video thumbnail URL (in real app, this would come from API response)
      if (video) {
        setVideo({
          ...video,
          thumbnail_url: URL.createObjectURL(file)
        });
      }
      
      toast.success('Thumbnail updated successfully');
    } catch (error) {
      toast.error('Failed to upload thumbnail');
    } finally {
      setIsUploadingThumbnail(false);
    }
  };

  const handleTagToggle = (tag: string) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.includes(tag)
        ? prev.tags.filter(t => t !== tag)
        : [...prev.tags, tag]
    }));
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

  if (!user || user.role !== 'admin') {
    return null;
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto px-4 py-8">
          <div className="max-w-4xl mx-auto">
            <div className="space-y-6">
              <div className="h-8 bg-muted rounded animate-pulse" />
              <div className="h-64 bg-muted rounded animate-pulse" />
              <div className="h-32 bg-muted rounded animate-pulse" />
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
          <p className="text-muted-foreground">The video you're trying to edit doesn't exist.</p>
          <Button onClick={() => router.push('/admin/videos')} className="mt-4">
            Back to Videos
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button variant="outline" onClick={() => router.back()}>
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back
              </Button>
              <div>
                <h1 className="text-3xl font-bold">Edit Video</h1>
                <p className="text-muted-foreground">
                  Update video information and settings
                </p>
              </div>
            </div>
            
            <div className="flex space-x-2">
              <Button variant="outline" asChild>
                <a href={`/videos/${video.id}`} target="_blank">
                  <Eye className="h-4 w-4 mr-2" />
                  Preview
                </a>
              </Button>
              <Button onClick={handleSave} disabled={isSaving}>
                {isSaving ? (
                  <div className="flex items-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Saving...
                  </div>
                ) : (
                  <>
                    <Save className="h-4 w-4 mr-2" />
                    Save Changes
                  </>
                )}
              </Button>
            </div>
          </div>

          <div className="grid lg:grid-cols-3 gap-6">
            {/* Main Form */}
            <div className="lg:col-span-2 space-y-6">
              {/* Basic Information */}
              <Card>
                <CardHeader>
                  <CardTitle>Basic Information</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="title">Title *</Label>
                    <Input
                      id="title"
                      value={formData.title}
                      onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                      placeholder="Enter video title"
                      maxLength={200}
                    />
                    <p className="text-xs text-muted-foreground">
                      {formData.title.length}/200 characters
                    </p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="description">Description</Label>
                    <Textarea
                      id="description"
                      value={formData.description}
                      onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                      placeholder="Enter video description"
                      rows={6}
                      className="resize-none"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="category">Category</Label>
                    <Select
                      value={formData.category}
                      onValueChange={(value) => setFormData(prev => ({ ...prev, category: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select a category" />
                      </SelectTrigger>
                      <SelectContent>
                        {categories.map((category) => (
                          <SelectItem key={category} value={category}>
                            {category}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label>Tags</Label>
                    <div className="flex flex-wrap gap-2">
                      {tags.map((tag) => (
                        <Badge
                          key={tag}
                          variant={formData.tags.includes(tag) ? 'default' : 'outline'}
                          className="cursor-pointer"
                          onClick={() => handleTagToggle(tag)}
                        >
                          {tag}
                        </Badge>
                      ))}
                    </div>
                    <p className="text-xs text-muted-foreground">
                      Click tags to add or remove them
                    </p>
                  </div>
                </CardContent>
              </Card>

              {/* Visibility Settings */}
              <Card>
                <CardHeader>
                  <CardTitle>Visibility & Access</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Public Video</Label>
                      <p className="text-sm text-muted-foreground">
                        Make this video visible to all users
                      </p>
                    </div>
                    <Switch
                      checked={formData.isPublic}
                      onCheckedChange={(checked) => setFormData(prev => ({ ...prev, isPublic: checked }))}
                    />
                  </div>

                  <Separator />

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Featured Video</Label>
                      <p className="text-sm text-muted-foreground">
                        Show this video in featured sections
                      </p>
                    </div>
                    <Switch
                      checked={formData.isFeatured}
                      onCheckedChange={(checked) => setFormData(prev => ({ ...prev, isFeatured: checked }))}
                    />
                  </div>
                </CardContent>
              </Card>

              {/* Advanced Settings */}
              <Card>
                <CardHeader>
                  <CardTitle>Advanced Settings</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Allow Downloads</Label>
                      <p className="text-sm text-muted-foreground">
                        Users can download this video file
                      </p>
                    </div>
                    <Switch
                      checked={formData.allowDownloads}
                      onCheckedChange={(checked) => setFormData(prev => ({ ...prev, allowDownloads: checked }))}
                    />
                  </div>

                  <Separator />

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Enable Comments</Label>
                      <p className="text-sm text-muted-foreground">
                        Allow users to comment on this video
                      </p>
                    </div>
                    <Switch
                      checked={formData.allowComments}
                      onCheckedChange={(checked) => setFormData(prev => ({ ...prev, allowComments: checked }))}
                    />
                  </div>

                  <Separator />

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Analytics Tracking</Label>
                      <p className="text-sm text-muted-foreground">
                        Track viewing analytics for this video
                      </p>
                    </div>
                    <Switch
                      checked={formData.trackAnalytics}
                      onCheckedChange={(checked) => setFormData(prev => ({ ...prev, trackAnalytics: checked }))}
                    />
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Thumbnail Management */}
              <Card>
                <CardHeader>
                  <CardTitle>Thumbnail</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="aspect-video relative overflow-hidden rounded-lg border">
                    <img
                      src={video.thumbnail_url}
                      alt={video.title}
                      className="w-full h-full object-cover"
                    />
                    {isUploadingThumbnail && (
                      <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
                      </div>
                    )}
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="thumbnail-upload">Upload Custom Thumbnail</Label>
                    <Input
                      id="thumbnail-upload"
                      type="file"
                      accept="image/*"
                      onChange={handleThumbnailUpload}
                      disabled={isUploadingThumbnail}
                    />
                    <p className="text-xs text-muted-foreground">
                      Recommended: 1920x1080 pixels, JPG or PNG
                    </p>
                  </div>

                  <Button
                    variant="outline"
                    className="w-full"
                    disabled={isUploadingThumbnail}
                  >
                    <Upload className="h-4 w-4 mr-2" />
                    Generate from Video
                  </Button>
                </CardContent>
              </Card>

              {/* Video Information */}
              <Card>
                <CardHeader>
                  <CardTitle>Video Information</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Duration:</span>
                    <span>{formatDuration(video.duration)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">File Size:</span>
                    <span>{formatFileSize(video.file_size)}</span>
                  </div>
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
                    <span className="text-muted-foreground">Views:</span>
                    <span>{video.view_count.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Status:</span>
                    <Badge variant={video.status === 'ready' ? 'default' : 'secondary'}>
                      {video.status}
                    </Badge>
                  </div>
                </CardContent>
              </Card>

              {/* Danger Zone */}
              <Card className="border-destructive">
                <CardHeader>
                  <CardTitle className="text-destructive">Danger Zone</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-4">
                    Once you delete a video, there is no going back. Please be certain.
                  </p>
                  <Button
                    variant="destructive"
                    className="w-full"
                    onClick={() => {
                      if (confirm('Are you sure you want to delete this video? This action cannot be undone.')) {
                        toast.success('Video deleted successfully');
                        router.push('/admin/videos');
                      }
                    }}
                  >
                    <Trash2 className="h-4 w-4 mr-2" />
                    Delete Video
                  </Button>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}