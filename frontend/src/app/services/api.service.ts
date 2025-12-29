import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class ApiService {
  base = environment.apiBase;
  constructor(private http: HttpClient) {}

  register(email: string, password: string) {
    return this.http.post(`${this.base}/auth/register`, { email, password });
  }

  login(username: string, password: string) {
    return this.http.post<{ access: string; refresh: string }>(
      `${this.base}/auth/login`,
      { username, password }
    );
  }

  me() {
    return this.http.get(`${this.base}/auth/me`);
  }

  listDecks() {
    return this.http.get<any[]>(`${this.base}/decks/`);
  }

  createDeck(payload: any) {
    return this.http.post(`${this.base}/decks/`, payload);
  }

  updateDeck(deckId: number, patch: any) {
    return this.http.patch(`${this.base}/decks/${deckId}/`, patch);
  }

  forceDue(deckId: number, resetProgress: boolean) {
    const q = new URLSearchParams();
    q.set('reset_progress', resetProgress ? 'true' : 'false');
    return this.http.post(`${this.base}/decks/${deckId}/force_due/?${q.toString()}`, {});
  }

  addCard(deckId: number, front: string, back: string, tags: string[]) {
    return this.http.post(`${this.base}/decks/${deckId}/cards/`, { front, back, tags });
  }

  due(limit = 50, deckId?: number) {
    const q = new URLSearchParams();
    q.set('limit', String(limit));
    if (deckId) q.set('deck_id', String(deckId));
    return this.http.get<any[]>(`${this.base}/review/due?${q.toString()}`);
  }

  cram(limit = 50, deckId?: number) {
    const q = new URLSearchParams();
    q.set('limit', String(limit));
    if (deckId) q.set('deck_id', String(deckId));
    return this.http.get<any[]>(`${this.base}/review/cram?${q.toString()}`);
  }

  review(cardId: number, grade: number, think_ms: number, grade_ms: number, session_id: string) {
    return this.http.post(`${this.base}/review/${cardId}`, {
      grade,
      think_ms,
      grade_ms,
      session_id,
    });
  }
}

