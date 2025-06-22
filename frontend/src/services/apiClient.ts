// API client configuration and base utilities

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public statusText: string,
    public data?: any
  ) {
    super(message);
    this.name = 'APIError';
  }
}

export interface APIResponse<T = any> {
  data: T;
  success: boolean;
  message?: string;
  error?: string;
}

class APIClient {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new APIError(
          errorData.message || `HTTP ${response.status}: ${response.statusText}`,
          response.status,
          response.statusText,
          errorData
        );
      }

      // Handle different response types
      const contentType = response.headers.get('content-type');
      if (contentType?.includes('application/json')) {
        return response.json();
      } else if (contentType?.includes('text/')) {
        return response.text() as unknown as T;
      } else {
        return response.blob() as unknown as T;
      }
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }
      
      // Network or other errors
      throw new APIError(
        error instanceof Error ? error.message : 'Network error',
        0,
        'Network Error'
      );
    }
  }

  // HTTP method helpers
  async get<T>(endpoint: string, params?: Record<string, any>): Promise<T> {
    const searchParams = params 
      ? '?' + new URLSearchParams(params).toString()
      : '';
    
    return this.request<T>(`${endpoint}${searchParams}`, {
      method: 'GET',
    });
  }

  async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async put<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'DELETE',
    });
  }

  async patch<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    });
  }

  // File upload helper
  async upload<T>(endpoint: string, file: File | FormData, onProgress?: (progress: number) => void): Promise<T> {
    const formData = file instanceof FormData ? file : new FormData();
    if (file instanceof File) {
      formData.append('file', file);
    }

    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      
      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable && onProgress) {
          const progress = (event.loaded / event.total) * 100;
          onProgress(progress);
        }
      });

      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          try {
            const response = JSON.parse(xhr.responseText);
            resolve(response);
          } catch {
            resolve(xhr.responseText as unknown as T);
          }
        } else {
          reject(new APIError(
            `Upload failed: ${xhr.statusText}`,
            xhr.status,
            xhr.statusText
          ));
        }
      });

      xhr.addEventListener('error', () => {
        reject(new APIError('Upload failed', 0, 'Network Error'));
      });

      xhr.open('POST', `${this.baseURL}${endpoint}`);
      xhr.send(formData);
    });
  }
}

// Create a singleton instance
export const apiClient = new APIClient();

// Export the class for testing or custom instances
export { APIClient };
