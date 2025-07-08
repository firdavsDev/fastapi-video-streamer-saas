'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Play, TrendingUp, Clock, Star } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { VideoCard } from '@/components/video-card';
import { useAuthStore, useVideoStore, Video } from '@/lib/store';

// Mock data for demonstration
const mockFeaturedVideo: Video = {
  id: '1',
  title: 'Company Quarterly Results Presentation',
  description: 'Comprehensive overview of Q4 performance and strategic initiatives for the upcoming year.',
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

const mockRecentVideos: Video[] = [
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
  }
];

const mockPopularVideos: Video[] = [
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

export default function HomePage() {
  const { user } = useAuthStore();
  const { setVideos } = useVideoStore();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Simulate loading data
    setTimeout(() => {
      setVideos([...mockRecentVideos, ...mockPopularVideos]);
      setIsLoading(false);
    }, 1000);
  }, [setVideos]);

  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20">
        {/* Hero Section */}
        <section className="container mx-auto px-4 py-20">
          <div className="text-center max-w-4xl mx-auto">
            <h1 className="text-4xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
              Enterprise Video Platform
            </h1>
            <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
              Secure, scalable video hosting solution trusted by leading companies worldwide. Upload, manage, and stream your corporate content with enterprise-grade security.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/auth/login">
                <Button size="lg" className="text-lg px-8 py-3">
                  <Play className="mr-2 h-5 w-5" />
                  Get Started
                </Button>
              </Link>
              <Link href="/demo">
                <Button variant="outline" size="lg" className="text-lg px-8 py-3">
                  Watch Demo
                </Button>
              </Link>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="container mx-auto px-4 py-16">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Trusted by Industry Leaders</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Join thousands of companies who trust our platform for their video hosting needs.
            </p>
          </div>
          
          {/* Client Logos */}
          <div className="mb-16">
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-8 items-center opacity-60">
              {[
                'TechCorp', 'InnovateLab', 'GlobalSoft', 'DataFlow', 'CloudTech', 'NextGen'
              ].map((company) => (
                <div key={company} className="text-center">
                  <div className="h-12 bg-muted rounded-lg flex items-center justify-center">
                    <span className="font-semibold text-muted-foreground">{company}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Features Grid */}
          <div className="grid md:grid-cols-3 gap-8">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Play className="mr-2 h-5 w-5 text-primary" />
                  Secure Streaming
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Enterprise-grade security with JWT authentication, role-based access control, and encrypted streaming.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <TrendingUp className="mr-2 h-5 w-5 text-primary" />
                  Analytics Dashboard
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Comprehensive analytics with viewing statistics, engagement metrics, and detailed reports.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Clock className="mr-2 h-5 w-5 text-primary" />
                  Progress Tracking
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">
                  Automatic progress saving allows users to resume videos exactly where they left off.
                </p>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* Testimonials Section */}
        <section className="container mx-auto px-4 py-16 bg-muted/30">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">What Our Clients Say</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              See how leading companies are transforming their video workflows with our platform.
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center mb-4">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                  ))}
                </div>
                <p className="text-muted-foreground mb-4">
                  "This platform has revolutionized how we handle our training videos. The security features and analytics are exactly what we needed."
                </p>
                <div className="flex items-center">
                  <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center mr-3">
                    <span className="text-sm font-semibold">JD</span>
                  </div>
                  <div>
                    <p className="font-semibold">John Davis</p>
                    <p className="text-sm text-muted-foreground">CTO, TechCorp</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center mb-4">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                  ))}
                </div>
                <p className="text-muted-foreground mb-4">
                  "The upload process is seamless and the streaming quality is exceptional. Our team loves the progress tracking feature."
                </p>
                <div className="flex items-center">
                  <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center mr-3">
                    <span className="text-sm font-semibold">SM</span>
                  </div>
                  <div>
                    <p className="font-semibold">Sarah Miller</p>
                    <p className="text-sm text-muted-foreground">Head of Learning, InnovateLab</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center mb-4">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                  ))}
                </div>
                <p className="text-muted-foreground mb-4">
                  "Outstanding platform with enterprise-grade security. The admin dashboard provides all the insights we need."
                </p>
                <div className="flex items-center">
                  <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center mr-3">
                    <span className="text-sm font-semibold">MR</span>
                  </div>
                  <div>
                    <p className="font-semibold">Michael Rodriguez</p>
                    <p className="text-sm text-muted-foreground">IT Director, GlobalSoft</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </section>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8 space-y-12">
        {/* Welcome Header */}
        <div className="text-center">
          <h1 className="text-3xl font-bold mb-2">
            Welcome back, {user.name}
          </h1>
          <p className="text-muted-foreground">
            Continue watching or discover new content
          </p>
        </div>

        {/* Featured Video */}
        <section>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold">Featured Content</h2>
            <Badge variant="outline" className="flex items-center">
              <Star className="mr-1 h-3 w-3" />
              Editor's Pick
            </Badge>
          </div>
          
          <Card className="overflow-hidden">
            <div className="md:flex">
              <div className="md:w-2/3">
                <div className="aspect-video relative overflow-hidden">
                  <Link href={`/watch/${mockFeaturedVideo.id}`}>
                    <img
                      src={mockFeaturedVideo.thumbnail_url}
                      alt={mockFeaturedVideo.title}
                      className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
                    />
                    <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity duration-300">
                      <div className="bg-white/20 backdrop-blur-sm rounded-full p-4">
                        <Play className="h-12 w-12 text-white fill-white" />
                      </div>
                    </div>
                  </Link>
                  
                  {/* Progress bar */}
                  {mockFeaturedVideo.progress && (
                    <div className="absolute bottom-0 left-0 right-0 h-1 bg-black/20">
                      <div 
                        className="h-full bg-red-500"
                        style={{ width: `${mockFeaturedVideo.progress}%` }}
                      />
                    </div>
                  )}
                </div>
              </div>
              
              <div className="md:w-1/3 p-6">
                <h3 className="text-xl font-semibold mb-3">
                  {mockFeaturedVideo.title}
                </h3>
                <p className="text-muted-foreground mb-4">
                  {mockFeaturedVideo.description}
                </p>
                
                <div className="space-y-3 text-sm text-muted-foreground">
                  <div className="flex items-center justify-between">
                    <span>Duration</span>
                    <span>{formatDuration(mockFeaturedVideo.duration)}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Views</span>
                    <span>{mockFeaturedVideo.view_count.toLocaleString()}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span>Quality</span>
                    <span>{mockFeaturedVideo.metadata.resolution}</span>
                  </div>
                </div>

                <Link href={`/watch/${mockFeaturedVideo.id}`}>
                  <Button className="w-full mt-6">
                    <Play className="mr-2 h-4 w-4" />
                    {mockFeaturedVideo.progress ? 'Continue Watching' : 'Watch Now'}
                  </Button>
                </Link>
              </div>
            </div>
          </Card>
        </section>

        {/* Recent Videos */}
        <section>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold">Recently Added</h2>
            <Link href="/search">
              <Button variant="outline">View All</Button>
            </Link>
          </div>
          
          {isLoading ? (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {[...Array(4)].map((_, i) => (
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
          ) : (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {mockRecentVideos.map((video) => (
                <VideoCard key={video.id} video={video} />
              ))}
            </div>
          )}
        </section>

        {/* Popular Videos */}
        <section>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold">Most Popular</h2>
            <Link href="/search?sort=popular">
              <Button variant="outline">View All</Button>
            </Link>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {mockPopularVideos.map((video) => (
              <VideoCard key={video.id} video={video} />
            ))}
          </div>
        </section>

        {/* Quick Actions for Admins */}
        {user.role === 'admin' && (
          <section>
            <h2 className="text-2xl font-bold mb-6">Quick Actions</h2>
            <div className="grid md:grid-cols-3 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Upload Videos</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground mb-4">
                    Add new video content to your library
                  </p>
                  <Link href="/admin/videos/upload">
                    <Button className="w-full">
                      <Play className="mr-2 h-4 w-4" />
                      Upload Now
                    </Button>
                  </Link>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Manage Videos</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground mb-4">
                    Edit, organize, and manage your video collection
                  </p>
                  <Link href="/admin/videos">
                    <Button variant="outline" className="w-full">
                      Manage Library
                    </Button>
                  </Link>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>View Analytics</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground mb-4">
                    Track performance and engagement metrics
                  </p>
                  <Link href="/admin">
                    <Button variant="outline" className="w-full">
                      View Dashboard
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            </div>
          </section>
        )}
      </div>
    </div>
  );
}