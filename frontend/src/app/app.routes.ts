import { Routes } from '@angular/router';
import { LoginComponent } from './pages/login/login';
import { DecksComponent } from './pages/decks/decks';
import { ReviewComponent } from './pages/review/review';

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  { path: 'decks', component: DecksComponent },
  { path: 'review', component: ReviewComponent },
  { path: '', pathMatch: 'full', redirectTo: 'login' },
];
