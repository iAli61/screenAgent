import { useState } from 'react';
import { useSettingsStore } from '../../stores/useSettingsStore';
import { useROIStore } from '../../stores/useROIStore';
import { useSaveSettings } from '../../services/settingsApi';

export function Settings() {
  const { ai, monitoring, updateAISettings, updateMonitoringSettings } = useSettingsStore();
  const { setCurrentCoordinates } = useROIStore();
  const saveSettingsMutation = useSaveSettings();
  
  // Local state for form inputs
  const [aiModel, setAiModel] = useState(ai.model || 'gpt-4o');
  const [defaultPrompt, setDefaultPrompt] = useState(ai.customPrompt || 'Describe what you see in this screenshot, focusing on the most important elements and any notable changes or activities.');
  const [autoAnalyze, setAutoAnalyze] = useState(ai.autoAnalyze || false);
  const [changeSensitivity, setChangeSensitivity] = useState(monitoring.threshold || 20);
  
  // ROI settings
  const [roiX, setRoiX] = useState(328);
  const [roiY, setRoiY] = useState(2);
  const [roiWidth, setRoiWidth] = useState(1927);
  const [roiHeight, setRoiHeight] = useState(1026);

  const handleSaveAISettings = async () => {
    try {
      updateAISettings({
        model: aiModel,
        customPrompt: defaultPrompt,
        autoAnalyze: autoAnalyze,
      });
      
      await saveSettingsMutation.mutateAsync({
        ai: {
          model: aiModel,
          customPrompt: defaultPrompt,
          autoAnalyze: autoAnalyze,
        }
      });
      
      alert('AI settings saved successfully!');
    } catch (error) {
      console.error('Failed to save AI settings:', error);
      alert('Failed to save AI settings. Please try again.');
    }
  };

  const handleSaveMonitoringSettings = async () => {
    try {
      updateMonitoringSettings({
        threshold: changeSensitivity,
      });
      
      // Update ROI coordinates
      setCurrentCoordinates({
        x: roiX,
        y: roiY,
        width: roiWidth,
        height: roiHeight,
      });
      
      await saveSettingsMutation.mutateAsync({
        monitoring: {
          threshold: changeSensitivity,
        }
      });
      
      // Also save ROI to backend
      await fetch('/api/configuration/roi', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          roi: [roiX, roiY, roiWidth, roiHeight]
        }),
      });
      
      alert('Monitoring settings saved successfully!');
    } catch (error) {
      console.error('Failed to save monitoring settings:', error);
      alert('Failed to save monitoring settings. Please try again.');
    }
  };

  return (
    <div className="space-y-6">
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">AI Analysis Settings</h2>
          <p className="card-subtitle">Configure AI-powered screenshot analysis</p>
        </div>
        
        <form className="space-y-4" onSubmit={(e) => { e.preventDefault(); handleSaveAISettings(); }}>
          <div>
            <label className="flex items-center">
              <input 
                type="checkbox" 
                className="mr-2" 
                checked={autoAnalyze}
                onChange={(e) => setAutoAnalyze(e.target.checked)}
              />
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
              value={aiModel}
              onChange={(e) => setAiModel(e.target.value)}
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
              value={defaultPrompt}
              onChange={(e) => setDefaultPrompt(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-sm text-gray-600 mt-1">
              This prompt will be used for automatic analysis. You can customize it for specific use cases.
            </p>
          </div>
          
          <button type="submit" className="btn btn-primary" disabled={saveSettingsMutation.isPending}>
            {saveSettingsMutation.isPending ? '💾 Saving...' : '💾 Save Settings'}
          </button>
        </form>
      </div>
      
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Monitoring Settings</h2>
          <p className="card-subtitle">Configure how ScreenAgent monitors your screen</p>
        </div>
        
        <form className="space-y-4" onSubmit={(e) => { e.preventDefault(); handleSaveMonitoringSettings(); }}>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Default ROI (Region of Interest)
            </label>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs text-gray-600 mb-1">X Position</label>
                <input 
                  type="number" 
                  value={roiX}
                  onChange={(e) => setRoiX(parseInt(e.target.value) || 0)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-600 mb-1">Y Position</label>
                <input 
                  type="number" 
                  value={roiY}
                  onChange={(e) => setRoiY(parseInt(e.target.value) || 0)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-600 mb-1">Width</label>
                <input 
                  type="number" 
                  value={roiWidth}
                  onChange={(e) => setRoiWidth(parseInt(e.target.value) || 0)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-xs text-gray-600 mb-1">Height</label>
                <input 
                  type="number" 
                  value={roiHeight}
                  onChange={(e) => setRoiHeight(parseInt(e.target.value) || 0)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
            <p className="text-sm text-gray-600 mt-1">
              Define the specific area of the screen to monitor (in pixels). Current: X:{roiX}, Y:{roiY}, W:{roiWidth}, H:{roiHeight}
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Change Sensitivity
            </label>
            <input 
              type="range" 
              min="1" 
              max="100" 
              value={changeSensitivity}
              onChange={(e) => setChangeSensitivity(parseInt(e.target.value))}
              className="w-full"
            />
            <div className="flex justify-between text-sm text-gray-600 mt-1">
              <span>Very Sensitive</span>
              <span>Balanced (Current: {changeSensitivity}%)</span>
              <span>Less Sensitive</span>
            </div>
            <p className="text-sm text-gray-600 mt-1">
              Higher sensitivity will capture more minor changes.
            </p>
          </div>
          
          <button type="submit" className="btn btn-primary" disabled={saveSettingsMutation.isPending}>
            {saveSettingsMutation.isPending ? '💾 Saving...' : '💾 Save Settings'}
          </button>
        </form>
      </div>
    </div>
  )
}
