'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Search, Filter, SortAsc, Grid3X3, List, Calendar, Eye, Clock } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { VideoCard } from '@/components/video-card';
import { useAuthStore, useVideoStore, Video } from '@/lib/store';

// Mock search data
const mockAllVideos: Video[] = [
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
    status: 'ready',
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
    description: 'Key moments from our annual team building activities and workshops.',
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
    status: 'ready',
    file_size: 534120000,
    metadata: { resolution: '1920x1080', codec: 'H.264', bitrate: 4200 }
  },
  {
    id: '6',
    title: 'CEO Town Hall: Vision 2024',
    description: 'Strategic vision and goals for the upcoming year, featuring Q&A session.',
    duration: 2134,
    thumbnail_url: 'https://images.pexels.com/photos/3184287/pexels-photo-3184287.jpeg',
    upload_date: '2024-01-10T10:00:00Z',
    view_count: 4521,
    status: 'ready',
    file_size: 1024500000,
    metadata: { resolution: '1920x1080', codec: 'H.264', bitrate: 5500 }
  },
  {
    id: '7',
    title: 'Technical Deep Dive: System Architecture',
    description: 'Comprehensive overview of our platform architecture and scalability solutions.',
    duration: 1789,
    thumbnail_url: 'https://images.pexels.com/photos/3184418/pexels-photo-3184418.jpeg',
    upload_date: '2024-01-09T15:30:00Z',
    view_count: 3456,
    status: 'ready',
    file_size: 867300000,
    metadata: { resolution: '1920x1080', codec: 'H.264', bitrate: 5000 }
  },
  {
    id: '8',
    title: 'Marketing Campaign Results Analysis',
    description: 'Data-driven insights from our latest marketing campaigns and ROI analysis.',
    duration: 967,
    thumbnail_url: 'https://images.pexels.com/photos/3184357/pexels-photo-3184357.jpeg',
    upload_date: '2024-01-08T13:15:00Z',
    view_count: 2987,
    status: 'ready',
    file_size: 467800000,
    metadata: { resolution: '1920x1080', codec: 'H.264', bitrate: 4000 }
  }
];

export default function SearchPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user } = useAuthStore();
  const { searchQuery, setSearchQuery } = useVideoStore();
  
  const [videos, setVideos] = useState<Video[]>([]);
  const [filteredVideos, setFilteredVideos] = useState<Video[]>([]);
  const [localSearchQuery, setLocalSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('upload_date');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!user) {
      router.push('/auth/login');
      return;
    }

    // Get query from URL
    const urlQuery = searchParams.get('q') || '';
    const urlSort = searchParams.get('sort') || 'upload_date';
    
    setLocalSearchQuery(urlQuery);
    setSortBy(urlSort);
    setSearchQuery(urlQuery);

    // Simulate loading videos
    setTimeout(() => {
      setVideos(mockAllVideos);
      setIsLoading(false);
    }, 1000);
  }, [user, router, searchParams, setSearchQuery]);

  useEffect(() => {
    let filtered = [...videos];

    // Filter by search query
    if (localSearchQuery) {
      filtered = filtered.filter(video =>
        video.title.toLowerCase().includes(localSearchQuery.toLowerCase()) ||
        video.description.toLowerCase().includes(localSearchQuery.toLowerCase())
      );
    }

    // Sort videos
    switch (sortBy) {
      case 'upload_date':
        filtered.sort((a, b) => new Date(b.upload_date).getTime() - new Date(a.upload_date).getTime());
        break;
      case 'view_count':
        filtered.sort((a, b) => b.view_count - a.view_count);
        break;
      case 'duration':
        filtered.sort((a, b) => b.duration - a.duration);
        break;
      case 'title':
        filtered.sort((a, b) => a.title.localeCompare(b.title));
        break;
    }

    setFilteredVideos(filtered);
  }, [videos, localSearchQuery, sortBy]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    const params = new URLSearchParams();
    if (localSearchQuery) params.set('q', localSearchQuery);
    if (sortBy !== 'upload_date') params.set('sort', sortBy);
    
    router.push(`/search?${params.toString()}`);
    setSearchQuery(localSearchQuery);
  };

  const getSortLabel = (value: string) => {
    switch (value) {
      case 'upload_date': return 'Latest';
      case 'view_count': return 'Most Popular';
      case 'duration': return 'Longest';
      case 'title': return 'Alphabetical';
      default: return 'Latest';
    }
  };

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <div className="space-y-6">
          {/* Header */}
          <div>
            <h1 className="text-3xl font-bold">Browse Videos</h1>
            <p className="text-muted-foreground mt-1">
              Discover and search through our video library
            </p>
          </div>

          {/* Search and Filters */}
          <Card>
            <CardContent className="p-6">
              <form onSubmit={handleSearch} className="space-y-4">
                <div className="flex flex-col md:flex-row gap-4">
                  <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Search videos..."
                      value={localSearchQuery}
                      onChange={(e) => setLocalSearchQuery(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                  <Button type="submit">Search</Button>
                </div>
              </form>

              <div className="flex flex-col md:flex-row md:items-center md:justify-between mt-4 gap-4">
                <div className="flex items-center space-x-2">
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="outline">
                        <SortAsc className="h-4 w-4 mr-2" />
                        Sort: {getSortLabel(sortBy)}
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent>
                      <DropdownMenuItem onClick={() => setSortBy('upload_date')}>
                        <Calendar className="h-4 w-4 mr-2" />
                        Latest
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => setSortBy('view_count')}>
                        <Eye className="h-4 w-4 mr-2" />
                        Most Popular
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => setSortBy('duration')}>
                        <Clock className="h-4 w-4 mr-2" />
                        Longest
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => setSortBy('title')}>
                        <Filter className="h-4 w-4 mr-2" />
                        Alphabetical
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

          {/* Results Count */}
          {!isLoading && (
            <div className="flex items-center justify-between">
              <p className="text-muted-foreground">
                {filteredVideos.length} video{filteredVideos.length !== 1 ? 's' : ''} found
                {localSearchQuery && ` for "${localSearchQuery}"`}
              </p>
            </div>
          )}

          {/* Video Grid/List */}
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
          ) : filteredVideos.length > 0 ? (
            <div className={cn(
              viewMode === 'grid' 
                ? 'grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6'
                : 'space-y-4'
            )}>
              {filteredVideos.map((video) => (
                <VideoCard
                  key={video.id}
                  video={video}
                  className={viewMode === 'list' ? 'flex-row' : ''}
                />
              ))}
            </div>
          ) : (
            <Card>
              <CardContent className="p-12 text-center">
                <div className="space-y-4">
                  <div className="mx-auto w-12 h-12 bg-muted rounded-full flex items-center justify-center">
                    <Search className="h-6 w-6 text-muted-foreground" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold">No videos found</h3>
                    <p className="text-muted-foreground">
                      {localSearchQuery 
                        ? `No videos match your search for "${localSearchQuery}"`
                        : 'No videos available'
                      }
                    </p>
                  </div>
                  <Button 
                    variant="outline"
                    onClick={() => {
                      setLocalSearchQuery('');
                      setSearchQuery('');
                      router.push('/search');
                    }}
                  >
                    Clear Search
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}

function cn(...classes: string[]) {
  return classes.filter(Boolean).join(' ');
}