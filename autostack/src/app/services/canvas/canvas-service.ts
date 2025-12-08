import { inject, Injectable } from '@angular/core';
import { BehaviorSubject, Observable } from 'rxjs';
import {
  IArchitectureComponent,
  IPosition,
  ICanvasSettings,
  ComponentType,
  IComponentTemplate,
  IDragData,
  IDropResult,
  SelectionState,
  ISize,
} from '../../models';
import { ComponentTemplateService } from '../component/component-template-service';
import { v4 as uuidv4 } from 'uuid';

@Injectable({
  providedIn: 'root',
})
export class CanvasService {
  private componentsSubject = new BehaviorSubject<IArchitectureComponent[]>([]);
  private componentTemplateService = inject(ComponentTemplateService);

  components$: Observable<IArchitectureComponent[]> =
    this.componentsSubject.asObservable();

  private settingsSubject = new BehaviorSubject<ICanvasSettings>({
    zoom: 1,
    pan: { x: 0, y: 0 },
    gridEnabled: true,
    gridSize: 20,
    snapToGrid: true,
    backgroundColor: '#f5f5f5',
  });
  settings$: Observable<ICanvasSettings> = this.settingsSubject.asObservable();

  private selectionSubject = new BehaviorSubject<SelectionState>({
    selectedComponents: [],
    selectedConnections: [],
    multiSelect: false,
    selectionBox: undefined,
  });

  selection$: Observable<SelectionState> = this.selectionSubject.asObservable();

  addComponent(dragData: IDragData, position: IPosition): IDropResult {
    if (!dragData.componentType) {
      return { success: false, error: 'No component type provided' };
    }

    const template = this.componentTemplateService.getTemplate(dragData.componentType);
    if (!template) {
      return { success: false, error: 'Invalid component type' };
    }

    const snappedPosition = this.snapToGrid(position);
    const component: IArchitectureComponent = {
      id: uuidv4(),
      type: template.type,
      name: template.defaultName,
      position: snappedPosition,
      size: template.defaultSize,
      properties: { ...template.defaultProperties },
      metadata: {
        created: new Date(),
        lastModified: new Date(),
        color: template.color,
        icon: template.icon,
        zIndex: this.componentsSubject.value.length,
      },
    };

    const currentComponents = this.componentsSubject.value;
    this.componentsSubject.next([...currentComponents, component]);
    return { success: true, position: snappedPosition };
  }

  updateComponentPosition(id: string, position: IPosition): void {
    const components = this.componentsSubject.value;
    const component = components.find((c) => c.id === id);
    if (component) {
      component.position = this.snapToGrid(position);
      component.metadata.lastModified = new Date();
      this.componentsSubject.next([...components]);
    }
  }

  updateComponentSize(id: string, size: ISize): void {
    const components = this.componentsSubject.value;
    const component = components.find((c) => c.id === id);
    if (component) {
      component.size = {
        width:
          Math.round(size.width / this.settingsSubject.value.gridSize) *
          this.settingsSubject.value.gridSize,
        height:
          Math.round(size.height / this.settingsSubject.value.gridSize) *
          this.settingsSubject.value.gridSize,
      };
      component.metadata.lastModified = new Date();
      this.componentsSubject.next([...components]);
    }
  }

  deleteComponent(id: string): void {
    const components = this.componentsSubject.value.filter((c) => c.id !== id);
    this.componentsSubject.next(components);
    const selection = this.selectionSubject.value;
    selection.selectedComponents = selection.selectedComponents.filter(
      (c) => c !== id
    );
    this.selectionSubject.next({ ...selection });
  }

  duplicateComponent(id: string): void {
    const components = this.componentsSubject.value;
    const component = components.find((c) => c.id === id);
    if (component) {
      const newComponent: IArchitectureComponent = {
        ...component,
        id: uuidv4(),
        position: {
          x: component.position.x + 20,
          y: component.position.y + 20,
        },
        metadata: {
          ...component.metadata,
          created: new Date(),
          lastModified: new Date(),
          zIndex: components.length,
        },
      };
      this.componentsSubject.next([...components, newComponent]);
      this.selectComponent(newComponent.id);
    }
  }

  selectComponent(id: string, multiSelect: boolean = false): void {
    const currentSelection = this.selectionSubject.value;
    if (!multiSelect) {
      currentSelection.selectedComponents = [id];
    } else {
      if (!currentSelection.selectedComponents.includes(id)) {
        currentSelection.selectedComponents.push(id);
      }
    }
    this.selectionSubject.next({ ...currentSelection, multiSelect });
  }

  deselectAll(): void {
    this.selectionSubject.next({
      selectedComponents: [],
      selectedConnections: [],
      multiSelect: false,
      selectionBox: undefined,
    });
  }

  updateZoom(zoom: number): void {
    const settings = this.settingsSubject.value;
    const newZoom = Math.max(0.5, Math.min(2, zoom));
    this.settingsSubject.next({ ...settings, zoom: newZoom });
  }

  updatePan(pan: IPosition): void {
    const settings = this.settingsSubject.value;
    this.settingsSubject.next({ ...settings, pan });
  }

  toggleGrid(): void {
    const settings = this.settingsSubject.value;
    this.settingsSubject.next({
      ...settings,
      gridEnabled: !settings.gridEnabled,
    });
  }

  private snapToGrid(position: IPosition): IPosition {
    const settings = this.settingsSubject.value;
    if (!settings.snapToGrid) return position;

    const gridSize = settings.gridSize;
    return {
      x: Math.round(position.x / gridSize) * gridSize,
      y: Math.round(position.y / gridSize) * gridSize,
    };
  }
}
