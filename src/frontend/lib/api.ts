/**
 * API client for STONESOUP backend
 * Handles authentication, search requests, and member operations
 */

// Server imports are moved to api-server.ts to avoid client bundling issues
import { 
  SearchRequest, 
  QuickSearchRequest, 
  SearchResponse, 
  HybridSearchResponse, 
  SearchSuggestion, 
  AISummaryResponse, 
  Member, 
  MemberProfile,
  ApiResponse,
  SearchType,
  SearchScope,
  SearchSort,
  SEARCH_DEFAULTS
} from './types';

// Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_VERSION = 'v1';
const API_URL = `${API_BASE_URL}/api/${API_VERSION}`;

// Error classes
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?: string,
    public details?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export class AuthError extends ApiError {
  constructor(message: string = 'Authentication required') {
    super(message, 401, 'AUTH_ERROR');
    this.name = 'AuthError';
  }
}

export class NetworkError extends ApiError {
  constructor(message: string = 'Network error occurred') {
    super(message, 0, 'NETWORK_ERROR');
    this.name = 'NetworkError';
  }
}

// API Client class
export class ApiClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string = API_URL) {
    this.baseUrl = baseUrl;
  }

  // Set authentication token
  setToken(token: string) {
    this.token = token;
  }

  // Get authentication headers
  private getAuthHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    // Only add auth header if we have a token AND Clerk is configured
    // In demo mode (no CLERK_PUBLISHABLE_KEY), skip auth header
    if (this.token && process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    return headers;
  }

  // Make API request with error handling
  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${endpoint}`;
    
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          ...this.getAuthHeaders(),
          ...options.headers,
        },
      });

      // Handle different response types
      let data: any;
      const contentType = response.headers.get('content-type');
      
      if (contentType?.includes('application/json')) {
        data = await response.json();
      } else {
        data = await response.text();
      }

      if (!response.ok) {
        // Handle specific error cases
        if (response.status === 401) {
          throw new AuthError(data.message || 'Authentication required');
        }
        
        throw new ApiError(
          data.message || `HTTP ${response.status}: ${response.statusText}`,
          response.status,
          data.code,
          data.details
        );
      }

      return {
        data,
        success: true,
        status: response.status,
      };
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new NetworkError('Failed to connect to server');
      }
      
      throw new ApiError(
        error instanceof Error ? error.message : 'Unknown error occurred',
        0,
        'UNKNOWN_ERROR'
      );
    }
  }

  // GET request
  private async get<T>(endpoint: string, params?: Record<string, any>): Promise<ApiResponse<T>> {
    let url = endpoint;
    
    if (params) {
      const searchParams = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          searchParams.append(key, String(value));
        }
      });
      
      if (searchParams.toString()) {
        url += `?${searchParams.toString()}`;
      }
    }

    return this.makeRequest<T>(url, { method: 'GET' });
  }

  // POST request
  private async post<T>(endpoint: string, data?: any): Promise<ApiResponse<T>> {
    return this.makeRequest<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  // PUT request
  private async put<T>(endpoint: string, data?: any): Promise<ApiResponse<T>> {
    return this.makeRequest<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  // DELETE request
  private async delete<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.makeRequest<T>(endpoint, { method: 'DELETE' });
  }

  // Search endpoints
  async search(request: SearchRequest): Promise<SearchResponse | HybridSearchResponse> {
    const response = await this.post<SearchResponse | HybridSearchResponse>('/search', request);
    if (!response.data) {
      throw new ApiError('No search results returned', 500);
    }
    return response.data;
  }

  async quickSearch(request: QuickSearchRequest): Promise<HybridSearchResponse> {
    const response = await this.post<HybridSearchResponse>('/search/quick', request);
    if (!response.data) {
      throw new ApiError('No search results returned', 500);
    }
    return response.data;
  }

  async getSearchSuggestions(query: string, limit: number = 10): Promise<SearchSuggestion[]> {
    const response = await this.get<SearchSuggestion[]>('/search/suggestions', {
      q: query,
      limit,
    });
    return response.data || [];
  }

  async generateSearchSummary(
    request: SearchRequest,
    summaryType: string = 'overview'
  ): Promise<AISummaryResponse> {
    const response = await this.post<AISummaryResponse>('/search/summary', request, {
      summary_type: summaryType,
    });
    if (!response.data) {
      throw new ApiError('No summary generated', 500);
    }
    return response.data;
  }

  async getSearchAnalytics(days: number = 30): Promise<Record<string, any>> {
    const response = await this.get<Record<string, any>>('/search/analytics', { days });
    return response.data || {};
  }

  // Legacy search endpoints
  async searchMembers(
    query: string,
    skip: number = 0,
    limit: number = 50
  ): Promise<SearchResponse> {
    const response = await this.get<SearchResponse>('/search/members', {
      q: query,
      skip,
      limit,
    });
    if (!response.data) {
      throw new ApiError('No search results returned', 500);
    }
    return response.data;
  }

  async searchStories(
    query: string,
    skip: number = 0,
    limit: number = 50
  ): Promise<SearchResponse> {
    const response = await this.get<SearchResponse>('/search/stories', {
      q: query,
      skip,
      limit,
    });
    if (!response.data) {
      throw new ApiError('No search results returned', 500);
    }
    return response.data;
  }

  // Member endpoints
  async getMember(id: string): Promise<Member> {
    const response = await this.get<Member>(`/members/${id}`);
    if (!response.data) {
      throw new ApiError('Member not found', 404);
    }
    return response.data;
  }

  async getMemberProfile(id: string): Promise<MemberProfile> {
    const response = await this.get<MemberProfile>(`/members/${id}/profile`);
    if (!response.data) {
      throw new ApiError('Member profile not found', 404);
    }
    return response.data;
  }

  async getMembers(
    page: number = 1,
    pageSize: number = 20,
    filters?: Record<string, any>
  ): Promise<{ members: Member[]; total: number; hasNext: boolean }> {
    const params = {
      page,
      page_size: pageSize,
      ...filters,
    };

    const response = await this.get<any>('/members', params);
    
    return {
      members: response.data?.items || [],
      total: response.data?.total || 0,
      hasNext: response.data?.has_next || false,
    };
  }

  // Health check
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    const response = await this.get<{ status: string; timestamp: string }>('/health');
    return response.data || { status: 'unknown', timestamp: new Date().toISOString() };
  }
}

// Singleton instance
export const apiClient = new ApiClient();

// Server-side API functions are moved to api-server.ts to avoid client bundling issues
// This keeps the client bundle clean from server-only dependencies

// Client-side API functions (for React components)
export async function createClientApiClient(): Promise<ApiClient> {
  const client = new ApiClient();
  
  // For client-side, we'll get the token from Clerk's useAuth hook
  // This will be handled in the component that uses the API client
  
  return client;
}

// Utility functions for common search operations
export async function performQuickSearch(
  query: string,
  scope: SearchScope = SearchScope.ALL,
  limit: number = 20
): Promise<HybridSearchResponse> {
  const client = await createClientApiClient();
  return client.quickSearch({ query, scope, limit });
}

export async function performAdvancedSearch(
  query: string,
  options: Partial<SearchRequest> = {}
): Promise<SearchResponse | HybridSearchResponse> {
  const client = await createClientApiClient();
  
  const request: SearchRequest = {
    query,
    ...SEARCH_DEFAULTS,
    ...options,
  };
  
  return client.search(request);
}

export async function getSuggestions(
  query: string,
  limit: number = 10
): Promise<SearchSuggestion[]> {
  if (!query.trim()) {
    return [];
  }
  
  try {
    const client = await createClientApiClient();
    return await client.getSearchSuggestions(query, limit);
  } catch (error) {
    console.warn('Failed to get search suggestions:', error);
    return [];
  }
}

// Error handling utilities
export function isApiError(error: any): error is ApiError {
  return error instanceof ApiError;
}

export function isAuthError(error: any): error is AuthError {
  return error instanceof AuthError;
}

export function isNetworkError(error: any): error is NetworkError {
  return error instanceof NetworkError;
}

export function getErrorMessage(error: any): string {
  if (isApiError(error)) {
    return error.message;
  }
  
  if (error instanceof Error) {
    return error.message;
  }
  
  return 'An unknown error occurred';
}

export function getErrorCode(error: any): string | undefined {
  if (isApiError(error)) {
    return error.code;
  }
  
  return undefined;
}

// Retry utility for failed requests
export async function retryApiCall<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  delayMs: number = 1000
): Promise<T> {
  let lastError: any;
  
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      
      // Don't retry auth errors or 4xx errors
      if (isAuthError(error) || (isApiError(error) && error.status >= 400 && error.status < 500)) {
        throw error;
      }
      
      // Wait before retrying
      if (i < maxRetries - 1) {
        await new Promise(resolve => setTimeout(resolve, delayMs * (i + 1)));
      }
    }
  }
  
  throw lastError;
}