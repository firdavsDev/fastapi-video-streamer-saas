'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { 
  User, 
  Mail, 
  Calendar, 
  Shield, 
  Settings, 
  Camera,
  Key,
  Activity,
  CreditCard,
  Download,
  Eye,
  Clock,
  HardDrive
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Progress } from '@/components/ui/progress';
import { useAuthStore } from '@/lib/store';
import { toast } from 'sonner';

const mockSubscription = {
  plan: 'Professional',
  status: 'active',
  renewalDate: '2024-02-15T00:00:00Z',
  daysRemaining: 26,
  storageUsed: 1.2, // GB
  storageLimit: 5.0, // GB
  bandwidthUsed: 45.6, // GB
  bandwidthLimit: 100.0, // GB
  videosUploaded: 23,
  videoLimit: 100
};

const mockActivity = [
  {
    id: '1',
    action: 'Uploaded video',
    details: 'Company Quarterly Results Presentation',
    timestamp: '2024-01-15T10:00:00Z',
    type: 'upload'
  },
  {
    id: '2',
    action: 'Watched video',
    details: 'Product Demo: New Features Overview',
    timestamp: '2024-01-14T15:30:00Z',
    type: 'view'
  },
  {
    id: '3',
    action: 'Generated public link',
    details: 'Training Session: Security Best Practices',
    timestamp: '2024-01-13T09:15:00Z',
    type: 'share'
  },
  {
    id: '4',
    action: 'Updated profile',
    details: 'Changed display name and avatar',
    timestamp: '2024-01-12T14:20:00Z',
    type: 'profile'
  }
];

export default function ProfilePage() {
  const router = useRouter();
  const { user, logout } = useAuthStore();
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [activeTab, setActiveTab] = useState('profile');
  
  const [profileData, setProfileData] = useState({
    name: '',
    email: '',
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });

  useEffect(() => {
    if (!user) {
      router.push('/auth/login');
      return;
    }

    setProfileData({
      name: user.name,
      email: user.email,
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    });
    
    setIsLoading(false);
  }, [user, router]);

  const handleSaveProfile = async () => {
    setIsSaving(true);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      toast.success('Profile updated successfully');
    } catch (error) {
      toast.error('Failed to update profile');
    } finally {
      setIsSaving(false);
    }
  };

  const handleChangePassword = async () => {
    if (profileData.newPassword !== profileData.confirmPassword) {
      toast.error('New passwords do not match');
      return;
    }

    if (profileData.newPassword.length < 8) {
      toast.error('Password must be at least 8 characters long');
      return;
    }

    setIsSaving(true);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      setProfileData(prev => ({
        ...prev,
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      }));
      
      toast.success('Password changed successfully');
    } catch (error) {
      toast.error('Failed to change password');
    } finally {
      setIsSaving(false);
    }
  };

  const handleLogout = () => {
    logout();
    router.push('/auth/login');
    toast.success('Logged out successfully');
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'upload': return <Download className="h-4 w-4" />;
      case 'view': return <Eye className="h-4 w-4" />;
      case 'share': return <Settings className="h-4 w-4" />;
      case 'profile': return <User className="h-4 w-4" />;
      default: return <Activity className="h-4 w-4" />;
    }
  };

  if (!user) {
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

  const storagePercentage = (mockSubscription.storageUsed / mockSubscription.storageLimit) * 100;
  const bandwidthPercentage = (mockSubscription.bandwidthUsed / mockSubscription.bandwidthLimit) * 100;
  const videoPercentage = (mockSubscription.videosUploaded / mockSubscription.videoLimit) * 100;

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold">Profile Settings</h1>
              <p className="text-muted-foreground">
                Manage your account settings and preferences
              </p>
            </div>
            <Button variant="outline" onClick={handleLogout}>
              Sign Out
            </Button>
          </div>

          {/* Profile Overview Card */}
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center space-x-4">
                <div className="relative">
                  <Avatar className="h-20 w-20">
                    <AvatarImage src="/avatars/01.png" alt={user.name} />
                    <AvatarFallback className="text-lg">
                      {user.name.split(' ').map(n => n[0]).join('')}
                    </AvatarFallback>
                  </Avatar>
                  <Button
                    size="sm"
                    className="absolute -bottom-2 -right-2 h-8 w-8 rounded-full p-0"
                  >
                    <Camera className="h-4 w-4" />
                  </Button>
                </div>
                
                <div className="flex-1">
                  <h2 className="text-2xl font-semibold">{user.name}</h2>
                  <p className="text-muted-foreground">{user.email}</p>
                  <div className="flex items-center space-x-4 mt-2">
                    <Badge variant={user.role === 'admin' ? 'default' : 'secondary'}>
                      <Shield className="h-3 w-3 mr-1" />
                      {user.role}
                    </Badge>
                    <span className="text-sm text-muted-foreground">
                      Member since {formatDate('2023-06-15T00:00:00Z')}
                    </span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="profile">Profile</TabsTrigger>
              <TabsTrigger value="security">Security</TabsTrigger>
              <TabsTrigger value="subscription">Subscription</TabsTrigger>
              <TabsTrigger value="activity">Activity</TabsTrigger>
            </TabsList>

            {/* Profile Tab */}
            <TabsContent value="profile" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Personal Information</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="name">Display Name</Label>
                      <Input
                        id="name"
                        value={profileData.name}
                        onChange={(e) => setProfileData(prev => ({ ...prev, name: e.target.value }))}
                        placeholder="Enter your display name"
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="email">Email Address</Label>
                      <Input
                        id="email"
                        type="email"
                        value={profileData.email}
                        onChange={(e) => setProfileData(prev => ({ ...prev, email: e.target.value }))}
                        placeholder="Enter your email"
                      />
                    </div>
                  </div>

                  <div className="flex justify-end">
                    <Button onClick={handleSaveProfile} disabled={isSaving}>
                      {isSaving ? (
                        <div className="flex items-center">
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                          Saving...
                        </div>
                      ) : (
                        'Save Changes'
                      )}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Security Tab */}
            <TabsContent value="security" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Key className="h-5 w-5 mr-2" />
                    Change Password
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="current-password">Current Password</Label>
                    <Input
                      id="current-password"
                      type="password"
                      value={profileData.currentPassword}
                      onChange={(e) => setProfileData(prev => ({ ...prev, currentPassword: e.target.value }))}
                      placeholder="Enter current password"
                    />
                  </div>

                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="new-password">New Password</Label>
                      <Input
                        id="new-password"
                        type="password"
                        value={profileData.newPassword}
                        onChange={(e) => setProfileData(prev => ({ ...prev, newPassword: e.target.value }))}
                        placeholder="Enter new password"
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="confirm-password">Confirm New Password</Label>
                      <Input
                        id="confirm-password"
                        type="password"
                        value={profileData.confirmPassword}
                        onChange={(e) => setProfileData(prev => ({ ...prev, confirmPassword: e.target.value }))}
                        placeholder="Confirm new password"
                      />
                    </div>
                  </div>

                  <div className="flex justify-end">
                    <Button 
                      onClick={handleChangePassword} 
                      disabled={isSaving || !profileData.currentPassword || !profileData.newPassword}
                    >
                      {isSaving ? (
                        <div className="flex items-center">
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                          Changing...
                        </div>
                      ) : (
                        'Change Password'
                      )}
                    </Button>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Login History</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                      <div>
                        <p className="font-medium">Current Session</p>
                        <p className="text-sm text-muted-foreground">Chrome on Windows • 192.168.1.100</p>
                      </div>
                      <Badge variant="default">Active</Badge>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                      <div>
                        <p className="font-medium">Previous Session</p>
                        <p className="text-sm text-muted-foreground">Safari on macOS • 192.168.1.101</p>
                      </div>
                      <span className="text-sm text-muted-foreground">2 hours ago</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Subscription Tab */}
            <TabsContent value="subscription" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <CreditCard className="h-5 w-5 mr-2" />
                    Subscription Details
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-semibold">{mockSubscription.plan} Plan</h3>
                      <p className="text-sm text-muted-foreground">
                        Renews on {formatDate(mockSubscription.renewalDate)}
                      </p>
                    </div>
                    <Badge variant={mockSubscription.status === 'active' ? 'default' : 'secondary'}>
                      {mockSubscription.status}
                    </Badge>
                  </div>

                  <div className="bg-muted/50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">Days Remaining</span>
                      <span className="text-2xl font-bold text-primary">
                        {mockSubscription.daysRemaining}
                      </span>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      Your subscription will renew automatically
                    </p>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Usage Statistics</CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <HardDrive className="h-4 w-4 mr-2" />
                        <span className="text-sm font-medium">Storage Used</span>
                      </div>
                      <span className="text-sm text-muted-foreground">
                        {mockSubscription.storageUsed} GB / {mockSubscription.storageLimit} GB
                      </span>
                    </div>
                    <Progress value={storagePercentage} className="h-2" />
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <Activity className="h-4 w-4 mr-2" />
                        <span className="text-sm font-medium">Bandwidth Used</span>
                      </div>
                      <span className="text-sm text-muted-foreground">
                        {mockSubscription.bandwidthUsed} GB / {mockSubscription.bandwidthLimit} GB
                      </span>
                    </div>
                    <Progress value={bandwidthPercentage} className="h-2" />
                  </div>

                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <Eye className="h-4 w-4 mr-2" />
                        <span className="text-sm font-medium">Videos Uploaded</span>
                      </div>
                      <span className="text-sm text-muted-foreground">
                        {mockSubscription.videosUploaded} / {mockSubscription.videoLimit}
                      </span>
                    </div>
                    <Progress value={videoPercentage} className="h-2" />
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Activity Tab */}
            <TabsContent value="activity" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Clock className="h-5 w-5 mr-2" />
                    Recent Activity
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {mockActivity.map((activity) => (
                      <div key={activity.id} className="flex items-start space-x-3 p-3 bg-muted/50 rounded-lg">
                        <div className="flex-shrink-0 mt-1">
                          {getActivityIcon(activity.type)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="font-medium">{activity.action}</p>
                          <p className="text-sm text-muted-foreground truncate">
                            {activity.details}
                          </p>
                          <p className="text-xs text-muted-foreground mt-1">
                            {formatDateTime(activity.timestamp)}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
}