/**
 * TypeScript types for STONESOUP frontend application
 * Based on backend API schemas and Pydantic models
 */

// Base types
export interface BaseResponse {
  success: boolean;
  message?: string;
  timestamp?: string;
}

export interface ScoreExplanation {
  total_score: number;
  semantic_score?: number;
  text_score?: number;
  popularity_score?: number;
  recency_score?: number;
  explanation: string;
}

export interface SearchMetadata {
  query: string;
  total_results: number;
  execution_time_ms: number;
  search_type: string;
  semantic_threshold?: number;
  filters_applied?: Record<string, any>;
  page: number;
  page_size: number;
  generated_at: string;
}

// Enums
export enum SearchType {
  TEXT = 'text',
  SEMANTIC = 'semantic',
  HYBRID = 'hybrid'
}

export enum SearchScope {
  ALL = 'all',
  STORIES = 'stories',
  MEMBERS = 'members'
}

export enum SearchSort {
  RELEVANCE = 'relevance',
  RECENT = 'recent',
  POPULAR = 'popular',
  ALPHABETICAL = 'alphabetical'
}

export enum MemberStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  PENDING = 'pending',
  ARCHIVED = 'archived'
}

// Member types
export interface Member {
  id: string;
  email: string;
  name: string;
  username?: string;
  bio?: string;
  location?: string;
  timezone?: string;
  avatar_url?: string;
  title?: string;
  company?: string;
  years_of_experience?: number;
  hourly_rate?: number;
  skills: string[];
  expertise_areas: string[];
  industries: string[];
  linkedin_url?: string;
  github_url?: string;
  twitter_url?: string;
  website_url?: string;
  portfolio_urls: string[];
  is_active: boolean;
  is_verified: boolean;
  is_available: boolean;
  profile_completed: boolean;
  has_embedding: boolean;
  created_at: string;
  updated_at: string;
  last_active_at?: string;
  cauldron_id: string;
  profile_url?: string;
  story_count: number;
}

export interface MemberProfile extends Member {
  extra_metadata: Record<string, any>;
  recent_stories: any[];
  total_views: number;
  total_likes: number;
  engagement_score: number;
  response_rate?: number;
  top_skills: string[];
  skill_endorsements: Record<string, number>;
}

// Story types
export interface Story {
  id: string;
  title: string;
  content: string;
  story_type: string;
  status: string;
  is_ai_generated: boolean;
  member_id: string;
  cauldron_id: string;
  created_at: string;
  updated_at: string;
  member_names: string[];
  skills: string[];
  tags: string[];
  metadata: Record<string, any>;
  embedding_status: string;
  has_embedding: boolean;
}

// Search types
export interface SearchFilters {
  story_types?: string[];
  story_statuses?: string[];
  member_skills?: string[];
  member_locations?: string[];
  member_companies?: string[];
  date_from?: string;
  date_to?: string;
  ai_generated_only?: boolean;
  verified_members_only?: boolean;
  available_members_only?: boolean;
  min_experience?: number;
  max_experience?: number;
  min_rate?: number;
  max_rate?: number;
  tags?: string[];
  skills?: string[];
  industries?: string[];
}

export interface SearchRequest {
  query: string;
  search_type?: SearchType;
  scope?: SearchScope;
  page?: number;
  page_size?: number;
  sort?: SearchSort;
  filters?: SearchFilters;
  semantic_threshold?: number;
  boost_recent?: boolean;
  boost_popular?: boolean;
  generate_summary?: boolean;
  include_suggestions?: boolean;
  explain_scores?: boolean;
  include_highlights?: boolean;
}

export interface QuickSearchRequest {
  query: string;
  scope?: SearchScope;
  limit?: number;
}

export interface SearchResult {
  id: string;
  type: string;
  title: string;
  content: string;
  score: number;
  score_explanation?: ScoreExplanation;
  highlights?: Record<string, string[]>;
  created_at: string;
  updated_at: string;
  cauldron_id: string;
}

export interface MemberSearchResult extends SearchResult {
  type: 'member';
  member: Member;
  profile_completeness: number;
  skill_match: number;
  experience_relevance: number;
  availability_status: string;
  last_active?: string;
}

export interface StorySearchResult extends SearchResult {
  type: 'story';
  story: Story;
  content_quality: number;
  engagement_score: number;
  recency_score: number;
  member_names: string[];
  skill_matches: string[];
}

export interface SearchResponse {
  results: (MemberSearchResult | StorySearchResult)[];
  total: number;
  page: number;
  page_size: number;
  has_next: boolean;
  has_previous: boolean;
  search_metadata: SearchMetadata;
  result_counts: Record<string, number>;
  suggestions?: string[];
  ai_summary?: string;
}

export interface HybridSearchResponse extends BaseResponse {
  story_results: StorySearchResult[];
  story_total: number;
  member_results: MemberSearchResult[];
  member_total: number;
  search_metadata: SearchMetadata;
  hybrid_explanation: string;
  suggestions: string[];
  ai_summary?: string;
}

export interface SearchSuggestion {
  query: string;
  type: string;
  score: number;
  category?: string;
  result_count: number;
  popular: boolean;
}

export interface AISummaryResponse {
  summary: string;
  key_insights: string[];
  confidence_score: number;
  model_used: string;
  generation_time: number;
  result_count: number;
  query: string;
  summary_type: string;
  generated_at: string;
}

// UI State types
export interface SearchState {
  query: string;
  results: HybridSearchResponse | null;
  loading: boolean;
  error: string | null;
  suggestions: SearchSuggestion[];
  hasSearched: boolean;
  filters: SearchFilters;
  sort: SearchSort;
  scope: SearchScope;
}

export interface LoadingState {
  isLoading: boolean;
  message?: string;
  progress?: number;
}

export interface ErrorState {
  hasError: boolean;
  message: string;
  code?: string;
  details?: any;
}

// API Response types
export interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  success: boolean;
  status: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  has_next: boolean;
  has_previous: boolean;
}

// Auth types (from Clerk)
export interface User {
  id: string;
  email: string;
  firstName?: string;
  lastName?: string;
  username?: string;
  imageUrl?: string;
  createdAt: number;
  updatedAt: number;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  cauldronId?: string;
}

// Component props types
export interface SearchPageProps {
  initialQuery?: string;
  initialScope?: SearchScope;
}

export interface MemberCardProps {
  member: Member;
  searchResult?: MemberSearchResult;
  onClick?: (member: Member) => void;
  showScore?: boolean;
  showHighlights?: boolean;
  compact?: boolean;
}

export interface StoryCardProps {
  story: Story;
  searchResult?: StorySearchResult;
  onClick?: (story: Story) => void;
  showScore?: boolean;
  showHighlights?: boolean;
  compact?: boolean;
}

export interface SearchBarProps {
  onSearch: (query: string, scope?: SearchScope) => void;
  loading?: boolean;
  placeholder?: string;
  suggestions?: SearchSuggestion[];
  showSuggestions?: boolean;
  value?: string;
  onChange?: (value: string) => void;
}

export interface SearchResultsProps {
  results: HybridSearchResponse;
  loading?: boolean;
  onMemberClick?: (member: Member) => void;
  onStoryClick?: (story: Story) => void;
  showScores?: boolean;
  showHighlights?: boolean;
}

export interface SearchFiltersProps {
  filters: SearchFilters;
  onChange: (filters: SearchFilters) => void;
  onReset: () => void;
  loading?: boolean;
  memberOptions?: {
    skills: string[];
    locations: string[];
    companies: string[];
  };
}

export interface EmptyStateProps {
  title: string;
  description: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  icon?: React.ReactNode;
}

// Utility types
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

export type SearchResultType = MemberSearchResult | StorySearchResult;

// Constants
export const SEARCH_DEFAULTS = {
  page_size: 20,
  search_type: SearchType.HYBRID,
  scope: SearchScope.ALL,
  sort: SearchSort.RELEVANCE,
  semantic_threshold: 0.7,
  boost_recent: true,
  boost_popular: true,
  generate_summary: true,
  include_suggestions: true,
  include_highlights: true
} as const;

export const MEMBER_CARD_VARIANTS = {
  default: 'default',
  compact: 'compact',
  detailed: 'detailed'
} as const;

export const STORY_CARD_VARIANTS = {
  default: 'default',
  compact: 'compact',
  detailed: 'detailed'
} as const;