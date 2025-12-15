import { createFeatureSelector, createSelector } from '@ngrx/store';
import { OPERATIONS_FEATURE_KEY } from './operations.reducer';
import { IOperationsState, Operation } from './operations.models';
import { OperationStatus } from '../../services/operations/operations-service';

export const selectOperationsState = 
  createFeatureSelector<IOperationsState>(OPERATIONS_FEATURE_KEY);

// All operations
export const selectAllOperations = createSelector(
  selectOperationsState,
  state => state.operations
);

// Active operations (in progress)
export const selectActiveOperations = createSelector(
  selectAllOperations,
  operations => operations.filter(op => 
    op.status !== OperationStatus.COMPLETED &&
    op.status !== OperationStatus.FAILED
  )
);

// Completed operations
export const selectCompletedOperations = createSelector(
  selectAllOperations,
  operations => operations.filter(op => 
    op.status === OperationStatus.COMPLETED
  )
);

// Failed operations
export const selectFailedOperations = createSelector(
  selectAllOperations,
  operations => operations.filter(op => 
    op.status === OperationStatus.FAILED
  )
);

// Count of active operations
export const selectActiveOperationsCount = createSelector(
  selectActiveOperations,
  operations => operations.length
);

// Selected operation
export const selectSelectedOperationId = createSelector(
  selectOperationsState,
  state => state.selectedOperationId
);

export const selectSelectedOperation = createSelector(
  selectAllOperations,
  selectSelectedOperationId,
  (operations, selectedId) => 
    selectedId ? operations.find(op => op.id === selectedId) : null
);

// Get operation by ID
export const selectOperationById = (operationId: string) =>
  createSelector(
    selectAllOperations,
    operations => operations.find(op => op.id === operationId)
  );

// Has active operations
export const selectHasActiveOperations = createSelector(
  selectActiveOperationsCount,
  count => count > 0
);

// Recent operations (last 10)
export const selectRecentOperations = createSelector(
  selectAllOperations,
  operations => [...operations]
    .sort((a, b) => {
      const timeA = typeof a.timestamp === 'number' ? a.timestamp : new Date(a.timestamp).getTime();
      const timeB = typeof b.timestamp === 'number' ? b.timestamp : new Date(b.timestamp).getTime();
      return timeB - timeA;
    })
    .slice(0, 10)
);