'use client';

import React, { useState, useEffect, useCallback } from 'react';
// import { useUser } from '@clerk/nextjs';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import ErrorBoundary, { ErrorDisplay } from '@/components/ui/error-boundary';
import LoadingSkeleton from '@/components/ui/loading-skeleton';
import SearchBar from './search-bar';
import SearchResults from './search-results';
import { 
  Search, 
  Sparkles, 
  Users, 
  FileText,
  TrendingUp,
  Star,
  Zap
} from 'lucide-react';
import { 
  HybridSearchResponse,
  SearchPageProps,
  SearchScope,
  Member,
  Story,
  SearchState,
  SEARCH_DEFAULTS
} from '@/lib/types';
import { 
  performQuickSearch, 
  createClientApiClient,
  isApiError,
  getErrorMessage 
} from '@/lib/api';

const SearchPage: React.FC<SearchPageProps> = ({
  initialQuery = '',
  initialScope = SearchScope.ALL
}) => {
  // const { user, isLoaded: userLoaded } = useUser();
  const user = null;
  const userLoaded = true;
  
  const [searchState, setSearchState] = useState<SearchState>({
    query: initialQuery,
    results: null,
    loading: false,
    error: null,
    suggestions: [],
    hasSearched: false,
    filters: {},
    sort: SEARCH_DEFAULTS.sort,
    scope: initialScope
  });

  // Search function
  const handleSearch = useCallback(async (query: string, scope: SearchScope = SearchScope.ALL) => {
    if (!query.trim()) return;

    setSearchState(prev => ({
      ...prev,
      loading: true,
      error: null,
      query: query.trim(),
      scope
    }));

    try {
      // Set up API client with authentication
      const apiClient = await createClientApiClient();
      
      // Get token from Clerk if available
      if (user) {
        // Note: In a real implementation, you'd get the token from useAuth hook
        // This is a placeholder - the actual token retrieval depends on your setup
      }

      const results = await performQuickSearch(
        query.trim(),
        scope,
        SEARCH_DEFAULTS.page_size
      );

      setSearchState(prev => ({
        ...prev,
        results,
        loading: false,
        hasSearched: true,
        error: null
      }));

    } catch (error) {
      console.error('Search failed:', error);
      
      setSearchState(prev => ({
        ...prev,
        loading: false,
        error: getErrorMessage(error),
        results: null
      }));
    }
  }, [user]);

  // Handle member click
  const handleMemberClick = (member: Member) => {
    // Navigate to member profile or open modal
    console.log('Member clicked:', member);
    // Implementation would depend on your routing setup
    // e.g., router.push(`/members/${member.id}`);
  };

  // Handle story click
  const handleStoryClick = (story: Story) => {
    // Navigate to story detail or open modal
    console.log('Story clicked:', story);
    // Implementation would depend on your routing setup
    // e.g., router.push(`/stories/${story.id}`);
  };

  // Retry search
  const retrySearch = () => {
    if (searchState.query) {
      handleSearch(searchState.query, searchState.scope);
    }
  };

  // Clear error
  const clearError = () => {
    setSearchState(prev => ({ ...prev, error: null }));
  };

  // Initial search if query provided
  useEffect(() => {
    if (initialQuery && userLoaded) {
      handleSearch(initialQuery, initialScope);
    }
  }, [initialQuery, initialScope, userLoaded, handleSearch]);

  // Show loading skeleton while user data loads
  if (!userLoaded) {
    return <LoadingSkeleton type="search-bar" />;
  }

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-background">
        {/* Header */}
        <div className="border-b bg-card">
          <div className="container mx-auto px-4 py-6">
            <div className="text-center space-y-4">
              <div className="flex items-center justify-center space-x-2">
                <Search className="w-8 h-8 text-primary" />
                <h1 className="text-3xl font-bold">STONESOUP Search</h1>
                <Sparkles className="w-8 h-8 text-primary" />
              </div>
              <p className="text-muted-foreground max-w-2xl mx-auto">
                Discover talent and expertise in your community. Search through member profiles 
                and their stories to find exactly what you're looking for.
              </p>
            </div>
          </div>
        </div>

        {/* Search Interface */}
        <div className="container mx-auto px-4 py-8">
          <div className="space-y-8">
            {/* Search Bar */}
            <SearchBar
              onSearch={handleSearch}
              loading={searchState.loading}
              value={searchState.query}
              showSuggestions={true}
            />

            {/* Error Display */}
            {searchState.error && (
              <ErrorDisplay
                error={{ message: searchState.error }}
                onRetry={retrySearch}
                onDismiss={clearError}
              />
            )}

            {/* Search Stats */}
            {!searchState.hasSearched && !searchState.loading && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card className="text-center">
                  <CardContent className="p-6">
                    <Users className="w-12 h-12 mx-auto text-primary mb-4" />
                    <h3 className="font-semibold mb-2">Find Members</h3>
                    <p className="text-sm text-muted-foreground">
                      Search through member profiles, skills, and experience
                    </p>
                  </CardContent>
                </Card>
                
                <Card className="text-center">
                  <CardContent className="p-6">
                    <FileText className="w-12 h-12 mx-auto text-primary mb-4" />
                    <h3 className="font-semibold mb-2">Discover Stories</h3>
                    <p className="text-sm text-muted-foreground">
                      Explore achievements, case studies, and testimonials
                    </p>
                  </CardContent>
                </Card>
                
                <Card className="text-center">
                  <CardContent className="p-6">
                    <Zap className="w-12 h-12 mx-auto text-primary mb-4" />
                    <h3 className="font-semibold mb-2">AI-Powered</h3>
                    <p className="text-sm text-muted-foreground">
                      Get intelligent summaries and recommendations
                    </p>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Quick Search Suggestions */}
            {!searchState.hasSearched && !searchState.loading && (
              <Card>
                <CardContent className="p-6">
                  <h3 className="font-semibold mb-4 flex items-center">
                    <TrendingUp className="w-5 h-5 mr-2" />
                    Popular Searches
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {[
                      'Python developer',
                      'React engineer',
                      'Data scientist',
                      'Product manager',
                      'Designer',
                      'Machine learning',
                      'Full stack',
                      'DevOps'
                    ].map((suggestion) => (
                      <Button
                        key={suggestion}
                        variant="outline"
                        size="sm"
                        onClick={() => handleSearch(suggestion)}
                        className="text-xs"
                      >
                        {suggestion}
                      </Button>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Search Results */}
            {(searchState.results || searchState.loading) && (
              <SearchResults
                results={searchState.results!}
                loading={searchState.loading}
                onMemberClick={handleMemberClick}
                onStoryClick={handleStoryClick}
                showScores={false}
                showHighlights={true}
              />
            )}

            {/* Help Section */}
            {!searchState.hasSearched && !searchState.loading && (
              <Card className="bg-muted/50">
                <CardContent className="p-6">
                  <h3 className="font-semibold mb-4">Search Tips</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div>
                      <h4 className="font-medium mb-2">Member Search</h4>
                      <ul className="space-y-1 text-muted-foreground">
                        <li>• Search by name, title, or company</li>
                        <li>• Use skill keywords like "React" or "Python"</li>
                        <li>• Try location-based searches</li>
                      </ul>
                    </div>
                    <div>
                      <h4 className="font-medium mb-2">Story Search</h4>
                      <ul className="space-y-1 text-muted-foreground">
                        <li>• Find achievements and case studies</li>
                        <li>• Search by technology or methodology</li>
                        <li>• Discover thought leadership content</li>
                      </ul>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </ErrorBoundary>
  );
};

export default SearchPage;