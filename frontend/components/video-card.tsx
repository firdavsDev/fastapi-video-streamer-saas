'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Play, Clock, Eye, MoreVertical, Trash2, Edit } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Video } from '@/lib/store';
import { cn } from '@/lib/utils';
import { LazyThumbnail } from '@/components/lazy-thumbnail';

interface VideoCardProps {
  video: Video;
  showActions?: boolean;
  onDelete?: (id: string) => void;
  onEdit?: (id: string) => void;
  className?: string;
}

export function VideoCard({ 
  video, 
  showActions = false, 
  onDelete, 
  onEdit,
  className 
}: VideoCardProps) {
  const [isHovered, setIsHovered] = useState(false);

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
      case 'ready': return 'bg-green-500';
      case 'processing': return 'bg-yellow-500';
      case 'failed': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  return (
    <Card 
      className={cn(
        'group overflow-hidden transition-all duration-300 hover:shadow-lg hover:scale-[1.02] bg-card border border-border',
        className
      )}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="relative aspect-video overflow-hidden">
        <Link href={`/watch/${video.id}`}>
          <LazyThumbnail
            src={video.thumbnail_url || '/api/placeholder/640/360'}
            alt={video.title}
            className="w-full h-full transition-transform duration-300 group-hover:scale-105"
            quality="medium"
          />
          
          {/* Play overlay */}
          <div 
            className={cn(
              'absolute inset-0 bg-black/40 flex items-center justify-center transition-opacity duration-300',
              isHovered ? 'opacity-100' : 'opacity-0'
            )}
          >
            <div className="bg-white/20 backdrop-blur-sm rounded-full p-3">
              <Play className="h-8 w-8 text-white fill-white" />
            </div>
          </div>
        </Link>

        {/* Duration badge */}
        <Badge className="absolute bottom-2 right-2 bg-black/70 text-white hover:bg-black/70">
          <Clock className="h-3 w-3 mr-1" />
          {formatDuration(video.duration)}
        </Badge>

        {/* Status badge */}
        <div className="absolute top-2 left-2">
          <div className={cn('w-2 h-2 rounded-full', getStatusColor(video.status))} />
        </div>

        {/* Progress bar */}
        {video.progress && video.progress > 0 && (
          <div className="absolute bottom-0 left-0 right-0 h-1 bg-black/20">
            <div 
              className="h-full bg-red-500 transition-all duration-300"
              style={{ width: `${video.progress}%` }}
            />
          </div>
        )}

        {/* Actions menu */}
        {showActions && (
          <div className="absolute top-2 right-2">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  size="sm"
                  className="bg-black/20 hover:bg-black/40 text-white backdrop-blur-sm"
                >
                  <MoreVertical className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                {onEdit && (
                  <DropdownMenuItem onClick={() => onEdit(video.id)}>
                    <Edit className="h-4 w-4 mr-2" />
                    Edit
                  </DropdownMenuItem>
                )}
                {onDelete && (
                  <DropdownMenuItem 
                    onClick={() => onDelete(video.id)}
                    className="text-destructive"
                  >
                    <Trash2 className="h-4 w-4 mr-2" />
                    Delete
                  </DropdownMenuItem>
                )}
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        )}
      </div>

      <CardContent className="p-4">
        <div className="space-y-2">
          <Link href={`/watch/${video.id}`}>
            <h3 className="font-semibold text-foreground hover:text-primary transition-colors line-clamp-2">
              {video.title}
            </h3>
          </Link>
          
          {video.description && (
            <p className="text-sm text-muted-foreground line-clamp-2">
              {video.description}
            </p>
          )}

          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <div className="flex items-center space-x-3">
              <span className="flex items-center">
                <Eye className="h-3 w-3 mr-1" />
                {video.view_count.toLocaleString()}
              </span>
              <span>{formatDate(video.upload_date)}</span>
            </div>
            {video.file_size && (
              <span>{formatFileSize(video.file_size)}</span>
            )}
          </div>

          {video.metadata && (
            <div className="flex items-center space-x-2 text-xs text-muted-foreground">
              <Badge variant="outline" className="text-xs">
                {video.metadata.resolution}
              </Badge>
              <Badge variant="outline" className="text-xs">
                {video.metadata.codec}
              </Badge>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}