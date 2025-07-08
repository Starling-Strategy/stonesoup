'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Button } from '@/components/ui/button';
import { 
  User, 
  Calendar, 
  Tag, 
  TrendingUp, 
  Star,
  Target,
  BookOpen,
  Award,
  Lightbulb,
  Users,
  FileText,
  Clock,
  Brain,
  Zap
} from 'lucide-react';
import { Story, StorySearchResult, StoryCardProps } from '@/lib/types';
import { cn } from '@/lib/utils';

const StoryCard: React.FC<StoryCardProps> = ({
  story,
  searchResult,
  onClick,
  showScore = false,
  showHighlights = false,
  compact = false
}) => {
  const handleClick = () => {
    if (onClick) {
      onClick(story);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const getStoryTypeIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'achievement':
        return <Award className="w-4 h-4" />;
      case 'experience':
        return <BookOpen className="w-4 h-4" />;
      case 'skill_demonstration':
        return <Zap className="w-4 h-4" />;
      case 'testimonial':
        return <Users className="w-4 h-4" />;
      case 'case_study':
        return <FileText className="w-4 h-4" />;
      case 'thought_leadership':
        return <Lightbulb className="w-4 h-4" />;
      default:
        return <BookOpen className="w-4 h-4" />;
    }
  };

  const getStoryTypeColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'achievement':
        return 'success';
      case 'experience':
        return 'info';
      case 'skill_demonstration':
        return 'warning';
      case 'testimonial':
        return 'secondary';
      case 'case_study':
        return 'default';
      case 'thought_leadership':
        return 'outline';
      default:
        return 'secondary';
    }
  };

  const formatStoryType = (type: string) => {
    return type.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'published':
        return 'success';
      case 'draft':
        return 'warning';
      case 'pending_review':
        return 'info';
      case 'archived':
        return 'secondary';
      case 'rejected':
        return 'destructive';
      default:
        return 'secondary';
    }
  };

  const truncateContent = (content: string, maxLength: number = 200) => {
    if (content.length <= maxLength) return content;
    return content.substring(0, maxLength) + '...';
  };

  const renderHighlights = () => {
    if (!showHighlights || !searchResult?.highlights) return null;

    const highlights = searchResult.highlights;
    const highlightEntries = Object.entries(highlights);
    
    if (highlightEntries.length === 0) return null;

    return (
      <div className="mt-3 p-2 bg-muted/50 rounded-md">
        <p className="text-xs font-medium text-muted-foreground mb-1">Matches:</p>
        <div className="space-y-1">
          {highlightEntries.map(([field, matches]) => (
            <div key={field} className="text-xs">
              <span className="font-medium capitalize">{field}:</span>
              <div className="ml-2">
                {matches.map((match, index) => (
                  <div
                    key={index}
                    className="text-muted-foreground"
                    dangerouslySetInnerHTML={{ __html: match }}
                  />
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  if (compact) {
    return (
      <Card 
        className={cn(
          "hover:shadow-md transition-shadow cursor-pointer",
          "border-l-4 border-l-blue-500/20"
        )}
        onClick={handleClick}
      >
        <CardContent className="p-4">
          <div className="flex items-start justify-between">
            <div className="flex-1 min-w-0">
              <div className="flex items-center space-x-2 mb-2">
                <Badge variant={getStoryTypeColor(story.story_type)} className="text-xs">
                  {getStoryTypeIcon(story.story_type)}
                  <span className="ml-1">{formatStoryType(story.story_type)}</span>
                </Badge>
                
                {story.is_ai_generated && (
                  <Badge variant="outline" className="text-xs">
                    <Brain className="w-3 h-3 mr-1" />
                    AI Generated
                  </Badge>
                )}
                
                {showScore && searchResult && (
                  <Badge variant="outline" className="text-xs">
                    <Target className="w-3 h-3 mr-1" />
                    {Math.round(searchResult.score * 100)}%
                  </Badge>
                )}
              </div>
              
              <CardTitle className="text-sm font-medium mb-1 truncate">
                {story.title}
              </CardTitle>
              
              <p className="text-xs text-muted-foreground mb-2 line-clamp-2">
                {truncateContent(story.content, 120)}
              </p>
              
              <div className="flex items-center space-x-3 text-xs text-muted-foreground">
                {searchResult?.member_names && searchResult.member_names.length > 0 && (
                  <span className="flex items-center">
                    <User className="w-3 h-3 mr-1" />
                    {searchResult.member_names.join(', ')}
                  </span>
                )}
                
                <span className="flex items-center">
                  <Calendar className="w-3 h-3 mr-1" />
                  {formatDate(story.created_at)}
                </span>
              </div>
            </div>
            
            <Badge variant={getStatusColor(story.status)} className="text-xs">
              {story.status.charAt(0).toUpperCase() + story.status.slice(1)}
            </Badge>
          </div>
          
          {story.skills.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-1">
              {story.skills.slice(0, 3).map((skill) => (
                <Badge key={skill} variant="secondary" className="text-xs">
                  {skill}
                </Badge>
              ))}
              {story.skills.length > 3 && (
                <Badge variant="outline" className="text-xs">
                  +{story.skills.length - 3} more
                </Badge>
              )}
            </div>
          )}
          
          {renderHighlights()}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card 
      className={cn(
        "hover:shadow-lg transition-all cursor-pointer",
        "border-l-4 border-l-blue-500/20 hover:border-l-blue-500/50"
      )}
      onClick={handleClick}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-2 mb-2">
              <Badge variant={getStoryTypeColor(story.story_type)}>
                {getStoryTypeIcon(story.story_type)}
                <span className="ml-1">{formatStoryType(story.story_type)}</span>
              </Badge>
              
              {story.is_ai_generated && (
                <Badge variant="outline">
                  <Brain className="w-3 h-3 mr-1" />
                  AI Generated
                </Badge>
              )}
              
              <Badge variant={getStatusColor(story.status)}>
                {story.status.charAt(0).toUpperCase() + story.status.slice(1)}
              </Badge>
            </div>
            
            <CardTitle className="text-lg mb-2">{story.title}</CardTitle>
            
            <div className="flex items-center space-x-4 text-sm text-muted-foreground">
              {searchResult?.member_names && searchResult.member_names.length > 0 && (
                <span className="flex items-center">
                  <User className="w-4 h-4 mr-1" />
                  {searchResult.member_names.join(', ')}
                </span>
              )}
              
              <span className="flex items-center">
                <Calendar className="w-4 h-4 mr-1" />
                {formatDate(story.created_at)}
              </span>
              
              {story.updated_at !== story.created_at && (
                <span className="flex items-center">
                  <Clock className="w-4 h-4 mr-1" />
                  Updated {formatDate(story.updated_at)}
                </span>
              )}
            </div>
          </div>
          
          {showScore && searchResult && (
            <div className="flex flex-col items-end space-y-2">
              <Badge variant="outline" className="text-sm">
                <Target className="w-3 h-3 mr-1" />
                {Math.round(searchResult.score * 100)}% match
              </Badge>
            </div>
          )}
        </div>
      </CardHeader>
      
      <CardContent className="pt-0">
        <div className="mb-4">
          <p className="text-sm text-muted-foreground leading-relaxed">
            {truncateContent(story.content, 300)}
          </p>
        </div>
        
        {story.skills.length > 0 && (
          <div className="mb-4">
            <p className="text-sm font-medium text-muted-foreground mb-2">Skills</p>
            <div className="flex flex-wrap gap-1">
              {story.skills.map((skill) => (
                <Badge key={skill} variant="secondary" className="text-xs">
                  {skill}
                </Badge>
              ))}
            </div>
          </div>
        )}
        
        {story.tags.length > 0 && (
          <div className="mb-4">
            <p className="text-sm font-medium text-muted-foreground mb-2">Tags</p>
            <div className="flex flex-wrap gap-1">
              {story.tags.map((tag) => (
                <Badge key={tag} variant="outline" className="text-xs">
                  <Tag className="w-3 h-3 mr-1" />
                  {tag}
                </Badge>
              ))}
            </div>
          </div>
        )}
        
        {showScore && searchResult && (
          <>
            <Separator className="my-4" />
            <div className="p-3 bg-muted/50 rounded-md">
              <p className="text-xs font-medium text-muted-foreground mb-2">Match Details</p>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div>
                  <span className="text-muted-foreground">Content:</span>
                  <span className="ml-2 font-medium">
                    {Math.round(searchResult.content_quality * 100)}%
                  </span>
                </div>
                <div>
                  <span className="text-muted-foreground">Engagement:</span>
                  <span className="ml-2 font-medium">
                    {Math.round(searchResult.engagement_score * 100)}%
                  </span>
                </div>
                <div>
                  <span className="text-muted-foreground">Recency:</span>
                  <span className="ml-2 font-medium">
                    {Math.round(searchResult.recency_score * 100)}%
                  </span>
                </div>
                <div>
                  <span className="text-muted-foreground">Overall:</span>
                  <span className="ml-2 font-medium">
                    {Math.round(searchResult.score * 100)}%
                  </span>
                </div>
              </div>
              
              {searchResult.skill_matches && searchResult.skill_matches.length > 0 && (
                <div className="mt-2">
                  <p className="text-xs text-muted-foreground mb-1">Skill Matches:</p>
                  <div className="flex flex-wrap gap-1">
                    {searchResult.skill_matches.map((skill) => (
                      <Badge key={skill} variant="success" className="text-xs">
                        {skill}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </>
        )}
        
        {renderHighlights()}
      </CardContent>
    </Card>
  );
};

export default StoryCard;