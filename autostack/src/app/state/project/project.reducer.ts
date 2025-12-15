import { createReducer, on, Action } from '@ngrx/store';
import { ProjectActions } from './project.actions';
import { IProjectState, initialProjectState } from './project.models';

export const PROJECT_FEATURE_KEY = 'project';

export interface ProjectState {
  readonly [PROJECT_FEATURE_KEY]: IProjectState;
}

export interface ProjectPartialState {
  readonly [PROJECT_FEATURE_KEY]: IProjectState;
}

const reducer = createReducer(
  initialProjectState,

  // Load All Projects
  on(ProjectActions.loadProjects, (state) => ({
    ...state,
    loading: true,
    error: null,
  })),
  on(ProjectActions.loadProjectsSuccess, (state, { projects }) => ({
    ...state,
    projects,
    loading: false,
    error: null,
  })),
  on(ProjectActions.loadProjectsFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error,
  })),

  // Load Single Project
  on(ProjectActions.loadProject, (state, { projectId }) => ({
    ...state,
    currentProjectId: projectId,
    loading: true,
    error: null,
  })),
  on(ProjectActions.loadProjectSuccess, (state, { project }) => ({
    ...state,
    currentProject: project,
    currentProjectId: project.id,
    loading: false,
    error: null,
  })),
  on(ProjectActions.loadProjectFailure, (state, { error }) => ({
    ...state,
    currentProject: null,
    loading: false,
    error,
  })),

  // Load Project Architecture
  on(ProjectActions.loadProjectArchitecture, (state) => ({
    ...state,
    loadingArchitecture: true,
    error: null,
  })),
  on(
    ProjectActions.loadProjectArchitectureSuccess,
    (state, { architecture }) => ({
      ...state,
      currentArchitecture: architecture,
      loadingArchitecture: false,
      error: null,
    })
  ),
  on(ProjectActions.loadProjectArchitectureFailure, (state, { error }) => ({
    ...state,
    currentArchitecture: null,
    loadingArchitecture: false,
    error,
  })),

  // Create Project
  on(ProjectActions.createProject, (state) => ({
    ...state,
    creating: true,
    error: null,
  })),
  on(ProjectActions.createProjectSuccess, (state, { projectId }) => ({
    ...state,
    currentProjectId: projectId,
    creating: false,
    error: null,
  })),
  on(ProjectActions.createProjectFailure, (state, { error }) => ({
    ...state,
    creating: false,
    error,
  })),

  // Set Current Project
  on(ProjectActions.setCurrentProject, (state, { projectId }) => ({
    ...state,
    currentProjectId: projectId,
  })),

  // Set Project Details (legacy)
  on(ProjectActions.setProjectDetails, (state, { project }) => ({
    ...state,
    currentProject: project,
    currentProjectId: project.id,
    loading: false,
    error: null,
  })),

  on(ProjectActions.updateProject, (state) => ({
    ...state,
    loading: true,
    error: null,
  })),
  on(ProjectActions.updateProjectSuccess, (state, { projectId, updates }) => {
    // Update the current project if it matches the updated project
    const updatedCurrentProject =
      state.currentProjectId === projectId
        ? {
            ...state.currentProject!,
            ...updates,
            // Handle metadata updates for tags
            metadata: updates.tags
              ? { ...state.currentProject?.metadata, tags: updates.tags }
              : state.currentProject?.metadata,
          }
        : state.currentProject;

    // Update the project in the projects array
    const updatedProjects = state.projects.map((project) =>
      project.id === projectId
        ? {
            ...project,
            ...updates,
            metadata: updates.tags
              ? { ...project.metadata, tags: updates.tags }
              : project.metadata,
          }
        : project
    );

    return {
      ...state,
      currentProject: updatedCurrentProject,
      projects: updatedProjects,
      loading: false,
      error: null,
    };
  }),
  on(ProjectActions.updateProjectFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error,
  })),

  on(ProjectActions.initialiseRepository, (state) => ({
    ...state,
    loading: true,
    error: null,
  })),
  on(
    ProjectActions.initialiseRepositorySuccess,
    (state, { projectId, gitInfo }) => ({
      ...state,
      currentProject:
        state.currentProject?.id === projectId
          ? { ...state.currentProject, gitInfo }
          : state.currentProject,
      projects: state.projects.map((project) =>
        project.id === projectId ? { ...project, gitInfo } : project
      ),
    })
  ),
  on(ProjectActions.initialiseRepositoryFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error,
  })),

  // Reset State
  on(ProjectActions.resetProjectState, () => initialProjectState)
);

export function projectReducer(
  state: IProjectState | undefined,
  action: Action
) {
  return reducer(state, action);
}
