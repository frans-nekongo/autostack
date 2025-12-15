import { Component, inject, OnInit } from '@angular/core';
import { Router, RouterModule } from '@angular/router';
import {
  ProjectResult,
  ProjectService,
} from '../../services/project/project-service';
import { catchError, of, take } from 'rxjs';
import { UserService } from '../../services/user/user-service';
import { FormGroup, FormsModule } from '@angular/forms';
import { NgIcon, provideIcons } from '@ng-icons/core';
import { heroPaperAirplane } from '@ng-icons/heroicons/outline';
import { SideBar } from '../../components/side-bar/side-bar';
import { ChatFacade } from '../../state/chat/chat.facade';
import { LogFacade } from '../../state/logs/logs.facade';
import { CommonModule } from '@angular/common';
import {
  heroArrowPathSolid,
  heroSquaresPlusSolid,
  heroTrashSolid,
} from '@ng-icons/heroicons/solid';

type ActivityType =
  | 'update_project'
  | 'update_project_component'
  | 'delete_project'
  | 'delete_chat'
  | 'delete_component'
  | 'create_project'
  | 'create_chat'
  | 'create_component';

interface Activity {
  type: ActivityType;
}

@Component({
  selector: 'app-home',
  imports: [NgIcon, SideBar, FormsModule, CommonModule, RouterModule],
  templateUrl: './home.html',
  styleUrl: './home.scss',
  providers: [
    provideIcons({
      heroPaperAirplane,
      heroSquaresPlusSolid,
      heroTrashSolid,
      heroArrowPathSolid,
    }),
  ],
})
export class Home implements OnInit {
  private userService = inject(UserService);
  private chatFacade = inject(ChatFacade);
  private logFacade = inject(LogFacade);
  prompt: string = '';
  aiForm!: FormGroup;

  isLoading = false;
  error: string | null = null;

  userFullName: String = '';

  activityLogs$ = this.logFacade.activityLogs$;
  activityLogsLoading$ = this.logFacade.loading$;
  activityLogsError$ = this.logFacade.error$;

  greeting!: string;

  ngOnInit(): void {
    this.setGreeting();
    this.loadUserFullName();
    this.logFacade.loadActivityLogs();
  }

  setGreeting(): void {
    const today = new Date();
    const currentTime = today.getHours();

    if (currentTime < 12) {
      this.greeting = 'Good Morning';
    } else if (currentTime < 18) {
      this.greeting = 'Good Afternoon';
    } else {
      this.greeting = 'Good Evening';
    }
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

  getActivityTypeDisplay(activityType: string): string {
    const activityTypeMap: { [key: string]: string } = {
      update_project: 'Updated',
      update_project_component: 'Updated',
      delete_project: 'Deleted',
      delete_chat: 'Deleted',
      delete_component: 'Deleted',
      create_project: 'Created',
      create_chat: 'Created',
      create_component: 'Created',
    };

    return activityTypeMap[activityType] || 'Unknown Activity';
  }

  getIcon(activityType: string): string {
    const activityTypeMap: { [key: string]: string } = {
      update_project: 'heroArrowPathSolid',
      update_project_component: 'heroArrowPathSolid',
      delete_project: 'heroTrashSolid',
      delete_chat: 'heroTrashSolid',
      delete_component: 'Deleted Component',
      create_project: 'heroSquaresPlusSolid',
      create_chat: 'Created Chat',
      create_component: 'Created Component',
    };

    return activityTypeMap[activityType] || 'unknown';
  }

  getColour(activityType: string): string {
    const activityTypeMap: { [key: string]: string } = {
      update_project: '#3a6ea5',
      update_project_component: '#3a6ea5',
      delete_project: '#d74a49',
      delete_chat: '#d74a49',
      delete_component: '#d74a49',
      create_project: '#007f4e',
      create_chat: '#007f4e',
      create_component: '#007f4e',
    };

    return activityTypeMap[activityType] || 'unknown';
  }

  getUrl(activityType: string, itemId: string): string | null {
    const activityTypeMap: { [key: string]: string } = {
      create_project: `project/${itemId}`,
      update_project: `project/${itemId}`,
      create_chat: `chat/${itemId}`,
      create_component: `project/${itemId}`,
    };

    let isDeleted = false;
    this.activityLogs$.pipe(take(1)).subscribe((logs) => {
      isDeleted = logs.some((log) => {
        if (
          activityType === 'update_project' &&
          log.activityType === 'delete_project' &&
          log.projectId === itemId
        ) {
          return true;
        }
        if (
          activityType === 'create_project' &&
          log.activityType === 'delete_project' &&
          log.projectId === itemId
        ) {
          return true;
        }
        if (
          activityType === 'create_chat' &&
          log.activityType === 'delete_chat' &&
          log.chatId === itemId
        ) {
          return true;
        }
        if (
          activityType === 'create_component' &&
          log.activityType === 'delete_component' &&
          log.projectId === itemId
        ) {
          return true;
        }
        return false;
      });
    });

    // Return URL only if not deleted and URL exists in map
    if (isDeleted) {
      return null;
    }

    return activityTypeMap[activityType] || null;
  }

  isArray(value: any): boolean {
    return Array.isArray(value);
  }

  capitalizeFirstLetter(inputString: string): string {
    if (!inputString) {
      return inputString;
    }
    return inputString.charAt(0).toUpperCase() + inputString.slice(1);
  }
}
