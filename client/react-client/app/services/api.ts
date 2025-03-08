import { ProviderType } from '../types/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface PromptRequest {
  prompt: string;
  model?: string;
  provider?: ProviderType;
  temperature?: number;
}

interface PromptResponse {
  task_id: string;
}

interface TaskResponse {
  task_id: string;
  status: string;
  result?: any;
}

class ApiService {
  private static baseUrl = API_BASE_URL;

  static async submitPrompt(request: PromptRequest): Promise<PromptResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/prompt/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error submitting prompt:', error);
      throw error;
    }
  }

  static async getTaskStatus(taskId: string): Promise<TaskResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/prompt/status/${taskId}`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting task status:', error);
      throw error;
    }
  }

  static createWebSocket(taskId: string): WebSocket {
    const wsUrl = `${this.baseUrl.replace('http', 'ws')}/prompt/ws/${taskId}`;
    return new WebSocket(wsUrl);
  }
}

export default ApiService; 