import { createFeatureSelector, createSelector } from '@ngrx/store';
import { PROJECT_FEATURE_KEY } from './project.reducer';
import { IProjectState } from './project.models';

export const selectProjectStore =
  createFeatureSelector<IProjectState>(PROJECT_FEATURE_KEY);

// Current Project Selectors
export const selectCurrentProjectId = createSelector(
  selectProjectStore,
  (state: IProjectState) => state.currentProjectId
);

export const selectCurrentProject = createSelector(
  selectProjectStore,
  (state: IProjectState) => state.currentProject
);

export const selectCurrentArchitecture = createSelector(
  selectProjectStore,
  (state: IProjectState) => state.currentArchitecture
);

// Derived selectors for current project
export const selectCurrentProjectName = createSelector(
  selectCurrentProject,
  (project) => project?.name
);

export const selectCurrentProjectDescription = createSelector(
  selectCurrentProject,
  (project) => project?.description
);

export const selectCurrentProjectMetadata = createSelector(
  selectCurrentProject,
  (project) => project?.metadata
);

export const selectCurrentProjectGitInfo = createSelector(
  selectCurrentProject,
  (project) => project?.gitInfo
);

// Architecture details selectors
export const selectArchitectureComponents = createSelector(
  selectCurrentArchitecture,
  (architecture) => architecture?.components
);

export const selectArchitectureTechnologies = createSelector(
  selectCurrentArchitecture,
  (architecture) => architecture?.technologies
);

export const selectArchitectureConnections = createSelector(
  selectCurrentArchitecture,
  (architecture) => architecture?.connections
);

export const selectArchitectureMetadata = createSelector(
  selectCurrentArchitecture,
  (architecture) => architecture?.metadata
);

// Projects List Selectors
export const selectProjects = createSelector(
  selectProjectStore,
  (state: IProjectState) => state.projects
);

export const selectProjectsCount = createSelector(
  selectProjects,
  (projects) => projects.length
);

// Find specific project by ID
export const selectProjectById = (projectId: string) =>
  createSelector(selectProjects, (projects) =>
    projects.find((p) => p.id === projectId)
  );

// Loading and Error Selectors
export const selectLoading = createSelector(
  selectProjectStore,
  (state: IProjectState) => state.loading
);

export const selectLoadingArchitecture = createSelector(
  selectProjectStore,
  (state: IProjectState) => state.loadingArchitecture
);

export const selectCreating = createSelector(
  selectProjectStore,
  (state: IProjectState) => state.creating
);

export const selectError = createSelector(
  selectProjectStore,
  (state: IProjectState) => state.error
);

export const selectHasError = createSelector(selectError, (error) => !!error);

export const selectHasCurrentProject = createSelector(
  selectCurrentProject,
  (project) => !!project
);

export const selectHasCurrentArchitecture = createSelector(
  selectCurrentArchitecture,
  (architecture) => !!architecture
);

// Combined loading state
export const selectIsLoading = createSelector(
  selectLoading,
  selectLoadingArchitecture,
  selectCreating,
  (loading, loadingArch, creating) => loading || loadingArch || creating
);
