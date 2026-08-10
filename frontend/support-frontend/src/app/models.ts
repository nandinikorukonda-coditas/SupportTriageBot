export interface Ticket {
  id: string;
  category: string;
  text: string;
  status?: string;
  date?: string;
}

export interface AgentStage {
  id: string;
  name: string;
  status: 'complete' | 'pending' | 'failed';
  detail: string;
}

export interface ToolCall {
  toolId: string;
  toolName: string;
}

export interface TriageResult {
  ticketId?: string;
  ticket_id?: string;
  channel: 'text' | 'voice';
  originalText: string;
  category: string;
  suggestedResponse: string;
  confidence: number;
  similarTicketIds: string[];
  timingMs: number;
  agentTrace: AgentStage[];
  toolCalls: ToolCall[];
}

export interface FiledTicket {
  fileId: string;
  ticketId: string;
  category: string;
  confidence: number;
  suggestedResponse: string;
  similarTicketIds: string[];
  channel: 'text' | 'voice';
  originalText: string;
  agentComment: string;
  filedAt: string;
}
