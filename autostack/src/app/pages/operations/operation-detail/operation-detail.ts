import { Component, inject, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Subject, Observable, takeUntil } from 'rxjs';
import { OperationStatus } from '../../../services/operations/operations-service';
import { OperationsFacade } from '../../../state/operations/operations.facade';
import { Operation } from '../../../state/operations/operations.models';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-operation-detail',
  imports: [CommonModule, ],
  templateUrl: './operation-detail.html',
  styleUrl: './operation-detail.scss'
})
export class OperationDetail implements OnInit, OnDestroy{
private route = inject(ActivatedRoute);
  private router = inject(Router);
  private facade = inject(OperationsFacade);
  private destroy$ = new Subject<void>();

  operation$!: Observable<Operation | undefined>;
  operationId!: string;

  ngOnInit(): void {
    this.route.params.pipe(takeUntil(this.destroy$)).subscribe(params => {
      this.operationId = params['operationsId'];
      this.operation$ = this.facade.getOperationById(this.operationId);
    });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  goBack(): void {
    this.router.navigate(['../'], { relativeTo: this.route });
  }

  removeOperation(id: string): void {
    this.facade.removeOperation(id);
    this.goBack();
  }

  getStatusClass(status: OperationStatus): string {
    const classes: Record<OperationStatus, string> = {
      [OperationStatus.QUEUED]: 'bg-gray-100 text-gray-800',
      [OperationStatus.VALIDATING]: 'bg-blue-100 text-blue-800',
      [OperationStatus.CREATING_PROJECT]: 'bg-blue-100 text-blue-800',
      [OperationStatus.CREATING_TECHNOLOGIES]: 'bg-blue-100 text-blue-800',
      [OperationStatus.CREATING_COMPONENTS]: 'bg-blue-100 text-blue-800',
      [OperationStatus.CREATING_CONNECTIONS]: 'bg-blue-100 text-blue-800',
      [OperationStatus.DELETING_PROJECT]: 'bg-orange-100 text-orange-800',
      [OperationStatus.FINALIZING]: 'bg-blue-100 text-blue-800',
      [OperationStatus.COMPLETED]: 'bg-green-100 text-green-800',
      [OperationStatus.FAILED]: 'bg-red-100 text-red-800'
    };
    return classes[status] || 'bg-gray-100 text-gray-800';
  }

  getStatusLabel(status: OperationStatus): string {
    return status.replace(/_/g, ' ').toLowerCase()
      .replace(/\b\w/g, c => c.toUpperCase());
  }

  getProgressBarClass(status: OperationStatus): string {
    if (status === OperationStatus.COMPLETED) {
      return 'bg-green-600';
    } else if (status === OperationStatus.FAILED) {
      return 'bg-red-600';
    }
    return 'bg-blue-600';
  }

  formatTimestamp(timestamp: Date): string {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  }

  hasMetadata(metadata: any): boolean {
    if (!metadata) return false;
    const keys = Object.keys(metadata);
    return keys.length > 0 && keys.some(key => key !== 'projectName' && metadata[key] != null);
  }

  getMetadataKeys(metadata: any): string[] {
    if (!metadata) return [];
    return Object.keys(metadata).filter(key => key !== 'projectName' && metadata[key] != null);
  }

  formatKey(key: string): string {
    return key.replace(/([A-Z])/g, ' $1')
      .replace(/^./, str => str.toUpperCase())
      .trim();
  }

  isStatusReached(currentStatus: OperationStatus, checkStatus: string): boolean {
    const statusOrder = [
      'QUEUED',
      'VALIDATING',
      'CREATING_PROJECT',
      'CREATING_TECHNOLOGIES',
      'CREATING_COMPONENTS',
      'CREATING_CONNECTIONS',
      'FINALIZING',
      'COMPLETED',
      'FAILED'
    ];
    
    const currentIndex = statusOrder.indexOf(currentStatus);
    const checkIndex = statusOrder.indexOf(checkStatus);
    
    return currentIndex >= checkIndex || currentStatus === OperationStatus.COMPLETED || currentStatus === OperationStatus.FAILED;
  }
}
