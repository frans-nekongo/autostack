import { CommonModule } from '@angular/common';
import { Component, inject } from '@angular/core';
import { FormGroup, FormsModule } from '@angular/forms';
import { NgIcon, provideIcons } from '@ng-icons/core';
import { heroPaperAirplane } from '@ng-icons/heroicons/outline';
import { Apollo, gql } from 'apollo-angular';
import { Subject, takeUntil } from 'rxjs';
import { AiService, JobStatus } from '../../../services/ai/ai-service';
import { NotificationService } from '../../../services/notification/notification-service';

@Component({
  selector: 'app-create-project',
  imports: [CommonModule, FormsModule, NgIcon],
  templateUrl: './create-project.html',
  styleUrl: './create-project.scss',
  providers: [provideIcons({ heroPaperAirplane })],
})
export class CreateProject {
  prompt: string = '';
  private apollo = inject(Apollo);
  aiForm!: FormGroup;
  private destroy$ = new Subject<void>();
  private aiService = inject(AiService);
  private notificationService = inject(NotificationService);

  handleSubmit(): void {
    if (this.prompt.trim()) {
      console.log('Submitted prompt:', this.prompt);
      this.aiService
        .createProjectDescription(this.prompt)
        .pipe(takeUntil(this.destroy$))
        .subscribe({
          next: (jobCreated) => {
            console.log('Job Created: ', jobCreated.jobId);

            const subscription = this.aiService
              .subscribeToJob(jobCreated.jobId)
              .pipe(takeUntil(this.destroy$))
              .subscribe({
                next: (jobResult) => {
                  console.log(jobResult);

                  if (
                    jobResult.status === JobStatus.COMPLETED ||
                    jobResult.status === JobStatus.FAILED
                  ) {
                    this.notificationService.notifyJobComplete(jobResult);
                    this.notificationService.untrackJob(jobCreated.jobId);
                  }
                },
                error: (error) => {
                  console.error(error);
                  this.notificationService.addNotification({
                    id: jobCreated.jobId,
                    title: 'Subscription Error',
                    message: 'Failed to monitor job progress',
                    type: 'error',
                    timestamp: new Date(),
                  });
                },
              });

            this.notificationService.trackJob(jobCreated.jobId, subscription);
            this.notificationService.addNotification({
              id: jobCreated.jobId,
              title: 'Job Started',
              message:
                'Your project description is being generated in the background.',
              type: 'info',
              timestamp: new Date(),
            });
          },
          error: (error) => {
            console.error('Error creating job:', error);
            this.notificationService.addNotification({
              id: 'error',
              title: 'Error',
              message: 'Failed to create job. Please try again.',
              type: 'error',
              timestamp: new Date(),
            });
          },
        });
      this.prompt = '';
    }
  }

  handleKeyDown(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.handleSubmit();
    }
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
