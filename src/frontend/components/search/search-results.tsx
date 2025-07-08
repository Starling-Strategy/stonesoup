'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { EmptyState } from '@/components/ui/error-boundary';
import LoadingSkeleton from '@/components/ui/loading-skeleton';
import MemberCard from './member-card';
import StoryCard from './story-card';
import { 
  Clock, 
  Users, 
  FileText, 
  Brain, 
  ChevronRight,
  Filter,
  SortAsc,
  Eye,
  EyeOff,
  Lightbulb,
  Search
} from 'lucide-react';
import { 
  HybridSearchResponse, 
  SearchResultsProps, 
  Member, 
  Story 
} from '@/lib/types';
import { cn } from '@/lib/utils';

const SearchResults: React.FC<SearchResultsProps> = ({
  results,
  loading = false,
  onMemberClick,
  onStoryClick,
  showScores = false,
  showHighlights = true
}) => {
  const [showCompactView, setShowCompactView] = useState(false);
  const [showMemberScores, setShowMemberScores] = useState(showScores);
  const [showStoryScores, setShowStoryScores] = useState(showScores);
  const [showMemberHighlights, setShowMemberHighlights] = useState(showHighlights);
  const [showStoryHighlights, setShowStoryHighlights] = useState(showHighlights);

  if (loading) {
    return <LoadingSkeleton type="search-results" />;
  }

  const formatExecutionTime = (timeMs: number) => {
    if (timeMs < 1000) {
      return `${Math.round(timeMs)}ms`;
    }
    return `${(timeMs / 1000).toFixed(2)}s`;
  };

  const getTotalResults = () => {
    return results.member_total + results.story_total;
  };

  const handleMemberClick = (member: Member) => {
    if (onMemberClick) {
      onMemberClick(member);
    }
  };

  const handleStoryClick = (story: Story) => {
    if (onStoryClick) {
      onStoryClick(story);
    }
  };

  // Show empty state if no results
  if (getTotalResults() === 0) {
    return (
      <EmptyState
        title="No results found"
        description="Try adjusting your search terms or filters to find what you're looking for."
        icon={<Search className="w-8 h-8 text-muted-foreground" />}
        action={{
          label: "Clear search",
          onClick: () => window.location.reload()
        }}
        className="mt-8"
      />
    );
  }

  return (
    <div className="space-y-6">
      {/* Search metadata */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <h2 className="text-lg font-medium">
              {getTotalResults().toLocaleString()} results
            </h2>
            <Badge variant="outline" className="text-xs">
              <Clock className="w-3 h-3 mr-1" />
              {formatExecutionTime(results.search_metadata.execution_time_ms)}
            </Badge>
          </div>
          
          <div className="flex items-center space-x-2">
            <Badge variant="secondary" className="text-xs">
              <Users className="w-3 h-3 mr-1" />
              {results.member_total} members
            </Badge>
            <Badge variant="secondary" className="text-xs">
              <FileText className="w-3 h-3 mr-1" />
              {results.story_total} stories
            </Badge>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowCompactView(!showCompactView)}
            className="text-xs"
          >
            {showCompactView ? 'Detailed View' : 'Compact View'}
          </Button>
          
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              setShowMemberScores(!showMemberScores);
              setShowStoryScores(!showStoryScores);
            }}
            className="text-xs"
          >
            {showMemberScores ? <EyeOff className="w-3 h-3 mr-1" /> : <Eye className="w-3 h-3 mr-1" />}
            {showMemberScores ? 'Hide Scores' : 'Show Scores'}
          </Button>
        </div>
      </div>

      {/* AI Summary */}
      {results.ai_summary && (
        <Card className="border-l-4 border-l-blue-500">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center text-base">
              <Brain className="w-5 h-5 mr-2 text-blue-500" />
              AI Summary
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground leading-relaxed">
              {results.ai_summary}
            </p>
          </CardContent>
        </Card>
      )}

      {/* Hybrid search explanation */}
      {results.hybrid_explanation && (
        <Card className="bg-muted/50">
          <CardContent className="p-4">
            <div className="flex items-start space-x-3">
              <Lightbulb className="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium mb-1">Search Strategy</p>
                <p className="text-xs text-muted-foreground">
                  {results.hybrid_explanation}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Member Results */}
      {results.member_results.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <h3 className="text-lg font-medium flex items-center">
                <Users className="w-5 h-5 mr-2" />
                Members
              </h3>
              <Badge variant="secondary">
                {results.member_total}
              </Badge>
            </div>
            
            <div className="flex items-center space-x-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowMemberHighlights(!showMemberHighlights)}
                className="text-xs"
              >
                {showMemberHighlights ? 'Hide Highlights' : 'Show Highlights'}
              </Button>
            </div>
          </div>
          
          <div className={cn(
            "grid gap-4",
            showCompactView ? "grid-cols-1" : "grid-cols-1"
          )}>
            {results.member_results.map((result) => (
              <MemberCard
                key={result.member.id}
                member={result.member}
                searchResult={result}
                onClick={handleMemberClick}
                showScore={showMemberScores}
                showHighlights={showMemberHighlights}
                compact={showCompactView}
              />
            ))}
          </div>
          
          {results.member_total > results.member_results.length && (
            <div className="text-center pt-4">
              <Button variant="outline" className="flex items-center space-x-2">
                <span>View {results.member_total - results.member_results.length} more members</span>
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
          )}
        </div>
      )}

      {/* Separator between sections */}
      {results.member_results.length > 0 && results.story_results.length > 0 && (
        <Separator />
      )}

      {/* Story Results */}
      {results.story_results.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <h3 className="text-lg font-medium flex items-center">
                <FileText className="w-5 h-5 mr-2" />
                Stories
              </h3>
              <Badge variant="secondary">
                {results.story_total}
              </Badge>
            </div>
            
            <div className="flex items-center space-x-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowStoryHighlights(!showStoryHighlights)}
                className="text-xs"
              >
                {showStoryHighlights ? 'Hide Highlights' : 'Show Highlights'}
              </Button>
            </div>
          </div>
          
          <div className={cn(
            "grid gap-4",
            showCompactView ? "grid-cols-1" : "grid-cols-1"
          )}>
            {results.story_results.map((result) => (
              <StoryCard
                key={result.story.id}
                story={result.story}
                searchResult={result}
                onClick={handleStoryClick}
                showScore={showStoryScores}
                showHighlights={showStoryHighlights}
                compact={showCompactView}
              />
            ))}
          </div>
          
          {results.story_total > results.story_results.length && (
            <div className="text-center pt-4">
              <Button variant="outline" className="flex items-center space-x-2">
                <span>View {results.story_total - results.story_results.length} more stories</span>
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
          )}
        </div>
      )}

      {/* Search suggestions */}
      {results.suggestions && results.suggestions.length > 0 && (
        <Card className="bg-muted/50">
          <CardHeader className="pb-3">
            <CardTitle className="text-base">You might also like</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {results.suggestions.map((suggestion, index) => (
                <Button
                  key={index}
                  variant="outline"
                  size="sm"
                  className="text-xs"
                  onClick={() => {
                    // This would trigger a new search
                    // Implementation depends on parent component
                    console.log('Search suggestion clicked:', suggestion);
                  }}
                >
                  {suggestion}
                </Button>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default SearchResults;