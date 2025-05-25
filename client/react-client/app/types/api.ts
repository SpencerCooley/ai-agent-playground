export type ProviderType = 'openai' | 'anthropic' | 'google';

export interface ApiError {
  message: string;
  status?: number;
}

export interface PromptResponse {
  task_id: string;
}

export interface TaskResponse {
  task_id: string;
  status: string;
  result?: any;
}

export interface PlanRequest {
  prompt: string;
  plan_type: string;
  schema?: any;
}

export interface PlanResponse {
  plan: string;
  task_id?: string;
} 