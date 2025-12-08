import { ComponentType } from "../enum/component.enum";
import { IPosition, ISize } from "./position.interface";

export interface IArchitectureComponent {
  id: string;
  type: ComponentType;
  name: string;
  position: IPosition;
  size: ISize;
  properties: IComponentProperties;
  metadata: IComponentMetadata;
}

export interface IComponentProperties {
  description?: string;
  technology?: string;
  version?: string;
  environment?: string;
  customProperties?: { [key: string]: any };
}

export interface IComponentMetadata {
  created: Date;
  lastModified: Date;
  color?: string;
  icon?: string;
  zIndex: number;
}