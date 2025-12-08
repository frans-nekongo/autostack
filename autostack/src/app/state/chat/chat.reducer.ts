import { createReducer, on, Action } from '@ngrx/store';
import { ChatActions } from './chat.actions';
import { IChatState, initialChatState } from './chat.models';

export const CHAT_FEATURE_KEY = 'chat';

export interface ChatState {
  readonly [CHAT_FEATURE_KEY]: IChatState;
}

export interface ChatPartialState {
  readonly [CHAT_FEATURE_KEY]: IChatState;
}

const reducer = createReducer(
  initialChatState,
  on(ChatActions.setPendingPrompt, (state, { prompt }) => ({
    ...state,
    pendingPrompt: prompt,
    isGenerating: true,
    loading: true,
    error: null,
  })),
  // Generate Architecture
  on(ChatActions.generateArchitecture, (state) => ({
    ...state,
    isGenerating: true,
    loading: true,
    error: null,
  })),
  on(ChatActions.generateArchitectureSuccess, (state, { chatId, schema }) => ({
    ...state,
    currentChatId: chatId,
    isGenerating: false,
    loading: false,
    error: null,
    pendingPrompt: null,
  })),
  on(ChatActions.generateArchitectureFailure, (state, { error }) => ({
    ...state,
    isGenerating: false,
    loading: false,
    error,
    pendingPrompt: null,
  })),

  // Load Chat
  on(ChatActions.loadChat, (state, { chatId }) => ({
    ...state,
    currentChatId: chatId,
    loading: true,
    error: null,
  })),
  on(ChatActions.loadChatSuccess, (state, { chat }) => ({
    ...state,
    currentChat: chat,
    currentChatId: chat.id,
    loading: false,
    error: null,
  })),
  on(ChatActions.loadChatFailure, (state, { error }) => ({
    ...state,
    currentChat: null,
    loading: false,
    error,
  })),

  // Load Chats
  on(ChatActions.loadChats, (state) => ({
    ...state,
    loading: true,
    error: null,
  })),
  on(ChatActions.loadChatsSuccess, (state, { chats }) => ({
    ...state,
    chats,
    loading: false,
    error: null,
  })),
  on(ChatActions.loadChatsFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error,
  })),

  // Delete Chat
  on(ChatActions.deleteChat, (state) => ({
    ...state,
    loading: true,
    error: null,
  })),
  on(ChatActions.deleteChatSuccess, (state, { chatId }) => ({
    ...state,
    chats: state.chats.filter((chat) => chat.id !== chatId),
    currentChat: state.currentChat?.id === chatId ? null : state.currentChat,
    currentChatId: state.currentChatId === chatId ? null : state.currentChatId,
    loading: false,
    error: null,
  })),
  on(ChatActions.deleteChatFailure, (state, { error }) => ({
    ...state,
    loading: false,
    error,
  })),

  // Set Current Chat
  on(ChatActions.setCurrentChat, (state, { chatId }) => ({
    ...state,
    currentChatId: chatId,
  })),

  // Reset State
  on(ChatActions.resetChatState, () => initialChatState)
);

export function chatReducer(state: IChatState | undefined, action: Action) {
  return reducer(state, action);
}
