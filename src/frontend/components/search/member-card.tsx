'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Button } from '@/components/ui/button';
import { 
  MapPin, 
  Building, 
  Clock, 
  DollarSign, 
  Star, 
  ExternalLink,
  Github,
  Linkedin,
  Globe,
  Mail,
  Calendar,
  TrendingUp,
  Award,
  Target
} from 'lucide-react';
import { Member, MemberSearchResult, MemberCardProps } from '@/lib/types';
import { cn } from '@/lib/utils';

const MemberCard: React.FC<MemberCardProps> = ({
  member,
  searchResult,
  onClick,
  showScore = false,
  showHighlights = false,
  compact = false
}) => {
  const handleClick = () => {
    if (onClick) {
      onClick(member);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'available':
        return 'success';
      case 'busy':
        return 'warning';
      case 'unavailable':
        return 'destructive';
      default:
        return 'secondary';
    }
  };

  const getAvailabilityText = () => {
    if (!member.is_available) return 'Unavailable';
    if (searchResult?.availability_status) {
      return searchResult.availability_status.charAt(0).toUpperCase() + 
             searchResult.availability_status.slice(1);
    }
    return 'Available';
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
          "border-l-4 border-l-primary/20"
        )}
        onClick={handleClick}
      >
        <CardContent className="p-4">
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-3 flex-1">
              <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                {member.avatar_url ? (
                  <img 
                    src={member.avatar_url} 
                    alt={member.name}
                    className="w-10 h-10 rounded-full object-cover"
                  />
                ) : (
                  <span className="text-sm font-medium text-primary">
                    {member.name.charAt(0)}
                  </span>
                )}
              </div>
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2">
                  <p className="font-medium text-sm truncate">{member.name}</p>
                  {member.is_verified && (
                    <Badge variant="info" className="text-xs">
                      <Award className="w-3 h-3 mr-1" />
                      Verified
                    </Badge>
                  )}
                </div>
                
                <div className="flex items-center space-x-3 text-xs text-muted-foreground mt-1">
                  {member.title && (
                    <span className="truncate">{member.title}</span>
                  )}
                  {member.company && (
                    <span className="truncate flex items-center">
                      <Building className="w-3 h-3 mr-1" />
                      {member.company}
                    </span>
                  )}
                  {member.location && (
                    <span className="truncate flex items-center">
                      <MapPin className="w-3 h-3 mr-1" />
                      {member.location}
                    </span>
                  )}
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              {showScore && searchResult && (
                <Badge variant="outline" className="text-xs">
                  {Math.round(searchResult.score * 100)}%
                </Badge>
              )}
              
              <Badge variant={getStatusColor(getAvailabilityText())} className="text-xs">
                {getAvailabilityText()}
              </Badge>
            </div>
          </div>
          
          {member.skills.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-1">
              {member.skills.slice(0, 3).map((skill) => (
                <Badge key={skill} variant="secondary" className="text-xs">
                  {skill}
                </Badge>
              ))}
              {member.skills.length > 3 && (
                <Badge variant="outline" className="text-xs">
                  +{member.skills.length - 3} more
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
        "border-l-4 border-l-primary/20 hover:border-l-primary/50"
      )}
      onClick={handleClick}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center">
              {member.avatar_url ? (
                <img 
                  src={member.avatar_url} 
                  alt={member.name}
                  className="w-16 h-16 rounded-full object-cover"
                />
              ) : (
                <span className="text-xl font-medium text-primary">
                  {member.name.charAt(0)}
                </span>
              )}
            </div>
            
            <div className="flex-1">
              <div className="flex items-center space-x-2">
                <CardTitle className="text-xl">{member.name}</CardTitle>
                {member.is_verified && (
                  <Badge variant="info">
                    <Award className="w-3 h-3 mr-1" />
                    Verified
                  </Badge>
                )}
              </div>
              
              {member.title && (
                <p className="text-muted-foreground font-medium">{member.title}</p>
              )}
              
              <div className="flex items-center space-x-4 text-sm text-muted-foreground mt-1">
                {member.company && (
                  <span className="flex items-center">
                    <Building className="w-4 h-4 mr-1" />
                    {member.company}
                  </span>
                )}
                {member.location && (
                  <span className="flex items-center">
                    <MapPin className="w-4 h-4 mr-1" />
                    {member.location}
                  </span>
                )}
                {member.years_of_experience && (
                  <span className="flex items-center">
                    <Clock className="w-4 h-4 mr-1" />
                    {member.years_of_experience} years
                  </span>
                )}
              </div>
            </div>
          </div>
          
          <div className="flex flex-col items-end space-y-2">
            {showScore && searchResult && (
              <div className="flex items-center space-x-2">
                <Badge variant="outline" className="text-sm">
                  <Target className="w-3 h-3 mr-1" />
                  {Math.round(searchResult.score * 100)}% match
                </Badge>
              </div>
            )}
            
            <Badge variant={getStatusColor(getAvailabilityText())}>
              {getAvailabilityText()}
            </Badge>
            
            {member.hourly_rate && (
              <Badge variant="outline" className="text-sm">
                <DollarSign className="w-3 h-3 mr-1" />
                {formatCurrency(member.hourly_rate)}/hr
              </Badge>
            )}
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="pt-0">
        {member.bio && (
          <div className="mb-4">
            <p className="text-sm text-muted-foreground leading-relaxed">
              {member.bio}
            </p>
          </div>
        )}
        
        {member.skills.length > 0 && (
          <div className="mb-4">
            <p className="text-sm font-medium text-muted-foreground mb-2">Skills</p>
            <div className="flex flex-wrap gap-1">
              {member.skills.map((skill) => (
                <Badge key={skill} variant="secondary" className="text-xs">
                  {skill}
                </Badge>
              ))}
            </div>
          </div>
        )}
        
        {member.expertise_areas.length > 0 && (
          <div className="mb-4">
            <p className="text-sm font-medium text-muted-foreground mb-2">Expertise</p>
            <div className="flex flex-wrap gap-1">
              {member.expertise_areas.map((area) => (
                <Badge key={area} variant="outline" className="text-xs">
                  {area}
                </Badge>
              ))}
            </div>
          </div>
        )}
        
        <Separator className="my-4" />
        
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            {member.linkedin_url && (
              <Button variant="ghost" size="sm" className="p-2">
                <Linkedin className="w-4 h-4" />
              </Button>
            )}
            {member.github_url && (
              <Button variant="ghost" size="sm" className="p-2">
                <Github className="w-4 h-4" />
              </Button>
            )}
            {member.website_url && (
              <Button variant="ghost" size="sm" className="p-2">
                <Globe className="w-4 h-4" />
              </Button>
            )}
            {member.email && (
              <Button variant="ghost" size="sm" className="p-2">
                <Mail className="w-4 h-4" />
              </Button>
            )}
          </div>
          
          <div className="flex items-center space-x-4 text-xs text-muted-foreground">
            <span className="flex items-center">
              <Calendar className="w-3 h-3 mr-1" />
              Joined {formatDate(member.created_at)}
            </span>
            {member.story_count > 0 && (
              <span className="flex items-center">
                <TrendingUp className="w-3 h-3 mr-1" />
                {member.story_count} stories
              </span>
            )}
          </div>
        </div>
        
        {showScore && searchResult && (
          <div className="mt-4 p-3 bg-muted/50 rounded-md">
            <p className="text-xs font-medium text-muted-foreground mb-2">Match Details</p>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div>
                <span className="text-muted-foreground">Profile:</span>
                <span className="ml-2 font-medium">
                  {Math.round(searchResult.profile_completeness * 100)}%
                </span>
              </div>
              <div>
                <span className="text-muted-foreground">Skills:</span>
                <span className="ml-2 font-medium">
                  {Math.round(searchResult.skill_match * 100)}%
                </span>
              </div>
              <div>
                <span className="text-muted-foreground">Experience:</span>
                <span className="ml-2 font-medium">
                  {Math.round(searchResult.experience_relevance * 100)}%
                </span>
              </div>
              <div>
                <span className="text-muted-foreground">Overall:</span>
                <span className="ml-2 font-medium">
                  {Math.round(searchResult.score * 100)}%
                </span>
              </div>
            </div>
          </div>
        )}
        
        {renderHighlights()}
      </CardContent>
    </Card>
  );
};

export default MemberCard;