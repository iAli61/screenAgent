import { useEffect, useState, useRef } from 'react';
import { useROI } from '../../contexts/ROIContext';

interface ROI {
  x: number;
  y: number;
  width: number;
  height: number;
}

interface ROIModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function ROIModal({ isOpen, onClose }: ROIModalProps) {
  const { selectedROI, setSelectedROI } = useROI();
  const [isSelecting, setIsSelecting] = useState(false);
  const [dragStart, setDragStart] = useState<{ x: number; y: number } | null>(null);
  const [tempROI, setTempROI] = useState<ROI | null>(selectedROI);
  const imageRef = useRef<HTMLImageElement>(null);
  const [imageLoaded, setImageLoaded] = useState(false);
  const [isDragging, setIsDragging] = useState(false);

  // Initialize temp ROI when modal opens
  useEffect(() => {
    if (isOpen) {
      setTempROI(selectedROI);
      setIsSelecting(false);
      setDragStart(null);
      setImageLoaded(false);
      setIsDragging(false);
    }
  }, [isOpen, selectedROI]);

  // Handle global mouse events when dragging
  useEffect(() => {
    if (!isDragging || !isSelecting) return;

    const handleGlobalMouseMove = (e: MouseEvent) => {
      if (!dragStart || !imageLoaded || !imageRef.current) return;
      
      const coords = getImageCoordinates(e.clientX, e.clientY);
      const roi: ROI = {
        x: Math.min(dragStart.x, coords.x),
        y: Math.min(dragStart.y, coords.y),
        width: Math.abs(coords.x - dragStart.x),
        height: Math.abs(coords.y - dragStart.y)
      };
      
      console.log('Global mouse move - setting temp ROI:', roi);
      setTempROI(roi);
    };

    const handleGlobalMouseUp = () => {
      console.log('Global mouse up - ending drag');
      setIsDragging(false);
      setDragStart(null);
    };

    document.addEventListener('mousemove', handleGlobalMouseMove);
    document.addEventListener('mouseup', handleGlobalMouseUp);

    return () => {
      document.removeEventListener('mousemove', handleGlobalMouseMove);
      document.removeEventListener('mouseup', handleGlobalMouseUp);
    };
  }, [isDragging, isSelecting, dragStart, imageLoaded]);

  // Close modal on Escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  const handleRefreshPreview = () => {
    setImageLoaded(false);
    if (imageRef.current) {
      imageRef.current.src = `http://localhost:8000/api/screenshots/preview?${new Date().getTime()}`;
    }
  };

  const getImageCoordinates = (clientX: number, clientY: number) => {
    if (!imageRef.current) return { x: 0, y: 0 };
    
    const rect = imageRef.current.getBoundingClientRect();
    const scaleX = imageRef.current.naturalWidth / rect.width;
    const scaleY = imageRef.current.naturalHeight / rect.height;
    
    console.log('Image dimensions:', {
      natural: { width: imageRef.current.naturalWidth, height: imageRef.current.naturalHeight },
      display: { width: rect.width, height: rect.height },
      scale: { x: scaleX, y: scaleY }
    });
    
    return {
      x: Math.round((clientX - rect.left) * scaleX),
      y: Math.round((clientY - rect.top) * scaleY)
    };
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    console.log('Mouse down event triggered');
    
    if (!isSelecting) {
      console.log('Not in selection mode');
      return;
    }
    
    if (!imageLoaded) {
      console.log('Image not loaded yet');
      return;
    }
    
    const coords = getImageCoordinates(e.clientX, e.clientY);
    console.log('Mouse down coordinates:', coords);
    setDragStart(coords);
    setTempROI(null);
    setIsDragging(true);
    e.preventDefault();
    e.stopPropagation();
  };

  const handleStartSelection = () => {
    console.log('Starting selection');
    setIsSelecting(true);
    setTempROI(null);
  };

  const handleCancelSelection = () => {
    console.log('Cancelling selection');
    setIsSelecting(false);
    setDragStart(null);
    setTempROI(selectedROI);
  };

  const handleClearROI = () => {
    console.log('Clearing ROI');
    setTempROI(null);
    setIsSelecting(false);
    setDragStart(null);
  };

  const handleSave = () => {
    console.log('Saving ROI:', tempROI);
    setSelectedROI(tempROI);
    onClose();
  };

  const handleCancel = () => {
    setTempROI(selectedROI);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black bg-opacity-75"
        onClick={handleCancel}
      />
      
      {/* Modal Content */}
      <div className="relative w-[90vw] max-w-4xl max-h-[90vh] mx-4 bg-white rounded-lg shadow-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b bg-gray-50 flex-shrink-0">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Select Region of Interest</h2>
            <p className="text-sm text-gray-600">Click and drag on the preview to select a region to monitor</p>
          </div>
          <button
            onClick={handleCancel}
            className="p-2 hover:bg-gray-200 rounded-full transition-colors"
            aria-label="Close modal"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        {/* Content */}
        <div className="flex-1 overflow-auto p-4">
          <div className="space-y-4">
            {/* Status indicators */}
            <div className="flex gap-2 text-sm flex-wrap">
              <span className={`px-2 py-1 rounded ${imageLoaded ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                Image: {imageLoaded ? 'Loaded' : 'Loading...'}
              </span>
              <span className={`px-2 py-1 rounded ${isSelecting ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'}`}>
                Selection: {isSelecting ? 'Active' : 'Inactive'}
              </span>
              <span className={`px-2 py-1 rounded ${isDragging ? 'bg-purple-100 text-purple-800' : 'bg-gray-100 text-gray-800'}`}>
                Dragging: {isDragging ? 'Yes' : 'No'}
              </span>
              <span className={`px-2 py-1 rounded ${dragStart ? 'bg-orange-100 text-orange-800' : 'bg-gray-100 text-gray-800'}`}>
                Start Point: {dragStart ? `${dragStart.x},${dragStart.y}` : 'None'}
              </span>
            </div>

            {/* Controls */}
            <div className="flex gap-2 flex-wrap">
              <button 
                className={`btn ${isSelecting ? 'btn-secondary' : 'btn-primary'}`} 
                onClick={isSelecting ? handleCancelSelection : handleStartSelection}
                disabled={!imageLoaded}
              >
                {isSelecting ? '❌ Cancel Selection' : '🎯 Select New ROI'}
              </button>
              <button 
                className="btn btn-secondary" 
                onClick={handleRefreshPreview}
              >
                🔄 Refresh Preview
              </button>
              {tempROI && (
                <button 
                  className="btn btn-secondary" 
                  onClick={handleClearROI}
                >
                  🗑️ Clear ROI
                </button>
              )}
            </div>

            {/* Preview Image */}
            <div className="flex justify-center">
              <div className="relative inline-block max-w-full">
                <img 
                  ref={imageRef}
                  src={`http://localhost:8000/api/screenshots/preview?${new Date().getTime()}`}
                  alt="Screen preview"
                  className={`max-w-full h-auto rounded-lg border-2 select-none ${
                    isSelecting && imageLoaded ? 'border-blue-500 cursor-crosshair' : 'border-gray-300'
                  }`}
                  onLoad={() => {
                    console.log('Image loaded successfully');
                    setImageLoaded(true);
                  }}
                  onError={() => {
                    console.error('Failed to load preview image');
                    setImageLoaded(false);
                  }}
                  onMouseDown={handleMouseDown}
                  draggable={false}
                />
                
                {!imageLoaded && (
                  <div className="absolute inset-0 flex items-center justify-center bg-gray-100 rounded-lg">
                    <div className="text-gray-500">Loading preview...</div>
                  </div>
                )}
                
                {/* ROI Overlay */}
                {tempROI && imageRef.current && imageLoaded && (
                  <div
                    className="absolute border-2 border-blue-500 bg-blue-200 bg-opacity-30 pointer-events-none"
                    style={{
                      left: `${(tempROI.x / imageRef.current.naturalWidth) * 100}%`,
                      top: `${(tempROI.y / imageRef.current.naturalHeight) * 100}%`,
                      width: `${(tempROI.width / imageRef.current.naturalWidth) * 100}%`,
                      height: `${(tempROI.height / imageRef.current.naturalHeight) * 100}%`,
                    }}
                  />
                )}
              </div>
            </div>

            {/* ROI Information */}
            {tempROI && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <h3 className="font-semibold text-green-800 mb-2">Selected Region:</h3>
                <div className="text-sm text-green-700 grid grid-cols-2 gap-2">
                  <div>X: {tempROI.x}px</div>
                  <div>Y: {tempROI.y}px</div>
                  <div>Width: {tempROI.width}px</div>
                  <div>Height: {tempROI.height}px</div>
                </div>
              </div>
            )}

            {/* Instructions */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="text-blue-800">
                <strong>Instructions:</strong> {isSelecting 
                  ? 'Click and drag on the preview image to select a region to monitor.'
                  : 'Click "Select New ROI" button and then drag on the image to define the area you want to monitor for changes.'
                }
              </p>
            </div>
          </div>
        </div>
        
        {/* Footer */}
        <div className="flex items-center justify-end gap-2 px-4 py-3 border-t bg-gray-50 flex-shrink-0">
          <button
            onClick={handleCancel}
            className="btn btn-secondary"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="btn btn-primary"
          >
            Save ROI
          </button>
        </div>
      </div>
    </div>
  );
}
