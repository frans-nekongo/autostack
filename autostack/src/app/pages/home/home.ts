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
  private projectService = inject(ProjectService);
  private userService = inject(UserService);
  private chatFacade = inject(ChatFacade);
  prompt: string = '';
  aiForm!: FormGroup;

  projects: ProjectResult[] = [];
  isLoading = false;
  error: string | null = null;

  userFullName: String = '';

  ngOnInit(): void {
    this.loadUserFullName();
    this.loadProjects();
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

  loadProjects(): void {
    this.isLoading = true;
    this.error = null;

    this.projectService
      .fetchAllProjects()
      .pipe(
        catchError((error) => {
          console.error('Error fetching projects:', error);
          this.error = 'Failed to load projects. Please try again later.';
          this.isLoading = false;
          return of(null);
        })
      )
      .subscribe({
        next: (projectResult: any) => {
          this.isLoading = false;

          if (projectResult) {
            this.projects = projectResult.map((project: any) =>
              this.transformProjectResult(project)
            );
          } else {
            this.error = 'No projects found.';
          }
        },
        error: (error) => {
          console.error('Error in subscription:', error);
          this.isLoading = false;
          this.error = 'An unexpected error occurred.';
        },
      });
  }

  private transformProjectResult(projectResult: ProjectResult): ProjectResult {
    return {
      id: projectResult.id,
      name: projectResult.name,
      author: projectResult.author,
      description: projectResult.description || 'No description available',
      version: projectResult.version,
      status: projectResult.status,
      metadata: projectResult.metadata,
      gitInfo: {
        ...projectResult.gitInfo,
      },
    };
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
