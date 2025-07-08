# STONESOUP Frontend Search Interface

A comprehensive search interface for STONESOUP that enables users to discover talent and expertise through an AI-powered search experience.

## Features

### 🔍 Advanced Search Capabilities
- **Hybrid Search**: Combines semantic and text-based search for optimal results
- **Multi-scope Search**: Search across members, stories, or all content
- **Real-time Suggestions**: Intelligent autocomplete with trending and popular queries
- **AI-Powered Summaries**: Get insights and patterns from search results

### 🎨 Modern UI/UX
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Accessibility**: Full keyboard navigation and screen reader support
- **Dark Mode**: Automatic theme switching based on user preferences
- **Loading States**: Smooth skeleton loading and progress indicators

### 👥 Member Discovery
- **Rich Member Cards**: Display profiles with skills, experience, and availability
- **Score Visualization**: See match relevance with detailed breakdowns
- **Social Integration**: LinkedIn, GitHub, and portfolio links
- **Verification Status**: Highlighted verified members and expertise

### 📚 Story Exploration
- **Story Cards**: Showcase achievements, case studies, and testimonials
- **Content Highlighting**: Search term highlighting in results
- **Skill Matching**: Visual indication of skill matches
- **Type Categorization**: Different story types with unique styling

### 🔐 Authentication & Security
- **Clerk Integration**: Secure authentication with social login options
- **Multi-tenancy**: Automatic cauldron (organization) scoping
- **Protected Routes**: Secure access to search functionality

## File Structure

```
src/frontend/
├── app/
│   ├── page.tsx                 # Main search page
│   ├── search/
│   │   └── page.tsx            # Dedicated search route
│   ├── layout.tsx              # Root layout with Clerk provider
│   └── globals.css             # Global styles and search-specific CSS
├── components/
│   ├── search/
│   │   ├── index.ts            # Component exports
│   │   ├── search-page.tsx     # Main search page component
│   │   ├── search-bar.tsx      # Search input with suggestions
│   │   ├── search-results.tsx  # Results display component
│   │   ├── member-card.tsx     # Member result card
│   │   └── story-card.tsx      # Story result card
│   └── ui/
│       ├── index.ts            # UI component exports
│       ├── button.tsx          # Button component
│       ├── input.tsx           # Input component
│       ├── card.tsx            # Card components
│       ├── badge.tsx           # Badge component
│       ├── separator.tsx       # Separator component
│       ├── skeleton.tsx        # Skeleton loader
│       ├── loading-spinner.tsx # Loading spinner
│       ├── loading-skeleton.tsx# Complex loading states
│       └── error-boundary.tsx  # Error handling components
└── lib/
    ├── api.ts                  # API client and utilities
    ├── types.ts                # TypeScript type definitions
    └── utils.ts                # Utility functions
```

## Key Components

### SearchPage (`components/search/search-page.tsx`)
The main search interface component that orchestrates the entire search experience.

**Features:**
- Search state management
- Authentication integration
- Error handling and recovery
- Empty states and onboarding

### SearchBar (`components/search/search-bar.tsx`)
Advanced search input with intelligent suggestions and scope selection.

**Features:**
- Debounced suggestion fetching
- Keyboard navigation
- Scope filtering (All, Members, Stories)
- Real-time search suggestions

### MemberCard (`components/search/member-card.tsx`)
Rich member profile cards with comprehensive information display.

**Features:**
- Compact and detailed view modes
- Skill and experience visualization
- Social media integration
- Availability status indicators

### StoryCard (`components/search/story-card.tsx`)
Story cards showcasing achievements and content with visual categorization.

**Features:**
- Story type categorization
- Content highlighting
- Skill matching indicators
- AI-generated content badges

## Setup Instructions

### 1. Install Dependencies
```bash
cd src/frontend
npm install
```

### 2. Environment Configuration
Create a `.env.local` file with the following variables:

```env
# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key
CLERK_SECRET_KEY=your_clerk_secret_key

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Required Dependencies
The search interface requires these additional packages (already added to package.json):

```json
{
  "@radix-ui/react-separator": "^1.1.0",
  "@radix-ui/react-slot": "^1.1.0"
}
```

### 4. Clerk Setup
1. Create a Clerk application at [clerk.dev](https://clerk.dev)
2. Configure social providers (Google, GitHub, LinkedIn)
3. Set up webhooks for user synchronization
4. Add the Clerk keys to your environment variables

### 5. API Integration
Ensure your backend API is running and accessible at the configured URL. The search interface expects:

- `POST /api/v1/search/quick` - Quick search endpoint
- `POST /api/v1/search` - Advanced search endpoint
- `GET /api/v1/search/suggestions` - Search suggestions
- `GET /api/v1/members/{id}` - Member details
- Authentication via JWT tokens

### 6. Development Server
```bash
npm run dev
```

Visit `http://localhost:3000` to see the search interface.

## Usage Examples

### Basic Search
```typescript
import { SearchPage } from '@/components/search';

function App() {
  return <SearchPage />;
}
```

### Search with Initial Query
```typescript
import { SearchPage } from '@/components/search';

function App() {
  return (
    <SearchPage 
      initialQuery="React developer" 
      initialScope="members" 
    />
  );
}
```

### Custom Member Card
```typescript
import { MemberCard } from '@/components/search';

function MemberList({ members }) {
  return (
    <div className="space-y-4">
      {members.map(member => (
        <MemberCard
          key={member.id}
          member={member}
          onClick={(member) => console.log('Clicked:', member)}
          showScore={true}
          compact={false}
        />
      ))}
    </div>
  );
}
```

## API Integration

### Authentication
The API client automatically handles Clerk authentication:

```typescript
import { createClientApiClient } from '@/lib/api';

// Client-side usage
const apiClient = await createClientApiClient();
const results = await apiClient.quickSearch({
  query: 'Python developer',
  scope: 'members',
  limit: 20
});
```

### Error Handling
Comprehensive error handling with user-friendly messages:

```typescript
import { isApiError, getErrorMessage } from '@/lib/api';

try {
  const results = await performQuickSearch('developer');
} catch (error) {
  if (isApiError(error)) {
    console.log('API Error:', error.status, error.message);
  } else {
    console.log('Unknown Error:', getErrorMessage(error));
  }
}
```

## Customization

### Styling
The interface uses Tailwind CSS with custom design tokens. Modify `app/globals.css` for theme customization:

```css
:root {
  --primary: 222.2 47.4% 11.2%;
  --primary-foreground: 210 40% 98%;
  /* Add your custom colors */
}
```

### Component Variants
Components support multiple variants for different use cases:

```typescript
// Compact member cards
<MemberCard member={member} compact={true} />

// Detailed story cards with scores
<StoryCard story={story} showScore={true} showHighlights={true} />
```

### Custom Icons
Replace Lucide React icons with your preferred icon library:

```typescript
import { Search } from 'your-icon-library';

// Update icon imports in components
```

## Performance Optimizations

### Lazy Loading
Components are optimized for performance with:
- Lazy loading of heavy components
- Image optimization with Next.js
- Debounced search suggestions
- Virtualized lists for large result sets

### Caching
- API response caching
- Suggestion memoization
- Component state optimization

## Accessibility

### Keyboard Navigation
- Full keyboard support for search interface
- Arrow key navigation in suggestions
- Tab-friendly component focus

### Screen Readers
- Proper ARIA labels and descriptions
- Semantic HTML structure
- Screen reader announcements for state changes

### Color Contrast
- WCAG AA compliant color schemes
- High contrast mode support
- Color-blind friendly design

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Verify `NEXT_PUBLIC_API_URL` environment variable
   - Check CORS configuration on backend
   - Ensure API server is running

2. **Authentication Issues**
   - Verify Clerk configuration
   - Check environment variables
   - Ensure user is signed in

3. **Search Not Working**
   - Check backend API endpoints
   - Verify search service is running
   - Check network requests in browser dev tools

4. **Styling Issues**
   - Ensure Tailwind CSS is properly configured
   - Check for conflicting CSS rules
   - Verify design tokens in globals.css

### Debug Mode
Enable debug logging by setting:

```env
NODE_ENV=development
```

This will show detailed API logs and error information.

## Contributing

When contributing to the search interface:

1. Follow the existing component patterns
2. Add proper TypeScript types
3. Include accessibility features
4. Write responsive CSS
5. Add error handling
6. Update documentation

## Future Enhancements

- [ ] Advanced filtering interface
- [ ] Saved searches functionality
- [ ] Search analytics dashboard
- [ ] Export search results
- [ ] Real-time search updates
- [ ] Voice search integration
- [ ] Mobile app optimization