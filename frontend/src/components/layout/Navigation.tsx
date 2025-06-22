import { Tab } from '@/stores'

interface NavigationProps {
  activeTab: Tab
  onTabChange: (tab: Tab) => void
}

export function Navigation({ activeTab, onTabChange }: NavigationProps) {
  const tabs = [
    { id: 'screenshots' as const, label: 'Screenshots' },
    { id: 'monitoring' as const, label: 'Monitoring' },
    { id: 'roi' as const, label: 'Select ROI' },
    { id: 'settings' as const, label: 'Settings' },
  ]

  return (
    <nav className="bg-white border-b-2 border-gray-200">
      <div className="flex">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`px-6 py-4 font-medium text-sm border-b-2 transition-colors ${
              activeTab === tab.id
                ? 'text-blue-600 border-blue-600 bg-white'
                : 'text-gray-600 border-transparent hover:text-gray-900 hover:bg-gray-50'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>
    </nav>
  )
}
