import { createFeatureSelector, createSelector } from "@ngrx/store";
import { PROJECT_FEATURE_KEY } from "./project.reducer";
import { IProjectState } from "./project.models";

export const selectProjectStore = createFeatureSelector<IProjectState>(PROJECT_FEATURE_KEY);

/**
 * Set Project
 */
export const selectProject = createSelector(
    selectProjectStore,
    (state: IProjectState) => state.project
)

export const selectProjectLoading = createSelector(
    selectProjectStore,
    (state: IProjectState) => state.loading
)

export const selectProjectError = createSelector(
    selectProjectStore,
    (state: IProjectState) => state.error
)

