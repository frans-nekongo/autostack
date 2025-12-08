import { Component, inject } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { NgIcon, provideIcons } from '@ng-icons/core';
import { heroPaperAirplane } from '@ng-icons/heroicons/outline';
import { ChatFacade } from '../../../state/chat/chat.facade';
import { Logo } from "../../../components/logo/logo";

@Component({
  selector: 'app-new-chat',
  imports: [FormsModule, NgIcon, Logo],
  templateUrl: './new-chat.html',
  styleUrl: './new-chat.scss',
  providers: [provideIcons({ heroPaperAirplane })]
})
export class NewChat {
  prompt: string = '';
  private chatFacade = inject(ChatFacade)

  onKeyDown(event: KeyboardEvent) {
    // Submit on Enter, allow new line on Shift+Enter
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.onChatSubmit();
    }
  }

  onChatSubmit() {
    const trimmedDescription = this.prompt.trim();
    
    if (trimmedDescription) {
      // Dispatch action - navigation will happen automatically in effects
      this.chatFacade.generateArchitecture(trimmedDescription);
      
      // Clear the input
      this.prompt = '';
    }
  }
}
