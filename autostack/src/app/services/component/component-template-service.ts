import { Injectable } from '@angular/core';
import {
  ComponentCategory,
  ComponentType,
  IComponentTemplate,
} from '../../models';

@Injectable({
  providedIn: 'root',
})
export class ComponentTemplateService {
  private templates: IComponentTemplate[] = [
    {
      type: ComponentType.DATABASE,
      defaultName: 'Database',
      icon: 'database',
      color: '#3B82F6', // blue-500
      defaultSize: { width: 120, height: 80 },
      defaultProperties: {
        technology: 'PostgreSQL',
        description: 'Primary database',
      },
      description: 'Database storage system',
      category: ComponentCategory.DATA,
    },
    {
      type: ComponentType.CACHE,
      defaultName: 'Cache',
      icon: 'zap',
      color: '#F59E0B', // amber-500
      defaultSize: { width: 100, height: 70 },
      defaultProperties: {
        technology: 'Redis',
        description: 'Caching layer',
      },
      description: 'In-memory cache',
      category: ComponentCategory.DATA,
    },
    {
      type: ComponentType.FILE_STORAGE,
      defaultName: 'File Storage',
      icon: 'folder',
      color: '#10B981', // emerald-500
      defaultSize: { width: 110, height: 75 },
      defaultProperties: {
        technology: 'AWS S3',
        description: 'File storage system',
      },
      description: 'Object/File storage',
      category: ComponentCategory.STORAGE,
    },

    // Compute Components
    {
      type: ComponentType.API,
      defaultName: 'API',
      icon: 'globe',
      color: '#8B5CF6', // violet-500
      defaultSize: { width: 100, height: 70 },
      defaultProperties: {
        technology: 'REST API',
        description: 'API endpoint',
      },
      description: 'REST/GraphQL API',
      category: ComponentCategory.COMPUTE,
    },
    {
      type: ComponentType.SERVICE,
      defaultName: 'Service',
      icon: 'cpu',
      color: '#EF4444', // red-500
      defaultSize: { width: 110, height: 75 },
      defaultProperties: {
        technology: 'Node.js',
        description: 'Business logic service',
      },
      description: 'Backend service',
      category: ComponentCategory.COMPUTE,
    },
    {
      type: ComponentType.MICROSERVICE,
      defaultName: 'Microservice',
      icon: 'box',
      color: '#06B6D4', // cyan-500
      defaultSize: { width: 130, height: 80 },
      defaultProperties: {
        technology: 'Docker',
        description: 'Microservice container',
      },
      description: 'Containerized microservice',
      category: ComponentCategory.COMPUTE,
    },

    // Network Components
    {
      type: ComponentType.LOAD_BALANCER,
      defaultName: 'Load Balancer',
      icon: 'shuffle',
      color: '#F97316', // orange-500
      defaultSize: { width: 130, height: 70 },
      defaultProperties: {
        technology: 'NGINX',
        description: 'Load balancing',
      },
      description: 'Traffic distribution',
      category: ComponentCategory.NETWORK,
    },
    {
      type: ComponentType.GATEWAY,
      defaultName: 'Gateway',
      icon: 'shield',
      color: '#84CC16', // lime-500
      defaultSize: { width: 120, height: 70 },
      defaultProperties: {
        technology: 'API Gateway',
        description: 'API gateway',
      },
      description: 'API gateway/proxy',
      category: ComponentCategory.NETWORK,
    },
    {
      type: ComponentType.CDN,
      defaultName: 'CDN',
      icon: 'cloud',
      color: '#EC4899', // pink-500
      defaultSize: { width: 100, height: 70 },
      defaultProperties: {
        technology: 'CloudFlare',
        description: 'Content delivery network',
      },
      description: 'Content delivery network',
      category: ComponentCategory.NETWORK,
    },

    // Integration Components
    {
      type: ComponentType.QUEUE,
      defaultName: 'Message Queue',
      icon: 'list',
      color: '#6366F1', // indigo-500
      defaultSize: { width: 140, height: 70 },
      defaultProperties: {
        technology: 'RabbitMQ',
        description: 'Message queue system',
      },
      description: 'Message queue/broker',
      category: ComponentCategory.INTEGRATION,
    },
    {
      type: ComponentType.EXTERNAL_SERVICE,
      defaultName: 'External Service',
      icon: 'external-link',
      color: '#64748B', // slate-500
      defaultSize: { width: 140, height: 80 },
      defaultProperties: {
        technology: 'Third-party API',
        description: 'External service integration',
      },
      description: 'Third-party service',
      category: ComponentCategory.INTEGRATION,
    },

    // Frontend Components
    {
      type: ComponentType.UI,
      defaultName: 'UI Application',
      icon: 'monitor',
      color: '#14B8A6', // teal-500
      defaultSize: { width: 130, height: 80 },
      defaultProperties: {
        technology: 'Angular',
        description: 'User interface',
      },
      description: 'Frontend application',
      category: ComponentCategory.FRONTEND,
    },
  ];

  getTemplates(): IComponentTemplate[] {
    return [...this.templates];
  } 

  getTemplatesByCategory(category: ComponentCategory): IComponentTemplate[] {
    return this.templates.filter(template => template.category === category);
  }

  getTemplate(type: ComponentType): IComponentTemplate | undefined {
    return this.templates.find(template => template.type === type);
  }

  getCategories(): ComponentCategory[] {
    return Object.values(ComponentCategory);
  }
}
