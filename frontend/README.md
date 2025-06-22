# ScreenAgent React Frontend

A modern, modular React frontend for ScreenAgent with TypeScript, Tailwind CSS, and comprehensive state management.

## Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# In another terminal, start the backend
cd .. && python main.py
```

Open http://localhost:3000 to view the application.

## Features

- 🚀 **React 18** with TypeScript for type safety
- 🎨 **Tailwind CSS** for modern, responsive styling
- ⚡ **Vite** for fast development and building
- 📊 **React Query** for efficient data fetching and caching
- 🗄️ **Zustand** for lightweight state management
- 🧪 **Vitest** for testing with React Testing Library
- 📖 **Storybook** for component development and documentation

## Project Structure

```
src/
├── components/          # React components
│   ├── layout/         # Layout components (Header, Navigation)
│   ├── features/       # Feature-specific components
│   └── ui/             # Reusable UI components
├── hooks/              # Custom React hooks
├── services/           # API and service layers
├── stores/             # Zustand state stores
├── types/              # TypeScript type definitions
├── utils/              # Utility functions
└── constants/          # Application constants
```

## Available Scripts

### Development
- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run preview` - Preview production build

### Code Quality
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking

### Testing
- `npm run test` - Run unit tests
- `npm run test:ui` - Run tests with UI
- `npm run test:coverage` - Run tests with coverage

### Storybook
- `npm run storybook` - Start Storybook for component development
- `npm run build-storybook` - Build Storybook for production

## Technology Stack

| Technology | Purpose | Version |
|------------|---------|---------|
| React | UI Framework | 18.2+ |
| TypeScript | Type Safety | 5.2+ |
| Vite | Build Tool | 5.0+ |
| Tailwind CSS | Styling | 3.3+ |
| React Query | Data Fetching | 5.8+ |
| Zustand | State Management | 4.4+ |
| React Hook Form | Form Management | 7.47+ |
| Vitest | Testing Framework | 0.34+ |
| Storybook | Component Development | 7.5+ |

## Architecture

The frontend follows a modular architecture designed for scalability and maintainability:

### Component Organization
- **Layout Components**: Header, Navigation, Sidebar
- **Feature Components**: Screenshots, Monitoring, ROI Selection, Settings
- **UI Components**: Button, Card, Input, Modal (reusable)

### State Management
- **Zustand stores** for global state management
- **React Query** for server state and caching
- **Local state** for component-specific state

### API Integration
- Centralized API client with error handling
- React Query hooks for data fetching
- Optimistic updates for better UX

## Development Guidelines

### Component Structure

```typescript
interface ComponentProps {
  // TypeScript props
}

export function Component({ prop }: ComponentProps) {
  // 1. Hooks at the top
  const [state, setState] = useState()
  const { data, loading } = useQuery()
  
  // 2. Event handlers
  const handleClick = () => {}
  
  // 3. Early returns for loading/error states
  if (loading) return <LoadingSpinner />
  
  // 4. Main render
  return <div>{/* JSX */}</div>
}
```

### Styling Guidelines
- Use Tailwind utility classes for styling
- Create custom CSS classes for complex components
- Follow mobile-first responsive design
- Use CSS custom properties for theming

### State Management
- Use Zustand for global application state
- Use React Query for server state
- Keep component state local when possible
- Implement optimistic updates for better UX

## Future Features

This frontend is designed to support upcoming features:

### Projects Management
- Project switching interface
- Project-specific screenshots and data
- Project settings and configuration

### Chat AI Integration
- Chat interface for AI conversations
- Message history and session management
- Real-time chat updates via WebSocket

### Voice Functionality
- Audio recording components
- Voice transcription display
- Audio file management

### Multi-Model Comparison
- Side-by-side AI model comparisons
- Model performance metrics
- Comparison result visualization

## Configuration

### Environment Variables

```bash
# .env file
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
```

### Proxy Configuration

The development server proxies API calls to the Python backend:

```typescript
// vite.config.ts
server: {
  proxy: {
    '/api': 'http://localhost:8000',
    '/ws': 'ws://localhost:8000'
  }
}
```

## Testing

### Unit Tests
```bash
npm run test                # Run all tests
npm run test:coverage       # Run with coverage
npm run test:ui            # Run with UI
```

### Component Testing
```typescript
import { render, screen } from '@testing-library/react'
import { Component } from './Component'

test('renders component', () => {
  render(<Component />)
  expect(screen.getByText('Content')).toBeInTheDocument()
})
```

## Deployment

### Build for Production
```bash
npm run build
```

The build output will be in the `dist/` directory.

### Preview Production Build
```bash
npm run preview
```

## Contributing

1. Follow the component structure guidelines
2. Write tests for new components
3. Use TypeScript for type safety
4. Follow the existing code style
5. Update documentation as needed

## Troubleshooting

### Common Issues

**Dependencies not found**: Run `npm install`

**Tailwind styles not working**: Check PostCSS configuration

**API calls failing**: Ensure Python backend is running on port 8000

**TypeScript errors**: Check tsconfig.json and type definitions

### Development Tips

- Use React DevTools for debugging
- Use the Network tab to debug API calls
- Check the console for error messages
- Use Storybook for isolated component development

For more detailed information, see the main documentation in the `docs/` directory.
