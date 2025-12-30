import { props, createActionGroup, emptyProps } from '@ngrx/store';
import { ChatInfo } from './chat.models';

export const ChatActions = createActionGroup({
  source: 'Chat',
  events: {
    // Pending Prompt
    'Set Pending Prompt': props<{ prompt: string }>(),

    // Generate Architecture (Create New Chat)
    'Generate Architecture': props<{ description: string }>(),
    'Generate Architecture Success': props<{
      chatId: string;
      schema: any;
    }>(),
    'Generate Architecture Failure': props<{ 
      error: string;
      isValidationError?: boolean;
      unsupportedItems?: any[];
      supportedItems?: any[];
    }>(),

    'Regenerate Architecture': props<{ chatId: string; description: string }>(),
    'Regenerate Architecture Success': props<{
      chatId: string;
      schema: any;
    }>(),
    'Regenerate Architecture Failure': props<{
      error: string;
      isValidationError: boolean;
      unsupportedItems?: any;
      supportedItems?: any;
    }>(),

    // Load Specific Chat
    'Load Chat': props<{ chatId: string }>(),
    'Load Chat Success': props<{ chat: ChatInfo }>(),
    'Load Chat Failure': props<{ error: string }>(),

    // Load All Chats
    'Load Chats': emptyProps(),
    'Load Chats Success': props<{ chats: ChatInfo[] }>(),
    'Load Chats Failure': props<{ error: string }>(),

    // Delete Chat
    'Delete Chat': props<{ chatId: string }>(),
    'Delete Chat Success': props<{ chatId: string }>(),
    'Delete Chat Failure': props<{ error: string }>(),

    // Set Current Chat
    'Set Current Chat': props<{ chatId: string }>(),

    // Reset State
    'Reset Chat State': emptyProps(),
    'Clear Validation Error': emptyProps(),
  },
});