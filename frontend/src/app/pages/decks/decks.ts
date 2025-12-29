import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { ApiService } from '../../services/api.service';
import { AuthService } from '../../services/auth.service';

type Unit = 'min' | 'hour' | 'day' | 'week';

@Component({
  selector: 'app-decks',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './decks.html',
  styleUrl: './decks.css',
})
export class DecksComponent {
  msg = '';
  decks: any[] = [];
  creatingDeck = false;
  adding = false;

  units: Unit[] = ['min', 'hour', 'day', 'week'];

  // ✅ inject AuthService too
  constructor(
    private api: ApiService,
    private router: Router,
    private auth: AuthService
  ) {
    this.refresh();
  }

  goReview(): void {
    this.router.navigateByUrl('/review');
  }

  // ✅ logout handler
  logout(): void {
    this.auth.logout();               // clears tokens
    this.router.navigateByUrl('/login'); // back to login
  }

  refresh(): void {
    this.msg = '';
    this.api.listDecks().subscribe({
      next: (d) => (this.decks = d),
      error: (e) => (this.msg = JSON.stringify(e?.error ?? e)),
    });
  }

  unitLabel(u: Unit): string {
    return u === 'min' ? 'minutes' : u === 'hour' ? 'hours' : u === 'day' ? 'days' : 'weeks';
  }

  toMinutes(valueStr: string, unit: Unit): number {
    const v = Number(valueStr || 0);
    const mult = unit === 'min' ? 1 : unit === 'hour' ? 60 : unit === 'day' ? 1440 : 10080;
    const mins = Math.round(v * mult);
    return Math.max(1, mins);
  }

  fromMinutes(minutes: number, unit: Unit): number {
    const div = unit === 'min' ? 1 : unit === 'hour' ? 60 : unit === 'day' ? 1440 : 10080;
    return Math.max(1, Math.round(minutes / div));
  }

  createDeck(
    name: string,
    description: string,
    mode: string,
    againVal: string, againUnit: Unit,
    hardVal: string, hardUnit: Unit,
    goodVal: string, goodUnit: Unit,
    easyVal: string, easyUnit: Unit
  ): void {
    if (this.creatingDeck) return;
    this.creatingDeck = true;
    this.msg = '';

    const payload = {
      name,
      description,
      schedule_mode: mode === 'fixed' ? 'fixed' : 'hybrid',

      again_minutes: this.toMinutes(againVal, againUnit),
      again_unit: againUnit,

      hard_minutes: this.toMinutes(hardVal, hardUnit),
      hard_unit: hardUnit,

      good_minutes: this.toMinutes(goodVal, goodUnit),
      good_unit: goodUnit,

      easy_minutes: this.toMinutes(easyVal, easyUnit),
      easy_unit: easyUnit,
    };

    this.api.createDeck(payload).subscribe({
      next: () => {
        this.creatingDeck = false;
        this.refresh();
      },
      error: (e) => {
        this.creatingDeck = false;
        this.msg = JSON.stringify(e?.error ?? e);
      },
    });
  }

  saveDeckSettings(
    d: any,
    mode: string,
    againVal: string, againUnit: Unit,
    hardVal: string, hardUnit: Unit,
    goodVal: string, goodUnit: Unit,
    easyVal: string, easyUnit: Unit
  ): void {
    this.msg = '';

    const patch = {
      schedule_mode: mode === 'fixed' ? 'fixed' : 'hybrid',

      again_minutes: this.toMinutes(againVal, againUnit),
      again_unit: againUnit,

      hard_minutes: this.toMinutes(hardVal, hardUnit),
      hard_unit: hardUnit,

      good_minutes: this.toMinutes(goodVal, goodUnit),
      good_unit: goodUnit,

      easy_minutes: this.toMinutes(easyVal, easyUnit),
      easy_unit: easyUnit,
    };

    this.api.updateDeck(d.id, patch).subscribe({
      next: () => this.refresh(),
      error: (e) => (this.msg = JSON.stringify(e?.error ?? e)),
    });
  }

  clearInputs(...els: Array<HTMLInputElement>): void {
    for (const el of els) el.value = '';
  }

  addCard(
    deckId: number,
    front: string,
    back: string,
    tagsCsv: string,
    frontEl: HTMLInputElement,
    backEl: HTMLInputElement,
    tagsEl: HTMLInputElement
  ): void {
    if (this.adding) return;
    this.adding = true;
    this.msg = '';

    const tags = tagsCsv.split(',').map(t => t.trim()).filter(Boolean);

    this.api.addCard(deckId, front, back, tags).subscribe({
      next: () => {
        this.adding = false;
        this.clearInputs(frontEl, backEl, tagsEl);
      },
      error: (e) => {
        this.adding = false;
        this.msg = JSON.stringify(e?.error ?? e);
      },
    });
  }

  forceDue(deckId: number, resetProgress: boolean) {
    this.msg = '';
    this.api.forceDue(deckId, resetProgress).subscribe({
      next: (r: any) => (this.msg = `Forced due: ${r.forced} cards (reset_progress=${r.reset_progress})`),
      error: (e) => (this.msg = JSON.stringify(e?.error ?? e)),
    });
  }
}
