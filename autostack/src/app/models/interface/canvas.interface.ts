import { ComponentType } from "../enum/component.enum";
import { IPosition } from "./position.interface";

export interface ICanvasEvent {
  type: CanvasEventType;
  payload?: any;
  timestamp: Date;
}

export enum CanvasEventType {
  COMPONENT_ADDED = 'component_added',
  COMPONENT_REMOVED = 'component_removed',
  COMPONENT_MOVED = 'component_moved',
  COMPONENT_RESIZED = 'component_resized',
  COMPONENT_SELECTED = 'component_selected',
  CONNECTION_CREATED = 'connection_created',
  CONNECTION_REMOVED = 'connection_removed',
  CONNECTION_MODIFIED = 'connection_modified',
  CANVAS_ZOOMED = 'canvas_zoomed',
  CANVAS_PANNED = 'canvas_panned'
}

export interface IDragData {
  type: 'component' | 'connection';
  componentType?: ComponentType;
  componentId?: string;
  connectionId?: string;
}

export interface IDropResult {
  success: boolean;
  position?: IPosition;
  error?: string;
}

export interface SelectionState {
  selectedComponents: string[];
  selectedConnections: string[];
  multiSelect: boolean;
  selectionBox?: SelectionBox;
}

export interface SelectionBox {
  start: IPosition;
  end: IPosition;
  active: boolean;
}

export interface UndoRedoAction {
  id: string;
  type: ActionType;
  timestamp: Date;
  description: string;
  previousState: any;
  newState: any;
}

export enum ActionType {
  ADD_COMPONENT = 'add_component',
  REMOVE_COMPONENT = 'remove_component',
  MOVE_COMPONENT = 'move_component',
  RESIZE_COMPONENT = 'resize_component',
  MODIFY_COMPONENT = 'modify_component',
  ADD_CONNECTION = 'add_connection',
  REMOVE_CONNECTION = 'remove_connection',
  MODIFY_CONNECTION = 'modify_connection',
  BATCH_ACTION = 'batch_action'
}