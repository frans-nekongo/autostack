import { createActionGroup, props, emptyProps } from '@ngrx/store';
import { Operation } from './operations.models';
import { OperationUpdate } from '../../services/operations/operations-service';

export const OperationsActions = createActionGroup({
  source: 'Operations',
  events: {
    // Start Operation
    'Start Operation': props<{
      operationId: string;
      operationType: string;
      metadata?: any;
    }>(),

    // Receive Update (from subscription)
    'Operation Update': props<{ update: OperationUpdate }>(),

    // Select Operation
    'Select Operation': props<{ operationId: string }>(),
    'Clear Selection': emptyProps(),

    // Remove Completed Operation
    'Remove Operation': props<{ operationId: string }>(),
    'Clear Completed Operations': emptyProps(),

    // Error
    'Operation Error': props<{ operationId: string; error: string }>()
  }
});