import { Action, createReducer, on } from '@ngrx/store';
import { ILogState, initialLogState } from './logs.models';
import { LogActions } from './logs.actions';

export const LOG_FEATURE_KEY = 'log';

export interface LogState {
  readonly [LOG_FEATURE_KEY]: ILogState;
}

export interface LogPartialState {
  readonly [LOG_FEATURE_KEY]: ILogState;
}

const reducer = createReducer(
  initialLogState,

  on(LogActions.loadLogs, (state) => ({
    ...state,
    loading: true,
    error: null,
  })),

  on(LogActions.loadLogsSuccess, (state, { activityLogs }) => ({
    ...state,
    activityLogs,
    loading: false,
    error: null,
  })),

  on(LogActions.loadLogsFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error,
  }))
);

export function logsReducer(state: ILogState | undefined, action: Action) {
  return reducer(state, action);
}
