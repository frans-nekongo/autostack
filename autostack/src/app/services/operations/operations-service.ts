import { Injectable, inject } from '@angular/core';
import { Apollo, gql } from 'apollo-angular';
import { Observable } from 'rxjs';
import { map, takeWhile } from 'rxjs/operators';

export enum OperationStatus {
  QUEUED = 'QUEUED',
  VALIDATING = 'VALIDATING',
  CREATING_PROJECT = 'CREATING_PROJECT',
  CREATING_TECHNOLOGIES = 'CREATING_TECHNOLOGIES',
  CREATING_COMPONENTS = 'CREATING_COMPONENTS',
  CREATING_CONNECTIONS = 'CREATING_CONNECTIONS',
  DELETING_PROJECT = 'DELETING_PROJECT',
  FINALIZING = 'FINALIZING',
  COMPLETED = 'COMPLETED',
  FAILED = 'FAILED',
}

export interface OperationUpdate {
  operationId: string;
  status: OperationStatus;
  message: string;
  progress: number; // 0-100
  projectId?: string;
  error?: string;
  timestamp?: string;
}

export interface InitiateProjectResponse {
  success: boolean;
  operationId: string;
  message: string;
  error?: string;
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
export class OperationsService {
  private apollo = inject(Apollo);

  private INITIATE_PROJECT_MUTATION = gql`
    mutation CreateFullProjectAsync($input: FullProjectInput!) {
      createFullProjectAsync(input: $input) {
        success
        operationId
        message
        error
      }
    }
  `;

  private PROJECT_CREATION_SUBSCRIPTION = gql`
    subscription ProjectCreationStatus($operationId: String!) {
      projectCreationStatus(operationId: $operationId) {
        operationId
        status
        message
        progress
        projectId
        error
      }
    }
  `;

  initiateProjectCreation(
    schema: any,
    chatId: string
  ): Observable<InitiateProjectResponse> {
    const input = this.transformToFullProjectInput(schema, chatId);

    return this.apollo
      .mutate<{ createFullProjectAsync: InitiateProjectResponse }>({
        mutation: this.INITIATE_PROJECT_MUTATION,
        variables: { input },
      })
      .pipe(map((result) => result.data!.createFullProjectAsync));
  }

  subscribeToOperation(operationId: string): Observable<OperationUpdate> {
    console.log(operationId)
    return this.apollo
      .subscribe<{ projectCreationStatus: OperationUpdate }>({
        query: this.PROJECT_CREATION_SUBSCRIPTION,
        variables: { operationId },
      })
      .pipe(
        map((result) => result.data!.projectCreationStatus),
        // Auto-complete when done
        takeWhile(
          (update) =>
            update.status !== OperationStatus.COMPLETED &&
            update.status !== OperationStatus.FAILED,
          true // inclusive - emit the final value
        )
      );
  }

  createProjectWithProgress(
    schema: any,
    chatId: string
  ): Observable<OperationUpdate> {
    return new Observable((subscriber) => {
      this.initiateProjectCreation(schema, chatId).subscribe({
        next: (response) => {
          if (response.success) {
            // Start subscription
            this.subscribeToOperation(response.operationId).subscribe({
              next: (update) => subscriber.next(update),
              error: (err) => subscriber.error(err),
              complete: () => subscriber.complete(),
            });
          } else {
            subscriber.error(new Error(response.error || 'Failed to initiate'));
          }
        },
        error: (err) => subscriber.error(err),
      });
    });
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
        const value = valueParts.join('=');
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

  private transformToFullProjectInput(data: any, chatId: string) {
    return {
      project: {
        name: data.project.name,
        author: data.project.author,
        description: data.project.description,
        version: data.project.version || '1.0.0',
        status: 'created',
        chatId: chatId,
        metadata: null,
      },
      technologies:
        data.technologies?.map((tech: any) => ({
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
        data.components?.map((component: any) => ({
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
        data.connections?.map((connection: any) => ({
          source: connection.source,
          target: connection.target,
          type: connection.type || 'api',
          port: connection.port || null,
        })) || [],
    };
  }
}
