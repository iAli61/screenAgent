import { useState } from 'react';
import { useTakeScreenshot, useScreenshots, useDeleteAllScreenshots, useAnalyzeScreenshot } from '../../services/screenshotApi';
import { useROI } from '../../contexts/ROIContext';
import { ImageModal } from '../ui/ImageModal';
import { useScreenshotStore } from '../../stores/useScreenshotStore';

export function SingleScreenshot() {
  const { selectedROI } = useROI();
  const takeScreenshotMutation = useTakeScreenshot();
  const deleteAllMutation = useDeleteAllScreenshots();
  const analyzeScreenshotMutation = useAnalyzeScreenshot();
  const { data: screenshotsData, isLoading, error, refetch } = useScreenshots();
  const { screenshots: storeScreenshots } = useScreenshotStore();
  
  // Modal state
  const [selectedImage, setSelectedImage] = useState<{
    url: string;
    alt: string;
    metadata: any;
    analysis?: {
      status: 'pending' | 'completed' | 'error';
      result?: string;
      error?: string;
    };
  } | null>(null);

  const handleTakeScreenshot = async () => {
    try {
      // Use the selected ROI if available
      const params = selectedROI ? { roi: selectedROI } : {};
      await takeScreenshotMutation.mutateAsync(params);
      // Refetch screenshots after taking a new one
      refetch();
    } catch (error) {
      console.error('Failed to take screenshot:', error);
      // Optionally show error message to user
    }
  };

  const handleDeleteAll = async () => {
    try {
      await deleteAllMutation.mutateAsync();
      // Optionally refetch screenshots to update the UI
      await refetch();
    } catch (error) {
      console.error('Failed to delete all screenshots:', error);
    }
  };

  const handleImageClick = (screenshot: any) => {
    // Get analysis data from store if available
    const storeScreenshot = storeScreenshots.find(s => s.id === screenshot.id);
    const analysis = storeScreenshot?.analysis;
    
    setSelectedImage({
      url: `http://localhost:8000/api/screenshots/${screenshot.id}`,
      alt: `Screenshot ${screenshot.id}`,
      metadata: {
        id: screenshot.id,
        timestamp: screenshot.timestamp,
        width: screenshot.width,
        height: screenshot.height,
        size_bytes: screenshot.size_bytes
      },
      analysis: analysis
    });
  };

  const handleAnalyzeImage = async (imageId: string, prompt?: string, provider?: string, model?: string) => {
    try {
      // Update the screenshot status to pending
      const { updateScreenshot } = useScreenshotStore.getState();
      updateScreenshot(imageId, {
        analysis: { status: 'pending' }
      });

      // Update the modal if this is the currently selected image
      setSelectedImage(prev => {
        if (prev && prev.metadata.id === imageId) {
          return {
            ...prev,
            analysis: { status: 'pending' }
          };
        }
        return prev;
      });

      const result = await analyzeScreenshotMutation.mutateAsync({ 
        id: imageId, 
        prompt: prompt || 'Describe what you see in this screenshot in detail.',
        provider: provider,
        model: model
      });
      console.log('Analysis result:', result);
      
      const analysisResult = {
        status: 'completed' as const,
        result: result.result?.analysis || 'Analysis completed successfully'
      };
      
      // Update the screenshot with analysis result
      updateScreenshot(imageId, {
        analysis: analysisResult
      });
      
      // Update the modal if this is the currently selected image
      setSelectedImage(prev => {
        if (prev && prev.metadata.id === imageId) {
          return {
            ...prev,
            analysis: analysisResult
          };
        }
        return prev;
      });
      
      // Trigger a refetch to update the UI
      refetch();
    } catch (error) {
      console.error('Failed to analyze screenshot:', error);
      
      const errorResult = {
        status: 'error' as const,
        error: error instanceof Error ? error.message : 'Analysis failed'
      };
      
      // Update screenshot with error status
      const { updateScreenshot } = useScreenshotStore.getState();
      updateScreenshot(imageId, {
        analysis: errorResult
      });
      
      // Update the modal if this is the currently selected image
      setSelectedImage(prev => {
        if (prev && prev.metadata.id === imageId) {
          return {
            ...prev,
            analysis: errorResult
          };
        }
        return prev;
      });
      
      alert('Failed to analyze screenshot. Please try again.');
    }
  };

  return (
    <div className="space-y-6">
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Single Screenshot</h2>
          <p className="card-subtitle">Take manual screenshots and manage your collection</p>
        </div>
        
        <div className="flex gap-2 mb-4">
          <button 
            className="btn btn-success" 
            onClick={handleTakeScreenshot}
            disabled={takeScreenshotMutation.isPending}
          >
            {takeScreenshotMutation.isPending 
              ? '⏳ Taking...' 
              : selectedROI 
                ? '📸 Take ROI Screenshot' 
                : '📸 Take Full Screenshot'
            }
          </button>
          <button 
            className="btn btn-danger"
            onClick={handleDeleteAll}
            disabled={deleteAllMutation.isPending}
          >
            {deleteAllMutation.isPending ? '⏳ Deleting...' : '🗑️ Delete All Screenshots'}
          </button>
        </div>
        
        {/* ROI Status */}
        {selectedROI && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
            <p className="text-blue-800 text-sm">
              <strong>🎯 ROI Selected:</strong> {selectedROI.width}×{selectedROI.height} at ({selectedROI.x}, {selectedROI.y})
            </p>
          </div>
        )}
      </div>
      
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Screenshot Gallery</h2>
          <p className="card-subtitle">View and manage your manually captured screenshots</p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {isLoading ? (
            <div className="text-center text-gray-500 py-8 col-span-full">
              Loading screenshots...
            </div>
          ) : error ? (
            <div className="text-center text-red-500 py-8 col-span-full">
              Error loading screenshots: {error.message}
            </div>
          ) : screenshotsData && screenshotsData.screenshots.length > 0 ? (
            screenshotsData.screenshots.map((screenshot) => (
              <div key={screenshot.id} className="border rounded-lg p-4 bg-white shadow-sm">
                <img 
                  src={`http://localhost:8000/api/screenshots/${screenshot.id}`}
                  alt={`Screenshot ${screenshot.id}`}
                  className="w-full h-auto rounded mb-2 cursor-pointer hover:opacity-90 transition-opacity"
                  onClick={() => handleImageClick(screenshot)}
                  onError={(e) => {
                    console.error('Image failed to load:', screenshot.id);
                    e.currentTarget.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjEwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjNmNGY2Ii8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzY4NzI4MCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkltYWdlIGZhaWxlZCB0byBsb2FkPC90ZXh0Pjwvc3ZnPg==';
                  }}
                />
                <div className="text-sm text-gray-600 space-y-1">
                  <p className="font-medium">{screenshot.id.slice(0, 8)}...</p>
                  <p>{new Date(screenshot.timestamp).toLocaleString()}</p>
                  <p>{screenshot.width} x {screenshot.height}</p>
                  <p>{(screenshot.size_bytes / 1024).toFixed(1)} KB</p>
                </div>
              </div>
            ))
          ) : (
            <div className="text-center text-gray-500 py-8 col-span-full">
              No screenshots available. Take your first screenshot!
            </div>
          )}
        </div>
      </div>

      {/* Image Modal */}
      {selectedImage && (
        <ImageModal
          isOpen={!!selectedImage}
          onClose={() => setSelectedImage(null)}
          imageUrl={selectedImage.url}
          imageAlt={selectedImage.alt}
          metadata={selectedImage.metadata}
          onAnalyze={handleAnalyzeImage}
          analysisData={selectedImage.analysis}
        />
      )}
    </div>
  )
}
