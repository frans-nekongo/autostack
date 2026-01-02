import { OperationStatus } from "../../services/operations/operations-service";


export interface Operation {
  id: string;
  type: 'PROJECT_CREATION'; 
  status: OperationStatus;
  message: string;
  progress: number;
  projectId?: string;
  error?: string;
  timestamp: Date;
  metadata?: {
    projectName?: string;
    [key: string]: any;
  };
}

export interface IOperationsState {
  operations: Operation[];
  activeOperationIds: string[];
  selectedOperationId: string | null;
  loading: boolean;
  error: string | null;
}

export const initialOperationsState: IOperationsState = {
  operations: [],
  activeOperationIds: [],
  selectedOperationId: null,
  loading: false,
  error: null
};
