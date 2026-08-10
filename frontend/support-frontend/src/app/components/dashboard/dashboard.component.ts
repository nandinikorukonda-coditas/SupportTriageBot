import { Component, Input, OnInit } from '@angular/core';
import { Ticket, FiledTicket } from '../../models';
import { TriageService } from '../../services/triage.service';

@Component({
  selector: 'app-dashboard',
  standalone: false,
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  tickets: Ticket[] = [];
  @Input() filedTickets: FiledTicket[] = [];
  loading = false;
  activeTab: 'filed' | 'all' = 'filed';

  constructor(private triage: TriageService) { }

  ngOnInit(): void {
    this.loading = true;
    this.triage.getCorpus().subscribe({
      next: tickets => {
        this.tickets = tickets;
        this.loading = false;
      },
      error: err => {
        console.error('Failed to load tickets', err);
        this.loading = false;
      }
    });
  }
}
