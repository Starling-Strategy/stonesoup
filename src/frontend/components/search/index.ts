// Search component exports
export { default as SearchPage } from './search-page';
export { default as SearchBar } from './search-bar';
export { default as SearchResults } from './search-results';
export { default as MemberCard } from './member-card';
export { default as StoryCard } from './story-card';

// Re-export types for convenience
export type {
  SearchPageProps,
  SearchBarProps,
  SearchResultsProps,
  MemberCardProps,
  StoryCardProps
} from '../../lib/types';