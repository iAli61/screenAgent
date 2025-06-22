interface HeaderProps {
  className?: string
}

export function Header({ className = '' }: HeaderProps) {
  return (
    <header className={`bg-white shadow-sm p-4 ${className}`}>
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-blue-600 mb-2">
            📸 ScreenAgent
          </h1>
          <p className="text-gray-600">
            Smart screen monitoring with AI-powered analysis
          </p>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-500">
            Status: <span className="text-green-600">Active</span>
          </span>
          <span className="text-sm text-gray-500">
            ROI: (100, 100, 800, 800)
          </span>
        </div>
      </div>
    </header>
  )
}
