import { inject } from '@angular/core';
import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { catchError, switchMap, throwError } from 'rxjs';
import { AuthService } from './auth.service';

let isRefreshing = false;

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(AuthService);

  const access = auth.getAccess();
  const authReq = access
    ? req.clone({ setHeaders: { Authorization: `Bearer ${access}` } })
    : req;

  return next(authReq).pipe(
    catchError((err: HttpErrorResponse) => {
      // Only attempt refresh on 401
      if (err.status !== 401) return throwError(() => err);

      // Prevent refresh loop / multiple simultaneous refreshes
      if (isRefreshing) return throwError(() => err);
      isRefreshing = true;

      const refresh = auth.getRefresh();
      if (!refresh) {
        isRefreshing = false;
        auth.logout();
        return throwError(() => err);
      }

      return auth.refresh().pipe(
        switchMap(({ access: newAccess }) => {
          localStorage.setItem('access', newAccess);
          isRefreshing = false;

          const retryReq = req.clone({
            setHeaders: { Authorization: `Bearer ${newAccess}` },
          });
          return next(retryReq);
        }),
        catchError((e) => {
          isRefreshing = false;
          auth.logout();
          return throwError(() => e);
        })
      );
    })
  );
};
