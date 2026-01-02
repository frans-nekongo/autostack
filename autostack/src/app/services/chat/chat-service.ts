import { inject, Injectable } from '@angular/core';
import { Apollo, gql } from 'apollo-angular';
import { map, Observable } from 'rxjs';
import { ChatInfo } from '../../state/chat/chat.models';

const GENERATE_ARCHITECTURE = gql`
  query GenerateArchitecture($description: String!) {
    generateArchitecture(description: $description) {
      success
      schema
      chatId
      error
    }
  }
`;

const GET_CHAT = gql`
  query GetChat($chatId: String!) {
    getChat(chatId: $chatId) {
      id
      chatTitle
      prompt
      initialSchema
      createdAt
      updatedAt
      hasValidationError
      validationError
    }
  }
`;

const LIST_CHATS = gql`
  query ListChats {
    listChats {
      id
      chatTitle
      prompt
      initialSchema
      createdAt
      updatedAt
    }
  }
`;

const DELETE_CHAT = gql`
  mutation DeleteChat($chatId: String!) {
    deleteChat(chatId: $chatId) {
      success
      error
    }
  }
`;

const REGENERATE_ARCHITECTURE = gql`
  query RegenerateArchitecture($chatId: String!, $description: String!) {
    regenerateArchitecture(chatId: $chatId, description: $description) {
      success
      schema
      chatId
      error
      isValidationError
      unsupportedItems {
        technologies
        frameworks
        componentTypes
      }
      supportedItems {
        technologies
        frameworks
        componentTypes
      }
    }
  }
`;

const RATE_SCHEMA = gql`
  mutation RateSchema($chatId: String!, $score: Int!, $comment: String) {
    rateSchema(chatId: $chatId, score: $score, comment: $comment) {
      success
      message
      error
    }
  }
`;

export interface GenerateArchitectureResponse {
  success: boolean;
  schema?: any;
  chatId?: string;
  error?: string;
  isValidationError?: boolean;
  unsupportedItems?: {
    technologies?: string[];
    frameworks?: string[];
    componentTypes?: string[];
  };
  supportedItems?: {
    technologies?: Record<string, string[]>;
    frameworks?: string[];
    componentTypes?: string[];
  };
}

export interface DeleteChatResponse {
  success: boolean;
  error?: string;
}

export interface RateSchemaResponse {
  success: boolean;
  message?: string;
  error?: string;
}

@Injectable({
  providedIn: 'root',
})
export class ChatService {
  private apollo = inject(Apollo);

  generateArchitecture(
    description: string
  ): Observable<GenerateArchitectureResponse> {
    return this.apollo
      .query<{ generateArchitecture: GenerateArchitectureResponse }>({
        query: GENERATE_ARCHITECTURE,
        variables: { description },
      })
      .pipe(
        map((result) => {
          if (result.error) {
            throw new Error(result.error.message);
          }
          return result.data!.generateArchitecture;
        })
      );
  }

  regenerateArchitecture(
    chatId: string,
    description: string
  ): Observable<GenerateArchitectureResponse> {
    return this.apollo
      .query<{ regenerateArchitecture: GenerateArchitectureResponse }>({
        query: REGENERATE_ARCHITECTURE,
        variables: { chatId, description },
      })
      .pipe(
        map((result) => {
          if (result.error) {
            throw new Error(result.error.message);
          }
          return result.data!.regenerateArchitecture;
        })
      );
  }

  getChat(chatId: string): Observable<ChatInfo> {
    return this.apollo
      .query<{ getChat: ChatInfo | null }>({
        query: GET_CHAT,
        variables: { chatId },
        fetchPolicy: 'network-only',
      })
      .pipe(
        map((result) => {
          if (result.error) {
            throw new Error(result.error.message);
          }
          return result.data?.getChat as ChatInfo;
        })
      );
  }

  listChats(): Observable<ChatInfo[]> {
    return this.apollo
      .query<{ listChats: ChatInfo[] }>({
        query: LIST_CHATS,
        fetchPolicy: 'network-only',
      })
      .pipe(
        map((result) => {
          if (result.error) {
            throw new Error(result.error.message);
          }
          return result.data?.listChats as ChatInfo[];
        })
      );
  }

  deleteChat(chatId: string): Observable<DeleteChatResponse> {
    return this.apollo
      .mutate<{ deleteChat: DeleteChatResponse }>({
        mutation: DELETE_CHAT,
        variables: { chatId },
      })
      .pipe(
        map((result) => {
          if (result.error) {
            throw new Error(result.error.message);
          }
          return result.data!.deleteChat;
        })
      );
  }

  rateSchema(
    chatId: string,
    score: number,
    comment: string | null
  ): Observable<RateSchemaResponse> {
    return this.apollo
      .mutate<{ rateSchema: RateSchemaResponse }>({
        mutation: RATE_SCHEMA,
        variables: { chatId, score, comment },
      })
      .pipe(
        map((result) => {
          if (result.error) {
            throw new Error(result.error.message);
          }
          return result.data!.rateSchema;
        })
      );
  }
}
