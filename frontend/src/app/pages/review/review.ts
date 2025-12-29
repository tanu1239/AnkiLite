import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { ApiService } from '../../services/api.service';

type Mode = 'due' | 'cram';

@Component({
  selector: 'app-review',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './review.html',
  styleUrl: './review.css',
})
export class ReviewComponent {
  msg = '';

  // deck/mode controls
  decks: any[] = [];
  selectedDeckIdStr: string = 'all';
  mode: Mode = 'due';

  // queue state
  queue: any[] = [];
  card: any | null = null;
  private initialQueueSize = 0;

  loading = false;
  grading = false;

  revealed = false;
  sessionId = `s-${Date.now()}`;

  // timing
  shownAt = 0;
  revealedAt = 0;

  constructor(private api: ApiService, private router: Router) {
    this.bootstrap();
  }

  // --- UI helpers used by review.html ---
  deckName(): string {
    if (this.selectedDeckIdStr === 'all') return 'All decks';
    const id = Number(this.selectedDeckIdStr);
    const d = this.decks.find((x) => Number(x.id) === id);
    return d?.name ?? `Deck ${this.selectedDeckIdStr}`;
  }

  progressPct(): number {
    if (this.initialQueueSize <= 0) return 0;
    const done = Math.max(0, this.initialQueueSize - (this.queue.length + (this.card ? 1 : 0)));
    const pct = Math.round((done / this.initialQueueSize) * 100);
    return Math.max(0, Math.min(100, pct));
  }

  switchToCram(): void {
    this.mode = 'cram';
    this.loadQueue();
  }

  reviewAllDecks(): void {
    this.selectedDeckIdStr = 'all';
    this.loadQueue();
  }

  goBack(): void {
    this.router.navigateByUrl('/decks');
  }

  onDeckChange(v: string): void {
    this.selectedDeckIdStr = v;
    this.loadQueue();
  }

  onModeChange(v: string): void {
    this.mode = (v === 'cram' ? 'cram' : 'due');
    this.loadQueue();
  }

  // --- lifecycle/bootstrap ---
  private bootstrap(): void {
    // Load decks for dropdown, then load queue
    this.api.listDecks().subscribe({
      next: (ds) => {
        this.decks = ds ?? [];
        this.loadQueue();
      },
      error: (e) => {
        this.msg = this.prettyErr(e);
        // still try queue in case API works partially
        this.loadQueue();
      }
    });
  }

  // --- core review flow ---
  loadQueue(): void {
    this.msg = '';
    this.loading = true;

    const deckId =
      this.selectedDeckIdStr === 'all' ? undefined : Number(this.selectedDeckIdStr);

    const obs =
      this.mode === 'cram'
        ? this.api.cram(50, deckId) // needs ApiService.cram()
        : this.api.due(50, deckId);

    obs.subscribe({
      next: (cards) => {
        this.queue = Array.isArray(cards) ? cards : [];
        this.initialQueueSize = this.queue.length;
        this.nextCard();
        this.loading = false;
      },
      error: (e) => {
        this.loading = false;
        this.msg = this.prettyErr(e);
      },
    });
  }

  nextCard(): void {
    this.revealed = false;
    this.revealedAt = 0;

    this.card = this.queue.shift() ?? null;
    this.shownAt = performance.now();
  }

  reveal(): void {
    if (!this.card) return;
    this.revealed = true;
    this.revealedAt = performance.now();
  }

  grade(g: number): void {
    if (!this.card || this.grading) return;

    this.grading = true;
    const now = performance.now();

    // think_ms: time until reveal (or until grade if user never revealed)
    const think_ms = Math.max(
      0,
      Math.round((this.revealed ? this.revealedAt : now) - this.shownAt)
    );

    // grade_ms: time from reveal to button click (0 if never revealed)
    const grade_ms = this.revealed
      ? Math.max(0, Math.round(now - this.revealedAt))
      : 0;

    this.api
      .review(this.card.id, g, think_ms, grade_ms, this.sessionId)
      .subscribe({
        next: () => {
          this.grading = false;
          this.nextCard();
        },
        error: (e) => {
          this.grading = false;
          this.msg = this.prettyErr(e);
        },
      });
  }

  // --- utils ---
  private prettyErr(e: any): string {
    const body = e?.error ?? e;
    if (typeof body === 'string') return body;
    try {
      return JSON.stringify(body);
    } catch {
      return String(body);
    }
  }
}
