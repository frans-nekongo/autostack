import { createFeatureSelector, createSelector } from '@ngrx/store';
import { CHAT_FEATURE_KEY } from './chat.reducer';
import { IChatState } from './chat.models';

export const selectChatStore = createFeatureSelector<IChatState>(CHAT_FEATURE_KEY);

// Current chat selectors
export const selectCurrentChatId = createSelector(
  selectChatStore,
  (state: IChatState) => state.currentChatId
);

export const selectCurrentChat = createSelector(
  selectChatStore,
  (state: IChatState) => state.currentChat
);

export const selectCurrentChatSchema = createSelector(
  selectCurrentChat,
  (chat) => chat?.initialSchema
);

export const selectCurrentChatTitle = createSelector(
  selectCurrentChat,
  (chat) => chat?.chatTitle
);

export const selectCurrentChatPrompt = createSelector(
  selectCurrentChat,
  (chat) => chat?.prompt
);

// Chats list selectors
export const selectChats = createSelector(
  selectChatStore,
  (state: IChatState) => state.chats
);

export const selectChatsCount = createSelector(
  selectChats,
  (chats) => chats.length
);

// Loading and error selectors
export const selectLoading = createSelector(
  selectChatStore,
  (state: IChatState) => state.loading
);

export const selectError = createSelector(
  selectChatStore,
  (state: IChatState) => state.error
);

export const selectIsGenerating = createSelector(
  selectChatStore,
  (state: IChatState) => state.isGenerating
);

export const selectHasError = createSelector(
  selectError,
  (error) => !!error
);

export const selectHasCurrentChat = createSelector(
  selectCurrentChat,
  (chat) => !!chat
);

export const selectPendingPrompt = createSelector(
  selectChatStore,
  (state: IChatState) => state.pendingPrompt
);