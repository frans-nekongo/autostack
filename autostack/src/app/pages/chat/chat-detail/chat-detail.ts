import { Component, inject, OnDestroy, OnInit } from '@angular/core';
import { provideIcons, NgIcon } from '@ng-icons/core';
import {
  heroClipboardDocument,
  heroPaperAirplane,
} from '@ng-icons/heroicons/outline';
import { ChatFacade } from '../../../state/chat/chat.facade';
import {
  BehaviorSubject,
  combineLatest,
  Observable,
  Subject,
  take,
  takeUntil,
} from 'rxjs';
import { ActivatedRoute, Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
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
import { ProjectFacade } from '../../../state/project/project.facade';
import { OperationsFacade } from '../../../state/operations/operations.facade';
import { ChatService } from '../../../services/chat/chat-service';

interface ProjectSchema {
  project: {
    name: string;
    author: string;
    description: string;
    version: string;
  };
  technologies: Array<{
    name: string;
    type: string;
    version: string;
  }>;
  components: Array<{
    component_id: string;
    name: string;
    technology: string;
    framework: string;
    port: number;
    type: string;
    environment_variables: any;
    dependencies?: any[];
  }>;
  connections: Array<{
    source: string;
    target: string;
    type: string;
    port: number;
  }>;
}

@Component({
  selector: 'app-chat-detail',
  imports: [CommonModule, NgIcon, FormsModule],
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
      heroClipboardDocument,
      heroPaperAirplane
    }),
  ],
})
export class ChatDetail implements OnInit, OnDestroy {
  private chatFacade = inject(ChatFacade);
  private projectFacade = inject(ProjectFacade);
  private operationsFacade = inject(OperationsFacade);
  private destroy$ = new Subject<void>();
  private route = inject(ActivatedRoute);
  private chatService = inject(ChatService);


  currentChat$ = this.chatFacade.currentChat$;
  loading$ = this.chatFacade.loading$;
  error$ = this.chatFacade.error$;
  isValidationError$ = this.chatFacade.isValidationError$;
  unsupportedItems$ = this.chatFacade.unsupportedItems$;
  supportedItems$ = this.chatFacade.supportedItems$;
  activeOperationsCount$ = this.operationsFacade.activeOperationsCount$;
  isCreating = false;

  generationResult$!: Observable<ProjectCreatedResponse | null>;
  errorMessage$!: Observable<string | null>;
  isGenerating$!: Observable<boolean>;
  private generationResultSubject =
    new BehaviorSubject<ProjectCreatedResponse | null>(null);
  private errorMessageSubject = new BehaviorSubject<string | null>(null);
  private isGeneratingSubject = new BehaviorSubject<boolean>(false);

  isLoadingCreation = false;
  projectCreateMessage!: string;

  // Edit mode properties
  isEditMode = false;
  editSection: 'project' | 'components' | 'connections' = 'project';
  editedSchema!: ProjectSchema;

  showErrorModal = false;
  editedPrompt = '';
  validationErrorMessage = '';
  unsupportedTechnologies: string[] = [];
  unsupportedFrameworks: string[] = [];
  supportedTechnologiesFormatted = '';
  supportedFrameworksFormatted = '';

  selectedRating: number | null = null;
  ratingComment: string = '';
  ratingMessage: string = '';
  ratingSuccess: boolean = false;

  ngOnInit(): void {
    this.route.params.pipe(takeUntil(this.destroy$)).subscribe((params) => {
      const chatId = params['chatid'];
      if (chatId) {
        // Reset edit mode and schema when navigating to a new chat
        this.isEditMode = false;
        this.editSection = 'project';
        this.editedSchema = null as any;
        this.projectCreateMessage = '';

        this.chatFacade.loadChat(chatId);
      }
    });

    // Initialize editedSchema when chat loads
    this.currentChat$.pipe(takeUntil(this.destroy$)).subscribe((chat) => {
      if (chat?.initialSchema) {
        // Always create a fresh copy when chat changes
        this.editedSchema = JSON.parse(JSON.stringify(chat.initialSchema));
      }
    });

    this.isValidationError$
      .pipe(takeUntil(this.destroy$))
      .subscribe((isValidationError) => {
        if (isValidationError) {
          this.showErrorModal = true;

          // Get the current prompt
          this.currentChat$.pipe(take(1)).subscribe((chat) => {
            this.editedPrompt = chat?.prompt || '';
          });
        }
      });

    // Subscribe to error details
    combineLatest([this.error$, this.unsupportedItems$, this.supportedItems$])
      .pipe(takeUntil(this.destroy$))
      .subscribe(([error, unsupported, supported]) => {
        if (error && unsupported && supported) {
          this.validationErrorMessage = error;
          this.unsupportedTechnologies = unsupported.technologies || [];
          this.unsupportedFrameworks = unsupported.frameworks || [];

          // Format supported items for display
          if (supported.technologies) {
            this.supportedTechnologiesFormatted = Object.entries(
              supported.technologies
            )
              .map(
                ([category, techs]) =>
                  `${category}: ${(techs as string[]).join(', ')}`
              )
              .join('\n');
          }

          if (supported.frameworks) {
            this.supportedFrameworksFormatted = supported.frameworks.join(', ');
          }
        }
      });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  closeErrorModal(): void {
    this.showErrorModal = false;
    this.chatFacade.clearValidationError();
  }

  retryWithUpdatedPrompt(): void {
    if (!this.editedPrompt.trim()) {
      return;
    }

    this.currentChat$.pipe(take(1)).subscribe((chat) => {
      if (chat?.id) {
        this.chatFacade.regenerateArchitecture(chat.id, this.editedPrompt);
        this.showErrorModal = false;
      }
    });
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

    return iconMap[framework.toLowerCase()] || '';
  }

  onEditSchema(): void {
    if (this.isEditMode) {
      // Cancel edit - reload original schema
      this.currentChat$.pipe(take(1)).subscribe((chat) => {
        if (chat?.initialSchema) {
          this.editedSchema = JSON.parse(JSON.stringify(chat.initialSchema));
        }
      });
      this.isEditMode = false;
      this.editSection = 'project';
    } else {
      // Enter edit mode
      this.isEditMode = true;
      this.editSection = 'project';
    }
  }

  saveSection(): void {
    // Exit edit mode for this section, showing the buttons again
    this.isEditMode = false;
  }

  addComponent(): void {
    const newComponent = {
      component_id: `component-${Date.now()}`,
      name: 'New Component',
      technology: 'nodejs',
      framework: 'none',
      port: 8000,
      type: 'api',
      environment_variables: {},
      dependencies: [],
    };
    this.editedSchema.components.push(newComponent);
  }

  removeComponent(index: number): void {
    this.editedSchema.components.splice(index, 1);
  }

  addConnection(): void {
    if (this.editedSchema.components.length >= 2) {
      const newConnection = {
        source: this.editedSchema.components[0].component_id,
        target: this.editedSchema.components[1].component_id,
        type: 'api-call',
        port: this.editedSchema.components[1].port,
      };
      this.editedSchema.connections.push(newConnection);
    }
  }

  removeConnection(index: number): void {
    this.editedSchema.connections.splice(index, 1);
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

        // Use editedSchema instead of initialSchema
        const schemaToUse = this.editedSchema;

        if (!schemaToUse) {
          this.errorMessageSubject.next('No schema found');
          this.isGeneratingSubject.next(false);
          return;
        }

        try {
          // Validate the schema has required fields
          if (
            !schemaToUse.project ||
            !schemaToUse.project.name ||
            !schemaToUse.project.author ||
            !schemaToUse.project.description
          ) {
            this.errorMessageSubject.next(
              'Invalid schema: Missing required project information'
            );
            this.isGeneratingSubject.next(false);
            return;
          }

          this.projectFacade.createProject(schemaToUse, chat.id);
          this.showSuccessMessage(
            'Project creation started! Check notifications for progress.'
          );
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

  private showSuccessMessage(message: string): void {
    this.projectCreateMessage = message;
  }

  getAvailableFrameworks(
    technology: string
  ): Array<{ value: string; label: string }> {
    const frameworkMap: {
      [key: string]: Array<{ value: string; label: string }>;
    } = {
      nodejs: [
        { value: 'none', label: 'None' },
        { value: 'express', label: 'Express' },
        { value: 'nestjs', label: 'NestJS' },
        { value: 'react', label: 'React' },
        { value: 'nextjs', label: 'Next.js' },
        { value: 'angular', label: 'Angular' },
        { value: 'vue', label: 'Vue' },
        { value: 'svelte', label: 'Svelte' },
      ],
      python: [
        { value: 'none', label: 'None' },
        { value: 'django', label: 'Django' },
        { value: 'flask', label: 'Flask' },
        { value: 'fastapi', label: 'FastAPI' },
      ],
      java: [{ value: 'none', label: 'None' }],
      go: [{ value: 'none', label: 'None' }],
      postgresql: [{ value: 'none', label: 'None' }],
      mysql: [{ value: 'none', label: 'None' }],
      mongodb: [{ value: 'none', label: 'None' }],
      sqlite: [{ value: 'none', label: 'None' }],
      redis: [{ value: 'none', label: 'None' }],
      kafka: [{ value: 'none', label: 'None' }],
    };

    return (
      frameworkMap[technology.toLowerCase()] || [
        { value: 'none', label: 'None' },
      ]
    );
  }

  onTechnologyChange(component: any): void {
    // Reset framework to 'none' when technology changes
    const availableFrameworks = this.getAvailableFrameworks(
      component.technology
    );
    // Check if current framework is still valid for the new technology
    const isFrameworkValid = availableFrameworks.some(
      (f) => f.value === component.framework
    );
    if (!isFrameworkValid) {
      component.framework = 'none';
    }
  }

  openEditPromptModal(): void {
    this.currentChat$.pipe(take(1)).subscribe((chat) => {
      if (chat) {
        this.editedPrompt = chat.prompt;
        this.validationErrorMessage = chat.validationError?.message || '';
        this.unsupportedTechnologies =
          chat.validationError?.unsupported_technologies || [];
        this.unsupportedFrameworks =
          chat.validationError?.unsupported_frameworks || [];
        this.supportedTechnologiesFormatted = this.formatSupportedTechnologies(
          chat.validationError?.supported_technologies
        );
        this.supportedFrameworksFormatted =
          chat.validationError?.supported_frameworks?.join(', ') || '';
        this.showErrorModal = true;
      }
    });
  }

  private formatSupportedTechnologies(
    technologies?: Record<string, string[]>
  ): string {
    if (!technologies) return '';
    return Object.entries(technologies)
      .map(([category, techs]) => `${category}: ${techs.join(', ')}`)
      .join('\n');
  }

  objectKeys(obj: any): string[] {
    return obj ? Object.keys(obj) : [];
  }

  submitRating(): void {
  if (!this.selectedRating || !this.currentChat$) {
    return;
  }

  this.currentChat$.pipe(take(1)).subscribe(chat => {
    if (!chat?.id) return;

    this.chatService.rateSchema(chat.id, this.selectedRating!, this.ratingComment || null)
      .subscribe({
        next: (response) => {
          this.ratingSuccess = response.success;
          this.ratingMessage = response.success 
            ? (response.message || 'Thank you for rating the generated schema!')
            : (response.error || 'Failed to submit rating');
          
          if (response.success) {
            // Optionally clear the form after successful submission
            setTimeout(() => {
              this.ratingMessage = '';
            }, 5000);
          }
        },
        error: (error) => {
          this.ratingSuccess = false;
          this.ratingMessage = 'An error occurred while submitting your rating';
          console.error('Rating error:', error);
        }
      });
  });
}
}
