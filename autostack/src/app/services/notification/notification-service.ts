import { inject, Injectable } from '@angular/core';
import { JobResult, JobStatus } from '../ai/ai-service';
import { Subject } from 'rxjs';
import { MatSnackBar } from '@angular/material/snack-bar';


export interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'success' | 'error' | 'info';
  timestamp: Date;
  jobResult?: JobResult;
}

@Injectable({
  providedIn: 'root'
})
export class NotificationService {
  private notificationsSubject = new Subject<Notification>();
  public notifications$ = this.notificationsSubject.asObservable();
  private activeJobs = new Map<string, any>();
  private snackBar = inject(MatSnackBar)

  addNotification(notification: Notification) {
    this.notificationsSubject.next(notification);
    
    // Show snackbar
    const config = {
      duration: 5000,
      horizontalPosition: 'right' as const,
      verticalPosition: 'top' as const,
      panelClass: [`snackbar-${notification.type}`]
    };

    this.snackBar.open(notification.message, 'View', config);
  }

  notifyJobComplete(jobResult: JobResult) {
    if (jobResult.status === JobStatus.COMPLETED) {
      this.addNotification({
        id: jobResult.id,
        title: 'Project Description Complete',
        message: 'Your project description has been generated successfully!',
        type: 'success',
        timestamp: new Date(),
        jobResult
      });
    } else if (jobResult.status === JobStatus.FAILED) {
      this.addNotification({
        id: jobResult.id,
        title: 'Project Description Failed',
        message: jobResult.error || 'An error occurred while processing your request.',
        type: 'error',
        timestamp: new Date(),
        jobResult
      });
    }
  }

  trackJob(jobId: string, subscription: any) {
    this.activeJobs.set(jobId, subscription);
  }

  untrackJob(jobId: string) {
    const subscription = this.activeJobs.get(jobId);
    if (subscription) {
      subscription.unsubscribe();
      this.activeJobs.delete(jobId);
    }
  }

  getActiveJobsCount(): number {
    return this.activeJobs.size;
  }
  
}
