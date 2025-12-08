import { Component, inject } from '@angular/core';
import { ChatFacade } from '../../../state/chat/chat.facade';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-loading-chat',
  imports: [CommonModule],
  templateUrl: './loading-chat.html',
  styleUrl: './loading-chat.scss',
})
export class LoadingChat {
  private chatFacade = inject(ChatFacade);
  pendingPrompt$ = this.chatFacade.pendingPrompt$;
}
