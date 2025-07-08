'use client';

import React from 'react';
import { Skeleton } from '@/components/ui/skeleton';
import { Card, CardContent, CardHeader } from '@/components/ui/card';

interface LoadingSkeletonProps {
  type?: 'member' | 'story' | 'search-bar' | 'search-results';
  count?: number;
  compact?: boolean;
}

const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({ 
  type = 'member', 
  count = 1,
  compact = false
}) => {
  const MemberSkeleton = ({ compact }: { compact?: boolean }) => (
    <Card className="w-full">
      <CardHeader className={compact ? "p-4" : "pb-3"}>
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-4">
            <Skeleton className={compact ? "w-10 h-10 rounded-full" : "w-16 h-16 rounded-full"} />
            <div className="flex-1 space-y-2">
              <Skeleton className="h-4 w-32" />
              <Skeleton className="h-3 w-24" />
              <div className="flex items-center space-x-2">
                <Skeleton className="h-3 w-16" />
                <Skeleton className="h-3 w-20" />
              </div>
            </div>
          </div>
          <div className="flex flex-col items-end space-y-2">
            <Skeleton className="h-5 w-20" />
            <Skeleton className="h-4 w-16" />
          </div>
        </div>
      </CardHeader>
      {!compact && (
        <CardContent className="pt-0">
          <div className="space-y-3">
            <div className="space-y-2">
              <Skeleton className="h-3 w-full" />
              <Skeleton className="h-3 w-3/4" />
            </div>
            <div className="space-y-2">
              <Skeleton className="h-3 w-12" />
              <div className="flex flex-wrap gap-1">
                <Skeleton className="h-5 w-16" />
                <Skeleton className="h-5 w-20" />
                <Skeleton className="h-5 w-14" />
              </div>
            </div>
          </div>
        </CardContent>
      )}
    </Card>
  );

  const StorySkeleton = ({ compact }: { compact?: boolean }) => (
    <Card className="w-full">
      <CardHeader className={compact ? "p-4" : "pb-3"}>
        <div className="flex items-start justify-between">
          <div className="flex-1 space-y-2">
            <div className="flex items-center space-x-2">
              <Skeleton className="h-5 w-24" />
              <Skeleton className="h-5 w-16" />
            </div>
            <Skeleton className="h-5 w-3/4" />
            <div className="flex items-center space-x-3">
              <Skeleton className="h-3 w-20" />
              <Skeleton className="h-3 w-24" />
            </div>
          </div>
          {!compact && (
            <div className="flex flex-col items-end space-y-2">
              <Skeleton className="h-5 w-20" />
            </div>
          )}
        </div>
      </CardHeader>
      {!compact && (
        <CardContent className="pt-0">
          <div className="space-y-3">
            <div className="space-y-2">
              <Skeleton className="h-3 w-full" />
              <Skeleton className="h-3 w-full" />
              <Skeleton className="h-3 w-2/3" />
            </div>
            <div className="space-y-2">
              <Skeleton className="h-3 w-12" />
              <div className="flex flex-wrap gap-1">
                <Skeleton className="h-5 w-16" />
                <Skeleton className="h-5 w-20" />
                <Skeleton className="h-5 w-14" />
              </div>
            </div>
          </div>
        </CardContent>
      )}
    </Card>
  );

  const SearchBarSkeleton = () => (
    <div className="w-full max-w-2xl mx-auto space-y-4">
      <div className="flex items-center space-x-2">
        <Skeleton className="h-12 flex-1" />
        <Skeleton className="h-12 w-24" />
      </div>
      <div className="flex items-center space-x-4">
        <Skeleton className="h-8 w-16" />
        <Skeleton className="h-8 w-16" />
        <Skeleton className="h-8 w-20" />
      </div>
    </div>
  );

  const SearchResultsSkeleton = () => (
    <div className="space-y-6">
      {/* Search metadata skeleton */}
      <div className="flex items-center justify-between">
        <Skeleton className="h-6 w-48" />
        <Skeleton className="h-6 w-32" />
      </div>
      
      {/* AI summary skeleton */}
      <div className="p-4 bg-muted/50 rounded-md space-y-2">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-3 w-full" />
        <Skeleton className="h-3 w-3/4" />
      </div>
      
      {/* Results skeleton */}
      <div className="space-y-4">
        <Skeleton className="h-6 w-32" />
        <div className="grid gap-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <MemberSkeleton key={i} />
          ))}
        </div>
      </div>
      
      <div className="space-y-4">
        <Skeleton className="h-6 w-24" />
        <div className="grid gap-4">
          {Array.from({ length: 2 }).map((_, i) => (
            <StorySkeleton key={i} />
          ))}
        </div>
      </div>
    </div>
  );

  if (type === 'search-bar') {
    return <SearchBarSkeleton />;
  }

  if (type === 'search-results') {
    return <SearchResultsSkeleton />;
  }

  return (
    <div className="space-y-4">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i}>
          {type === 'member' ? (
            <MemberSkeleton compact={compact} />
          ) : (
            <StorySkeleton compact={compact} />
          )}
        </div>
      ))}
    </div>
  );
};

export default LoadingSkeleton;