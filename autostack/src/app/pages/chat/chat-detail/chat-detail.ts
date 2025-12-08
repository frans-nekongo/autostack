import { Component, inject, OnDestroy, OnInit } from '@angular/core';
import { provideIcons, NgIcon } from '@ng-icons/core';
import { heroPaperAirplane } from '@ng-icons/heroicons/outline';
import { ChatFacade } from '../../../state/chat/chat.facade';
import { BehaviorSubject, Observable, Subject, take, takeUntil } from 'rxjs';
import { ActivatedRoute } from '@angular/router';
import { CommonModule } from '@angular/common';
import {
  diAngularOriginal,
  diApachekafkaOriginal,
  diDjangorestOriginal,
  diExpressOriginal,
  diFastapiOriginal,
  diFlaskOriginal,
  diGoOriginal,
  diJavaOriginal,
  diMongodbOriginal,
  diMysqlOriginal,
  diNestjsOriginal,
  diNextjsOriginal,
  diNodejsOriginal,
  diPostgresqlOriginal,
  diPythonOriginal,
  diReactOriginal,
  diRedisOriginal,
  diSqliteOriginal,
  diSvelteOriginal,
  diVuejsOriginal,
} from '@ng-icons/devicon/original';
import {
  ProjectCreatedResponse,
  ProjectService,
} from '../../../services/project/project-service';

@Component({
  selector: 'app-chat-detail',
  imports: [CommonModule, NgIcon],
  templateUrl: './chat-detail.html',
  styleUrl: './chat-detail.scss',
  providers: [
    provideIcons({
      diDjangorestOriginal,
      diAngularOriginal,
      diFlaskOriginal,
      diFastapiOriginal,
      diExpressOriginal,
      diNestjsOriginal,
      diReactOriginal,
      diNextjsOriginal,
      diVuejsOriginal,
      diSvelteOriginal,
      diPostgresqlOriginal,
      diMysqlOriginal,
      diMongodbOriginal,
      diSqliteOriginal,
      diRedisOriginal,
      diApachekafkaOriginal,
      diNodejsOriginal,
      diPythonOriginal,
      diJavaOriginal,
      diGoOriginal,
    }),
  ],
})
export class ChatDetail implements OnInit, OnDestroy {
  private chatFacade = inject(ChatFacade);
  private destroy$ = new Subject<void>();
  private route = inject(ActivatedRoute);
  private projectService = inject(ProjectService);

  currentChat$ = this.chatFacade.currentChat$;
  loading$ = this.chatFacade.loading$;
  error$ = this.chatFacade.error$;

  generationResult$!: Observable<ProjectCreatedResponse | null>;
  errorMessage$!: Observable<string | null>;
  isGenerating$!: Observable<boolean>;
  private generationResultSubject =
    new BehaviorSubject<ProjectCreatedResponse | null>(null);
  private errorMessageSubject = new BehaviorSubject<string | null>(null);
  private isGeneratingSubject = new BehaviorSubject<boolean>(false);

  isLoadingCreation = false
  ngOnInit(): void {
    this.route.params.subscribe(params => {
      const chatId = params['chatid'];
      if (chatId) {
        this.chatFacade.loadChat(chatId);
      }
    });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  getIcon(framework: string): string {
    const iconMap: { [key: string]: string } = {
      // Backend frameworks
      django: 'diDjangorestOriginal',
      flask: 'diFlaskOriginal',
      fastapi: 'diFastapiOriginal',
      express: 'diExpressOriginal',
      nestjs: 'diNestjsOriginal',

      // Frontend frameworks
      react: 'diReactOriginal',
      nextjs: 'diNextjsOriginal',
      angular: 'diAngularOriginal',
      vue: 'diVuejsOriginal',
      svelte: 'diSvelteOriginal',

      // Databases
      postgresql: 'diPostgresqlOriginal',
      mysql: 'diMysqlOriginal',
      mongodb: 'diMongodbOriginal',
      sqlite: 'diSqliteOriginal',
      redis: 'diRedisOriginal',
      kafka: 'diApachekafkaOriginal',

      // Runtimes/Languages
      nodejs: 'diNodejsOriginal',
      python: 'diPythonOriginal',
      java: 'diJavaOriginal',
      go: 'diGoOriginal',

      // No framework
      vanilla: '',
      none: '',
    };

    // Convert to lowercase to handle case variations and return the icon name
    return iconMap[framework.toLowerCase()] || '';
  }

  onGenerateProject(): void {
    this.generationResultSubject.next(null);
    this.errorMessageSubject.next(null);
    this.isGeneratingSubject.next(true);

    this.currentChat$.pipe(take(1)).subscribe({
      next: (chat) => {
        if (!chat) {
          this.errorMessageSubject.next('No chat selected');
          this.isGeneratingSubject.next(false);
          return;
        }

        if (!chat.initialSchema) {
          this.errorMessageSubject.next('No schema found in the chat');
          this.isGeneratingSubject.next(false);
          return;
        }

        try {
          // Validate the schema has required fields
          if (
            !chat.initialSchema.project ||
            !chat.initialSchema.project.name ||
            !chat.initialSchema.project.author ||
            !chat.initialSchema.project.description
          ) {
            this.errorMessageSubject.next(
              'Invalid schema: Missing required project information'
            );
            this.isGeneratingSubject.next(false);
            return;
          }

          // Call the project service
          this.projectService
            .createFullProject(chat.initialSchema, chat.id)
            .subscribe({
              next: (result) => {
                this.generationResultSubject.next(result);
                this.isGeneratingSubject.next(false);

                // Optional: Show success notification
                if (result.success) {
                  console.log('Project created with ID:', result.projectId);
                  // You could also navigate to the project page
                  // this.router.navigate(['/projects', result.projectId]);
                }
              },
              error: (error) => {
                this.errorMessageSubject.next(
                  'Failed to create project: ' + error.message
                );
                this.isGeneratingSubject.next(false);
              },
            });
        } catch (error) {
          this.errorMessageSubject.next(
            'Error processing schema: ' + (error as Error).message
          );
          this.isGeneratingSubject.next(false);
        }
      },
      error: (error) => {
        this.errorMessageSubject.next('Error loading chat: ' + error.message);
        this.isGeneratingSubject.next(false);
      },
    });
  }
}
