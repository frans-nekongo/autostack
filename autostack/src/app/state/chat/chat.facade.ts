import { Injectable, inject } from '@angular/core';
import { Store } from '@ngrx/store';

import { ChatActions } from './chat.actions';
import * as ChatSelectors from './chat.selectors';

@Injectable({
  providedIn: 'root',
})
export class ChatFacade {
  private readonly store = inject(Store);

  // Selectors
  currentChatId$ = this.store.select(ChatSelectors.selectCurrentChatId);
  currentChat$ = this.store.select(ChatSelectors.selectCurrentChat);
  currentChatSchema$ = this.store.select(ChatSelectors.selectCurrentChatSchema);
  currentChatTitle$ = this.store.select(ChatSelectors.selectCurrentChatTitle);
  currentChatPrompt$ = this.store.select(ChatSelectors.selectCurrentChatPrompt);
  chats$ = this.store.select(ChatSelectors.selectChats);
  chatsCount$ = this.store.select(ChatSelectors.selectChatsCount);
  loading$ = this.store.select(ChatSelectors.selectLoading);
  error$ = this.store.select(ChatSelectors.selectError);
  isGenerating$ = this.store.select(ChatSelectors.selectIsGenerating);
  hasError$ = this.store.select(ChatSelectors.selectHasError);
  hasCurrentChat$ = this.store.select(ChatSelectors.selectHasCurrentChat);
  pendingPrompt$ = this.store.select(ChatSelectors.selectPendingPrompt);

  // Actions

  /**
   * Set the prompt while completing the request
   */
  setPendingPrompt(prompt: string): void {
    this.store.dispatch(ChatActions.setPendingPrompt({ prompt }));
  }

  /**
   * Generate architecture from description (creates new chat)
   * Automatically navigates to /chat/:id on success
   */
  generateArchitecture(description: string): void {
    this.store.dispatch(ChatActions.generateArchitecture({ description }));
  }

  /**
   * Load a specific chat by ID
   */
  loadChat(chatId: string): void {
    this.store.dispatch(ChatActions.loadChat({ chatId }));
  }

  /**
   * Load all chats
   */
  loadChats(): void {
    this.store.dispatch(ChatActions.loadChats());
  }

  /**
   * Delete a chat by ID
   */
  deleteChat(chatId: string): void {
    this.store.dispatch(ChatActions.deleteChat({ chatId }));
  }

  /**
   * Set the current chat ID (for navigation)
   */
  setCurrentChat(chatId: string): void {
    this.store.dispatch(ChatActions.setCurrentChat({ chatId }));
  }

  /**
   * Reset the chat state to initial values
   */
  resetChatState(): void {
    this.store.dispatch(ChatActions.resetChatState());
  }
}
