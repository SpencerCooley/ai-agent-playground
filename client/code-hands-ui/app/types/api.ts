export type ProviderType = 'openai' | 'anthropic' | 'google';

export interface ApiError {
  message: string;
  status?: number;
} 