import { useState } from 'react';
import { Prompt, updatePrompt } from '../../services/promptsApi';

interface PromptEditorProps {
  prompt: Prompt;
  onSave?: (updatedPrompt: Prompt) => void;
  onCancel?: () => void;
}

export function PromptEditor({ prompt, onSave, onCancel }: PromptEditorProps) {
  const [text, setText] = useState(prompt.text);
  const [isSaving, setIsSaving] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  const handleTextChange = (newText: string) => {
    setText(newText);
    setHasChanges(newText !== prompt.text);
  };

  const handleSave = async () => {
    if (!hasChanges) return;
    
    setIsSaving(true);
    try {
      const updatedPrompt = await updatePrompt(prompt.id, {
        text: text,
        name: prompt.name,
        description: prompt.description
      });
      
      setHasChanges(false);
      onSave?.(updatedPrompt);
      
      // Show success feedback
      console.log('Prompt saved successfully');
    } catch (error) {
      console.error('Failed to save prompt:', error);
      // You could add toast notification here
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setText(prompt.text);
    setHasChanges(false);
    onCancel?.();
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-medium text-gray-700">
          Edit Prompt: {prompt.name}
        </h4>
        <div className="flex items-center gap-2">
          {hasChanges && (
            <span className="text-xs text-orange-600 font-medium">
              Unsaved changes
            </span>
          )}
        </div>
      </div>
      
      <div className="relative">
        <textarea
          value={text}
          onChange={(e) => handleTextChange(e.target.value)}
          placeholder="Enter your custom analysis prompt..."
          className="w-full p-3 text-sm border rounded-md resize-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 pr-16"
          rows={4}
        />
        
        {/* Small save button positioned inside textarea */}
        <div className="absolute top-2 right-2 flex gap-1">
          {hasChanges && (
            <button
              onClick={handleCancel}
              className="inline-flex items-center justify-center p-1.5 rounded bg-gray-100 hover:bg-gray-200 text-gray-600 hover:text-gray-700 transition-all duration-200"
              title="Cancel changes"
              disabled={isSaving}
            >
              <svg className="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
          
          <button
            onClick={handleSave}
            disabled={!hasChanges || isSaving}
            className="inline-flex items-center justify-center p-1.5 rounded bg-blue-600 hover:bg-blue-700 text-white disabled:opacity-50 disabled:cursor-not-allowed hover:scale-105 transition-all duration-200 shadow-sm"
            title={isSaving ? 'Saving...' : hasChanges ? 'Save changes' : 'No changes to save'}
          >
            {isSaving ? (
              <svg className="animate-spin h-3 w-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            ) : (
              <svg className="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            )}
          </button>
        </div>
      </div>
      
      {prompt.description && (
        <p className="text-xs text-gray-500 italic">
          {prompt.description}
        </p>
      )}
    </div>
  );
}
