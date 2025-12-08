import { inject, Injectable } from '@angular/core';
import { Apollo, gql } from 'apollo-angular';
import { map, Observable } from 'rxjs';
import {
  COMPONENT_TYPE,
  GeneratedComponent,
  GeneratedSchema,
  TECHNOLOGY_CATEGORY,
} from './util';

export interface ProjectMetadata {
  created_date?: string | null;
  last_modified?: string | null;
  tags?: string[] | null;
  environment?: string | null;
  directory?: string | null;
}

export interface GitInfo {
  latestCommit?: string | null;
  branch?: string | null;
  is_dirty?: boolean | null;
  commits?: string[] | null;
}

export interface ProjectResult {
  id: string;
  name: string;
  author?: string | null;
  description?: string | null;
  version: string;
  status?: string | null;
  metadata?: ProjectMetadata | null;
  gitInfo?: GitInfo | null;
}

interface EnvironmentVariable {
  name: string;
  value: string;
}

interface Configuration {
  name: string;
  value: string;
}

interface Technology {
  name: string;
  version: string;
  category?: string;
  port?: number;
  enabled: boolean;
  environment_variables?: EnvironmentVariable[];
  configuration?: Configuration[];
}

interface Component {
  component_id: string;
  type: string;
  name: string;
  technology?: string;
  framework?: string;
  port?: number;
  environment_variables?: Record<string, any>;
  dependencies?: string[];
}

interface Connection {
  source: string;
  target: string;
  type: string;
  port?: number;
}

interface ProjectArchitecture {
  project_id: string;
  project_name: string;
  technologies: Technology[];
  components: Component[];
  connections: Connection[];
  metadata: {
    component_count: number;
    connection_count: number;
    technology_count: number;
  };
}

interface ArchitectureResponse {
  success: boolean;
  data?: ProjectArchitecture;
  error?: string;
  message?: string;
}

export interface ProjectCreatedResponse {
  success: boolean;
  projectId: string;
  error: string;
  message: string;
}

enum TechnologyCategory {
  RUNTIME = 'RUNTIME',
  DATABASE = 'DATABASE',
  CACHE = 'CACHE',
  QUEUE = 'QUEUE',
  SERVICE = 'SERVICE',
}

enum ComponentTypeInput {
  DATABASE = 'DATABASE',
  CACHE = 'CACHE',
  API = 'API',
  WEB = 'WEB',
  GATEWAY = 'GATEWAY',
  EXTERNAL = 'EXTERNAL',
}

@Injectable({
  providedIn: 'root',
})
export class ProjectService {
  private apollo = inject(Apollo);

  fetchAllProjects(): Observable<ProjectResult | null | undefined> {
    const FETCH_ALL_PROJECTS = gql`
      query FetchAllProjects {
        fetchAllProjects {
          id
          name
          author
          description
          version
          status
          metadata {
            createdDate
            lastModified
            tags
            environment
            directory
          }
          gitInfo {
            latestCommit
            branch
            isDirty
            commits
          }
        }
      }
    `;

    return this.apollo
      .query<{ fetchAllProjects: ProjectResult | null | undefined }>({
        query: FETCH_ALL_PROJECTS,
        fetchPolicy: 'network-only',
      })
      .pipe(map((result) => result.data?.fetchAllProjects));
  }

  fetchProjectArchitecture(
    projectId: string
  ): Observable<ProjectArchitecture | null | undefined> {
    const FETCH_PROJECT_ARCHITECTURE = gql`
      query fetchProjectArchitecture($projectId: String!) {
        fetchProjectArchitecture(projectId: $projectId) {
          success
          data
          error
          message
        }
      }
    `;

    return this.apollo
      .query<{
        fetchProjectArchitecture: ProjectArchitecture | null | undefined;
      }>({
        query: FETCH_PROJECT_ARCHITECTURE,
        variables: { projectId },
        fetchPolicy: 'network-only',
      })
      .pipe(map((result) => result.data?.fetchProjectArchitecture));
  }

  createFullProject(
    schema: GeneratedSchema,
    chatId: string
  ): Observable<ProjectCreatedResponse> {
    const input = this.transformToFullProjectInput(schema, chatId);

    const CREATE_FULL_PROJECT_DETAILED = gql`
      mutation CreateFullProject(
        $input: FullProjectInput!
      ) {
        createFullProject(
          input: $input
        ) {
          success
          projectId
          error
          message
        }
      }
    `;

    return this.apollo
      .mutate<{ createFullProject: ProjectCreatedResponse }>({
        mutation: CREATE_FULL_PROJECT_DETAILED,
        variables: { input },
      })
      .pipe(map((result) => result.data!.createFullProject));
  }

  generateC4Diagram(architecture: ProjectArchitecture): string {
    const lines: string[] = [];

    // C4 Context diagram header
    lines.push('C4Context');
    lines.push(
      `  title Architectural Diagram for ${architecture.project_name}`
    );
    lines.push('');

    // Add system boundary
    lines.push(`  System_Boundary(system, "${architecture.project_name}") {`);

    const componentsByType = this.groupComponentsByType(
      architecture.components
    );

    // Add containers (components) inside the system boundary
    for (const [type, components] of Object.entries(componentsByType)) {
      for (const comp of components) {
        const techInfo = this.getTechnologyInfo(
          comp,
          architecture.technologies
        );
        const description = techInfo ? `${comp.type} (${techInfo})` : comp.type;

        // Use different C4 element types based on component type
        const c4Type = this.getC4ElementType(comp.type);
        lines.push(
          `    ${c4Type}(${comp.component_id}, "${comp.name}", "${description}")`
        );
      }
    }

    lines.push('  }');
    lines.push('');

    const externalComponents = architecture.components.filter(
      (c) => c.type === 'external'
    );
    if (externalComponents.length > 0) {
      for (const ext of externalComponents) {
        lines.push(
          `  System_Ext(${ext.component_id}, "${ext.name}", "${ext.type}")`
        );
      }
      lines.push('');
    }

    // Add relationships (connections)
    if (architecture.connections.length > 0) {
      for (const conn of architecture.connections) {
        const label = this.getConnectionLabel(conn);
        lines.push(`  Rel(${conn.source}, ${conn.target}, "${label}")`);
      }
    }

    lines.push('');
    lines.push('  UpdateRelStyle(system, system, $offsetY="-40")');

    return lines.join('\n');
  }

  generateC4ContainerDiagram(architecture: ProjectArchitecture): string {
    const lines: string[] = [];

    lines.push('C4Container');
    lines.push(`  title Container diagram for ${architecture.project_name}`);
    lines.push('');

    lines.push(
      `  Container_Boundary(system, "${architecture.project_name}") {`
    );

    // Add all components as containers
    for (const comp of architecture.components) {
      if (comp.type === 'external') continue;

      const techInfo = this.getTechnologyInfo(comp, architecture.technologies);
      const technology = techInfo || comp.technology || comp.type;

      lines.push(
        `    Container(${comp.component_id}, "${
          comp.name
        }", "${technology}", "${comp.framework || ''}")`
      );
    }

    lines.push('  }');
    lines.push('');

    // External systems
    const externalComponents = architecture.components.filter(
      (c) => c.type === 'external'
    );
    for (const ext of externalComponents) {
      lines.push(`  System_Ext(${ext.component_id}, "${ext.name}", "")`);
    }

    if (externalComponents.length > 0) {
      lines.push('');
    }

    // Relationships
    for (const conn of architecture.connections) {
      const label = this.getConnectionLabel(conn);
      lines.push(`  Rel(${conn.source}, ${conn.target}, "${label}")`);
    }

    return lines.join('\n');
  }

  private groupComponentsByType(
    components: Component[]
  ): Record<string, Component[]> {
    return components.reduce((acc, comp) => {
      if (!acc[comp.type]) {
        acc[comp.type] = [];
      }
      acc[comp.type].push(comp);
      return acc;
    }, {} as Record<string, Component[]>);
  }

  private getTechnologyInfo(
    component: Component,
    technologies: Technology[]
  ): string | null {
    if (component.technology) {
      const tech = technologies.find((t) => t.name === component.technology);
      if (tech) {
        return `${tech.name} ${
          tech.version !== 'latest' ? tech.version : ''
        }`.trim();
      }
      return component.technology;
    }
    return null;
  }

  private getC4ElementType(componentType: string): string {
    const typeMap: Record<string, string> = {
      database: 'ContainerDb',
      cache: 'ContainerQueue',
      api: 'Container',
      web: 'Container',
      gateway: 'Container',
      queue: 'ContainerQueue',
      service: 'Container',
    };

    return typeMap[componentType] || 'Container';
  }

  private getConnectionLabel(connection: Connection): string {
    const parts: string[] = [];

    if (connection.type) {
      parts.push(connection.type.toUpperCase());
    }

    if (connection.port) {
      parts.push(`port ${connection.port}`);
    }

    return parts.length > 0 ? parts.join(' - ') : 'uses';
  }

  private parseEnvironmentVariables(
    env: string
  ): Array<{ name: string; value: string }> | null {
    if (!env) return null;

    return env
      .split(',')
      .map((item) => item.trim())
      .filter((item) => item.includes('='))
      .map((item) => {
        const [name, ...valueParts] = item.split('=');
        const value = valueParts.join('='); // Handle values containing '='
        return { name: name.trim(), value: value.trim() };
      });
  }

  private mapTechnologyTypeToCategory(type: string): TechnologyCategory {
    const typeLower = type.toLowerCase();
    switch (typeLower) {
      case 'database':
        return TechnologyCategory.DATABASE;
      case 'runtime':
      case 'node':
      case 'python':
      case 'java':
        return TechnologyCategory.RUNTIME;
      case 'cache':
      case 'redis':
      case 'memcached':
        return TechnologyCategory.CACHE;
      case 'queue':
      case 'rabbitmq':
      case 'kafka':
        return TechnologyCategory.QUEUE;
      case 'service':
        return TechnologyCategory.SERVICE;
      default:
        return TechnologyCategory.RUNTIME;
    }
  }

  private mapComponentToType(type?: string): ComponentTypeInput {
    if (!type) return ComponentTypeInput.EXTERNAL;

    const typeUpper = type.toUpperCase();
    switch (typeUpper) {
      case 'DATABASE':
        return ComponentTypeInput.DATABASE;
      case 'CACHE':
        return ComponentTypeInput.CACHE;
      case 'API':
        return ComponentTypeInput.API;
      case 'WEB':
        return ComponentTypeInput.WEB;
      case 'GATEWAY':
        return ComponentTypeInput.GATEWAY;
      case 'EXTERNAL':
        return ComponentTypeInput.EXTERNAL;
      default:
        // Try to infer from the string
        const typeLower = type.toLowerCase();
        if (typeLower.includes('api')) return ComponentTypeInput.API;
        if (typeLower.includes('web')) return ComponentTypeInput.WEB;
        if (typeLower.includes('gateway')) return ComponentTypeInput.GATEWAY;
        if (typeLower.includes('database') || typeLower.includes('db'))
          return ComponentTypeInput.DATABASE;
        if (typeLower.includes('cache')) return ComponentTypeInput.CACHE;
        return ComponentTypeInput.EXTERNAL;
    }
  }

  private transformToFullProjectInput(data: GeneratedSchema, chatId: string) {
    return {
      project: {
        name: data.project.name,
        author: data.project.author,
        description: data.project.description,
        version: data.project.version || '1.0.0',
        status: 'created',
        metadata: null,
        chatId: chatId,
      },
      technologies:
        data.technologies?.map((tech) => ({
          name: tech.name,
          version: tech.version || 'latest',
          category: this.mapTechnologyTypeToCategory(tech.type),
          port: null,
          environmentVariables: this.parseEnvironmentVariables(
            tech.environment_variables as string
          ),
          configuration: null,
          enabled: true,
        })) || [],
      components:
        data.components?.map((component) => ({
          componentId: component.component_id,
          name: component.name,
          type: this.mapComponentToType(component.type),
          technology: component.technology,
          framework: component.framework,
          port: component.port || null,
          environmentVariables: component.environment_variables || null,
          dependencies: component.dependencies || [],
        })) || [],
      connections:
        data.connections?.map((connection) => ({
          source: connection.source,
          target: connection.target,
          type: connection.type || 'api',
          port: connection.port || null,
        })) || [],
    };
  }
}
