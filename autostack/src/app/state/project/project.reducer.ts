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
  on(
    ProjectActions.setProject,
    (state, { id, name, author, description, version, status, metadata, git_info }) => ({
      ...state,
      project: {
        id,
        name,
        author,
        description,
        version,
        status,
        metadata,
        git_info
      },
      loading: false,
      error: null,
    })
  )
);

export function projectReducer(
    state: IProjectState | undefined,
    action: Action
) {
    return reducer(state, action)
}