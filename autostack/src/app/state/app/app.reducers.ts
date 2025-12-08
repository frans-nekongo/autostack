import { ActionReducerMap } from "@ngrx/store";
import { projectReducer } from "../project/project.reducer";
import { IProjectState } from "../project/project.models";
import { IChatState } from "../chat/chat.models";
import { chatReducer } from "../chat/chat.reducer";

export interface State {
  project: IProjectState,
  chat: IChatState
}

export const reducers: ActionReducerMap<State> = {
  project: projectReducer,
  chat: chatReducer
}