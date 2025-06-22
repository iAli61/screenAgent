import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './apiClient';
import { useSettingsStore, type AISettings, type MonitoringSettings, type UISettings } from '../stores';

// Query keys
export const SETTINGS_QUERY_KEYS = {
  settings: ['settings'] as const,
  aiSettings: ['settings', 'ai'] as const,
  monitoringSettings: ['settings', 'monitoring'] as const,
  uiSettings: ['settings', 'ui'] as const,
} as const;

// Types for API responses
interface SettingsResponse {
  ai: AISettings;
  monitoring: MonitoringSettings;
  ui: UISettings;
}

interface SaveSettingsRequest {
  ai?: Partial<AISettings>;
  monitoring?: Partial<MonitoringSettings>;
  ui?: Partial<UISettings>;
}

// Fetch all settings
export function useSettings() {
  return useQuery({
    queryKey: SETTINGS_QUERY_KEYS.settings,
    queryFn: () => apiClient.get<SettingsResponse>('/api/settings'),
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
  });
}

// Fetch specific settings sections
export function useAISettings() {
  return useQuery({
    queryKey: SETTINGS_QUERY_KEYS.aiSettings,
    queryFn: () => apiClient.get<AISettings>('/api/settings/ai'),
    staleTime: 5 * 60 * 1000,
  });
}

export function useMonitoringSettings() {
  return useQuery({
    queryKey: SETTINGS_QUERY_KEYS.monitoringSettings,
    queryFn: () => apiClient.get<MonitoringSettings>('/api/settings/monitoring'),
    staleTime: 30 * 1000, // 30 seconds for monitoring settings
  });
}

// Save settings mutation
export function useSaveSettings() {
  const queryClient = useQueryClient();
  const { markAsSaved } = useSettingsStore();

  return useMutation({
    mutationFn: (data: SaveSettingsRequest) => 
      apiClient.post<{ message: string }>('/api/settings', data),
    onSuccess: () => {
      // Mark as saved in store
      markAsSaved();
      
      // Invalidate all settings queries
      queryClient.invalidateQueries({ queryKey: SETTINGS_QUERY_KEYS.settings });
    },
    onError: (error) => {
      console.error('Failed to save settings:', error);
    },
  });
}

// Save AI settings
export function useSaveAISettings() {
  const queryClient = useQueryClient();
  const { updateAISettings, markAsSaved } = useSettingsStore();

  return useMutation({
    mutationFn: (data: Partial<AISettings>) => 
      apiClient.put<AISettings>('/api/settings/ai', data),
    onMutate: (data) => {
      // Optimistically update store
      updateAISettings(data);
    },
    onSuccess: (updatedSettings) => {
      // Update cache with server response
      queryClient.setQueryData(SETTINGS_QUERY_KEYS.aiSettings, updatedSettings);
      markAsSaved();
    },
    onError: (error) => {
      console.error('Failed to save AI settings:', error);
      // Revert optimistic update could be implemented here
    },
  });
}

// Save monitoring settings
export function useSaveMonitoringSettings() {
  const queryClient = useQueryClient();
  const { updateMonitoringSettings, markAsSaved } = useSettingsStore();

  return useMutation({
    mutationFn: (data: Partial<MonitoringSettings>) => 
      apiClient.put<MonitoringSettings>('/api/settings/monitoring', data),
    onMutate: (data) => {
      // Optimistically update store
      updateMonitoringSettings(data);
    },
    onSuccess: (updatedSettings) => {
      // Update cache
      queryClient.setQueryData(SETTINGS_QUERY_KEYS.monitoringSettings, updatedSettings);
      markAsSaved();
    },
    onError: (error) => {
      console.error('Failed to save monitoring settings:', error);
    },
  });
}

// Reset settings to defaults
export function useResetSettings() {
  const queryClient = useQueryClient();
  const { resetToDefaults } = useSettingsStore();

  return useMutation({
    mutationFn: () => apiClient.post('/api/settings/reset'),
    onSuccess: () => {
      // Reset store to defaults
      resetToDefaults();
      
      // Invalidate all settings queries to refetch from server
      queryClient.invalidateQueries({ queryKey: SETTINGS_QUERY_KEYS.settings });
    },
    onError: (error) => {
      console.error('Failed to reset settings:', error);
    },
  });
}

// Export settings (backup)
export function useExportSettings() {
  return useMutation({
    mutationFn: () => apiClient.get<Blob>('/api/settings/export'),
    onSuccess: (blob) => {
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `screenagent-settings-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    },
    onError: (error) => {
      console.error('Failed to export settings:', error);
    },
  });
}

// Import settings (restore)
export function useImportSettings() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (file: File) => apiClient.upload('/api/settings/import', file),
    onSuccess: () => {
      // Invalidate all settings to refetch updated data
      queryClient.invalidateQueries({ queryKey: SETTINGS_QUERY_KEYS.settings });
    },
    onError: (error) => {
      console.error('Failed to import settings:', error);
    },
  });
}
