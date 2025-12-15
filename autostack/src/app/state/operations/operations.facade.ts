import { Injectable, inject } from '@angular/core';
import { Store } from '@ngrx/store';
import { OperationsActions } from './operations.actions';
import * as OperationsSelectors from './operations.selectors';
import { OperationsService } from '../../services/operations/operations-service';

@Injectable({
  providedIn: 'root'
})
export class OperationsFacade {
  private store = inject(Store);
  private operationsService = inject(OperationsService);

  // Selectors
  allOperations$ = this.store.select(OperationsSelectors.selectAllOperations);
  activeOperations$ = this.store.select(OperationsSelectors.selectActiveOperations);
  completedOperations$ = this.store.select(OperationsSelectors.selectCompletedOperations);
  failedOperations$ = this.store.select(OperationsSelectors.selectFailedOperations);
  activeOperationsCount$ = this.store.select(OperationsSelectors.selectActiveOperationsCount);
  hasActiveOperations$ = this.store.select(OperationsSelectors.selectHasActiveOperations);
  recentOperations$ = this.store.select(OperationsSelectors.selectRecentOperations);
  selectedOperation$ = this.store.select(OperationsSelectors.selectSelectedOperation);

  /**
   * Create a project with progress tracking
   */
  createProjectWithTracking(schema: any, chatId: string): void {
    this.operationsService
      .createProjectWithProgress(schema, chatId)
      .subscribe({
        next: update => {
          // Dispatch each update to the store
          this.store.dispatch(OperationsActions.operationUpdate({ update }));
        },
        error: err => {
          console.error('Operation error:', err);
        }
      });
  }

  /**
   * Start tracking an existing operation
   */
  trackOperation(operationId: string): void {
    this.store.dispatch(
      OperationsActions.startOperation({
        operationId,
        operationType: 'PROJECT_CREATION'
      })
    );

    this.operationsService.subscribeToOperation(operationId).subscribe({
      next: update => {
        this.store.dispatch(OperationsActions.operationUpdate({ update }));
      },
      error: err => {
        this.store.dispatch(
          OperationsActions.operationError({
            operationId,
            error: err.message
          })
        );
      }
    });
  }

  /**
   * Select an operation to view details
   */
  selectOperation(operationId: string): void {
    this.store.dispatch(OperationsActions.selectOperation({ operationId }));
  }

  /**
   * Clear selected operation
   */
  clearSelection(): void {
    this.store.dispatch(OperationsActions.clearSelection());
  }

  /**
   * Remove an operation from the list
   */
  removeOperation(operationId: string): void {
    this.store.dispatch(OperationsActions.removeOperation({ operationId }));
  }

  /**
   * Clear all completed operations
   */
  clearCompleted(): void {
    this.store.dispatch(OperationsActions.clearCompletedOperations());
  }

  /**
   * Get specific operation by ID
   */
  getOperationById(operationId: string) {
    return this.store.select(OperationsSelectors.selectOperationById(operationId));
  }
}