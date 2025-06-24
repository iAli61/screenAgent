// Service exports for easy importing
export { apiClient, APIClient, APIError } from './apiClient';

// Screenshot services
export {
  useScreenshots,
  useScreenshot,
  useUploadScreenshot,
  useDeleteScreenshot,
  useAnalyzeScreenshot,
  useScreenshotAnalysis,
  useTakeScreenshot,
  QUERY_KEYS as SCREENSHOT_QUERY_KEYS,
} from './screenshotApi';

// Settings services
export {
  useSettings,
  useAISettings,
  useMonitoringSettings,
  useSaveSettings,
  useSaveAISettings,
  useSaveMonitoringSettings,
  useResetSettings,
  useExportSettings,
  useImportSettings,
  SETTINGS_QUERY_KEYS,
} from './settingsApi';

// ROI services
export {
  useROISelections,
  useROISelection,
  useROIPreview,
  useROIMonitoring,
  useCreateROISelection,
  useUpdateROISelection,
  useDeleteROISelection,
  useStartROIMonitoring,
  useStopROIMonitoring,
  useValidateROI,
  ROI_QUERY_KEYS,
} from './roiApi';

// Analysis services
export {
  useAnalysisHistory,
  useAnalysisResult,
  useAnalysisModels,
  useAnalyzeScreenshot as useAnalyzeScreenshotService,
  useMultiModelAnalysis,
  useReanalyze,
  useSaveAnalysis,
  useDeleteAnalysis,
  useExportAnalysis,
  ANALYSIS_QUERY_KEYS,
  type AnalysisResult,
  type AnalysisModel,
} from './analysisApi';

// Models services
export {
  useModels,
  useProviderInfo,
  getProviderOptions,
  getModelOptions,
  MODELS_QUERY_KEYS,
  type Provider,
  type ModelsResponse,
  type ProviderInfoResponse,
} from './modelsApi';

// Type exports
export type { APIResponse } from './apiClient';
