'use client';

import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, File, X, CheckCircle, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useVideoStore, UploadProgress } from '@/lib/store';
import { cn } from '@/lib/utils';

interface UploadDropzoneProps {
  onUpload?: (files: File[]) => void;
  maxSize?: number;
  acceptedTypes?: string[];
  className?: string;
}

export function UploadDropzone({
  onUpload,
  maxSize = 200 * 1024 * 1024, // 200MB
  acceptedTypes = ['video/mp4', 'video/avi', 'video/mov', 'video/mkv'],
  className
}: UploadDropzoneProps) {
  const { uploads, addUpload, updateUpload, removeUpload } = useVideoStore();
  const [isDragActive, setIsDragActive] = useState(false);

  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: any[]) => {
    setIsDragActive(false);
    
    // Handle rejected files
    rejectedFiles.forEach(({ file, errors }) => {
      console.error(`File ${file.name} rejected:`, errors);
    });

    // Process accepted files
    acceptedFiles.forEach((file) => {
      const uploadId = Math.random().toString(36).substr(2, 9);
      
      const uploadProgress: UploadProgress = {
        id: uploadId,
        filename: file.name,
        progress: 0,
        status: 'uploading'
      };

      addUpload(uploadProgress);

      // Simulate upload progress
      simulateUpload(uploadId, file);
    });

    onUpload?.(acceptedFiles);
  }, [addUpload, onUpload]);

  const simulateUpload = (uploadId: string, file: File) => {
    let progress = 0;
    const interval = setInterval(() => {
      progress += Math.random() * 15;
      
      if (progress >= 100) {
        clearInterval(interval);
        updateUpload(uploadId, { progress: 100, status: 'processing' });
        
        // Simulate processing
        setTimeout(() => {
          updateUpload(uploadId, { status: 'completed' });
          
          // Auto-remove after completion
          setTimeout(() => {
            removeUpload(uploadId);
          }, 3000);
        }, 2000);
      } else {
        updateUpload(uploadId, { progress });
      }
    }, 200);
  };

  const { getRootProps, getInputProps, isDragAccept, isDragReject } = useDropzone({
    onDrop,
    onDragEnter: () => setIsDragActive(true),
    onDragLeave: () => setIsDragActive(false),
    accept: {
      'video/*': ['.mp4', '.avi', '.mov', '.mkv', '.webm']
    },
    maxSize,
    multiple: true
  });

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'failed':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return <File className="h-4 w-4 text-blue-500" />;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'uploading': return 'Uploading...';
      case 'processing': return 'Processing...';
      case 'completed': return 'Completed';
      case 'failed': return 'Failed';
      default: return 'Unknown';
    }
  };

  return (
    <div className={cn('space-y-4', className)}>
      {/* Upload dropzone */}
      <Card
        {...getRootProps()}
        className={cn(
          'border-2 border-dashed cursor-pointer transition-all duration-300',
          isDragAccept && 'border-green-500 bg-green-50',
          isDragReject && 'border-red-500 bg-red-50',
          isDragActive && !isDragAccept && !isDragReject && 'border-primary bg-primary/5',
          'hover:border-primary hover:bg-primary/5'
        )}
      >
        <CardContent className="flex flex-col items-center justify-center py-12 px-6 text-center">
          <input {...getInputProps()} />
          
          <div className={cn(
            'rounded-full p-4 mb-4 transition-colors',
            isDragAccept ? 'bg-green-100' : 
            isDragReject ? 'bg-red-100' : 
            'bg-muted'
          )}>
            <Upload className={cn(
              'h-8 w-8',
              isDragAccept ? 'text-green-600' :
              isDragReject ? 'text-red-600' :
              'text-muted-foreground'
            )} />
          </div>

          <h3 className="text-lg font-semibold mb-2">
            {isDragActive ? 'Drop files here' : 'Upload Videos'}
          </h3>
          
          <p className="text-muted-foreground mb-4">
            Drag and drop video files here, or click to select files
          </p>

          <div className="space-y-2 text-sm text-muted-foreground">
            <p>Supported formats: MP4, AVI, MOV, MKV, WebM</p>
            <p>Maximum file size: {formatFileSize(maxSize)}</p>
          </div>

          <Button variant="outline" className="mt-4">
            Select Files
          </Button>
        </CardContent>
      </Card>

      {/* Upload progress */}
      {uploads.length > 0 && (
        <Card>
          <CardContent className="p-4">
            <h4 className="font-semibold mb-4">Upload Progress</h4>
            <div className="space-y-4">
              {uploads.map((upload) => (
                <div key={upload.id} className="flex items-center space-x-4">
                  <div className="flex-shrink-0">
                    {getStatusIcon(upload.status)}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <p className="text-sm font-medium truncate">
                        {upload.filename}
                      </p>
                      <Badge variant="outline" className="text-xs">
                        {getStatusText(upload.status)}
                      </Badge>
                    </div>
                    
                    {upload.status === 'uploading' || upload.status === 'processing' ? (
                      <div className="space-y-1">
                        <Progress value={upload.progress} className="h-2" />
                        <p className="text-xs text-muted-foreground">
                          {upload.progress.toFixed(1)}%
                        </p>
                      </div>
                    ) : (
                      <div className="h-2 bg-muted rounded-full">
                        <div className={cn(
                          'h-full rounded-full transition-colors',
                          upload.status === 'completed' ? 'bg-green-500' : 'bg-red-500'
                        )} />
                      </div>
                    )}
                  </div>

                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeUpload(upload.id)}
                    className="flex-shrink-0"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}