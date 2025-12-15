import { CommonModule } from '@angular/common';
import {
  Component,
  EventEmitter,
  inject,
  Input,
  OnDestroy,
  OnInit,
  Output,
} from '@angular/core';
import { SidePane } from '../side-pane/side-pane';
import { Subject } from 'rxjs';
import { Router } from '@angular/router';
import { OperationsFacade } from '../../state/operations/operations.facade';

@Component({
  selector: 'app-notifications-pane',
  imports: [SidePane, CommonModule],
  templateUrl: './notifications-pane.html',
  styleUrl: './notifications-pane.scss',
})
export class NotificationsPane implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>();
  private facade = inject(OperationsFacade);
  private router = inject(Router);

  @Input() isOpen = false;
  @Output() closeModal = new EventEmitter<void>();

  activeOperations$ = this.facade.activeOperations$;
  completedOperations$ = this.facade.completedOperations$;
  failedOperations$ = this.facade.failedOperations$;
  activeOperationsCount$ = this.facade.activeOperationsCount$;
  recentOperations$ = this.facade.recentOperations$;

  ngOnInit(): void {}
  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  onClose(): void {
    this.closeModal.emit();
  }

  viewDetails(operationId: string): void {
    this.router.navigate(['/operations', operationId]);
    this.onClose();
  }

  goToProject(projectId: string, event: Event): void {
    event.stopPropagation();
    this.router.navigate(['/project', projectId]);
    this.onClose();
  }

  removeOperation(operationId: string, event: Event): void {
    event.stopPropagation();
    this.facade.removeOperation(operationId);
  }

  clearCompleted(): void {
    this.facade.clearCompleted();
  }

  getOperationTypeLabel(type: string): string {
    return type
      .replace('_', ' ')
      .toLowerCase()
      .split(' ')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }

  getTimeAgo(timestamp: Date): string {
    const seconds = Math.floor(
      (new Date().getTime() - new Date(timestamp).getTime()) / 1000
    );

    if (seconds < 60) return 'Just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
  }
}
