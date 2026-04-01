export interface SourceRef {
  title: string;
  chunk_id: string;
  relevance_score: number;
}

export interface ResearchResponse {
  request_id: string;
  summary: string;
  key_points: string[];
  comparison: string | null;
  sources: SourceRef[];
  confidence: number;
  low_confidence: boolean;
  latency_ms: number;
}

export interface QueryRequest {
  query: string;
  files?: string[];
}
