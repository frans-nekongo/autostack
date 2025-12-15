import { ChatFacade } from '../chat/chat.facade';
import { LogFacade } from '../logs/logs.facade';
import { OperationsFacade } from '../operations/operations.facade';
import { ProjectFacade } from '../project/project.facade';

export const appFacades = [
  ProjectFacade,
  ChatFacade,
  OperationsFacade,
  LogFacade,
];
