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
interface APIScreenshot {
  id: string;
  timestamp: string;
  width: number;
  height: number;
  format: string;
  size_bytes: number;
  file_path: string;
  metadata: any;
}

interface ScreenshotListResponse {
  success: boolean;
  screenshots: APIScreenshot[];
  total_count: number;
  offset: number;
  limit: number | null;
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

// Types for monitoring sessions
interface ROI {
  x: number;
  y: number;
  width: number;
  height: number;
}

interface MonitoringSession {
  success: boolean;
  session_id: string;
  roi: ROI;
  interval: number;
  threshold: number;
  status: 'running' | 'stopped' | 'paused';
  created_at: string;
  last_screenshot?: string;
  error?: string;
}

interface CreateSessionRequest {
  roi: ROI;
  interval?: number;
  threshold?: number;
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
    queryFn: () => apiClient.get<ScreenshotListResponse>('/api/screenshots/screenshots', params),
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
      apiClient.post<ScreenshotAnalysisResponse>(`/api/analysis/analyze`, { 
        screenshot_id: id, 
        prompt: prompt || "Analyze this screenshot and describe what you see." 
      }),
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
  const addScreenshot = useScreenshotStore(state => state.addScreenshot);

  return useMutation({
    mutationFn: async (params?: { roi?: ROI; filename?: string; metadata?: any }) => {
      const payload: any = {};
      
      if (params?.roi) {
        payload.roi = params.roi;
      }
      if (params?.filename) {
        payload.filename = params.filename;
      }
      if (params?.metadata) {
        payload.metadata = params.metadata;
      }
      
      const response = await apiClient.post('/api/screenshots/take', payload) as { data: any };
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.screenshots });
      if (data.screenshot) {
        addScreenshot(data.screenshot);
      }
    },
  });
}

// Delete all screenshots mutation
export function useDeleteAllScreenshots() {
  const queryClient = useQueryClient();
  const { clearScreenshots } = useScreenshotStore();

  return useMutation({
    mutationFn: () => apiClient.delete('/api/screenshots/screenshots'),
    onSuccess: () => {
      // Clear from store
      clearScreenshots();
      
      // Clear all screenshot-related cache
      queryClient.removeQueries({ queryKey: QUERY_KEYS.screenshots });
      queryClient.removeQueries({ 
        predicate: (query) => 
          query.queryKey[0] === 'screenshots' && 
          query.queryKey.length > 1 
      });
    },
    onError: (error) => {
      console.error('Delete all failed:', error);
    },
  });
}

// Monitoring Session API Functions
export function useCreateMonitoringSession() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (request: CreateSessionRequest): Promise<MonitoringSession> => {
      const response = await apiClient.post('/api/monitoring/sessions', request) as { data: MonitoringSession };
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['monitoring', 'sessions'] });
    },
  });
}

export function useMonitoringSessions() {
  return useQuery({
    queryKey: ['monitoring', 'sessions'],
    queryFn: async () => {
      const response = await apiClient.get('/api/monitoring/sessions') as { data: any };
      return response.data;
    },
  });
}

// Delete monitoring session
export function useDeleteMonitoringSession() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => apiClient.delete(`/api/monitoring/sessions/${id}`),
    onSuccess: () => {
      // Invalidate and refetch monitoring sessions
      queryClient.invalidateQueries({ queryKey: ['monitoringSessions'] });
    },
    onError: (error) => {
      console.error('Delete session failed:', error);
    },
  });
}

// Start monitoring session
export function useStartMonitoringSession() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => apiClient.post(`/api/monitoring/sessions/${id}/start`),
    onSuccess: () => {
      // Invalidate and refetch monitoring sessions
      queryClient.invalidateQueries({ queryKey: ['monitoringSessions'] });
    },
    onError: (error) => {
      console.error('Start session failed:', error);
    },
  });
}

// Stop monitoring session
export function useStopMonitoringSession() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => apiClient.post(`/api/monitoring/sessions/${id}/stop`),
    onSuccess: () => {
      // Invalidate and refetch monitoring sessions
      queryClient.invalidateQueries({ queryKey: ['monitoringSessions'] });
    },
    onError: (error) => {
      console.error('Stop session failed:', error);
    },
  });
}

// Pause monitoring session
export function usePauseMonitoringSession() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => apiClient.post(`/api/monitoring/sessions/${id}/pause`),
    onSuccess: () => {
      // Invalidate and refetch monitoring sessions
      queryClient.invalidateQueries({ queryKey: ['monitoringSessions'] });
    },
    onError: (error) => {
      console.error('Pause session failed:', error);
    },
  });
}

// Resume monitoring session
export function useResumeMonitoringSession() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => apiClient.post(`/api/monitoring/sessions/${id}/resume`),
    onSuccess: () => {
      // Invalidate and refetch monitoring sessions
      queryClient.invalidateQueries({ queryKey: ['monitoringSessions'] });
    },
    onError: (error) => {
      console.error('Resume session failed:', error);
    },
  });
}
