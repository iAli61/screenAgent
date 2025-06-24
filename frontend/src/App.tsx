import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'
import { Header } from '@/components/layout/Header'
import { Navigation } from '@/components/layout/Navigation'
import { SingleScreenshot } from '@/components/features/SingleScreenshot'
import { Monitoring } from '@/components/features/Monitoring'
import { ROISelector } from '@/components/features/ROISelector'
import { Settings } from '@/components/features/Settings'
import { ErrorBoundary, ToastContainer } from '@/components/ui'
import { useAppStore } from '@/stores'
import { ROIProvider } from '@/contexts/ROIContext'

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      refetchOnWindowFocus: false,
      staleTime: 30 * 1000, // 30 seconds
    },
    mutations: {
      retry: 1,
    },
  },
})

function AppContent() {
  const { currentTab, setCurrentTab } = useAppStore()

  const renderTabContent = () => {
    switch (currentTab) {
      case 'screenshots':
        return <SingleScreenshot />
      case 'monitoring':
        return <Monitoring />
      case 'roi':
        return <ROISelector />
      case 'settings':
        return <Settings />
      default:
        return <SingleScreenshot />
    }
  }

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="container mx-auto px-4 py-6">
          <Navigation 
            activeTab={currentTab} 
            onTabChange={setCurrentTab}
          />
          <main className="mt-6">
            {renderTabContent()}
          </main>
        </div>
      </div>
    </ErrorBoundary>
  )
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ROIProvider>
        <AppContent />
        <ToastContainer />
        <ReactQueryDevtools initialIsOpen={false} />
      </ROIProvider>
    </QueryClientProvider>
  )
}

export default App
