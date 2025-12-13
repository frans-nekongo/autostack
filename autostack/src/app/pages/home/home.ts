import { Component, inject, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import {
  ProjectResult,
  ProjectService,
} from '../../services/project/project-service';
import { catchError, of } from 'rxjs';
import { UserService } from '../../services/user/user-service';
import { FormGroup, FormsModule } from '@angular/forms';
import { NgIcon, provideIcons } from '@ng-icons/core';
import { heroPaperAirplane } from '@ng-icons/heroicons/outline';
import { SideBar } from '../../components/side-bar/side-bar';
import { ChatFacade } from '../../state/chat/chat.facade';

@Component({
  selector: 'app-home',
  imports: [NgIcon, SideBar, FormsModule],
  templateUrl: './home.html',
  styleUrl: './home.scss',
  providers: [provideIcons({ heroPaperAirplane })],
})
export class Home implements OnInit {
  private router = inject(Router);
  private userService = inject(UserService);
  private chatFacade = inject(ChatFacade);
  prompt: string = '';
  aiForm!: FormGroup;

  isLoading = false;
  error: string | null = null;

  userFullName: String = '';

  ngOnInit(): void {
    this.loadUserFullName();
  }

  loadUserFullName(): void {
    this.userService
      .fetchUserDetails()
      .pipe(
        catchError((error) => {
          return of(null);
        })
      )
      .subscribe({
        next: (userResult: any) => {
          this.userFullName = userResult.fullname;
        },
      });
  }

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
      this.chatFacade.setPendingPrompt(trimmedDescription);
      this.chatFacade.generateArchitecture(trimmedDescription);
      this.prompt = '';
    }
  }
}
