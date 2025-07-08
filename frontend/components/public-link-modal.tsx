'use client';

import { useState } from 'react';
import { Copy, ExternalLink, Eye, Calendar, Lock, Download, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { toast } from 'sonner';

interface PublicLink {
  id: string;
  url: string;
  expires_at: string;
  password_protected: boolean;
  download_allowed: boolean;
  view_limit: number;
  views_used: number;
  created_at: string;
}

interface PublicLinkModalProps {
  isOpen: boolean;
  onClose: () => void;
  videoId: string;
  videoTitle: string;
}

export function PublicLinkModal({ isOpen, onClose, videoId, videoTitle }: PublicLinkModalProps) {
  const [isGenerating, setIsGenerating] = useState(false);
  const [formData, setFormData] = useState({
    expires_in_days: '7',
    password_protected: false,
    password: '',
    download_allowed: false,
    view_limit: 0,
    unlimited_views: true
  });

  // Mock existing links
  const [existingLinks, setExistingLinks] = useState<PublicLink[]>([
    {
      id: '1',
      url: 'https://videostream.com/public/abc123def456',
      expires_at: '2024-01-22T10:00:00Z',
      password_protected: false,
      download_allowed: false,
      view_limit: 100,
      views_used: 23,
      created_at: '2024-01-15T10:00:00Z'
    },
    {
      id: '2',
      url: 'https://videostream.com/public/xyz789uvw012',
      expires_at: '2024-01-30T15:30:00Z',
      password_protected: true,
      download_allowed: true,
      view_limit: 0,
      views_used: 45,
      created_at: '2024-01-14T15:30:00Z'
    }
  ]);

  const handleGenerateLink = async () => {
    setIsGenerating(true);
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      const newLink: PublicLink = {
        id: Math.random().toString(36).substr(2, 9),
        url: `https://videostream.com/public/${Math.random().toString(36).substr(2, 12)}`,
        expires_at: new Date(Date.now() + parseInt(formData.expires_in_days) * 24 * 60 * 60 * 1000).toISOString(),
        password_protected: formData.password_protected,
        download_allowed: formData.download_allowed,
        view_limit: formData.unlimited_views ? 0 : formData.view_limit,
        views_used: 0,
        created_at: new Date().toISOString()
      };

      setExistingLinks(prev => [newLink, ...prev]);
      toast.success('Public link generated successfully');
      
      // Reset form
      setFormData({
        expires_in_days: '7',
        password_protected: false,
        password: '',
        download_allowed: false,
        view_limit: 0,
        unlimited_views: true
      });
    } catch (error) {
      toast.error('Failed to generate public link');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleCopyLink = (url: string) => {
    navigator.clipboard.writeText(url);
    toast.success('Link copied to clipboard');
  };

  const handleRevokeLink = (linkId: string) => {
    setExistingLinks(prev => prev.filter(link => link.id !== linkId));
    toast.success('Public link revoked');
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const isExpired = (dateString: string) => {
    return new Date(dateString) < new Date();
  };

  const getExpiryStatus = (dateString: string) => {
    const expiryDate = new Date(dateString);
    const now = new Date();
    const diffHours = (expiryDate.getTime() - now.getTime()) / (1000 * 60 * 60);
    
    if (diffHours < 0) return { status: 'expired', color: 'destructive' };
    if (diffHours < 24) return { status: 'expires soon', color: 'secondary' };
    return { status: 'active', color: 'default' };
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center">
            <ExternalLink className="h-5 w-5 mr-2" />
            Generate Public Link
          </DialogTitle>
          <DialogDescription>
            Create a shareable link for "{videoTitle}" that can be accessed without authentication
          </DialogDescription>
        </DialogHeader>

        <div className="grid lg:grid-cols-2 gap-6">
          {/* Generate New Link Form */}
          <Card>
            <CardHeader>
              <CardTitle>Create New Link</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="expires_in_days">Expiration</Label>
                <Select
                  value={formData.expires_in_days}
                  onValueChange={(value) => setFormData(prev => ({ ...prev, expires_in_days: value }))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1">1 day</SelectItem>
                    <SelectItem value="3">3 days</SelectItem>
                    <SelectItem value="7">1 week</SelectItem>
                    <SelectItem value="14">2 weeks</SelectItem>
                    <SelectItem value="30">1 month</SelectItem>
                    <SelectItem value="90">3 months</SelectItem>
                    <SelectItem value="365">1 year</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Password Protection</Label>
                  <p className="text-sm text-muted-foreground">
                    Require a password to access the video
                  </p>
                </div>
                <Switch
                  checked={formData.password_protected}
                  onCheckedChange={(checked) => setFormData(prev => ({ ...prev, password_protected: checked }))}
                />
              </div>

              {formData.password_protected && (
                <div className="space-y-2">
                  <Label htmlFor="password">Password</Label>
                  <Input
                    id="password"
                    type="password"
                    placeholder="Enter password"
                    value={formData.password}
                    onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
                  />
                </div>
              )}

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Allow Downloads</Label>
                  <p className="text-sm text-muted-foreground">
                    Allow users to download the video file
                  </p>
                </div>
                <Switch
                  checked={formData.download_allowed}
                  onCheckedChange={(checked) => setFormData(prev => ({ ...prev, download_allowed: checked }))}
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Unlimited Views</Label>
                  <p className="text-sm text-muted-foreground">
                    Allow unlimited number of views
                  </p>
                </div>
                <Switch
                  checked={formData.unlimited_views}
                  onCheckedChange={(checked) => setFormData(prev => ({ ...prev, unlimited_views: checked }))}
                />
              </div>

              {!formData.unlimited_views && (
                <div className="space-y-2">
                  <Label htmlFor="view_limit">View Limit</Label>
                  <Input
                    id="view_limit"
                    type="number"
                    min="1"
                    placeholder="Maximum number of views"
                    value={formData.view_limit || ''}
                    onChange={(e) => setFormData(prev => ({ ...prev, view_limit: parseInt(e.target.value) || 0 }))}
                  />
                </div>
              )}

              <Button
                onClick={handleGenerateLink}
                disabled={isGenerating || (formData.password_protected && !formData.password)}
                className="w-full"
              >
                {isGenerating ? (
                  <div className="flex items-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Generating...
                  </div>
                ) : (
                  <>
                    <ExternalLink className="h-4 w-4 mr-2" />
                    Generate Link
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          {/* Existing Links */}
          <Card>
            <CardHeader>
              <CardTitle>Active Links ({existingLinks.length})</CardTitle>
            </CardHeader>
            <CardContent>
              {existingLinks.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <ExternalLink className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No public links created yet</p>
                  <p className="text-sm">Generate your first link to get started</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {existingLinks.map((link) => {
                    const expiryStatus = getExpiryStatus(link.expires_at);
                    
                    return (
                      <div key={link.id} className="border rounded-lg p-4 space-y-3">
                        <div className="flex items-center justify-between">
                          <Badge variant={expiryStatus.color as any}>
                            {expiryStatus.status}
                          </Badge>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleRevokeLink(link.id)}
                            className="text-destructive hover:text-destructive"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>

                        <div className="space-y-2">
                          <div className="flex items-center space-x-2">
                            <Input
                              value={link.url}
                              readOnly
                              className="text-sm"
                            />
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleCopyLink(link.url)}
                            >
                              <Copy className="h-4 w-4" />
                            </Button>
                          </div>

                          <div className="grid grid-cols-2 gap-4 text-xs text-muted-foreground">
                            <div className="flex items-center">
                              <Calendar className="h-3 w-3 mr-1" />
                              Expires: {formatDate(link.expires_at)}
                            </div>
                            <div className="flex items-center">
                              <Eye className="h-3 w-3 mr-1" />
                              Views: {link.views_used}{link.view_limit > 0 ? `/${link.view_limit}` : ''}
                            </div>
                          </div>

                          <div className="flex items-center space-x-4 text-xs">
                            {link.password_protected && (
                              <div className="flex items-center text-amber-600">
                                <Lock className="h-3 w-3 mr-1" />
                                Password Protected
                              </div>
                            )}
                            {link.download_allowed && (
                              <div className="flex items-center text-blue-600">
                                <Download className="h-3 w-3 mr-1" />
                                Downloads Allowed
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </DialogContent>
    </Dialog>
  );
}