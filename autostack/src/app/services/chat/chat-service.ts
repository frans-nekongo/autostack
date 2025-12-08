import { inject, Injectable } from '@angular/core';
import { Apollo, gql } from 'apollo-angular';
import { map, Observable } from 'rxjs';

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

// Response Interfaces
export interface GenerateArchitectureResponse {
  success: boolean;
  schema?: any;
  chatId?: string;
  error?: string;
}

export interface ChatInfo {
  id: string;
  chatTitle?: string;
  prompt: string;
  initialSchema?: any;
  createdAt: string;
  updatedAt: string;
}

export interface DeleteChatResponse {
  success: boolean;
  error?: string;
}


@Injectable({
  providedIn: 'root',
})
export class ChatService {
  private apollo = inject(Apollo);

  generateArchitecture(description: string): Observable<GenerateArchitectureResponse> {
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
          return result.data?.getChat as ChatInfo
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

}
