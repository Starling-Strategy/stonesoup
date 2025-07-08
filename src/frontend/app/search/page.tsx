import { Suspense } from 'react';
import SearchPage from '@/components/search/search-page';
import LoadingSkeleton from '@/components/ui/loading-skeleton';

interface SearchPageProps {
  searchParams: {
    q?: string;
    scope?: string;
  };
}

export default function Search({ searchParams }: SearchPageProps) {
  const query = searchParams.q || '';
  const scope = searchParams.scope || 'all';

  return (
    <Suspense fallback={<LoadingSkeleton type="search-results" />}>
      <SearchPage 
        initialQuery={query}
        initialScope={scope as any}
      />
    </Suspense>
  );
}

export function generateMetadata({ searchParams }: SearchPageProps) {
  const query = searchParams.q;
  
  return {
    title: query 
      ? `Search results for "${query}" - STONESOUP`
      : 'Search - STONESOUP',
    description: query
      ? `Find talent and expertise for "${query}" in the STONESOUP community`
      : 'Search for talent, skills, and stories in the STONESOUP community'
  };
}