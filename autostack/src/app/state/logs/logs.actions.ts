import { createActionGroup, emptyProps, props } from '@ngrx/store';
import { ActivityLogResponse } from '../../services/logs/logs-service';

export const LogActions = createActionGroup({
  source: 'Log',
  events: {
    'Load Logs': emptyProps(),
    'Load Logs Success': props<{ activityLogs: ActivityLogResponse[] }>(),
    'Load Logs Failure': props<{ error: string }>(),
  },
});
