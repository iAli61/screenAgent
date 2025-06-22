import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './apiClient';
import { useScreenshotStore, type Screenshot } from '../stores';

// Query keys for caching
export const QUERY_KEYS = {
  screenshots: ['screenshots'] as const,
  screenshot: (id: string) => ['screenshots', id] as const,
  screenshotAnalysis: (id: string) => ['screenshots', id, 'analysis'] as const,
} as const;

// Types for API responses
interface ScreenshotListResponse {
  screenshots: Screenshot[];
  total: number;
  page: number;
  perPage: number;
}

interface ScreenshotAnalysisResponse {
  id: string;
  analysis: string;
  confidence: number;
  timestamp: string;
}

interface UploadResponse {
  screenshot: Screenshot;
  message: string;
}

// Fetch screenshots with pagination and filtering
export function useScreenshots(params?: {
  page?: number;
  perPage?: number;
  search?: string;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}) {
  return useQuery({
    queryKey: [...QUERY_KEYS.screenshots, params],
    queryFn: () => apiClient.get<ScreenshotListResponse>('/api/screenshots', params),
    staleTime: 30 * 1000, // 30 seconds
    gcTime: 5 * 60 * 1000, // 5 minutes
    refetchOnWindowFocus: false,
  });
}

// Fetch single screenshot by ID
export function useScreenshot(id: string) {
  return useQuery({
    queryKey: QUERY_KEYS.screenshot(id),
    queryFn: () => apiClient.get<Screenshot>(`/api/screenshots/${id}`),
    enabled: !!id,
    staleTime: 60 * 1000, // 1 minute
  });
}

// Upload screenshot mutation
export function useUploadScreenshot() {
  const queryClient = useQueryClient();
  const { addScreenshot, setUploading } = useScreenshotStore();

  return useMutation({
    mutationFn: async ({ file, onProgress }: { file: File; onProgress?: (progress: number) => void }) => {
      setUploading(true, 0);
      
      return apiClient.upload<UploadResponse>('/api/screenshots/upload', file, (progress) => {
        setUploading(true, progress);
        onProgress?.(progress);
      });
    },
    onSuccess: (data) => {
      // Add to store
      addScreenshot(data.screenshot);
      
      // Invalidate and refetch screenshots list
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.screenshots });
      
      setUploading(false, 0);
    },
    onError: (error) => {
      console.error('Upload failed:', error);
      setUploading(false, 0);
    },
  });
}

// Delete screenshot mutation
export function useDeleteScreenshot() {
  const queryClient = useQueryClient();
  const { removeScreenshot } = useScreenshotStore();

  return useMutation({
    mutationFn: (id: string) => apiClient.delete(`/api/screenshots/${id}`),
    onSuccess: (_, id) => {
      // Remove from store
      removeScreenshot(id);
      
      // Remove from cache
      queryClient.removeQueries({ queryKey: QUERY_KEYS.screenshot(id) });
      queryClient.removeQueries({ queryKey: QUERY_KEYS.screenshotAnalysis(id) });
      
      // Invalidate screenshots list
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.screenshots });
    },
    onError: (error) => {
      console.error('Delete failed:', error);
    },
  });
}

// Analyze screenshot mutation
export function useAnalyzeScreenshot() {
  const queryClient = useQueryClient();
  const { updateScreenshot } = useScreenshotStore();

  return useMutation({
    mutationFn: ({ id, prompt }: { id: string; prompt?: string }) => 
      apiClient.post<ScreenshotAnalysisResponse>(`/api/screenshots/${id}/analyze`, { prompt }),
    onMutate: ({ id }) => {
      // Optimistically update status
      updateScreenshot(id, {
        analysis: { status: 'pending' }
      });
    },
    onSuccess: (data, { id }) => {
      // Update screenshot with analysis result
      updateScreenshot(id, {
        analysis: {
          status: 'completed',
          result: data.analysis,
        }
      });
      
      // Update cache
      queryClient.setQueryData(QUERY_KEYS.screenshotAnalysis(id), data);
    },
    onError: (error, { id }) => {
      // Update screenshot with error status
      updateScreenshot(id, {
        analysis: {
          status: 'error',
          error: error instanceof Error ? error.message : 'Analysis failed'
        }
      });
      
      console.error('Analysis failed:', error);
    },
  });
}

// Get screenshot analysis
export function useScreenshotAnalysis(id: string) {
  return useQuery({
    queryKey: QUERY_KEYS.screenshotAnalysis(id),
    queryFn: () => apiClient.get<ScreenshotAnalysisResponse>(`/api/screenshots/${id}/analysis`),
    enabled: !!id,
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: false, // Don't retry if analysis doesn't exist
  });
}

// Take new screenshot
export function useTakeScreenshot() {
  const queryClient = useQueryClient();
  const { addScreenshot } = useScreenshotStore();

  return useMutation({
    mutationFn: (params?: { roi?: boolean; filename?: string }) => 
      apiClient.post<{ screenshot: Screenshot }>('/api/screenshots/take', params),
    onSuccess: (data) => {
      // Add to store
      addScreenshot(data.screenshot);
      
      // Invalidate screenshots list
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.screenshots });
    },
    onError: (error) => {
      console.error('Screenshot failed:', error);
    },
  });
}
