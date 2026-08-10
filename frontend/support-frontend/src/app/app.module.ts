import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';

import { AppComponent } from './app.component';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { NewTicketComponent } from './components/new-ticket/new-ticket.component';
import { TicketDetailsComponent } from './components/ticket-details/ticket-details.component';
import { CorpusComponent } from './components/corpus/corpus.component';

@NgModule({
  declarations: [
    AppComponent,
    DashboardComponent, 
    NewTicketComponent,
    TicketDetailsComponent,
    CorpusComponent
  ],
  imports: [BrowserModule, FormsModule, HttpClientModule],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
