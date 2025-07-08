'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import LoadingSpinner from '@/components/ui/loading-spinner';
import { 
  Search, 
  Filter, 
  X, 
  Clock,
  TrendingUp,
  Users,
  FileText,
  Zap,
  ChevronDown
} from 'lucide-react';
import { 
  SearchScope, 
  SearchSuggestion, 
  SearchBarProps 
} from '@/lib/types';
import { cn } from '@/lib/utils';
import { getSuggestions } from '@/lib/api';

const SearchBar: React.FC<SearchBarProps> = ({
  onSearch,
  loading = false,
  placeholder = "Search for talent, skills, or stories...",
  suggestions = [],
  showSuggestions = true,
  value = "",
  onChange
}) => {
  const [inputValue, setInputValue] = useState(value);
  const [selectedScope, setSelectedScope] = useState<SearchScope>(SearchScope.ALL);
  const [showScopeMenu, setShowScopeMenu] = useState(false);
  const [showSuggestionsDropdown, setShowSuggestionsDropdown] = useState(false);
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);
  const [currentSuggestions, setCurrentSuggestions] = useState<SearchSuggestion[]>(suggestions);
  const [selectedSuggestionIndex, setSelectedSuggestionIndex] = useState(-1);
  
  const inputRef = useRef<HTMLInputElement>(null);
  const suggestionsRef = useRef<HTMLDivElement>(null);
  const scopeMenuRef = useRef<HTMLDivElement>(null);
  const debounceRef = useRef<NodeJS.Timeout>();

  // Handle input value changes
  useEffect(() => {
    if (onChange) {
      onChange(inputValue);
    }
  }, [inputValue, onChange]);

  // Debounced suggestions fetch
  const fetchSuggestions = useCallback(async (query: string) => {
    if (!query.trim() || !showSuggestions) {
      setCurrentSuggestions([]);
      return;
    }

    setLoadingSuggestions(true);
    
    try {
      const newSuggestions = await getSuggestions(query, 8);
      setCurrentSuggestions(newSuggestions);
    } catch (error) {
      console.warn('Failed to fetch suggestions:', error);
      setCurrentSuggestions([]);
    } finally {
      setLoadingSuggestions(false);
    }
  }, [showSuggestions]);

  // Debounce suggestions
  useEffect(() => {
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    debounceRef.current = setTimeout(() => {
      fetchSuggestions(inputValue);
    }, 300);

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, [inputValue, fetchSuggestions]);

  // Handle clicks outside to close dropdowns
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        suggestionsRef.current && 
        !suggestionsRef.current.contains(event.target as Node) &&
        !inputRef.current?.contains(event.target as Node)
      ) {
        setShowSuggestionsDropdown(false);
        setSelectedSuggestionIndex(-1);
      }
      
      if (
        scopeMenuRef.current && 
        !scopeMenuRef.current.contains(event.target as Node)
      ) {
        setShowScopeMenu(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setInputValue(newValue);
    setShowSuggestionsDropdown(true);
    setSelectedSuggestionIndex(-1);
  };

  const handleInputFocus = () => {
    if (currentSuggestions.length > 0) {
      setShowSuggestionsDropdown(true);
    }
  };

  const handleSearch = () => {
    if (inputValue.trim()) {
      onSearch(inputValue.trim(), selectedScope);
      setShowSuggestionsDropdown(false);
      setSelectedSuggestionIndex(-1);
    }
  };

  const handleSuggestionClick = (suggestion: SearchSuggestion) => {
    setInputValue(suggestion.query);
    setShowSuggestionsDropdown(false);
    setSelectedSuggestionIndex(-1);
    onSearch(suggestion.query, selectedScope);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!showSuggestionsDropdown || currentSuggestions.length === 0) {
      if (e.key === 'Enter') {
        handleSearch();
      }
      return;
    }

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedSuggestionIndex(prev => 
          prev < currentSuggestions.length - 1 ? prev + 1 : prev
        );
        break;
      
      case 'ArrowUp':
        e.preventDefault();
        setSelectedSuggestionIndex(prev => prev > 0 ? prev - 1 : -1);
        break;
      
      case 'Enter':
        e.preventDefault();
        if (selectedSuggestionIndex >= 0) {
          handleSuggestionClick(currentSuggestions[selectedSuggestionIndex]);
        } else {
          handleSearch();
        }
        break;
      
      case 'Escape':
        setShowSuggestionsDropdown(false);
        setSelectedSuggestionIndex(-1);
        break;
    }
  };

  const clearInput = () => {
    setInputValue('');
    setShowSuggestionsDropdown(false);
    setSelectedSuggestionIndex(-1);
    inputRef.current?.focus();
  };

  const getScopeIcon = (scope: SearchScope) => {
    switch (scope) {
      case SearchScope.MEMBERS:
        return <Users className="w-4 h-4" />;
      case SearchScope.STORIES:
        return <FileText className="w-4 h-4" />;
      default:
        return <Search className="w-4 h-4" />;
    }
  };

  const getScopeLabel = (scope: SearchScope) => {
    switch (scope) {
      case SearchScope.MEMBERS:
        return 'Members';
      case SearchScope.STORIES:
        return 'Stories';
      default:
        return 'All';
    }
  };

  const getSuggestionIcon = (type: string) => {
    switch (type) {
      case 'trending':
        return <TrendingUp className="w-4 h-4 text-orange-500" />;
      case 'popular':
        return <Zap className="w-4 h-4 text-yellow-500" />;
      case 'recent':
        return <Clock className="w-4 h-4 text-blue-500" />;
      default:
        return <Search className="w-4 h-4 text-muted-foreground" />;
    }
  };

  const formatSuggestionType = (type: string) => {
    switch (type) {
      case 'completion':
        return 'Complete';
      case 'correction':
        return 'Did you mean';
      case 'related':
        return 'Related';
      case 'trending':
        return 'Trending';
      case 'popular':
        return 'Popular';
      default:
        return type;
    }
  };

  return (
    <div className="relative w-full max-w-4xl mx-auto">
      {/* Main search input */}
      <div className="relative flex items-center">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-muted-foreground" />
          
          <Input
            ref={inputRef}
            type="text"
            placeholder={placeholder}
            value={inputValue}
            onChange={handleInputChange}
            onFocus={handleInputFocus}
            onKeyDown={handleKeyDown}
            className="pl-10 pr-10 h-12 text-base"
            disabled={loading}
          />
          
          {inputValue && (
            <Button
              variant="ghost"
              size="sm"
              onClick={clearInput}
              className="absolute right-2 top-1/2 transform -translate-y-1/2 p-1 h-auto"
            >
              <X className="w-4 h-4" />
            </Button>
          )}
        </div>
        
        {/* Scope selector */}
        <div className="relative ml-2" ref={scopeMenuRef}>
          <Button
            variant="outline"
            onClick={() => setShowScopeMenu(!showScopeMenu)}
            className="h-12 px-4 flex items-center space-x-2"
            disabled={loading}
          >
            {getScopeIcon(selectedScope)}
            <span className="hidden sm:inline">{getScopeLabel(selectedScope)}</span>
            <ChevronDown className="w-4 h-4" />
          </Button>
          
          {showScopeMenu && (
            <Card className="absolute top-full mt-1 right-0 z-50 w-40">
              <CardContent className="p-1">
                {Object.values(SearchScope).map((scope) => (
                  <Button
                    key={scope}
                    variant="ghost"
                    onClick={() => {
                      setSelectedScope(scope);
                      setShowScopeMenu(false);
                    }}
                    className={cn(
                      "w-full justify-start text-left",
                      selectedScope === scope && "bg-muted"
                    )}
                  >
                    {getScopeIcon(scope)}
                    <span className="ml-2">{getScopeLabel(scope)}</span>
                  </Button>
                ))}
              </CardContent>
            </Card>
          )}
        </div>
        
        {/* Search button */}
        <Button
          onClick={handleSearch}
          disabled={!inputValue.trim() || loading}
          className="ml-2 h-12 px-6"
        >
          {loading ? (
            <LoadingSpinner size="sm" />
          ) : (
            <>
              <Search className="w-4 h-4 mr-2" />
              <span className="hidden sm:inline">Search</span>
            </>
          )}
        </Button>
      </div>
      
      {/* Suggestions dropdown */}
      {showSuggestionsDropdown && showSuggestions && (
        <Card 
          ref={suggestionsRef}
          className="absolute top-full mt-2 left-0 right-0 z-50 max-h-96 overflow-y-auto"
        >
          <CardContent className="p-2">
            {loadingSuggestions ? (
              <div className="flex items-center justify-center p-4">
                <LoadingSpinner size="sm" />
                <span className="ml-2 text-sm text-muted-foreground">
                  Finding suggestions...
                </span>
              </div>
            ) : currentSuggestions.length > 0 ? (
              <div className="space-y-1">
                {currentSuggestions.map((suggestion, index) => (
                  <Button
                    key={`${suggestion.query}-${index}`}
                    variant="ghost"
                    onClick={() => handleSuggestionClick(suggestion)}
                    className={cn(
                      "w-full justify-start text-left p-3 h-auto",
                      selectedSuggestionIndex === index && "bg-muted"
                    )}
                  >
                    <div className="flex items-center space-x-3 w-full">
                      {getSuggestionIcon(suggestion.type)}
                      
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">
                          {suggestion.query}
                        </p>
                        <div className="flex items-center space-x-2 mt-1">
                          <Badge variant="outline" className="text-xs">
                            {formatSuggestionType(suggestion.type)}
                          </Badge>
                          {suggestion.category && (
                            <Badge variant="secondary" className="text-xs">
                              {suggestion.category}
                            </Badge>
                          )}
                          {suggestion.popular && (
                            <Badge variant="success" className="text-xs">
                              Popular
                            </Badge>
                          )}
                        </div>
                      </div>
                      
                      <div className="text-xs text-muted-foreground">
                        {suggestion.result_count} results
                      </div>
                    </div>
                  </Button>
                ))}
              </div>
            ) : inputValue.trim() && (
              <div className="p-4 text-center text-sm text-muted-foreground">
                No suggestions found
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default SearchBar;