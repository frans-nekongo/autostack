import { createFeatureSelector, createSelector } from '@ngrx/store';
import { ILogState } from './logs.models';
import { LOG_FEATURE_KEY } from './logs.reducer';

export const selectLogStore = createFeatureSelector<ILogState>(LOG_FEATURE_KEY);

export const selectActivityLogs = createSelector(
  selectLogStore,
  (state: ILogState) => state.activityLogs
);

export const selectLoading = createSelector(
  selectLogStore,
  (state: ILogState) => state.loading
);

export const selectError = createSelector(
  selectLogStore,
  (state: ILogState) => state.error
);

export const selectHasError = createSelector(selectError, (error) => !!error);

export const selectIsLoading = createSelector(
  selectLoading,
  (loading) => loading
);
