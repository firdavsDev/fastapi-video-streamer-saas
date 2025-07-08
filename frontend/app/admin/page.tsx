'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { 
  BarChart3, 
  Video, 
  Users, 
  Upload, 
  Eye, 
  TrendingUp,
  Clock,
  HardDrive
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { useAuthStore } from '@/lib/store';
import Link from 'next/link';

// Mock analytics data
const mockAnalytics = {
  totalVideos: 247,
  totalViews: 15420,
  totalUsers: 89,
  storageUsed: 1.2, // TB
  storageLimit: 5.0, // TB
  monthlyGrowth: 12.5,
  popularVideos: [
    { id: '1', title: 'CEO Town Hall: Vision 2024', views: 4521 },
    { id: '2', title: 'Technical Deep Dive: System Architecture', views: 3456 },
    { id: '3', title: 'Marketing Campaign Results Analysis', views: 2987 },
    { id: '4', title: 'Security Best Practices Training', views: 2103 },
    { id: '5', title: 'Customer Success Stories', views: 1876 }
  ],
  recentUploads: [
    { id: '1', title: 'Company Quarterly Results', uploadDate: '2024-01-15', status: 'ready' },
    { id: '2', title: 'Product Demo: New Features', uploadDate: '2024-01-14', status: 'processing' },
    { id: '3', title: 'Team Building Workshop', uploadDate: '2024-01-12', status: 'ready' },
    { id: '4', title: 'Customer Testimonials', uploadDate: '2024-01-11', status: 'ready' }
  ],
  viewsData: [
    { month: 'Sep', views: 8420 },
    { month: 'Oct', views: 9230 },
    { month: 'Nov', views: 12100 },
    { month: 'Dec', views: 15420 }
  ]
};

export default function AdminDashboard() {
  const router = useRouter();
  const { user } = useAuthStore();

  useEffect(() => {
    if (!user) {
      router.push('/auth/login');
      return;
    }
    
    if (user.role !== 'admin') {
      router.push('/');
      return;
    }
  }, [user, router]);

  if (!user || user.role !== 'admin') {
    return null;
  }

  const storagePercentage = (mockAnalytics.storageUsed / mockAnalytics.storageLimit) * 100;

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <div className="space-y-8">
          {/* Header */}
          <div className="flex flex-col md:flex-row md:items-center md:justify-between">
            <div>
              <h1 className="text-3xl font-bold">Admin Dashboard</h1>
              <p className="text-muted-foreground mt-1">
                Monitor your video platform performance and analytics
              </p>
            </div>
            <div className="flex gap-3 mt-4 md:mt-0">
              <Link href="/admin/videos/upload">
                <Button>
                  <Upload className="h-4 w-4 mr-2" />
                  Upload Video
                </Button>
              </Link>
              <Link href="/admin/videos">
                <Button variant="outline">
                  <Video className="h-4 w-4 mr-2" />
                  Manage Videos
                </Button>
              </Link>
            </div>
          </div>

          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Videos</CardTitle>
                <Video className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{mockAnalytics.totalVideos}</div>
                <p className="text-xs text-muted-foreground">
                  +12 from last month
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Views</CardTitle>
                <Eye className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{mockAnalytics.totalViews.toLocaleString()}</div>
                <p className="text-xs text-muted-foreground">
                  +{mockAnalytics.monthlyGrowth}% from last month
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Active Users</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{mockAnalytics.totalUsers}</div>
                <p className="text-xs text-muted-foreground">
                  +3 new users this week
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Storage Used</CardTitle>
                <HardDrive className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {mockAnalytics.storageUsed} TB
                </div>
                <Progress value={storagePercentage} className="mt-2" />
                <p className="text-xs text-muted-foreground mt-1">
                  {mockAnalytics.storageLimit - mockAnalytics.storageUsed} TB available
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Charts and Analytics */}
          <div className="grid lg:grid-cols-2 gap-6">
            {/* Views Chart */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <TrendingUp className="h-5 w-5 mr-2" />
                  Monthly Views
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {mockAnalytics.viewsData.map((data, index) => (
                    <div key={data.month} className="flex items-center justify-between">
                      <span className="text-sm font-medium">{data.month}</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-32 bg-muted rounded-full h-2">
                          <div
                            className="bg-primary h-2 rounded-full"
                            style={{
                              width: `${(data.views / Math.max(...mockAnalytics.viewsData.map(d => d.views))) * 100}%`
                            }}
                          />
                        </div>
                        <span className="text-sm text-muted-foreground w-16 text-right">
                          {data.views.toLocaleString()}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Popular Videos */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <BarChart3 className="h-5 w-5 mr-2" />
                  Most Popular Videos
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {mockAnalytics.popularVideos.map((video, index) => (
                    <div key={video.id} className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <Badge variant="outline" className="w-6 h-6 rounded-full p-0 flex items-center justify-center text-xs">
                          {index + 1}
                        </Badge>
                        <span className="text-sm font-medium truncate max-w-48">
                          {video.title}
                        </span>
                      </div>
                      <span className="text-sm text-muted-foreground">
                        {video.views.toLocaleString()}
                      </span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recent Activity */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Clock className="h-5 w-5 mr-2" />
                Recent Uploads
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {mockAnalytics.recentUploads.map((upload) => (
                  <div key={upload.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Video className="h-8 w-8 text-muted-foreground" />
                      <div>
                        <h4 className="font-medium">{upload.title}</h4>
                        <p className="text-sm text-muted-foreground">
                          Uploaded on {new Date(upload.uploadDate).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <Badge
                      variant={upload.status === 'ready' ? 'default' : 'secondary'}
                    >
                      {upload.status}
                    </Badge>
                  </div>
                ))}
              </div>
              
              <div className="mt-6 text-center">
                <Link href="/admin/videos">
                  <Button variant="outline">View All Videos</Button>
                </Link>
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-3 gap-4">
                <Link href="/admin/videos/upload">
                  <Button className="w-full justify-start" variant="outline">
                    <Upload className="h-4 w-4 mr-2" />
                    Upload New Video
                  </Button>
                </Link>
                <Link href="/admin/videos">
                  <Button className="w-full justify-start" variant="outline">
                    <Video className="h-4 w-4 mr-2" />
                    Manage Videos
                  </Button>
                </Link>
                <Link href="/admin/users">
                  <Button className="w-full justify-start" variant="outline">
                    <Users className="h-4 w-4 mr-2" />
                    Manage Users
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}