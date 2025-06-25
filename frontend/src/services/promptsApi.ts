import { apiClient } from './apiClient';

export interface Prompt {
  id: string;
  name: string;
  text: string;
  description?: string;
}

export interface PromptsResponse {
  prompts: Record<string, Prompt>;
}

export interface PromptUpdate {
  text: string;
  name?: string;
  description?: string;
}

/**
 * Get all available prompts
 */
export const usePrompts = () => {
  return apiClient.get<PromptsResponse>('/api/prompts/');
};

/**
 * Get a specific prompt by ID
 */
export const usePrompt = (promptId: string) => {
  return apiClient.get<Prompt>(`/api/prompts/${promptId}`);
};

/**
 * Update a specific prompt
 */
export const useUpdatePrompt = () => {
  return {
    mutateAsync: async (data: { promptId: string; updates: PromptUpdate }) => {
      return updatePrompt(data.promptId, data.updates);
    }
  };
};

/**
 * Update a prompt by ID
 */
export const updatePrompt = async (promptId: string, updates: PromptUpdate): Promise<Prompt> => {
  const response = await fetch(`http://localhost:8000/api/prompts/${promptId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(updates),
  });

  if (!response.ok) {
    throw new Error(`Failed to update prompt: ${response.statusText}`);
  }

  return response.json();
};

/**
 * Get all prompts (direct fetch)
 */
export const fetchPrompts = async (): Promise<PromptsResponse> => {
  const response = await fetch('http://localhost:8000/api/prompts/');
  
  if (!response.ok) {
    throw new Error(`Failed to fetch prompts: ${response.statusText}`);
  }

  return response.json();
};
