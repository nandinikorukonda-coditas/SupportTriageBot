import { Component, EventEmitter, Input, Output, OnChanges, SimpleChanges } from '@angular/core';
import { TriageService } from '../../services/triage.service';
import { TriageResult } from '../../models';

@Component({
  selector: 'app-new-ticket',
  standalone: false,
  templateUrl: './new-ticket.component.html',
  styleUrls: ['./new-ticket.component.css']
})
export class NewTicketComponent implements OnChanges {
  @Input() presetText: string = '';
  @Output() ticketProcessed = new EventEmitter<TriageResult>();

  text = '';
  activeTab: 'text' | 'voice' = 'text';
  processing = false;
  selectedAudioName: string = '';

  quickPresets = [
    { label: '💳 Double Charge', text: 'I noticed I was charged twice for order #OD9849582. The payment failed first, but debited twice.' },
    { label: '📱 App Crash', text: 'Every time I try to update my profile photo or bio in settings, the app freezes and crashes on iOS.' },
    { label: '📦 Damaged Item', text: 'I received my Roadster check shirt (Order #FK-83948), but the sleeve is torn and stained. Need replacement.' },
    { label: '🚚 Stuck Order', text: 'My package tracking TRK-8495829 has been stuck at Bengaluru sorting hub for 4 days.' },
    { label: '🎟️ Promo Failed', text: 'Trying to apply promo code FIRST50 at checkout, but app says invalid promo code.' }
  ];

  sampleAudioFiles = [
    { name: 'billing_refund_issue.mp3', label: '💳 Billing Refund Audio' },
    { name: 'app_crash_bug.mp3', label: '📱 App Crash Audio' },
    { name: 'delivery_delay_rider.mp3', label: '🚚 Rider Delay Audio' }
  ];

  constructor(private triage: TriageService) {}

  ngOnChanges(changes: SimpleChanges) {
    if (changes['presetText'] && changes['presetText'].currentValue) {
      this.text = changes['presetText'].currentValue;
      this.activeTab = 'text';
    }
  }

  usePreset(presetText: string) {
    this.text = presetText;
  }

  submitText() {
    if (!this.text.trim() || this.processing) return;
    this.processing = true;
    this.triage.submitTextTicket(this.text).subscribe({
      next: (result) => {
        this.processing = false;
        this.text = ''; // Clear input
        this.ticketProcessed.emit(result);
      },
      error: (err) => {
        this.processing = false;
        console.error(err);
        alert('Error submitting text ticket: ' + (err.error?.detail || err.message));
      }
    });
  }

  uploadVoiceFile(event: any) {
    const file = event.target.files[0];
    if (!file) return;
    this.selectedAudioName = file.name;
    this.processVoiceFile(file);
    event.target.value = '';
  }

  triggerSampleAudio(filename: string) {
    this.selectedAudioName = filename;
    this.processing = true;

    fetch(`assets/sample-audio/${filename}`)
      .then(res => res.blob())
      .then(blob => {
        const file = new File([blob], filename, { type: 'audio/mp3' });
        this.processVoiceFile(file);
      })
      .catch(err => {
        console.warn('Assets fetch fallback:', err);
        const fallbackFile = new File(['audio content for ' + filename], filename, { type: 'audio/mp3' });
        this.processVoiceFile(fallbackFile);
      });
  }

  private processVoiceFile(file: File) {
    this.processing = true;
    this.triage.submitVoiceTicket(file).subscribe({
      next: (result) => {
        this.processing = false;
        this.ticketProcessed.emit(result);
      },
      error: (err) => {
        this.processing = false;
        console.error(err);
        alert('Error processing voice file: ' + (err.error?.detail || err.message));
      }
    });
  }
}
