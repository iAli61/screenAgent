import { useEffect, useState } from 'react';
import { useModels, getProviderOptions, getModelOptions } from '../../services/modelsApi';
import { fetchPrompts, Prompt } from '../../services/promptsApi';
import { PromptEditor } from './PromptEditor';

interface AnalysisData {
  status: 'pending' | 'completed' | 'error';
  result?: string;
  error?: string;
}

interface ImageModalProps {
  isOpen: boolean;
  onClose: () => void;
  imageUrl: string;
  imageAlt: string;
  metadata?: {
    id: string;
    timestamp: string;
    width: number;
    height: number;
    size_bytes: number;
  };
  onAnalyze?: (screenshotId: string, prompt?: string, provider?: string, model?: string) => void;
  analysisData?: AnalysisData;
}

export function ImageModal({ isOpen, onClose, imageUrl, imageAlt, metadata, onAnalyze, analysisData }: ImageModalProps) {
  // State for prompt selection
  const [selectedPrompt, setSelectedPrompt] = useState('general');
  const [customPrompt, setCustomPrompt] = useState('Describe what you see in this screenshot in detail.');
  
  // State for provider and model selection
  const [selectedProvider, setSelectedProvider] = useState('');
  const [selectedModel, setSelectedModel] = useState('');
  
  // State for prompts management
  const [prompts, setPrompts] = useState<Record<string, Prompt>>({});
  const [promptsLoading, setPromptsLoading] = useState(false);
  const [editingPrompt, setEditingPrompt] = useState<string | null>(null);
  
  // Fetch available models and providers
  const { data: modelsData, isLoading: modelsLoading } = useModels();

  // Get the prompt text based on selection
  const getPromptText = (promptType: string) => {
    // If we have prompts from API, use them
    if (prompts[promptType]?.text) {
      return prompts[promptType].text;
    }
    
    // Fallback to hardcoded prompts if API is not available
    switch (promptType) {
      case 'general':
        return 'Describe what you see in this screenshot in detail.';
      case 'ui_elements':
        return 'Identify all UI elements, buttons, menus, and interface components visible in this screenshot.';
      case 'text_extraction':
        return 'Extract and list all visible text content from this screenshot.';
      case 'ux_analysis':
        return 'Analyze the user experience and usability aspects of this interface.';
      case 'issue_detection':
        return 'Identify any potential issues, errors, or problems visible in this screenshot.';
      default:
        return 'Describe what you see in this screenshot in detail.';
    }
  };

  // Load prompts from API
  const loadPrompts = async () => {
    setPromptsLoading(true);
    try {
      const response = await fetchPrompts();
      setPrompts(response.prompts);
    } catch (error) {
      console.error('Failed to load prompts:', error);
      // Keep using fallback prompts
    } finally {
      setPromptsLoading(false);
    }
  };

  // Handler for analyzing with prompt
  const handleAnalyzeWithPrompt = (screenshotId: string) => {
    if (onAnalyze) {
      const prompt = selectedPrompt === 'custom' ? customPrompt : getPromptText(selectedPrompt);
      onAnalyze(screenshotId, prompt, selectedProvider || undefined, selectedModel || undefined);
    }
  };
  
  // Get available provider options
  const providerOptions = getProviderOptions(modelsData);
  
  // Get available model options for selected provider
  const modelOptions = getModelOptions(selectedProvider, modelsData);
  
  // Load prompts when modal opens
  useEffect(() => {
    if (isOpen) {
      loadPrompts();
    }
  }, [isOpen]);
  
  // Set default provider when data loads
  useEffect(() => {
    if (modelsData && !selectedProvider && providerOptions.length > 0) {
      setSelectedProvider(providerOptions[0].value);
    }
  }, [modelsData, selectedProvider, providerOptions]);
  
  // Set default model when provider changes
  useEffect(() => {
    if (selectedProvider && modelOptions.length > 0 && !modelOptions.find(m => m.value === selectedModel)) {
      setSelectedModel(modelOptions[0].value);
    }
  }, [selectedProvider, modelOptions, selectedModel]);

  // Close modal on Escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      // Prevent body scroll when modal is open
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black bg-opacity-75"
        onClick={onClose}
      />
      
      {/* Modal Content */}
      <div className="modal-resizable relative w-[90vw] max-w-none max-h-[90vh] mx-4 bg-white rounded-lg shadow-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="modal-header-compact flex items-center justify-between px-3 py-2 border-b bg-gray-50 flex-shrink-0">
          <div className="flex-1">
            {metadata && (
              <div className="text-xs text-gray-600">
                <span className="font-medium">ID:</span> {metadata.id.substring(0, 8)}...
                <span className="ml-3 font-medium">Size:</span> {metadata.width} × {metadata.height}
                <span className="ml-3 font-medium">File Size:</span> {formatFileSize(metadata.size_bytes)}
                <span className="ml-3 font-medium">Date:</span> {formatDate(metadata.timestamp)}
              </div>
            )}
          </div>
          <button
            onClick={onClose}
            className="ml-3 p-1.5 hover:bg-gray-200 rounded-full transition-colors"
            aria-label="Close modal"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        {/* Main Content Section */}
        <div className="flex-1 flex flex-col min-h-0 overflow-y-auto">
          {/* Image Container with Action Buttons */}
          <div className="relative flex-shrink-0 flex items-center justify-center p-4">
            <img
              src={imageUrl}
              alt={imageAlt}
              className="max-w-full max-h-full object-contain rounded"
              style={{ maxHeight: 'calc(50vh - 100px)' }}
            />
            
            {/* Action Buttons Overlay */}
            <div className="absolute top-6 right-6 flex gap-2">
              <button
                onClick={() => {
                  navigator.clipboard.writeText(imageUrl);
                  // You could add a toast notification here
                }}
                className="p-2 bg-white/90 hover:bg-white shadow-lg rounded-lg border transition-all duration-200 hover:scale-105"
                title="Copy URL"
              >
                <svg className="w-4 h-4 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
              </button>
              <button
                onClick={async () => {
                  try {
                    const response = await fetch(imageUrl);
                    const blob = await response.blob();
                    const clipboardItem = new ClipboardItem({ [blob.type]: blob });
                    await navigator.clipboard.write([clipboardItem]);
                    // You could add a toast notification here
                  } catch (error) {
                    console.error('Failed to copy image to clipboard:', error);
                    // You could add an error toast notification here
                  }
                }}
                className="p-2 bg-white/90 hover:bg-white shadow-lg rounded-lg border transition-all duration-200 hover:scale-105"
                title="Copy Image to Clipboard"
              >
                <svg className="w-4 h-4 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                </svg>
              </button>
              <a
                href={imageUrl}
                download
                className="p-2 bg-white/90 hover:bg-white shadow-lg rounded-lg border transition-all duration-200 hover:scale-105"
                title="Download"
              >
                <svg className="w-4 h-4 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </a>
            </div>
          </div>
          
          {/* AI Analysis Panel - Now below the image */}
          <div className="border-t bg-gray-50 flex-shrink-0">
            <div className="p-4 flex-1 overflow-y-auto">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2 mb-4">
                🤖 AI Analysis
              </h3>
              
              {/* Compact Analysis Configuration Section */}
              <div className="bg-white p-3 rounded-lg border mb-4">
                <div className="flex flex-col gap-3">
                  {/* Analysis Prompt with Provider, Model, and Button in one row */}
                  <div className="flex flex-col lg:flex-row lg:items-end gap-3">
                    <div className="flex-1">
                      <label className="text-xs font-medium text-gray-600 block mb-1">Analysis Prompt:</label>
                      <select
                        value={selectedPrompt}
                        onChange={(e) => setSelectedPrompt(e.target.value)}
                        className="w-full p-2 text-sm border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        disabled={promptsLoading}
                      >
                        {promptsLoading ? (
                          <option>Loading prompts...</option>
                        ) : (
                          <>
                            {Object.values(prompts).map(prompt => (
                              <option key={prompt.id} value={prompt.id}>
                                {prompt.name}
                              </option>
                            ))}
                            <option value="custom">✏️ Custom Prompt</option>
                          </>
                        )}
                      </select>
                    </div>
                    
                    <div className="flex-1 lg:flex-none lg:w-32">
                      <label className="text-xs font-medium text-gray-600 block mb-1">Provider:</label>
                      <select
                        value={selectedProvider}
                        onChange={(e) => setSelectedProvider(e.target.value)}
                        className="w-full p-2 text-sm border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        disabled={modelsLoading}
                      >
                        {modelsLoading ? (
                          <option>Loading...</option>
                        ) : (
                          providerOptions.map(provider => (
                            <option key={provider.value} value={provider.value}>
                              {provider.label}
                            </option>
                          ))
                        )}
                      </select>
                    </div>
                    
                    <div className="flex-1 lg:flex-none lg:w-40">
                      <label className="text-xs font-medium text-gray-600 block mb-1">Model:</label>
                      <select
                        value={selectedModel}
                        onChange={(e) => setSelectedModel(e.target.value)}
                        className="w-full p-2 text-sm border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        disabled={modelsLoading || !selectedProvider}
                      >
                        {modelOptions.length === 0 ? (
                          <option>No models</option>
                        ) : (
                          modelOptions.map(model => (
                            <option key={model.value} value={model.value}>
                              {model.label}
                            </option>
                          ))
                        )}
                      </select>
                    </div>
                    
                    {/* Small Analyze Button with Send Icon */}
                    {metadata && onAnalyze && (
                      <div>
                        <button
                          onClick={() => handleAnalyzeWithPrompt(metadata.id)}
                          className="inline-flex items-center justify-center p-2 rounded-md bg-blue-600 text-white border border-transparent shadow-sm hover:bg-blue-700 hover:scale-105 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
                          title={analysisData?.status === 'pending' ? 'Analyzing...' : 'Analyze Screenshot'}
                          disabled={
                            analysisData?.status === 'pending' || 
                            (selectedPrompt === 'custom' && !customPrompt.trim()) ||
                            !selectedProvider ||
                            !selectedModel ||
                            modelsLoading
                          }
                        >
                          {analysisData?.status === 'pending' ? (
                            <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                          ) : (
                            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                            </svg>
                          )}
                        </button>
                      </div>
                    )}
                  </div>
                </div>

                {/* Show custom prompt input when "custom" is selected */}
                {selectedPrompt === 'custom' && (
                  <div className="mt-3">
                    <textarea
                      value={customPrompt}
                      onChange={(e) => setCustomPrompt(e.target.value)}
                      placeholder="Enter your custom analysis prompt..."
                      className="w-full p-2 text-xs border rounded-md resize-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      rows={2}
                    />
                  </div>
                )}
                
                {/* Show prompt editor for API prompts */}
                {selectedPrompt !== 'custom' && prompts[selectedPrompt] && editingPrompt === selectedPrompt && (
                  <div className="mt-3">
                    <PromptEditor
                      prompt={prompts[selectedPrompt]}
                      onSave={(updatedPrompt) => {
                        setPrompts(prev => ({
                          ...prev,
                          [updatedPrompt.id]: updatedPrompt
                        }));
                        setEditingPrompt(null);
                      }}
                      onCancel={() => setEditingPrompt(null)}
                    />
                  </div>
                )}
                
                {/* Show selected prompt preview when not custom and not editing */}
                {selectedPrompt !== 'custom' && editingPrompt !== selectedPrompt && (
                  <div className="mt-2 flex items-center justify-between">
                    <div className="text-xs text-gray-600 italic flex-1">
                      "{getPromptText(selectedPrompt)}"
                    </div>
                    {prompts[selectedPrompt] && (
                      <button
                        onClick={() => setEditingPrompt(selectedPrompt)}
                        className="ml-2 p-1 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded transition-all duration-200"
                        title="Edit this prompt"
                      >
                        <svg className="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                      </button>
                    )}
                  </div>
                )}
              </div>

              {/* Analysis Results Section */}
              <div className="bg-white p-4 rounded-lg border">
                {!analysisData ? (
                  <div className="text-center text-gray-500 py-8">
                    <div className="mb-4">
                      <svg className="w-12 h-12 mx-auto text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                      </svg>
                    </div>
                    <p className="text-sm">Select a prompt and click "Analyze" to get AI insights about this screenshot</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <h4 className="text-sm font-semibold text-gray-800 flex items-center gap-2">
                      📊 Analysis Results
                    </h4>
                    
                    {/* Analysis Status */}
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-gray-700">Status:</span>
                      {analysisData.status === 'pending' && (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                          ⏳ Analyzing...
                        </span>
                      )}
                      {analysisData.status === 'completed' && (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          ✅ Complete
                        </span>
                      )}
                      {analysisData.status === 'error' && (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                          ❌ Error
                        </span>
                      )}
                    </div>

                    {/* Analysis Result */}
                    {analysisData.result && (
                      <div>
                        <h5 className="text-sm font-medium text-gray-700 mb-2">Analysis Result:</h5>
                        <div className="bg-gray-50 p-3 rounded border text-sm text-gray-800 leading-relaxed whitespace-pre-wrap">
                          {analysisData.result}
                        </div>
                      </div>
                    )}

                    {/* Error Message */}
                    {analysisData.error && (
                      <div>
                        <h5 className="text-sm font-medium text-red-700 mb-2">Error:</h5>
                        <div className="bg-red-50 p-3 rounded border border-red-200 text-sm text-red-800">
                          {analysisData.error}
                        </div>
                      </div>
                    )}

                    {/* Loading Animation */}
                    {analysisData.status === 'pending' && (
                      <div className="flex items-center justify-center py-4">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
