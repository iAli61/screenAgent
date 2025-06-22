export function Settings() {
  return (
    <div className="space-y-6">
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">AI Analysis Settings</h2>
          <p className="card-subtitle">Configure AI-powered screenshot analysis</p>
        </div>
        
        <form className="space-y-4">
          <div>
            <label className="flex items-center">
              <input type="checkbox" className="mr-2" />
              Enable AI Analysis
            </label>
            <p className="text-sm text-gray-600 mt-1">
              Automatically analyze screenshots with AI to describe content and identify important elements.
            </p>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              AI Model
            </label>
            <input 
              type="text" 
              defaultValue="gpt-4o"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-sm text-gray-600 mt-1">
              Specify the AI model to use for analysis (e.g., gpt-4o, claude-3, etc.)
            </p>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Default Analysis Prompt
            </label>
            <textarea 
              rows={3}
              defaultValue="Describe what you see in this screenshot, focusing on the most important elements and any notable changes or activities."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-sm text-gray-600 mt-1">
              This prompt will be used for automatic analysis. You can customize it for specific use cases.
            </p>
          </div>
          
          <button type="submit" className="btn btn-primary">
            💾 Save Settings
          </button>
        </form>
      </div>
      
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Monitoring Settings</h2>
          <p className="card-subtitle">Configure how ScreenAgent monitors your screen</p>
        </div>
        
        <form className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Change Sensitivity
            </label>
            <input 
              type="range" 
              min="1" 
              max="100" 
              defaultValue="20"
              className="w-full"
            />
            <div className="flex justify-between text-sm text-gray-600 mt-1">
              <span>Very Sensitive</span>
              <span>Balanced</span>
              <span>Less Sensitive</span>
            </div>
            <p className="text-sm text-gray-600 mt-1">
              Higher sensitivity will capture more minor changes.
            </p>
          </div>
          
          <button type="submit" className="btn btn-primary">
            💾 Save Settings
          </button>
        </form>
      </div>
    </div>
  )
}
