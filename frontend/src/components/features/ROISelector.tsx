import { useState, useRef } from 'react';
import { useROI } from '../../contexts/ROIContext';

interface ROI {
  x: number;
  y: number;
  width: number;
  height: number;
}

export function ROISelector() {
  const { selectedROI, setSelectedROI } = useROI();
  const [isSelecting, setIsSelecting] = useState(false);
  const [dragStart, setDragStart] = useState<{ x: number; y: number } | null>(null);
  const imageRef = useRef<HTMLImageElement>(null);

  const handleSelectROI = () => {
    setIsSelecting(true);
    setSelectedROI(null);
  };

  const handleRefreshPreview = () => {
    // Force reload the preview image
    const img = document.querySelector('img[alt="Screen preview"]') as HTMLImageElement;
    if (img) {
      img.src = img.src + '?' + new Date().getTime();
    }
  };

  const getImageCoordinates = (clientX: number, clientY: number) => {
    if (!imageRef.current) return { x: 0, y: 0 };
    
    const rect = imageRef.current.getBoundingClientRect();
    const scaleX = imageRef.current.naturalWidth / rect.width;
    const scaleY = imageRef.current.naturalHeight / rect.height;
    
    return {
      x: Math.round((clientX - rect.left) * scaleX),
      y: Math.round((clientY - rect.top) * scaleY)
    };
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    if (!isSelecting) return;
    
    const coords = getImageCoordinates(e.clientX, e.clientY);
    setDragStart(coords);
    e.preventDefault();
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isSelecting || !dragStart) return;
    
    const coords = getImageCoordinates(e.clientX, e.clientY);
    const roi: ROI = {
      x: Math.min(dragStart.x, coords.x),
      y: Math.min(dragStart.y, coords.y),
      width: Math.abs(coords.x - dragStart.x),
      height: Math.abs(coords.y - dragStart.y)
    };
    
    setSelectedROI(roi);
  };

  const handleMouseUp = () => {
    if (!isSelecting || !selectedROI) return;
    
    setIsSelecting(false);
    setDragStart(null);
    
    // Log the selected ROI coordinates
    console.log('Selected ROI:', selectedROI);
  };

  const clearROI = () => {
    setSelectedROI(null);
    setIsSelecting(false);
    setDragStart(null);
  };

  return (
    <div className="space-y-6">
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Select Region of Interest</h2>
          <p className="card-subtitle">Configure the area to monitor for changes</p>
        </div>
        
        <div className="mb-4">
          <div className="relative inline-block">
            <img 
              ref={imageRef}
              src="http://localhost:8000/api/screenshots/preview" 
              alt="Screen preview"
              className={`max-w-full h-auto rounded-lg border-2 ${
                isSelecting ? 'border-blue-500 cursor-crosshair' : 'border-gray-300'
              }`}
              onMouseDown={handleMouseDown}
              onMouseMove={handleMouseMove}
              onMouseUp={handleMouseUp}
              onMouseLeave={handleMouseUp}
              draggable={false}
            />
            
            {/* ROI Overlay */}
            {selectedROI && imageRef.current && (
              <div
                className="absolute border-2 border-blue-500 bg-blue-200 bg-opacity-30 pointer-events-none"
                style={{
                  left: `${(selectedROI.x / imageRef.current.naturalWidth) * 100}%`,
                  top: `${(selectedROI.y / imageRef.current.naturalHeight) * 100}%`,
                  width: `${(selectedROI.width / imageRef.current.naturalWidth) * 100}%`,
                  height: `${(selectedROI.height / imageRef.current.naturalHeight) * 100}%`,
                }}
              />
            )}
          </div>
        </div>
        
        <div className="flex gap-2 mb-4">
          <button 
            className={`btn ${isSelecting ? 'btn-secondary' : 'btn-primary'}`} 
            onClick={isSelecting ? clearROI : handleSelectROI}
          >
            {isSelecting ? '❌ Cancel Selection' : '🎯 Select New ROI'}
          </button>
          <button className="btn btn-secondary" onClick={handleRefreshPreview}>
            🔄 Refresh Preview
          </button>
          {selectedROI && (
            <button className="btn btn-secondary" onClick={clearROI}>
              🗑️ Clear ROI
            </button>
          )}
        </div>
        
        {/* ROI Information */}
        {selectedROI && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-4">
            <h3 className="font-semibold text-green-800 mb-2">Selected Region:</h3>
            <div className="text-sm text-green-700 grid grid-cols-2 gap-2">
              <div>X: {selectedROI.x}px</div>
              <div>Y: {selectedROI.y}px</div>
              <div>Width: {selectedROI.width}px</div>
              <div>Height: {selectedROI.height}px</div>
            </div>
          </div>
        )}
        
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-blue-800">
            <strong>How it works:</strong> {isSelecting 
              ? 'Click and drag on the preview image to select a region to monitor.'
              : 'ScreenAgent monitors your selected region and automatically captures screenshots when significant changes are detected. Use the buttons above to manually capture or change the monitored area.'
            }
          </p>
        </div>
      </div>
      
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Monitoring Statistics</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-gray-900">0</div>
            <div className="text-sm text-gray-600">Total Screenshots</div>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-gray-900">0h 0m</div>
            <div className="text-sm text-gray-600">Monitoring Time</div>
          </div>
          <div className="text-center p-4 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-gray-900">Never</div>
            <div className="text-sm text-gray-600">Last Capture</div>
          </div>
        </div>
      </div>
    </div>
  )
}
