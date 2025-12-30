import {
  ProjectResult,
  ProjectArchitecture,
  ProductionEnvironment,
} from '../../services/project/project-service';

export interface IProjectState {
  currentProjectId: string | null;
  currentProject: ProjectResult | null;
  currentArchitecture: ProjectArchitecture | null;
  currentProductionEnvironment: ProductionEnvironment | null; 
  projects: ProjectResult[];
  loading: boolean;
  loadingArchitecture: boolean;
  creating: boolean;
  loadingProductionEnvironment: boolean; 
  error: string | null;
}

export const initialProjectState: IProjectState = {
  currentProjectId: null,
  currentProject: null,
  currentArchitecture: null,
  currentProductionEnvironment: null,
  projects: [],
  loading: false,
  loadingArchitecture: false,
  creating: false,
  loadingProductionEnvironment: false,
  error: null,
};
