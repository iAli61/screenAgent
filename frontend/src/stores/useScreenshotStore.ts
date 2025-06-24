import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

export interface Screenshot {
  id: string;
  filename: string;
  timestamp: string;
  path: string;
  size: number;
  metadata?: {
    width: number;
    height: number;
    format: string;
  };
  analysis?: {
    status: 'pending' | 'completed' | 'error';
    result?: string;
    error?: string;
  };
}

interface ScreenshotState {
  // Screenshot data
  screenshots: Screenshot[];
  selectedScreenshot: Screenshot | null;
  
  // Gallery state
  sortBy: 'date' | 'name' | 'size';
  sortOrder: 'asc' | 'desc';
  searchQuery: string;
  currentPage: number;
  itemsPerPage: number;
  
  // Upload state
  isUploading: boolean;
  uploadProgress: number;
  
  // Actions
  setScreenshots: (screenshots: Screenshot[]) => void;
  addScreenshot: (screenshot: Screenshot) => void;
  removeScreenshot: (id: string) => void;
  clearScreenshots: () => void;
  selectScreenshot: (screenshot: Screenshot | null) => void;
  updateScreenshot: (id: string, updates: Partial<Screenshot>) => void;
  
  // Gallery actions
  setSortBy: (sortBy: 'date' | 'name' | 'size') => void;
  setSortOrder: (order: 'asc' | 'desc') => void;
  setSearchQuery: (query: string) => void;
  setCurrentPage: (page: number) => void;
  
  // Upload actions
  setUploading: (uploading: boolean, progress?: number) => void;
  
  // Computed getters
  getFilteredScreenshots: () => Screenshot[];
  getPaginatedScreenshots: () => Screenshot[];
}

export const useScreenshotStore = create<ScreenshotState>()(
  devtools(
    (set, get) => ({
      // Initial state
      screenshots: [],
      selectedScreenshot: null,
      sortBy: 'date',
      sortOrder: 'desc',
      searchQuery: '',
      currentPage: 1,
      itemsPerPage: 12,
      isUploading: false,
      uploadProgress: 0,

      // Actions
      setScreenshots: (screenshots) => 
        set((state) => ({ ...state, screenshots }), false, 'setScreenshots'),

      addScreenshot: (screenshot) => 
        set((state) => ({ 
          ...state, 
          screenshots: [screenshot, ...state.screenshots] 
        }), false, 'addScreenshot'),

      removeScreenshot: (id) => 
        set((state) => ({ 
          ...state, 
          screenshots: state.screenshots.filter(s => s.id !== id),
          selectedScreenshot: state.selectedScreenshot?.id === id ? null : state.selectedScreenshot
        }), false, 'removeScreenshot'),

      clearScreenshots: () => 
        set((state) => ({ 
          ...state, 
          screenshots: [],
          selectedScreenshot: null
        }), false, 'clearScreenshots'),

      selectScreenshot: (screenshot) => 
        set((state) => ({ ...state, selectedScreenshot: screenshot }), false, 'selectScreenshot'),

      updateScreenshot: (id, updates) => 
        set((state) => ({
          ...state,
          screenshots: state.screenshots.map(s => 
            s.id === id ? { ...s, ...updates } : s
          ),
          selectedScreenshot: state.selectedScreenshot?.id === id 
            ? { ...state.selectedScreenshot, ...updates }
            : state.selectedScreenshot
        }), false, 'updateScreenshot'),

      // Gallery actions
      setSortBy: (sortBy) => 
        set((state) => ({ ...state, sortBy, currentPage: 1 }), false, 'setSortBy'),

      setSortOrder: (sortOrder) => 
        set((state) => ({ ...state, sortOrder, currentPage: 1 }), false, 'setSortOrder'),

      setSearchQuery: (searchQuery) => 
        set((state) => ({ ...state, searchQuery, currentPage: 1 }), false, 'setSearchQuery'),

      setCurrentPage: (currentPage) => 
        set((state) => ({ ...state, currentPage }), false, 'setCurrentPage'),

      // Upload actions
      setUploading: (isUploading, uploadProgress = 0) => 
        set((state) => ({ ...state, isUploading, uploadProgress }), false, 'setUploading'),

      // Computed getters
      getFilteredScreenshots: () => {
        const { screenshots, searchQuery, sortBy, sortOrder } = get();
        
        let filtered = screenshots;
        
        // Apply search filter
        if (searchQuery) {
          filtered = filtered.filter(screenshot => 
            screenshot.filename.toLowerCase().includes(searchQuery.toLowerCase())
          );
        }
        
        // Apply sorting
        filtered.sort((a, b) => {
          let comparison = 0;
          
          switch (sortBy) {
            case 'date':
              comparison = new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime();
              break;
            case 'name':
              comparison = a.filename.localeCompare(b.filename);
              break;
            case 'size':
              comparison = a.size - b.size;
              break;
          }
          
          return sortOrder === 'asc' ? comparison : -comparison;
        });
        
        return filtered;
      },

      getPaginatedScreenshots: () => {
        const { currentPage, itemsPerPage } = get();
        const filtered = get().getFilteredScreenshots();
        const startIndex = (currentPage - 1) * itemsPerPage;
        const endIndex = startIndex + itemsPerPage;
        
        return filtered.slice(startIndex, endIndex);
      },
    }),
    {
      name: 'screenshot-store',
    }
  )
);
