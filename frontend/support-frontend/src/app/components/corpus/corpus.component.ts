import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import { Ticket } from '../../models';
import { TriageService } from '../../services/triage.service';

@Component({
  selector: 'app-corpus',
  standalone: false,
  templateUrl: './corpus.component.html',
  styleUrls: ['./corpus.component.css']
})
export class CorpusComponent implements OnInit {
  @Output() sampleSelected = new EventEmitter<string>();

  tickets: Ticket[] = [];
  filteredTickets: Ticket[] = [];
  searchQuery: string = '';
  selectedCategory: string = 'All';

  categories = ['All', 'Billing', 'Delivery', 'Technical', 'Account', 'Product Quality'];

  constructor(private triage: TriageService) {}

  ngOnInit(): void {
    this.triage.getCorpus().subscribe({
      next: tickets => {
        this.tickets = tickets;
        this.applyFilter();
      },
      error: err => console.error('Failed to fetch corpus tickets', err)
    });
  }

  filterByCategory(cat: string) {
    this.selectedCategory = cat;
    this.applyFilter();
  }

  applyFilter() {
    this.filteredTickets = this.tickets.filter(t => {
      const matchCat = this.selectedCategory === 'All' || t.category.toLowerCase() === this.selectedCategory.toLowerCase();
      const matchQuery = !this.searchQuery || t.text.toLowerCase().includes(this.searchQuery.toLowerCase()) || t.id.toLowerCase().includes(this.searchQuery.toLowerCase());
      return matchCat && matchQuery;
    });
  }

  selectTicket(text: string) {
    this.sampleSelected.emit(text);
  }
}
