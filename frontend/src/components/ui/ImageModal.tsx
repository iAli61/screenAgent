import { useEffect } from 'react';

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
  onAnalyze?: (screenshotId: string) => void;
}

export function ImageModal({ isOpen, onClose, imageUrl, imageAlt, metadata, onAnalyze }: ImageModalProps) {
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
      <div className="relative max-w-7xl max-h-[90vh] mx-4 bg-white rounded-lg shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b bg-gray-50">
          <div className="flex-1">
            {metadata && (
              <div className="text-sm text-gray-600">
                <span className="font-medium">ID:</span> {metadata.id.substring(0, 8)}...
                <span className="ml-4 font-medium">Size:</span> {metadata.width} × {metadata.height}
                <span className="ml-4 font-medium">File Size:</span> {formatFileSize(metadata.size_bytes)}
                <span className="ml-4 font-medium">Date:</span> {formatDate(metadata.timestamp)}
              </div>
            )}
          </div>
          <button
            onClick={onClose}
            className="ml-4 p-2 hover:bg-gray-200 rounded-full transition-colors"
            aria-label="Close modal"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        {/* Image Container */}
        <div className="flex items-center justify-center p-4 max-h-[calc(90vh-120px)] overflow-auto">
          <img
            src={imageUrl}
            alt={imageAlt}
            className="max-w-full max-h-full object-contain rounded"
            style={{ maxHeight: 'calc(90vh - 120px)' }}
          />
        </div>
        
        {/* Footer */}
        <div className="flex items-center justify-between p-4 border-t bg-gray-50">
          <div className="text-sm text-gray-500">
            Press ESC to close or click outside the image
          </div>
          <div className="flex gap-2">
            {metadata && onAnalyze && (
              <button
                onClick={() => onAnalyze(metadata.id)}
                className="btn btn-primary text-sm"
              >
                🤖 Analyze
              </button>
            )}
            <a
              href={imageUrl}
              download
              className="btn btn-secondary text-sm"
            >
              📥 Download
            </a>
            <button
              onClick={() => {
                navigator.clipboard.writeText(imageUrl);
                // You could add a toast notification here
              }}
              className="btn btn-secondary text-sm"
            >
              📋 Copy URL
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
