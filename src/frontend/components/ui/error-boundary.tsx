'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { AlertCircle, RefreshCw, Home, Bug } from 'lucide-react';

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: React.ErrorInfo | null;
}

interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ComponentType<ErrorFallbackProps>;
}

interface ErrorFallbackProps {
  error: Error;
  resetError: () => void;
}

class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return {
      hasError: true,
      error,
      errorInfo: null
    };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    this.setState({
      error,
      errorInfo
    });
    
    // Log error to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('Error caught by boundary:', error, errorInfo);
    }
  }

  resetError = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    });
  };

  render() {
    if (this.state.hasError) {
      const FallbackComponent = this.props.fallback || DefaultErrorFallback;
      return (
        <FallbackComponent 
          error={this.state.error!} 
          resetError={this.resetError}
        />
      );
    }

    return this.props.children;
  }
}

const DefaultErrorFallback: React.FC<ErrorFallbackProps> = ({ error, resetError }) => {
  const isDevelopment = process.env.NODE_ENV === 'development';

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <div className="flex items-center space-x-2">
          <AlertCircle className="w-6 h-6 text-destructive" />
          <CardTitle className="text-destructive">Something went wrong</CardTitle>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="text-muted-foreground">
          An unexpected error occurred. Please try refreshing the page or contact support if the problem persists.
        </p>
        
        <div className="flex items-center space-x-2">
          <Button 
            onClick={resetError}
            variant="default"
            className="flex items-center space-x-2"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Try Again</span>
          </Button>
          
          <Button 
            onClick={() => window.location.href = '/'}
            variant="outline"
            className="flex items-center space-x-2"
          >
            <Home className="w-4 h-4" />
            <span>Go Home</span>
          </Button>
        </div>
        
        {isDevelopment && (
          <div className="mt-4 p-3 bg-muted rounded-md">
            <div className="flex items-center space-x-2 mb-2">
              <Bug className="w-4 h-4" />
              <span className="font-medium text-sm">Development Details</span>
            </div>
            <div className="space-y-2 text-sm">
              <div>
                <Badge variant="destructive" className="mb-1">
                  {error.name}
                </Badge>
                <p className="font-mono text-xs">{error.message}</p>
              </div>
              {error.stack && (
                <details className="text-xs">
                  <summary className="cursor-pointer text-muted-foreground hover:text-foreground">
                    Stack Trace
                  </summary>
                  <pre className="mt-2 p-2 bg-background rounded text-xs overflow-auto">
                    {error.stack}
                  </pre>
                </details>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

// Error display component for API errors
interface ErrorDisplayProps {
  error: {
    message: string;
    code?: string;
    status?: number;
    details?: any;
  };
  onRetry?: () => void;
  onDismiss?: () => void;
  className?: string;
}

export const ErrorDisplay: React.FC<ErrorDisplayProps> = ({
  error,
  onRetry,
  onDismiss,
  className
}) => {
  return (
    <Card className={className}>
      <CardContent className="p-4">
        <div className="flex items-start space-x-3">
          <AlertCircle className="w-5 h-5 text-destructive flex-shrink-0 mt-0.5" />
          <div className="flex-1 space-y-2">
            <div className="flex items-center space-x-2">
              <p className="font-medium text-sm">Error</p>
              {error.code && (
                <Badge variant="destructive" className="text-xs">
                  {error.code}
                </Badge>
              )}
              {error.status && (
                <Badge variant="outline" className="text-xs">
                  {error.status}
                </Badge>
              )}
            </div>
            <p className="text-sm text-muted-foreground">{error.message}</p>
            
            {(onRetry || onDismiss) && (
              <div className="flex items-center space-x-2 pt-2">
                {onRetry && (
                  <Button 
                    onClick={onRetry}
                    variant="outline"
                    size="sm"
                    className="flex items-center space-x-1"
                  >
                    <RefreshCw className="w-3 h-3" />
                    <span>Retry</span>
                  </Button>
                )}
                {onDismiss && (
                  <Button 
                    onClick={onDismiss}
                    variant="ghost"
                    size="sm"
                  >
                    Dismiss
                  </Button>
                )}
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

// Empty state component
interface EmptyStateProps {
  title: string;
  description: string;
  action?: {
    label: string;
    onClick: () => void;
  };
  icon?: React.ReactNode;
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  action,
  icon,
  className
}) => {
  return (
    <Card className={className}>
      <CardContent className="p-8 text-center">
        <div className="flex flex-col items-center space-y-4">
          {icon && (
            <div className="w-12 h-12 rounded-full bg-muted flex items-center justify-center">
              {icon}
            </div>
          )}
          
          <div className="space-y-2">
            <h3 className="text-lg font-medium">{title}</h3>
            <p className="text-muted-foreground text-sm max-w-md">{description}</p>
          </div>
          
          {action && (
            <Button onClick={action.onClick} className="mt-4">
              {action.label}
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default ErrorBoundary;