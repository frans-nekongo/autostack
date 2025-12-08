import { Injectable, inject } from '@angular/core';
import { createEffect, Actions, ofType } from '@ngrx/effects';
import { Router } from '@angular/router';
import { switchMap, map, catchError, tap } from 'rxjs/operators';
import { of } from 'rxjs';

import { ChatActions } from './chat.actions';
import { ChatService } from '../../services/chat/chat-service';

@Injectable()
export class ChatEffects {
  private actions$ = inject(Actions);
  private chatService = inject(ChatService);
  private router = inject(Router);

  // Generate architecture and navigate to chat page
  generateArchitecture$ = createEffect(() =>
    this.actions$.pipe(
      ofType(ChatActions.generateArchitecture),
      switchMap(({ description }) =>
        this.chatService.generateArchitecture(description).pipe(
          map((result) => {
            if (result.success && result.chatId && result.schema) {
              return ChatActions.generateArchitectureSuccess({
                chatId: result.chatId,
                schema: result.schema,
              });
            } else {
              return ChatActions.generateArchitectureFailure({
                error: result.error || 'Failed to generate architecture',
              });
            }
          }),
          catchError((error) =>
            of(
              ChatActions.generateArchitectureFailure({
                error: error.message || 'An error occurred',
              })
            )
          )
        )
      )
    )
  );

  navigateToLoadingChat$ = createEffect(
    () =>
      this.actions$.pipe(
        ofType(ChatActions.setPendingPrompt),
        tap(() => {
          this.router.navigate(['/chat', 'loading']);
        })
      ),
    { dispatch: false }
  );

  // Navigate to chat page after successful generation
  navigateToChat$ = createEffect(
    () =>
      this.actions$.pipe(
        ofType(ChatActions.generateArchitectureSuccess),
        tap(({ chatId }) => {
          this.router.navigate(['/chat', chatId], { replaceUrl: true });
        })
      ),
    { dispatch: false }
  );

  // Load specific chat
  loadChat$ = createEffect(() =>
    this.actions$.pipe(
      ofType(ChatActions.loadChat),
      switchMap(({ chatId }) =>
        this.chatService.getChat(chatId).pipe(
          map((chat) => {
            if (chat) {
              return ChatActions.loadChatSuccess({ chat });
            } else {
              return ChatActions.loadChatFailure({
                error: 'Chat not found',
              });
            }
          }),
          catchError((error) =>
            of(
              ChatActions.loadChatFailure({
                error: error.message || 'Failed to load chat',
              })
            )
          )
        )
      )
    )
  );

  // Load all chats
  loadChats$ = createEffect(() =>
    this.actions$.pipe(
      ofType(ChatActions.loadChats),
      switchMap(() =>
        this.chatService.listChats().pipe(
          map((chats) => ChatActions.loadChatsSuccess({ chats })),
          catchError((error) =>
            of(
              ChatActions.loadChatsFailure({
                error: error.message || 'Failed to load chats',
              })
            )
          )
        )
      )
    )
  );

  // Delete chat
  deleteChat$ = createEffect(() =>
    this.actions$.pipe(
      ofType(ChatActions.deleteChat),
      switchMap(({ chatId }) =>
        this.chatService.deleteChat(chatId).pipe(
          map((result) => {
            if (result.success) {
              return ChatActions.deleteChatSuccess({ chatId });
            } else {
              return ChatActions.deleteChatFailure({
                error: result.error || 'Failed to delete chat',
              });
            }
          }),
          catchError((error) =>
            of(
              ChatActions.deleteChatFailure({
                error: error.message || 'Failed to delete chat',
              })
            )
          )
        )
      )
    )
  );

  // Navigate away from deleted chat if currently viewing it
  navigateAfterDelete$ = createEffect(
    () =>
      this.actions$.pipe(
        ofType(ChatActions.deleteChatSuccess),
        tap(() => {
          // Optionally navigate to home or chat list
          const currentUrl = this.router.url;
          if (currentUrl.startsWith('/chat/')) {
            this.router.navigate(['/']);
          }
        })
      ),
    { dispatch: false }
  );
}
