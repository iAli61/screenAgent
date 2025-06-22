import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './apiClient';
import { useROIStore, type ROISelection, type ROICoordinates } from '../stores';

// Query keys
export const ROI_QUERY_KEYS = {
  selections: ['roi', 'selections'] as const,
  selection: (id: string) => ['roi', 'selections', id] as const,
  preview: ['roi', 'preview'] as const,
  monitoring: ['roi', 'monitoring'] as const,
} as const;

// Types for API responses
interface ROISelectionsResponse {
  selections: ROISelection[];
}

interface ROIPreviewResponse {
  imageUrl: string;
  timestamp: string;
  dimensions: {
    width: number;
    height: number;
  };
}

interface ROIMonitoringStatus {
  isActive: boolean;
  activeSelection?: ROISelection;
  lastCheck: string;
  changeDetected: boolean;
  changePercentage?: number;
}

interface CreateROIRequest {
  name: string;
  coordinates: ROICoordinates;
  isActive?: boolean;
}

// Fetch all ROI selections
export function useROISelections() {
  return useQuery({
    queryKey: ROI_QUERY_KEYS.selections,
    queryFn: () => apiClient.get<ROISelectionsResponse>('/api/roi/selections'),
    staleTime: 60 * 1000, // 1 minute
  });
}

// Fetch single ROI selection
export function useROISelection(id: string) {
  return useQuery({
    queryKey: ROI_QUERY_KEYS.selection(id),
    queryFn: () => apiClient.get<ROISelection>(`/api/roi/selections/${id}`),
    enabled: !!id,
  });
}

// Get screen preview for ROI selection
export function useROIPreview() {
  return useQuery({
    queryKey: ROI_QUERY_KEYS.preview,
    queryFn: () => apiClient.get<ROIPreviewResponse>('/api/roi/preview'),
    staleTime: 30 * 1000, // 30 seconds
    refetchInterval: 30 * 1000, // Auto-refresh every 30 seconds
  });
}

// Get current monitoring status
export function useROIMonitoring() {
  return useQuery({
    queryKey: ROI_QUERY_KEYS.monitoring,
    queryFn: () => apiClient.get<ROIMonitoringStatus>('/api/roi/monitoring/status'),
    staleTime: 5 * 1000, // 5 seconds
    refetchInterval: 10 * 1000, // Check every 10 seconds when monitoring
  });
}

// Create new ROI selection
export function useCreateROISelection() {
  const queryClient = useQueryClient();
  const { addSelection } = useROIStore();

  return useMutation({
    mutationFn: (data: CreateROIRequest) => 
      apiClient.post<ROISelection>('/api/roi/selections', data),
    onSuccess: (newSelection) => {
      // Add to store
      addSelection({
        name: newSelection.name,
        coordinates: newSelection.coordinates,
        isActive: newSelection.isActive,
      });
      
      // Invalidate selections query
      queryClient.invalidateQueries({ queryKey: ROI_QUERY_KEYS.selections });
    },
    onError: (error) => {
      console.error('Failed to create ROI selection:', error);
    },
  });
}

// Update ROI selection
export function useUpdateROISelection() {
  const queryClient = useQueryClient();
  const { updateSelection } = useROIStore();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<ROISelection> }) => 
      apiClient.put<ROISelection>(`/api/roi/selections/${id}`, data),
    onMutate: ({ id, data }) => {
      // Optimistically update store
      updateSelection(id, data);
    },
    onSuccess: (updatedSelection, { id }) => {
      // Update cache
      queryClient.setQueryData(ROI_QUERY_KEYS.selection(id), updatedSelection);
      queryClient.invalidateQueries({ queryKey: ROI_QUERY_KEYS.selections });
    },
    onError: (error) => {
      console.error('Failed to update ROI selection:', error);
      // Could implement optimistic update revert here
    },
  });
}

// Delete ROI selection
export function useDeleteROISelection() {
  const queryClient = useQueryClient();
  const { removeSelection } = useROIStore();

  return useMutation({
    mutationFn: (id: string) => apiClient.delete(`/api/roi/selections/${id}`),
    onSuccess: (_, id) => {
      // Remove from store
      removeSelection(id);
      
      // Remove from cache
      queryClient.removeQueries({ queryKey: ROI_QUERY_KEYS.selection(id) });
      queryClient.invalidateQueries({ queryKey: ROI_QUERY_KEYS.selections });
    },
    onError: (error) => {
      console.error('Failed to delete ROI selection:', error);
    },
  });
}

// Start ROI monitoring
export function useStartROIMonitoring() {
  const queryClient = useQueryClient();
  const { startMonitoring } = useROIStore();

  return useMutation({
    mutationFn: ({ selectionId, threshold }: { selectionId: string; threshold?: number }) => 
      apiClient.post('/api/roi/monitoring/start', { selectionId, threshold }),
    onSuccess: () => {
      // Update store
      startMonitoring();
      
      // Invalidate monitoring status
      queryClient.invalidateQueries({ queryKey: ROI_QUERY_KEYS.monitoring });
    },
    onError: (error) => {
      console.error('Failed to start ROI monitoring:', error);
    },
  });
}

// Stop ROI monitoring
export function useStopROIMonitoring() {
  const queryClient = useQueryClient();
  const { stopMonitoring } = useROIStore();

  return useMutation({
    mutationFn: () => apiClient.post('/api/roi/monitoring/stop'),
    onSuccess: () => {
      // Update store
      stopMonitoring();
      
      // Invalidate monitoring status
      queryClient.invalidateQueries({ queryKey: ROI_QUERY_KEYS.monitoring });
    },
    onError: (error) => {
      console.error('Failed to stop ROI monitoring:', error);
    },
  });
}

// Validate ROI coordinates
export function useValidateROI() {
  return useMutation({
    mutationFn: (coordinates: ROICoordinates) => 
      apiClient.post<{ valid: boolean; message?: string }>('/api/roi/validate', coordinates),
    onError: (error) => {
      console.error('ROI validation failed:', error);
    },
  });
}
