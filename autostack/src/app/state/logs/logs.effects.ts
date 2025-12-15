import { inject, Injectable } from '@angular/core';
import { LogsService } from '../../services/logs/logs-service';
import { Actions, createEffect, ofType } from '@ngrx/effects';
import { LogActions } from './logs.actions';
import { catchError, map, of, switchMap } from 'rxjs';

@Injectable()
export class LogEffects {
  private actions$ = inject(Actions);
  private logService = inject(LogsService);

  loadLogs$ = createEffect(() =>
    this.actions$.pipe(
      ofType(LogActions.loadLogs),
      switchMap(() =>
        this.logService.fetchAllActivityLogs().pipe(
          map((result) => {
            if (result && Array.isArray(result)) {
              return LogActions.loadLogsSuccess({
                activityLogs: result,
              });
            } else if (result) {
              return LogActions.loadLogsSuccess({
                activityLogs: [result],
              });
            } else {
              return LogActions.loadLogsFailure({
                error: 'No logs found',
              });
            }
          }),
          catchError((error) =>
            of(
              LogActions.loadLogsFailure({
                error: error.message || 'Failed to load logs',
              })
            )
          )
        )
      )
    )
  );
}
