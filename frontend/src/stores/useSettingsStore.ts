import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

export interface AISettings {
  model: string;
  temperature: number;
  maxTokens: number;
  customPrompt: string;
  autoAnalyze: boolean;
}

export interface MonitoringSettings {
  interval: number; // milliseconds
  threshold: number; // percentage difference
  enabled: boolean;
  notificationsEnabled: boolean;
  saveOnChange: boolean;
}

export interface UISettings {
  theme: 'light' | 'dark' | 'system';
  sidebarPosition: 'left' | 'right';
  gridSize: 'small' | 'medium' | 'large';
  showMetadata: boolean;
  autoRefresh: boolean;
}

interface SettingsState {
  // Settings data
  ai: AISettings;
  monitoring: MonitoringSettings;
  ui: UISettings;
  
  // State
  hasUnsavedChanges: boolean;
  
  // Actions
  updateAISettings: (settings: Partial<AISettings>) => void;
  updateMonitoringSettings: (settings: Partial<MonitoringSettings>) => void;
  updateUISettings: (settings: Partial<UISettings>) => void;
  resetToDefaults: () => void;
  saveSettings: () => Promise<void>;
  loadSettings: () => Promise<void>;
  markAsModified: () => void;
  markAsSaved: () => void;
}

const defaultSettings = {
  ai: {
    model: 'gpt-4',
    temperature: 0.7,
    maxTokens: 1000,
    customPrompt: '',
    autoAnalyze: false,
  },
  monitoring: {
    interval: 5000, // 5 seconds
    threshold: 10, // 10% difference
    enabled: false,
    notificationsEnabled: true,
    saveOnChange: true,
  },
  ui: {
    theme: 'system' as const,
    sidebarPosition: 'left' as const,
    gridSize: 'medium' as const,
    showMetadata: true,
    autoRefresh: false,
  },
};

export const useSettingsStore = create<SettingsState>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        ...defaultSettings,
        hasUnsavedChanges: false,

        // Actions
        updateAISettings: (settings) => {
          set((state) => ({
            ...state,
            ai: { ...state.ai, ...settings },
            hasUnsavedChanges: true,
          }), false, 'updateAISettings');
        },

        updateMonitoringSettings: (settings) => {
          set((state) => ({
            ...state,
            monitoring: { ...state.monitoring, ...settings },
            hasUnsavedChanges: true,
          }), false, 'updateMonitoringSettings');
        },

        updateUISettings: (settings) => {
          set((state) => ({
            ...state,
            ui: { ...state.ui, ...settings },
            hasUnsavedChanges: true,
          }), false, 'updateUISettings');
        },

        resetToDefaults: () => {
          set((state) => ({
            ...state,
            ...defaultSettings,
            hasUnsavedChanges: true,
          }), false, 'resetToDefaults');
        },

        saveSettings: async () => {
          const { ai, monitoring, ui } = get();
          
          try {
            // TODO: Implement API call to save settings
            const response = await fetch('/api/settings', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ ai, monitoring, ui }),
            });
            
            if (!response.ok) {
              throw new Error('Failed to save settings');
            }
            
            set((state) => ({
              ...state,
              hasUnsavedChanges: false,
            }), false, 'saveSettings');
          } catch (error) {
            console.error('Failed to save settings:', error);
            throw error;
          }
        },

        loadSettings: async () => {
          try {
            // TODO: Implement API call to load settings
            const response = await fetch('/api/settings');
            
            if (response.ok) {
              const settings = await response.json();
              set((state) => ({
                ...state,
                ai: { ...defaultSettings.ai, ...settings.ai },
                monitoring: { ...defaultSettings.monitoring, ...settings.monitoring },
                ui: { ...defaultSettings.ui, ...settings.ui },
                hasUnsavedChanges: false,
              }), false, 'loadSettings');
            }
          } catch (error) {
            console.error('Failed to load settings:', error);
            // Continue with default settings if loading fails
          }
        },

        markAsModified: () => {
          set((state) => ({
            ...state,
            hasUnsavedChanges: true,
          }), false, 'markAsModified');
        },

        markAsSaved: () => {
          set((state) => ({
            ...state,
            hasUnsavedChanges: false,
          }), false, 'markAsSaved');
        },
      }),
      {
        name: 'settings-store',
        // Only persist UI settings locally, other settings come from server
        partialize: (state) => ({ ui: state.ui }),
      }
    ),
    {
      name: 'settings-store',
    }
  )
);
