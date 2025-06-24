import { useQuery, useMutation } from '@tanstack/react-query';
import { apiClient } from './apiClient';

// Query keys
export const ANALYSIS_QUERY_KEYS = {
  history: ['analysis', 'history'] as const,
  result: (id: string) => ['analysis', 'results', id] as const,
  models: ['analysis', 'models'] as const,
} as const;

// Types for API responses
export interface AnalysisResult {
  id: string;
  screenshotId: string;
  model: string;
  prompt: string;
  result: string;
  confidence: number;
  timestamp: string;
  processingTime: number;
  metadata?: {
    tokensUsed: number;
    cost?: number;
  };
}

export interface AnalysisModel {
  id: string;
  name: string;
  provider: string;
  description: string;
  available: boolean;
  capabilities: string[];
  costPerToken?: number;
}

interface AnalysisHistoryResponse {
  results: AnalysisResult[];
  total: number;
  page: number;
  perPage: number;
}

interface AnalysisRequest {
  screenshotId: string;
  prompt?: string;
  provider?: string;
  model?: string;
  customSettings?: {
    temperature?: number;
    maxTokens?: number;
  };
}

interface MultiModelAnalysisRequest {
  screenshotId: string;
  models: string[];
  prompt?: string;
}

interface MultiModelAnalysisResponse {
  id: string;
  screenshotId: string;
  results: AnalysisResult[];
  comparison: {
    similarities: number;
    differences: string[];
    summary: string;
  };
}

// Fetch analysis history
export function useAnalysisHistory(params?: {
  page?: number;
  perPage?: number;
  screenshotId?: string;
  model?: string;
}) {
  return useQuery({
    queryKey: [...ANALYSIS_QUERY_KEYS.history, params],
    queryFn: () => apiClient.get<AnalysisHistoryResponse>('/api/analysis/history', params),
    staleTime: 30 * 1000, // 30 seconds
  });
}

// Fetch single analysis result
export function useAnalysisResult(id: string) {
  return useQuery({
    queryKey: ANALYSIS_QUERY_KEYS.result(id),
    queryFn: () => apiClient.get<AnalysisResult>(`/api/analysis/results/${id}`),
    enabled: !!id,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// Fetch available analysis models
export function useAnalysisModels() {
  return useQuery({
    queryKey: ANALYSIS_QUERY_KEYS.models,
    queryFn: () => apiClient.get<{ models: AnalysisModel[] }>('/api/analysis/models'),
    staleTime: 10 * 60 * 1000, // 10 minutes
    gcTime: 30 * 60 * 1000, // 30 minutes
  });
}

// Analyze screenshot with single model
export function useAnalyzeScreenshot() {
  return useMutation({
    mutationFn: (data: AnalysisRequest) => 
      apiClient.post<AnalysisResult>('/api/analysis/analyze', data),
    onError: (error) => {
      console.error('Analysis failed:', error);
    },
  });
}

// Analyze screenshot with multiple models for comparison
export function useMultiModelAnalysis() {
  return useMutation({
    mutationFn: (data: MultiModelAnalysisRequest) => 
      apiClient.post<MultiModelAnalysisResponse>('/api/analysis/multi-model', data),
    onError: (error) => {
      console.error('Multi-model analysis failed:', error);
    },
  });
}

// Re-analyze with different prompt
export function useReanalyze() {
  return useMutation({
    mutationFn: ({ resultId, newPrompt }: { resultId: string; newPrompt: string }) => 
      apiClient.post<AnalysisResult>(`/api/analysis/results/${resultId}/reanalyze`, { prompt: newPrompt }),
    onError: (error) => {
      console.error('Re-analysis failed:', error);
    },
  });
}

// Save analysis result
export function useSaveAnalysis() {
  return useMutation({
    mutationFn: ({ resultId, name, notes }: { resultId: string; name?: string; notes?: string }) => 
      apiClient.post(`/api/analysis/results/${resultId}/save`, { name, notes }),
    onError: (error) => {
      console.error('Failed to save analysis:', error);
    },
  });
}

// Delete analysis result
export function useDeleteAnalysis() {
  return useMutation({
    mutationFn: (resultId: string) => 
      apiClient.delete(`/api/analysis/results/${resultId}`),
    onError: (error) => {
      console.error('Failed to delete analysis:', error);
    },
  });
}

// Export analysis results
export function useExportAnalysis() {
  return useMutation({
    mutationFn: ({ resultIds, format }: { resultIds: string[]; format: 'json' | 'csv' | 'pdf' }) => 
      apiClient.post<Blob>('/api/analysis/export', { resultIds, format }),
    onSuccess: (blob, { format }) => {
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `analysis-export-${new Date().toISOString().split('T')[0]}.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    },
    onError: (error) => {
      console.error('Failed to export analysis:', error);
    },
  });
}
