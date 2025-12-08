import { Component, inject, OnInit } from '@angular/core';
import { ComponentCategory, IComponentTemplate, IDragData } from '../../models';
import { ComponentTemplateService } from '../../services/component/component-template-service';
import { CdkDragStart, CdkDragEnd, DragDropModule } from '@angular/cdk/drag-drop';

@Component({
  selector: 'app-component-menu',
  imports: [DragDropModule],
  templateUrl: './component-menu.html',
  styleUrl: './component-menu.scss'
})
export class ComponentMenu implements OnInit{
  private componentTemplateService: ComponentTemplateService = inject(ComponentTemplateService);

  templates: IComponentTemplate[] = [];
  categories = Object.values(ComponentCategory);
  activeCategory: ComponentCategory = ComponentCategory.COMPUTE;
  isCollapsed = false;
  dragPreview: IComponentTemplate | null = null;
  
  ngOnInit(): void {
    this.templates = this.componentTemplateService.getTemplates();
  }

  getTemplatesForCategory(category: ComponentCategory): IComponentTemplate[] {
    return this.templates.filter(template => template.category === category);
  }

  setActiveCategory(category: ComponentCategory): void {
    this.activeCategory = category;
  }

  onDragStarted(event: CdkDragStart, template: IComponentTemplate): void {
    this.dragPreview = template;
    
    // Set drag data for the canvas to consume
    const dragData: IDragData = {
      type: 'component',
      componentType: template.type
    };
    
    // Store drag data globally for canvas access
    (window as any).architectureDragData = dragData;
    
    // Add visual feedback
    document.body.classList.add('dragging-component');
  }

  onDragEnded(event: CdkDragEnd): void {
    this.dragPreview = null;
    document.body.classList.remove('dragging-component');
    
    // Clean up drag data
    delete (window as any).architectureDragData;
  }

  toggleCollapse(): void {
    this.isCollapsed = !this.isCollapsed;
  }

  getCategoryDisplayName(category: ComponentCategory): string {
    const displayNames: Record<ComponentCategory, string> = {
      [ComponentCategory.DATA]: 'Data',
      [ComponentCategory.COMPUTE]: 'Compute',
      [ComponentCategory.NETWORK]: 'Network',
      [ComponentCategory.STORAGE]: 'Storage',
      [ComponentCategory.SECURITY]: 'Security',
      [ComponentCategory.INTEGRATION]: 'Integration',
      [ComponentCategory.FRONTEND]: 'Frontend'
    };
    return displayNames[category];
  }

  getCategoryIcon(category: ComponentCategory): string {
    const icons: Record<ComponentCategory, string> = {
      [ComponentCategory.DATA]: 'database',
      [ComponentCategory.COMPUTE]: 'cpu',
      [ComponentCategory.NETWORK]: 'globe',
      [ComponentCategory.STORAGE]: 'hard-drive',
      [ComponentCategory.SECURITY]: 'shield',
      [ComponentCategory.INTEGRATION]: 'link',
      [ComponentCategory.FRONTEND]: 'monitor'
    };
    return icons[category];
  }
}
