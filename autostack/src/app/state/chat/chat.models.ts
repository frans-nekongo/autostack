export interface ChatInfo {
  id: string;
  chatTitle?: string;
  prompt: string;
  initialSchema?: any;
  createdAt: string;
  updatedAt: string;
  hasValidationError: boolean;
  validationError?: {
    message: string;
    unsupported_technologies?: string[];
    unsupported_frameworks?: string[];
    unsupported_component_types?: string[];
    supported_technologies?: Record<string, string[]>;
    supported_frameworks?: string[];
    supported_component_types?: string[];
  };
}

export interface IChatState {
  currentChatId: string | null;
  currentChat: ChatInfo | null;
  chats: ChatInfo[];
  pendingPrompt: string | null;
  loading: boolean;
  error: string | null;
  isGenerating: boolean;
  isValidationError: boolean;
  unsupportedItems: {
    technologies?: string[];
    frameworks?: string[];
    componentTypes?: string[];
  } | null;
  supportedItems: {
    technologies?: Record<string, string[]>;
    frameworks?: string[];
    componentTypes?: string[];
  } | null;
}

export const initialChatState: IChatState = {
  currentChatId: null,
  currentChat: null,
  chats: [],
  loading: false,
  error: null,
  isGenerating: false,
  pendingPrompt: null,
  isValidationError: false,
  unsupportedItems: null,
  supportedItems: null,
};
