import {
  ProjectResult,
  ProjectArchitecture,
} from '../../services/project/project-service';

export interface IProjectState {
  // Current selected project
  currentProjectId: string | null;
  currentProject: ProjectResult | null;
  currentArchitecture: ProjectArchitecture | null;

  // All projects list
  projects: ProjectResult[];

  // Loading states
  loading: boolean;
  loadingArchitecture: boolean;
  creating: boolean;

  // Error state
  error: string | null;
}

export const initialProjectState: IProjectState = {
  currentProjectId: null,
  currentProject: null,
  currentArchitecture: null,
  projects: [],
  loading: false,
  loadingArchitecture: false,
  creating: false,
  error: null,
};
