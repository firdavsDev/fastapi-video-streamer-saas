'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Video } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { UploadDropzone } from '@/components/upload-dropzone';
import { useAuthStore } from '@/lib/store';
import Link from 'next/link';

export default function UploadVideoPage() {
  const router = useRouter();
  const { user } = useAuthStore();
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);

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

  const handleFileUpload = (files: File[]) => {
    setUploadedFiles(prev => [...prev, ...files]);
  };

  if (!user || user.role !== 'admin') {
    return null;
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto space-y-6">
          {/* Header */}
          <div className="flex items-center space-x-4">
            <Link href="/admin/videos">
              <Button variant="outline" size="sm">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Videos
              </Button>
            </Link>
            <div>
              <h1 className="text-3xl font-bold">Upload Videos</h1>
              <p className="text-muted-foreground">
                Add new video content to your platform
              </p>
            </div>
          </div>

          {/* Upload Instructions */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Video className="h-5 w-5 mr-2" />
                Video Upload Guidelines
              </CardTitle>
              <CardDescription>
                Please review these guidelines before uploading your videos
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold mb-2">Supported Formats</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• MP4 (recommended)</li>
                    <li>• AVI</li>
                    <li>• MOV</li>
                    <li>• MKV</li>
                    <li>• WebM</li>
                  </ul>
                </div>
                
                <div>
                  <h4 className="font-semibold mb-2">Technical Requirements</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• Maximum file size: 200MB</li>
                    <li>• Recommended resolution: 1920x1080</li>
                    <li>• Minimum resolution: 720x480</li>
                    <li>• Recommended bitrate: 4-6 Mbps</li>
                  </ul>
                </div>
              </div>

              <div className="bg-muted/50 rounded-lg p-4">
                <h4 className="font-semibold mb-2">Processing Information</h4>
                <p className="text-sm text-muted-foreground">
                  After upload, videos will be automatically processed to extract metadata, 
                  generate thumbnails, and optimize for streaming. Processing time varies 
                  based on file size and complexity. You'll receive a notification when 
                  processing is complete.
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Upload Area */}
          <UploadDropzone
            onUpload={handleFileUpload}
            maxSize={200 * 1024 * 1024} // 200MB
            acceptedTypes={['video/mp4', 'video/avi', 'video/mov', 'video/mkv', 'video/webm']}
          />

          {/* Upload Summary */}
          {uploadedFiles.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Upload Summary</CardTitle>
                <CardDescription>
                  Files uploaded this session
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {uploadedFiles.map((file, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                      <div>
                        <p className="font-medium">{file.name}</p>
                        <p className="text-sm text-muted-foreground">
                          {(file.size / (1024 * 1024)).toFixed(2)} MB
                        </p>
                      </div>
                      <div className="text-sm text-green-600">
                        Uploaded
                      </div>
                    </div>
                  ))}
                </div>
                
                <div className="mt-6 flex gap-3">
                  <Link href="/admin/videos">
                    <Button>View All Videos</Button>
                  </Link>
                  <Button 
                    variant="outline"
                    onClick={() => setUploadedFiles([])}
                  >
                    Clear List
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Help Section */}
          <Card>
            <CardHeader>
              <CardTitle>Need Help?</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold mb-2">Common Issues</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• File size too large: Compress your video</li>
                    <li>• Unsupported format: Convert to MP4</li>
                    <li>• Upload failed: Check your internet connection</li>
                    <li>• Processing stuck: Contact support</li>
                  </ul>
                </div>
                
                <div>
                  <h4 className="font-semibold mb-2">Best Practices</h4>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• Use descriptive filenames</li>
                    <li>• Ensure good audio quality</li>
                    <li>• Upload during off-peak hours</li>
                    <li>• Test playback after processing</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}