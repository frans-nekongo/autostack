export interface ChatInfo {
  id: string;
  chatTitle?: string;
  prompt: string;
  initialSchema?: any;
  createdAt: string;
  updatedAt: string;
}

export interface IChatState {
  currentChatId: string | null;
  currentChat: ChatInfo | null;
  chats: ChatInfo[];
  pendingPrompt: string | null;
  loading: boolean;
  error: string | null;
  isGenerating: boolean;
}

export const initialChatState: IChatState = {
  currentChatId: null,
  currentChat: null,
  chats: [],
  loading: false,
  error: null,
  isGenerating: false,
  pendingPrompt: null
};