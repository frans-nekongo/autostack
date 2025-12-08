import { Component, inject, OnInit } from '@angular/core';
import { CanvasService } from '../../services/canvas/canvas-service';
import { Subject, takeUntil } from 'rxjs';
import {
  ComponentType,
  IArchitectureComponent,
  ICanvasSettings,
  IDragData,
  IPosition,
  ISize,
  SelectionState,
} from '../../models';
import { CdkDragDrop, CdkDragEnd, CdkDragStart } from '@angular/cdk/drag-drop';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-architecture-canvas',
  imports: [CommonModule],
  templateUrl: './architecture-canvas.html',
  styleUrl: './architecture-canvas.scss',
})
export class ArchitectureCanvas implements OnInit {
  private canvasService: CanvasService = inject(CanvasService);
  private destroy$ = new Subject<void>();
  ComponentType = ComponentType
  components: IArchitectureComponent[] = [];
  settings: ICanvasSettings = {
    zoom: 1,
    pan: { x: 0, y: 0 },
    gridEnabled: true,
    gridSize: 20,
    snapToGrid: true,
    backgroundColor: '#f5f5f5',
  };
  selection: SelectionState = {
    selectedComponents: [],
    selectedConnections: [],
    multiSelect: false,
  };

  contextMenu: { x: number; y: number; componentId?: string } | null = null;
  isDragging = false;
  isPanning = false;
  isResizing = false;
  resizeHandle: string | null = null;
  lastMousePosition: IPosition | null = null;
  resizingComponent: IArchitectureComponent | null = null;

  ngOnInit(): void {
    this.canvasService.components$
      .pipe(takeUntil(this.destroy$))
      .subscribe((components) => (this.components = components));
    this.canvasService.settings$
      .pipe(takeUntil(this.destroy$))
      .subscribe((settings) => (this.settings = settings));
    this.canvasService.selection$
      .pipe(takeUntil(this.destroy$))
      .subscribe((selection) => (this.selection = selection));

    // Prevent default context menu
    window.addEventListener('contextmenu', this.handleContextMenu.bind(this));
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
    window.removeEventListener(
      'contextmenu',
      this.handleContextMenu.bind(this)
    );
  }

  onDrop(event: any): void {
    const dragData: IDragData = (window as any).architectureDragData;
    if (!dragData || dragData.type !== 'component') return;

    const canvasRect = (
      event.container.element.nativeElement as HTMLElement
    ).getBoundingClientRect();
    const dropPoint: IPosition = {
      x:
        (event.dropPoint.x - canvasRect.left - this.settings.pan.x) /
        this.settings.zoom,
      y:
        (event.dropPoint.y - canvasRect.top - this.settings.pan.y) /
        this.settings.zoom,
    };

    this.canvasService.addComponent(dragData, dropPoint);
  }

  onComponentDragStarted(component: IArchitectureComponent): void {
    this.isDragging = true;
    this.closeContextMenu();
  }

  onComponentDragEnded(component: IArchitectureComponent, event: any): void {
    this.isDragging = false;
    const newPosition: IPosition = {
      x: event.dropPoint.x / this.settings.zoom - this.settings.pan.x,
      y: event.dropPoint.y / this.settings.zoom - this.settings.pan.y,
    };
    this.canvasService.updateComponentPosition(component.id, newPosition);
  }

  onCanvasMouseDown(event: MouseEvent): void {
    if (event.button === 2 || event.altKey) {
      // Right-click or Alt for panning
      this.isPanning = true;
      this.lastMousePosition = { x: event.clientX, y: event.clientY };
      this.closeContextMenu();
    } else if (!this.isDragging && !this.isResizing) {
      this.canvasService.deselectAll();
      this.closeContextMenu();
    }
  }

  onCanvasMouseMove(event: MouseEvent): void {
    if (this.isPanning && this.lastMousePosition) {
      const deltaX = event.clientX - this.lastMousePosition.x;
      const deltaY = event.clientY - this.lastMousePosition.y;
      const newPan: IPosition = {
        x: this.settings.pan.x + deltaX / this.settings.zoom,
        y: this.settings.pan.y + deltaY / this.settings.zoom,
      };
      this.canvasService.updatePan(newPan);
      this.lastMousePosition = { x: event.clientX, y: event.clientY };
    } else if (
      this.isResizing &&
      this.resizingComponent &&
      this.lastMousePosition
    ) {
      this.handleResize(event);
    }
  }

  onCanvasMouseUp(): void {
    this.isPanning = false;
    this.isResizing = false;
    this.resizingComponent = null;
    this.resizeHandle = null;
    this.lastMousePosition = null;
  }

  onCanvasWheel(event: WheelEvent): void {
    event.preventDefault();
    const zoomDelta = event.deltaY > 0 ? -0.1 : 0.1;
    this.canvasService.updateZoom(this.settings.zoom + zoomDelta);
  }

  onComponentClick(component: IArchitectureComponent, event: MouseEvent): void {
    event.stopPropagation();
    this.canvasService.selectComponent(
      component.id,
      event.ctrlKey || event.metaKey
    );
    this.closeContextMenu();
  }

  onResizeMouseDown(
    event: MouseEvent,
    component: IArchitectureComponent,
    handle: string
  ): void {
    event.stopPropagation();
    this.isResizing = true;
    this.resizingComponent = component;
    this.resizeHandle = handle;
    this.lastMousePosition = { x: event.clientX, y: event.clientY };
    this.canvasService.selectComponent(component.id);
  }

  handleResize(event: MouseEvent): void {
    if (
      !this.resizingComponent ||
      !this.resizeHandle ||
      !this.lastMousePosition
    )
      return;

    const deltaX =
      (event.clientX - this.lastMousePosition.x) / this.settings.zoom;
    const deltaY =
      (event.clientY - this.lastMousePosition.y) / this.settings.zoom;
    const newSize: ISize = { ...this.resizingComponent.size };
    let newPosition: IPosition = { ...this.resizingComponent.position };

    switch (this.resizeHandle) {
      case 'se':
        newSize.width = Math.max(50, newSize.width + deltaX);
        newSize.height = Math.max(50, newSize.height + deltaY);
        break;
      case 'sw':
        newSize.width = Math.max(50, newSize.width - deltaX);
        newPosition.x += deltaX;
        newSize.height = Math.max(50, newSize.height + deltaY);
        break;
      case 'ne':
        newSize.width = Math.max(50, newSize.width + deltaX);
        newSize.height = Math.max(50, newSize.height - deltaY);
        newPosition.y += deltaY;
        break;
      case 'nw':
        newSize.width = Math.max(50, newSize.width - deltaX);
        newSize.height = Math.max(50, newSize.height - deltaY);
        newPosition.x += deltaX;
        newPosition.y += deltaY;
        break;
    }

    this.canvasService.updateComponentSize(this.resizingComponent.id, newSize);
    this.canvasService.updateComponentPosition(
      this.resizingComponent.id,
      this.snapToGrid(newPosition)
    );
    this.lastMousePosition = { x: event.clientX, y: event.clientY };
  }

  handleContextMenu(event: MouseEvent): void {
    event.preventDefault();
    const canvasRect = (event.target as HTMLElement)
      .closest('.canvas-container')
      ?.getBoundingClientRect();
    if (!canvasRect) return;

    const component = this.components.find((comp) => {
      const rect = this.getComponentRect(comp);
      return (
        event.clientX >= rect.left &&
        event.clientX <= rect.right &&
        event.clientY >= rect.top &&
        event.clientY <= rect.bottom
      );
    });

    this.contextMenu = {
      x: event.clientX - canvasRect.left,
      y: event.clientY - canvasRect.top,
      componentId: component?.id,
    };
  }

  closeContextMenu(): void {
    this.contextMenu = null;
  }

  onContextMenuAction(action: string, componentId?: string): void {
    if (!componentId) return;
    switch (action) {
      case 'delete':
        this.canvasService.deleteComponent(componentId);
        break;
      case 'duplicate':
        this.canvasService.duplicateComponent(componentId);
        break;
    }
    this.closeContextMenu();
  }

  getComponentStyle(component: IArchitectureComponent): any {
    return {
      transform: `translate(${
        component.position.x * this.settings.zoom + this.settings.pan.x
      }px, 
                          ${
                            component.position.y * this.settings.zoom +
                            this.settings.pan.y
                          }px) 
                  scale(${this.settings.zoom})`,
      width: `${component.size.width}px`,
      height: `${component.size.height}px`,
      backgroundColor: component.metadata.color,
      border: this.selection.selectedComponents.includes(component.id)
        ? '2px solid #000'
        : '1px solid #666',
      borderRadius: this.getComponentBorderRadius(component.type),
    };
  }

  getComponentBorderRadius(type: ComponentType): string {
    switch (type) {
      case ComponentType.DATABASE:
        return '50%'; // Cylinder shape
      case ComponentType.API:
      case ComponentType.GATEWAY:
        return '8px'; // Slightly rounded
      default:
        return '4px'; // Standard rectangle
    }
  }

  getComponentRect(component: IArchitectureComponent): DOMRect {
    const x = component.position.x * this.settings.zoom + this.settings.pan.x;
    const y = component.position.y * this.settings.zoom + this.settings.pan.y;
    const width = component.size.width * this.settings.zoom;
    const height = component.size.height * this.settings.zoom;
    return new DOMRect(x, y, width, height);
  }

  snapToGrid(position: IPosition): IPosition {
    if (!this.settings.snapToGrid) return position;
    const gridSize = this.settings.gridSize;
    return {
      x: Math.round(position.x / gridSize) * gridSize,
      y: Math.round(position.y / gridSize) * gridSize,
    };
  }
}
