export function SingleScreenshot() {
  return (
    <div className="space-y-6">
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Single Screenshot</h2>
          <p className="card-subtitle">Take manual screenshots and manage your collection</p>
        </div>
        
        <div className="flex gap-2 mb-4">
          <button className="btn btn-success">
            📸 Take Single Screenshot
          </button>
          <button className="btn btn-danger">
            🗑️ Delete All Screenshots
          </button>
        </div>
      </div>
      
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Screenshot Gallery</h2>
          <p className="card-subtitle">View and manage your manually captured screenshots</p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {/* Screenshots will be loaded here */}
          <div className="text-center text-gray-500 py-8">
            No screenshots available. Take your first screenshot!
          </div>
        </div>
      </div>
    </div>
  )
}
