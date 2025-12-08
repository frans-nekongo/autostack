import { ComponentType } from "../enum/component.enum";
import { IComponentProperties } from "./architecture.interface";
import { ISize } from "./position.interface";

export interface IComponentTemplate {
  type: ComponentType;
  defaultName: string;
  icon: string;
  color: string;
  defaultSize: ISize;
  defaultProperties: IComponentProperties;
  description: string;
  category: ComponentCategory;
}

export enum ComponentCategory {
  DATA = 'data',
  COMPUTE = 'compute',
  NETWORK = 'network',
  STORAGE = 'storage',
  SECURITY = 'security',
  INTEGRATION = 'integration',
  FRONTEND = 'frontend'
}