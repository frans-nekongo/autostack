import { inject, Injectable } from '@angular/core';
import { Store } from '@ngrx/store';
import * as LogSelectors from './logs.selectors';
import { LogActions } from './logs.actions';

@Injectable({
  providedIn: 'root',
})
export class LogFacade {
  private readonly store = inject(Store);

  activityLogs$ = this.store.select(LogSelectors.selectActivityLogs);
  loading$ = this.store.select(LogSelectors.selectLoading);
  isLoading$ = this.store.select(LogSelectors.selectIsLoading);
  error$ = this.store.select(LogSelectors.selectError);
  hasError$ = this.store.select(LogSelectors.selectHasError);

  loadActivityLogs(): void {
    this.store.dispatch(LogActions.loadLogs());
  }
}
