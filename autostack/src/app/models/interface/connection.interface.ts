import { ConnectionType } from "../enum/connection.enum";

export interface IComponentConnection {
  id: string;
  sourceId: string;
  targetId: string;
  sourceAnchor: IConnectionAnchor;
  targetAnchor: IConnectionAnchor;
  type: ConnectionType;
  label?: string;
  properties: IConnectionProperties;
  style: IConnectionStyle;
}

export interface IConnectionAnchor {
  side: 'top' | 'right' | 'bottom' | 'left';
  offset: number; // 0-1, percentage along the side
}

export interface IConnectionProperties {
  description?: string;
  protocol?: string;
  dataFormat?: string;
  frequency?: string;
  isSecure?: boolean;
  customProperties?: { [key: string]: any };
}

export interface IConnectionStyle {
  color?: string;
  strokeWidth?: number;
  strokeStyle?: 'solid' | 'dashed' | 'dotted';
  arrowStyle?: 'simple' | 'filled' | 'diamond';
}