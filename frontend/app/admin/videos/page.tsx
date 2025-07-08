'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { 
  Search, 
  Filter, 
  Upload, 
  MoreVertical, 
  Edit, 
  Trash2, 
  Eye,
  Download,
  Grid3X3,
  List
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from '@/components/ui/dropdown-menu';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { VideoCard } from '@/components/video-card';
import { useAuthStore, Video } from '@/lib/store';
import { toast } from 'sonner';

// Mock video data
const mockVideos: Video[] = [
  {
    id: '1',
    title: 'Company Quarterly Results Presentation',
    description: 'Comprehensive overview of Q4 performance and strategic initiatives.',
    duration: 1847,
    thumbnail_url: 'https://images.pexels.com/photos/3183150/pexels-photo-3183150.jpeg',
    upload_date: '2024-01-15T10:00:00Z',
    view_count: 1243,
    status: 'ready',
    file_size: 856340000,
    metadata: { resolution: '1920x1080', codec: 'H.264', bitrate: 5000 }
  },
  {
    id: '2',
    title: 'Product Demo: New Features Overview',
    description: 'Detailed walkthrough of the latest product updates and features.',
    duration: 923,
    thumbnail_url: 'https://images.pexels.com/photos/3184306/pexels-photo-3184306.jpeg',
    upload_date: '2024-01-14T14:30:00Z',
    view_count: 856,
    status: 'processing',
    file_size: 445670000,
    metadata: { resolution: '1920x1080', codec: 'H.264', bitrate: 4000 }
  },
  {
    id: '3',
    title: 'Training Session: Security Best Practices',
    description: 'Essential security guidelines and protocols for all team members.',
    duration: 1456,
    thumbnail_url: 'https://images.pexels.com/photos/3184639/pexels-photo-3184639.jpeg',
    upload_date: '2024-01-13T09:15:00Z',
    view_count: 2103,
    status: 'ready',
    file_size: 698200000,
    metadata: { resolution: '1920x1080', codec: 'H.264', bitrate: 4500 }
  },
  {
    id: '4',
    title: 'Team Building Workshop Highlights',
    description: 'Key moments from our annual team building activities.',
    duration: 734,
    thumbnail_url: 'https://images.pexels.com/photos/3184338/pexels-photo-3184338.jpeg',
    upload_date: '2024-01-12T16:45:00Z',
    view_count: 567,
    status: 'ready',
    file_size: 356890000,
    metadata: { resolution: '1920x1080', codec: 'H.264', bitrate: 3500 }
  },
  {
    id: '5',
    title: 'Customer Success Stories',
    description: 'Inspiring testimonials and case studies from our valued customers.',
    duration: 1124,
    thumbnail_url: 'https://images.pexels.com/photos/3184465/pexels-photo-3184465.jpeg',
    upload_date: '2024-01-11T11:20:00Z',
    view_count: 1876,
    status: 'failed',
    file_size: 534120000,
    metadata: { resolution: '1920x1080', codec: 'H.264', bitrate: 4200 }
  }
];

export default function AdminVideosPage() {
  const router = useRouter();
  const { user } = useAuthStore();
  const [videos, setVideos] = useState<Video[]>([]);
  const [filteredVideos, setFilteredVideos] = useState<Video[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!user) {
      router.push('/auth/login');
      return;
    }
    
    if (user.role !== 'admin') {
      router.push('/');
      return;
    }

    // Simulate loading videos
    setTimeout(() => {
      setVideos(mockVideos);
      setFilteredVideos(mockVideos);
      setIsLoading(false);
    }, 1000);
  }, [user, router]);

  useEffect(() => {
    let filtered = videos;

    // Filter by search query
    if (searchQuery) {
      filtered = filtered.filter(video =>
        video.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        video.description.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Filter by status
    if (statusFilter !== 'all') {
      filtered = filtered.filter(video => video.status === statusFilter);
    }

    setFilteredVideos(filtered);
  }, [videos, searchQuery, statusFilter]);

  const handleDeleteVideo = (id: string) => {
    setVideos(prev => prev.filter(video => video.id !== id));
    toast.success('Video deleted successfully');
  };

  const handleEditVideo = (id: string) => {
    router.push(`/admin/videos/edit/${id}`);
  };

  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const formatFileSize = (bytes: number) => {
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ready': return 'default';
      case 'processing': return 'secondary';
      case 'failed': return 'destructive';
      default: return 'outline';
    }
  };

  if (!user || user.role !== 'admin') {
    return null;
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <div className="space-y-6">
          {/* Header */}
          <div className="flex flex-col md:flex-row md:items-center md:justify-between">
            <div>
              <h1 className="text-3xl font-bold">Video Management</h1>
              <p className="text-muted-foreground mt-1">
                Manage your video library and content
              </p>
            </div>
            <Link href="/admin/videos/upload">
              <Button>
                <Upload className="h-4 w-4 mr-2" />
                Upload Video
              </Button>
            </Link>
          </div>

          {/* Filters and Search */}
          <Card>
            <CardContent className="p-6">
              <div className="flex flex-col md:flex-row gap-4 md:items-center md:justify-between">
                <div className="flex flex-col sm:flex-row gap-4 flex-1">
                  <div className="relative flex-1 max-w-md">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Search videos..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                  
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="outline">
                        <Filter className="h-4 w-4 mr-2" />
                        Status: {statusFilter === 'all' ? 'All' : statusFilter}
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent>
                      <DropdownMenuItem onClick={() => setStatusFilter('all')}>
                        All
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => setStatusFilter('ready')}>
                        Ready
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => setStatusFilter('processing')}>
                        Processing
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => setStatusFilter('failed')}>
                        Failed
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>

                <div className="flex items-center space-x-2">
                  <Button
                    variant={viewMode === 'grid' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setViewMode('grid')}
                  >
                    <Grid3X3 className="h-4 w-4" />
                  </Button>
                  <Button
                    variant={viewMode === 'list' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setViewMode('list')}
                  >
                    <List className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Video Statistics */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-4">
                <div className="text-2xl font-bold">{videos.length}</div>
                <p className="text-xs text-muted-foreground">Total Videos</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="text-2xl font-bold">
                  {videos.filter(v => v.status === 'ready').length}
                </div>
                <p className="text-xs text-muted-foreground">Ready</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="text-2xl font-bold">
                  {videos.filter(v => v.status === 'processing').length}
                </div>
                <p className="text-xs text-muted-foreground">Processing</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="text-2xl font-bold">
                  {videos.reduce((sum, v) => sum + v.view_count, 0).toLocaleString()}
                </div>
                <p className="text-xs text-muted-foreground">Total Views</p>
              </CardContent>
            </Card>
          </div>

          {/* Video Content */}
          {isLoading ? (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {[...Array(8)].map((_, i) => (
                <Card key={i} className="overflow-hidden">
                  <div className="aspect-video bg-muted animate-pulse" />
                  <CardContent className="p-4">
                    <div className="space-y-2">
                      <div className="h-4 bg-muted rounded animate-pulse" />
                      <div className="h-3 bg-muted rounded w-3/4 animate-pulse" />
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : viewMode === 'grid' ? (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {filteredVideos.map((video) => (
                <VideoCard
                  key={video.id}
                  video={video}
                  showActions={true}
                  onDelete={handleDeleteVideo}
                  onEdit={handleEditVideo}
                />
              ))}
            </div>
          ) : (
            <Card>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Video</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Views</TableHead>
                    <TableHead>Duration</TableHead>
                    <TableHead>Size</TableHead>
                    <TableHead>Upload Date</TableHead>
                    <TableHead className="w-[100px]">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredVideos.map((video) => (
                    <TableRow key={video.id}>
                      <TableCell>
                        <div className="flex items-center space-x-3">
                          <img
                            src={video.thumbnail_url}
                            alt={video.title}
                            className="w-16 h-10 object-cover rounded"
                          />
                          <div>
                            <p className="font-medium">{video.title}</p>
                            <p className="text-sm text-muted-foreground truncate max-w-48">
                              {video.description}
                            </p>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant={getStatusColor(video.status)}>
                          {video.status}
                        </Badge>
                      </TableCell>
                      <TableCell>{video.view_count.toLocaleString()}</TableCell>
                      <TableCell>{formatDuration(video.duration)}</TableCell>
                      <TableCell>{formatFileSize(video.file_size)}</TableCell>
                      <TableCell>{formatDate(video.upload_date)}</TableCell>
                      <TableCell>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="sm">
                              <MoreVertical className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem asChild>
                              <Link href={`/watch/${video.id}`}>
                                <Eye className="h-4 w-4 mr-2" />
                                View
                              </Link>
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleEditVideo(video.id)}>
                              <Edit className="h-4 w-4 mr-2" />
                              Edit
                            </DropdownMenuItem>
                            <DropdownMenuItem>
                              <Download className="h-4 w-4 mr-2" />
                              Download
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem 
                              onClick={() => handleDeleteVideo(video.id)}
                              className="text-destructive"
                            >
                              <Trash2 className="h-4 w-4 mr-2" />
                              Delete
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Card>
          )}

          {filteredVideos.length === 0 && !isLoading && (
            <Card>
              <CardContent className="p-12 text-center">
                <div className="space-y-4">
                  <div className="mx-auto w-12 h-12 bg-muted rounded-full flex items-center justify-center">
                    <Search className="h-6 w-6 text-muted-foreground" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold">No videos found</h3>
                    <p className="text-muted-foreground">
                      {searchQuery || statusFilter !== 'all'
                        ? 'Try adjusting your search or filters'
                        : 'Upload your first video to get started'
                      }
                    </p>
                  </div>
                  <Link href="/admin/videos/upload">
                    <Button>
                      <Upload className="h-4 w-4 mr-2" />
                      Upload Video
                    </Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}