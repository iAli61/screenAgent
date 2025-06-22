import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

export type Tab = 'screenshots' | 'monitoring' | 'roi' | 'settings';

interface AppState {
  // Current active tab
  currentTab: Tab;
  
  // Global loading states
  isLoading: boolean;
  loadingMessage: string;
  
  // Global error state
  error: string | null;
  
  // UI state
  sidebarCollapsed: boolean;
  
  // Actions
  setCurrentTab: (tab: Tab) => void;
  setLoading: (loading: boolean, message?: string) => void;
  setError: (error: string | null) => void;
  toggleSidebar: () => void;
  clearError: () => void;
}

export const useAppStore = create<AppState>()(
  devtools(
    (set) => ({
      // Initial state
      currentTab: 'screenshots',
      isLoading: false,
      loadingMessage: '',
      error: null,
      sidebarCollapsed: false,

      // Actions
      setCurrentTab: (tab) => 
        set((state) => ({ ...state, currentTab: tab }), false, 'setCurrentTab'),

      setLoading: (loading, message = '') => 
        set((state) => ({ 
          ...state, 
          isLoading: loading, 
          loadingMessage: message 
        }), false, 'setLoading'),

      setError: (error) => 
        set((state) => ({ ...state, error }), false, 'setError'),

      clearError: () => 
        set((state) => ({ ...state, error: null }), false, 'clearError'),

      toggleSidebar: () => 
        set((state) => ({ 
          ...state, 
          sidebarCollapsed: !state.sidebarCollapsed 
        }), false, 'toggleSidebar'),
    }),
    {
      name: 'app-store',
    }
  )
);
