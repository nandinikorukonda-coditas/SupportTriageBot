import { Component, EventEmitter, Input, Output } from '@angular/core';
import { TriageResult } from '../../models';

@Component({
  selector: 'app-ticket-details',
  standalone: false,
  templateUrl: './ticket-details.component.html',
  styleUrls: ['./ticket-details.component.css']
})
export class TicketDetailsComponent {
  @Input() ticket: TriageResult | null = null;
  @Output() fileTicket = new EventEmitter<string>();
  
  agentComment = '';
  copied = false;

  submitFile(): void {
    if (!this.ticket) return;
    this.fileTicket.emit(this.agentComment.trim() || 'Filed via support triage workflow.');
    this.agentComment = '';
  }

  copyResponse(): void {
    if (!this.ticket?.suggestedResponse) return;
    navigator.clipboard.writeText(this.ticket.suggestedResponse);
    this.copied = true;
    setTimeout(() => this.copied = false, 2000);
  }
}
