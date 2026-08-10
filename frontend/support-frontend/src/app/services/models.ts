export interface Ticket {
  id: string;
  category: string;
  text: string;
  status?: string;
}

export interface TriageResult {
  category: string;
  suggested_response: string;
  confidence: number;
  similar_ticket_ids: string[];
  timing_ms?: number;
  agent_id?: string;
}
