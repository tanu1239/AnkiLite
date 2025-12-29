import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './login.html',
  styleUrl: './login.css',
})
export class LoginComponent {
  email = 'test@example.com';
  password = 'pass1234';
  msg = '';
  loading = false;

  constructor(private auth: AuthService, private router: Router) {}

  onLogin(): void {
    this.msg = '';
    this.loading = true;

    this.auth.login(this.email, this.password).subscribe({
      next: () => {
        // AuthService already stored access+refresh in localStorage
        this.loading = false;
        this.router.navigateByUrl('/decks');
      },
      error: (e) => {
        this.loading = false;
        this.msg = JSON.stringify(e?.error ?? e);
      },
    });
  }

  onRegister(): void {
    this.msg = '';
    this.loading = true;

    this.auth.register(this.email, this.password).subscribe({
      next: () => {
        this.loading = false;
        this.msg = 'Registered! Now click Login.';
      },
      error: (e) => {
        this.loading = false;
        this.msg = JSON.stringify(e?.error ?? e);
      },
    });
  }
}
