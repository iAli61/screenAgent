import { useQuery } from '@tanstack/react-query';
import { apiClient } from './apiClient';

// Query keys
export const MODELS_QUERY_KEYS = {
  all: ['models'] as const,
  provider: (provider: string) => ['models', 'provider', provider] as const,
} as const;

// Types for API responses
export interface Provider {
  name: string;
  models: string[];
}

export interface ModelsResponse {
  success: boolean;
  providers: Provider[];
  total_providers: number;
  total_models: number;
}

export interface ProviderInfoResponse {
  success: boolean;
  provider: string;
  models: string[];
  available: boolean;
}

// Fetch all available providers and models
export function useModels() {
  return useQuery({
    queryKey: MODELS_QUERY_KEYS.all,
    queryFn: () => apiClient.get<ModelsResponse>('/api/models'),
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
  });
}

// Fetch specific provider information
export function useProviderInfo(provider: string) {
  return useQuery({
    queryKey: MODELS_QUERY_KEYS.provider(provider),
    queryFn: () => apiClient.get<ProviderInfoResponse>(`/api/models/${provider}`),
    enabled: !!provider,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
  });
}

// Helper function to get formatted provider options for UI
export function getProviderOptions(modelsData?: ModelsResponse): Array<{ value: string; label: string; models: string[] }> {
  if (!modelsData?.providers) return [];
  
  return modelsData.providers.map(provider => ({
    value: provider.name,
    label: provider.name.charAt(0).toUpperCase() + provider.name.slice(1),
    models: provider.models
  }));
}

// Helper function to get model options for a specific provider
export function getModelOptions(provider: string, modelsData?: ModelsResponse): Array<{ value: string; label: string }> {
  if (!modelsData?.providers) return [];
  
  const selectedProvider = modelsData.providers.find(p => p.name === provider);
  if (!selectedProvider) return [];
  
  return selectedProvider.models.map(model => ({
    value: model,
    label: model
  }));
}
