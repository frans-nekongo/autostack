export interface IValidationResult {
  isValid: boolean;
  errors: IValidationError[];
  warnings: IValidationWarning[];
}

export interface IValidationError {
  id: string;
  type: 'component' | 'connection' | 'project';
  elementId?: string;
  message: string;
  severity: 'error' | 'warning' | 'info';
}

export interface IValidationWarning {
  id: string;
  type: 'component' | 'connection' | 'project';
  elementId?: string;
  message: string;
  suggestion?: string;
}