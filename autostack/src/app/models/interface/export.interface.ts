import { IArchitectureProject } from "./project.interface";

export interface IExportOptions {
  format: 'yaml' | 'json' | 'xml';
  includeMetadata: boolean;
  includePositions: boolean;
  prettyFormat: boolean;
  customFields?: string[];
}

export interface IImportResult {
  success: boolean;
  project?: IArchitectureProject;
  errors?: string[];
  warnings?: string[];
}