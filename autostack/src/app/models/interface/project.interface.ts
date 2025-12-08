import { IArchitectureComponent } from "./architecture.interface";
import { IComponentConnection } from "./connection.interface";
import { IPosition } from "./position.interface";

export interface IArchitectureProject {
  id: string;
  name: string;
  description?: string;
  version: string;
  metadata: IProjectMetadata;
  components: IArchitectureComponent[];
  connections: IComponentConnection[];
  canvas: CanvasSettings;
}

export interface IProjectMetadata {
  created: Date;
  lastModified: Date;
  author?: string;
  tags?: string[];
  category?: string;
}

export interface ICanvasSettings {
  zoom: number;
  pan: IPosition;
  gridEnabled: boolean;
  gridSize: number;
  snapToGrid: boolean;
  backgroundColor?: string;
}
