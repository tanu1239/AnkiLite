import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { Observable, tap } from 'rxjs';

type Tokens = { access: string; refresh: string };

@Injectable({ providedIn: 'root' })
export class AuthService {
  private base = environment.apiBase;

  constructor(private http: HttpClient) {}

  register(email: string, password: string) {
    return this.http.post(`${this.base}/auth/register`, { email, password });
  }

  login(username: string, password: string): Observable<Tokens> {
    return this.http
      .post<Tokens>(`${this.base}/auth/login`, { username, password })
      .pipe(
        tap((tokens) => {
          localStorage.setItem('access', tokens.access);
          localStorage.setItem('refresh', tokens.refresh);
        })
      );
  }

  refresh(): Observable<{ access: string }> {
    const refresh = localStorage.getItem('refresh');
    return this.http.post<{ access: string }>(`${this.base}/auth/refresh`, { refresh });
  }

  logout(): void {
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
  }

  getAccess(): string | null {
    return localStorage.getItem('access');
  }

  getRefresh(): string | null {
    return localStorage.getItem('refresh');
  }
}
