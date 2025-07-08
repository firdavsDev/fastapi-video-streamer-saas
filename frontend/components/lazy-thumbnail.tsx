'use client';

import { useState, useRef, useEffect } from 'react';
import { cn } from '@/lib/utils';

interface LazyThumbnailProps {
  src: string;
  alt: string;
  className?: string;
  quality?: 'low' | 'medium' | 'high';
  onLoad?: () => void;
  onError?: () => void;
}

export function LazyThumbnail({ 
  src, 
  alt, 
  className, 
  quality = 'medium',
  onLoad,
  onError 
}: LazyThumbnailProps) {
  const [isLoaded, setIsLoaded] = useState(false);
  const [isInView, setIsInView] = useState(false);
  const [hasError, setHasError] = useState(false);
  const imgRef = useRef<HTMLImageElement>(null);
  const observerRef = useRef<IntersectionObserver | null>(null);

  // Generate different quality URLs
  const getImageUrl = (quality: string) => {
    if (src.includes('pexels.com')) {
      const baseUrl = src.split('?')[0];
      switch (quality) {
        case 'low': return `${baseUrl}?auto=compress&cs=tinysrgb&w=300&h=200`;
        case 'medium': return `${baseUrl}?auto=compress&cs=tinysrgb&w=640&h=360`;
        case 'high': return `${baseUrl}?auto=compress&cs=tinysrgb&w=1280&h=720`;
        default: return src;
      }
    }
    return src;
  };

  useEffect(() => {
    const img = imgRef.current;
    if (!img) return;

    // Create intersection observer
    observerRef.current = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true);
          observerRef.current?.unobserve(img);
        }
      },
      {
        rootMargin: '50px',
        threshold: 0.1
      }
    );

    observerRef.current.observe(img);

    return () => {
      observerRef.current?.disconnect();
    };
  }, []);

  const handleLoad = () => {
    setIsLoaded(true);
    onLoad?.();
  };

  const handleError = () => {
    setHasError(true);
    onError?.();
  };

  return (
    <div className={cn('relative overflow-hidden bg-muted', className)}>
      {/* Skeleton loader */}
      {!isLoaded && !hasError && (
        <div className="absolute inset-0 bg-gradient-to-r from-muted via-muted/50 to-muted animate-pulse" />
      )}

      {/* Error fallback */}
      {hasError && (
        <div className="absolute inset-0 flex items-center justify-center bg-muted">
          <div className="text-center text-muted-foreground">
            <div className="w-12 h-12 mx-auto mb-2 bg-muted-foreground/20 rounded-full flex items-center justify-center">
              <svg
                className="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
            </div>
            <p className="text-xs">Failed to load</p>
          </div>
        </div>
      )}

      {/* Progressive image loading */}
      {isInView && !hasError && (
        <>
          {/* Low quality placeholder */}
          <img
            src={getImageUrl('low')}
            alt={alt}
            className={cn(
              'absolute inset-0 w-full h-full object-cover transition-opacity duration-300',
              isLoaded ? 'opacity-0' : 'opacity-100 blur-sm scale-110'
            )}
          />
          
          {/* High quality image */}
          <img
            ref={imgRef}
            src={getImageUrl(quality)}
            alt={alt}
            onLoad={handleLoad}
            onError={handleError}
            className={cn(
              'w-full h-full object-cover transition-opacity duration-300',
              isLoaded ? 'opacity-100' : 'opacity-0'
            )}
          />
        </>
      )}

      {/* Loading indicator */}
      {isInView && !isLoaded && !hasError && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-8 h-8 border-2 border-primary border-t-transparent rounded-full animate-spin" />
        </div>
      )}
    </div>
  );
}