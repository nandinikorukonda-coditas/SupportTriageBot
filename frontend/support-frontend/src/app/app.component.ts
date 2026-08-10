import { Component, OnInit } from '@angular/core';
import { FiledTicket, TriageResult } from './models';
import { TriageService } from './services/triage.service';

@Component({
  selector: 'app-root',
  standalone: false,
  template: `
    <div class="app-container">
      <!-- Navbar Header -->
      <header class="app-header">
        <div class="brand">
          <div class="brand-icon">
            <i class="fa-solid fa-robot"></i>
          </div>
          <div>
            <div class="brand-title">SupportTriage<span class="highlight">.ai</span></div>
            <div class="brand-subtitle">Autonomous RAG & MCP Multi-Agent Triage Engine</div>
          </div>
        </div>

        <div class="header-actions">
          <div class="status-pill">
            <span class="pulse-dot"></span>
            <span>FastAPI Server: <strong>:8000</strong></span>
          </div>

          <button class="btn-primary ingest-btn" (click)="triggerIngest()" [disabled]="ingesting">
            <i class="fa-solid" [ngClass]="ingesting ? 'fa-spinner fa-spin' : 'fa-database'"></i>
            <span>{{ ingesting ? 'Indexing RAG Vectors...' : 'Re-index Vector Store' }}</span>
          </button>
        </div>
      </header>

      <!-- Main Layout -->
      <main class="app-layout">
        <!-- Sidebar Column -->
        <aside class="sidebar-col">
          <app-new-ticket 
            [presetText]="selectedPreset"
            (ticketProcessed)="onTicketProcessed($event)">
          </app-new-ticket>

          <app-corpus (sampleSelected)="onSampleSelected($event)"></app-corpus>
        </aside>

        <!-- Main Column -->
        <section class="main-col">
          <app-ticket-details
            [ticket]="selectedResult"
            (fileTicket)="onFileTicket($event)">
          </app-ticket-details>

          <app-dashboard [filedTickets]="filedTickets"></app-dashboard>
        </section>
      </main>
    </div>
  `,
  styles: [`
    .app-container {
      max-width: 1440px;
      margin: 0 auto;
      padding: 24px 32px;
    }
    .app-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 28px;
      padding-bottom: 20px;
      border-bottom: 1px solid var(--glass-border);
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 14px;
    }
    .brand-icon {
      width: 46px;
      height: 46px;
      border-radius: 12px;
      background: var(--accent-gradient);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 22px;
      color: white;
      box-shadow: 0 0 20px rgba(108, 92, 231, 0.4);
    }
    .brand-title {
      font-family: 'Outfit', sans-serif;
      font-size: 24px;
      font-weight: 800;
      color: white;
      letter-spacing: -0.5px;
    }
    .brand-title .highlight {
      color: var(--accent-cyan);
    }
    .brand-subtitle {
      font-size: 13px;
      color: var(--text-body);
      margin-top: 2px;
    }
    .header-actions {
      display: flex;
      align-items: center;
      gap: 16px;
    }
    .status-pill {
      display: flex;
      align-items: center;
      gap: 8px;
      background: rgba(16, 185, 129, 0.1);
      border: 1px solid rgba(16, 185, 129, 0.25);
      color: #34d399;
      padding: 8px 14px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 500;
    }
    .pulse-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #10b981;
      box-shadow: 0 0 8px #10b981;
      animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.4; transform: scale(0.85); }
    }
    .app-layout {
      display: grid;
      grid-template-columns: 420px 1fr;
      gap: 28px;
    }
    @media (max-width: 1024px) {
      .app-layout {
        grid-template-columns: 1fr;
      }
    }
    .sidebar-col {
      display: flex;
      flex-direction: column;
      gap: 24px;
    }
    .main-col {
      display: flex;
      flex-direction: column;
      gap: 24px;
    }
  `]
})
export class AppComponent implements OnInit {
  selectedResult: TriageResult | null = null;
  filedTickets: FiledTicket[] = [];
  selectedPreset: string = '';
  ingesting = false;

  constructor(private triage: TriageService) {}

  ngOnInit() {
    this.refreshFiledTickets();
  }

  refreshFiledTickets() {
    this.triage.getFiledTickets().subscribe({
      next: tickets => this.filedTickets = tickets,
      error: err => console.error('Failed to load filed tickets', err)
    });
  }

  onTicketProcessed(result: TriageResult) {
    this.selectedResult = result;
  }

  onSampleSelected(text: string) {
    this.selectedPreset = text;
  }

  onFileTicket(comment: string) {
    if (!this.selectedResult) return;

    this.triage.fileTicket(this.selectedResult, comment).subscribe({
      next: res => {
        this.selectedResult = null; // Clear details view after filing
        this.refreshFiledTickets(); // Refresh filed tickets table
      },
      error: err => {
        console.error('Failed to file ticket via MCP endpoint', err);
        alert('Failed to file ticket via MCP endpoint: ' + (err.error?.detail || err.message));
      }
    });
  }

  triggerIngest() {
    this.ingesting = true;
    this.triage.ingestTickets().subscribe({
      next: res => {
        this.ingesting = false;
        alert(`Successfully indexed ${res.indexed} tickets into vector store!`);
      },
      error: err => {
        this.ingesting = false;
        console.error(err);
        alert('Indexing failed: ' + (err.error?.detail || err.message));
      }
    });
  }
}
