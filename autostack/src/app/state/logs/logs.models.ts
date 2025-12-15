import { ActivityLogResponse } from '../../services/logs/logs-service';

export interface ILogState {
  activityLogs: ActivityLogResponse[];
  projectLogs: any;
  loading: boolean;
  error: string | null;
}

export const initialLogState: ILogState = {
  activityLogs: [],
  projectLogs: undefined,
  loading: false,
  error: null,
};
