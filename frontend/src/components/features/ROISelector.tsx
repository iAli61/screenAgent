export function ROISelector() {
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
              src="/api/preview" 
              alt="Screen preview"
              className="max-w-full h-auto rounded-lg border-2 border-gray-300"
            />
          </div>
        </div>
        
        <div className="flex gap-2 mb-4">
          <button className="btn btn-primary">
            🎯 Select New ROI
          </button>
          <button className="btn btn-secondary">
            🔄 Refresh Preview
          </button>
        </div>
        
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-blue-800">
            <strong>How it works:</strong> ScreenAgent monitors your selected region and automatically 
            captures screenshots when significant changes are detected. Use the buttons above to 
            manually capture or change the monitored area.
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
