import { createReducer, on } from '@ngrx/store';
import { OperationsActions } from './operations.actions';
import { IOperationsState, initialOperationsState, Operation } from './operations.models';
import { OperationStatus } from '../../services/operations/operations-service';

export const OPERATIONS_FEATURE_KEY = 'operations';

const reducer = createReducer(
  initialOperationsState,

  // Start Operation
  on(OperationsActions.startOperation, (state, { operationId, type, metadata }) => {
    const newOperation: Operation = {
      id: operationId,
      type: type as any,
      status: OperationStatus.QUEUED,
      message: 'Operation queued',
      progress: 0,
      timestamp: new Date(),
      metadata
    };

    return {
      ...state,
      operations: [...state.operations, newOperation],
      activeOperationIds: [...state.activeOperationIds, operationId]
    };
  }),

  // Operation Update
  on(OperationsActions.operationUpdate, (state, { update }) => {
    const existingOp = state.operations.find(op => op.id === update.operationId);
    
    if (!existingOp) {
      // Create new operation if it doesn't exist
      const newOperation: Operation = {
        id: update.operationId,
        type: 'PROJECT_CREATION',
        status: update.status,
        message: update.message,
        progress: update.progress,
        projectId: update.projectId,
        error: update.error,
        timestamp: new Date()
      };

      return {
        ...state,
        operations: [...state.operations, newOperation],
        activeOperationIds: update.status === OperationStatus.COMPLETED || 
                           update.status === OperationStatus.FAILED
          ? state.activeOperationIds
          : [...state.activeOperationIds, update.operationId]
      };
    }

    // Update existing operation
    const updatedOperations = state.operations.map(op =>
      op.id === update.operationId
        ? {
            ...op,
            status: update.status,
            message: update.message,
            progress: update.progress,
            projectId: update.projectId || op.projectId,
            error: update.error,
            timestamp: new Date()
          }
        : op
    );

    // Remove from active if completed/failed
    const updatedActiveIds = 
      update.status === OperationStatus.COMPLETED || 
      update.status === OperationStatus.FAILED
        ? state.activeOperationIds.filter(id => id !== update.operationId)
        : state.activeOperationIds;

    return {
      ...state,
      operations: updatedOperations,
      activeOperationIds: updatedActiveIds
    };
  }),

  // Select Operation
  on(OperationsActions.selectOperation, (state, { operationId }) => ({
    ...state,
    selectedOperationId: operationId
  })),

  // Clear Selection
  on(OperationsActions.clearSelection, state => ({
    ...state,
    selectedOperationId: null
  })),

  // Remove Operation
  on(OperationsActions.removeOperation, (state, { operationId }) => ({
    ...state,
    operations: state.operations.filter(op => op.id !== operationId),
    activeOperationIds: state.activeOperationIds.filter(id => id !== operationId),
    selectedOperationId: state.selectedOperationId === operationId 
      ? null 
      : state.selectedOperationId
  })),

  // Clear Completed
  on(OperationsActions.clearCompletedOperations, state => ({
    ...state,
    operations: state.operations.filter(
      op => op.status !== OperationStatus.COMPLETED && 
            op.status !== OperationStatus.FAILED
    )
  })),

  // Error
  on(OperationsActions.operationError, (state, { operationId, error }) => ({
    ...state,
    operations: state.operations.map(op =>
      op.id === operationId
        ? { ...op, error, status: OperationStatus.FAILED }
        : op
    ),
    activeOperationIds: state.activeOperationIds.filter(id => id !== operationId)
  }))
);

export function operationsReducer(state: IOperationsState | undefined, action: any) {
  return reducer(state, action);
}