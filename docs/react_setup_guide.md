# ScreenAgent React Frontend Setup Guide

## Overview

This guide walks you through setting up the new React-based frontend for ScreenAgent. The React frontend is designed to be modular, maintainable, and ready for future features like projects, chat AI, voice functionality, and multi-model comparisons.

## Prerequisites

- Node.js 18+ and npm
- Python 3.7+ (for backend)
- Git

## Quick Start

### 1. Navigate to Frontend Directory

```bash
cd /home/alibina/repo/screenAgent/frontend
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Start Development Server

```bash
# Start the React development server (will run on port 3000)
npm run dev

# In another terminal, start the Python backend (runs on port 8000)
cd /home/alibina/repo/screenAgent
python main.py
```

### 4. Open Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

The React frontend will proxy API calls to the Python backend automatically.

## Development Scripts

```bash
# Development
npm run dev              # Start development server with hot reload
npm run build           # Build for production
npm run preview         # Preview production build

# Code Quality
npm run lint            # Run ESLint
npm run type-check      # Run TypeScript type checking

# Testing
npm run test            # Run unit tests
npm run test:ui         # Run tests with UI
npm run test:coverage   # Run tests with coverage

# Storybook (Component Development)
npm run storybook       # Start Storybook on port 6006
npm run build-storybook # Build Storybook for production
```

## Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── layout/         # Layout components (Header, Navigation)
│   │   ├── features/       # Feature components (Screenshots, ROI, etc.)
│   │   └── ui/             # Reusable UI components (Button, Card, etc.)
│   ├── hooks/              # Custom React hooks
│   ├── services/           # API and service layers
│   ├── stores/             # State management (Zustand)
│   ├── types/              # TypeScript type definitions
│   ├── utils/              # Utility functions
│   ├── constants/          # Application constants
│   ├── App.tsx             # Main App component
│   ├── main.tsx            # Application entry point
│   └── index.css           # Global styles with Tailwind
├── public/                 # Static assets
├── package.json            # Dependencies and scripts
├── vite.config.ts          # Vite configuration
├── tsconfig.json           # TypeScript configuration
├── tailwind.config.js      # Tailwind CSS configuration
└── postcss.config.js       # PostCSS configuration
```

## Current Implementation Status

### ✅ Completed

1. **Project Setup**
   - React 18 + TypeScript + Vite
   - Tailwind CSS for styling
   - ESLint + Prettier for code quality
   - Path aliases for clean imports

2. **Basic Component Structure**
   - Layout components (Header, Navigation)
   - Feature placeholders (SingleScreenshot, Monitoring, ROISelector, Settings)
   - Tab-based navigation system

3. **Development Environment**
   - Hot reload development server
   - Proxy configuration for backend API
   - TypeScript configuration with strict mode

### 🚧 In Progress (Next Steps)

1. **State Management Setup**
   - Install and configure Zustand
   - Create stores for screenshots, settings, ROI, app state

2. **API Integration**
   - Install React Query for data fetching
   - Create API client and hooks
   - Connect components to backend endpoints

3. **UI Component Library**
   - Create reusable Button, Card, Input components
   - Implement proper TypeScript props interfaces
   - Add error boundaries and loading states

## Migration Strategy

### Phase 1: Foundation (Current)
- ✅ React setup and basic structure
- 🚧 State management and API integration
- 📋 UI component library

### Phase 2: Core Features
- Screenshot management with gallery
- ROI selection with canvas interaction
- Monitoring dashboard with real-time updates
- Settings management with form validation

### Phase 3: Advanced Features
- Project management structure
- Multi-model AI comparison interface
- Chat system foundation
- Voice recording components

### Phase 4: Performance & Polish
- Virtual scrolling for large lists
- Image optimization and lazy loading
- Error handling and user feedback
- Testing and accessibility

## Backend Changes Required

The React frontend will require some backend API modifications:

### New Endpoints Needed

```python
# Project Management
GET /api/projects
POST /api/projects
GET /api/projects/:id
PUT /api/projects/:id
DELETE /api/projects/:id

# Multi-Model Analysis
GET /api/models/available
POST /api/analyze/multi-model
GET /api/analysis/:id/comparisons

# Real-time Updates
WebSocket /ws/screenshots
WebSocket /ws/monitoring
WebSocket /ws/analysis
```

### API Response Format Standardization

```json
{
  "success": true,
  "data": {...},
  "error": null,
  "timestamp": "2025-06-21T10:30:00Z"
}
```

## Development Guidelines

### Component Structure

```typescript
// components/features/FeatureName.tsx
interface FeatureNameProps {
  // Props with TypeScript types
}

export function FeatureName({ prop1, prop2 }: FeatureNameProps) {
  // Hooks at the top
  const [state, setState] = useState()
  const { data, loading, error } = useQuery()
  
  // Event handlers
  const handleClick = () => {}
  
  // Early returns for loading/error states
  if (loading) return <LoadingSpinner />
  if (error) return <ErrorMessage error={error} />
  
  // Main render
  return (
    <div className="component-container">
      {/* JSX content */}
    </div>
  )
}
```

### State Management

```typescript
// stores/useScreenshotStore.ts
import { create } from 'zustand'

interface ScreenshotStore {
  screenshots: Screenshot[]
  loading: boolean
  fetchScreenshots: () => Promise<void>
  addScreenshot: (screenshot: Screenshot) => void
}

export const useScreenshotStore = create<ScreenshotStore>((set, get) => ({
  screenshots: [],
  loading: false,
  fetchScreenshots: async () => {
    set({ loading: true })
    // API call logic
    set({ screenshots: data, loading: false })
  },
  addScreenshot: (screenshot) => 
    set((state) => ({ screenshots: [...state.screenshots, screenshot] }))
}))
```

### API Integration

```typescript
// services/api.ts
import { useQuery, useMutation } from '@tanstack/react-query'

export function useScreenshots() {
  return useQuery({
    queryKey: ['screenshots'],
    queryFn: () => fetch('/api/screenshots').then(res => res.json())
  })
}

export function useDeleteScreenshot() {
  return useMutation({
    mutationFn: (id: string) => 
      fetch(`/api/screenshots/${id}`, { method: 'DELETE' })
  })
}
```

## Troubleshooting

### Common Issues

1. **TypeScript Errors**: Install dependencies with `npm install` to resolve module not found errors
2. **Tailwind Not Working**: Ensure PostCSS and Tailwind are properly configured
3. **API Calls Failing**: Check that Python backend is running on port 8000
4. **Hot Reload Issues**: Restart the development server with `npm run dev`

### Performance Considerations

- Use React.memo for expensive components
- Implement virtual scrolling for large lists
- Lazy load images and components
- Use proper dependency arrays in useEffect

## Next Steps

1. **Install Dependencies**: Run `npm install` in the frontend directory
2. **Start Development**: Run both frontend and backend servers
3. **Follow Refactoring Plan**: Implement features according to the detailed plan in `frontend_refactoring_todo.md`
4. **Test Each Phase**: Ensure each phase works before moving to the next

## Resources

- [React Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Vite Documentation](https://vitejs.dev/)
- [React Query Documentation](https://tanstack.com/query/latest)
- [Zustand Documentation](https://github.com/pmndrs/zustand)

This setup provides a solid foundation for the React migration while maintaining backward compatibility and preparing for future features.
