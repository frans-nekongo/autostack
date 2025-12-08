import { ProjectResult } from "../../services/project/project-service";

export interface IProjectState {
  project: ProjectResult;
  loading: boolean;
  error: string | null;
}

export const initialProjectState: IProjectState = {
  project: {
    name: '',
    id: "",
    version: ""
  },
  loading: false,
  error: null,
};
