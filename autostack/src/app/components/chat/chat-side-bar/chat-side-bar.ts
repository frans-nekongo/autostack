import { Component, inject, OnInit } from '@angular/core';
import { Router, RouterModule } from '@angular/router';
import { provideIcons, NgIcon } from '@ng-icons/core';
import {
  heroPencilSquare,
  heroRectangleStack,
} from '@ng-icons/heroicons/outline';
import { ChatFacade } from '../../../state/chat/chat.facade';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-chat-side-bar',
  imports: [NgIcon, RouterModule, CommonModule],
  templateUrl: './chat-side-bar.html',
  styleUrl: './chat-side-bar.scss',
  providers: [
    provideIcons({
      heroPencilSquare,
      heroRectangleStack,
    }),
  ],
})
export class ChatSideBar implements OnInit{
  private router = inject(Router)
  private chatFacade = inject(ChatFacade);

  chats$ = this.chatFacade.chats$;
  chatsCount$ = this.chatFacade.chatsCount$;
  loading$ = this.chatFacade.loading$;

  ngOnInit(): void {
    // Load chats when sidebar initializes
    this.chatFacade.loadChats();
  }

  createNewChat(): void {
    // Navigate to home page for new chat creation
    window.location.href = '/';
  }

  navigateToChat(chatId: string) {
    this.router.navigate(['/chat', chatId]);
  }
}
