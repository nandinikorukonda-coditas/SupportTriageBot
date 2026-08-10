import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Ticket, TriageResult, FiledTicket } from '../models';

@Injectable({ providedIn: 'root' })
export class TriageService {
  private baseUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

  getCorpus(): Observable<Ticket[]> {
    return this.http.get<Ticket[]>(`${this.baseUrl}/tickets`);
  }

  getFiledTickets(): Observable<FiledTicket[]> {
    return this.http.get<FiledTicket[]>(`${this.baseUrl}/mcp/filed`);
  }

  ingestTickets(): Observable<any> {
    return this.http.post<any>(`${this.baseUrl}/ingest`, {});
  }

  submitTextTicket(text: string): Observable<TriageResult> {
    const formData = new FormData();
    formData.append('text', text);
    return this.http.post<TriageResult>(`${this.baseUrl}/submit`, formData);
  }

  submitVoiceTicket(file: File): Observable<TriageResult> {
    const formData = new FormData();
    formData.append('file', file, file.name);
    return this.http.post<TriageResult>(`${this.baseUrl}/submit-voice`, formData);
  }

  fileTicket(result: TriageResult, agentComment: string): Observable<any> {
    const formData = new FormData();
    const ticketId = result.ticketId || result.ticket_id || '';
    formData.append('ticket_id', ticketId);
    formData.append('category', result.category || 'General');
    formData.append('suggested_response', result.suggestedResponse || '');
    formData.append('original_text', result.originalText || '');
    formData.append('agent_comment', agentComment || 'Filed via support triage workflow.');
    formData.append('confirm', 'true');
    return this.http.post<any>(`${this.baseUrl}/mcp/file`, formData);
  }
}
