import { ActionReducerMap } from '@ngrx/store';
import { projectReducer } from '../project/project.reducer';
import { IProjectState } from '../project/project.models';
import { IChatState } from '../chat/chat.models';
import { chatReducer } from '../chat/chat.reducer';
import { operationsReducer } from '../operations/operations.reducer';
import { IOperationsState } from '../operations/operations.models';
import { logsReducer } from '../logs/logs.reducer';
import { ILogState } from '../logs/logs.models';

export interface State {
  project: IProjectState;
  chat: IChatState;
  operations: IOperationsState;
  log: ILogState;
}

export const reducers: ActionReducerMap<State> = {
  project: projectReducer,
  chat: chatReducer,
  operations: operationsReducer,
  log: logsReducer,
};
