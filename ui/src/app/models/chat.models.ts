export interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  citations?: Citation[];
  pending?: boolean;
  ts?: string;
}

export interface Citation {
  title?: string;
  url?: string;
  snippet?: string;
  index?: string;
}

export interface ChatRequest {
  prompt: string;
  thread_id?: string | null;
  history?: { role: string; content: string }[];
}

export interface ChatResponse {
  answer: string;
  thread_id?: string | null;
  run_id?: string | null;
  citations: Citation[];
  latency_ms?: number | null;
  timestamp: string;
}

export interface SamplePrompt {
  id: number;
  title: string;
  prompt: string;
  category: string;
  icon?: string;
}
