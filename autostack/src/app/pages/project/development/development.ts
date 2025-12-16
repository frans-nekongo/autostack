import {
  AfterViewInit,
  Component,
  ElementRef,
  inject,
  OnDestroy,
  OnInit,
  ViewChild,
} from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { Subject, takeUntil } from 'rxjs';
import { ProjectFacade } from '../../../state/project/project.facade';
import { NgIcon, provideIcons } from '@ng-icons/core';
import {
  diAngularOriginal,
  diFastapiOriginal,
  diNodejsOriginal,
  diPythonOriginal,
  diReactOriginal,
  diNextjsOriginal,
  diVuejsOriginal,
  diSvelteOriginal,
  diDjangorestOriginal,
  diFlaskOriginal,
  diExpressOriginal,
  diNestjsOriginal,
  diPostgresqlOriginal,
  diMysqlOriginal,
  diMongodbOriginal,
  diSqliteOriginal,
  diRedisOriginal,
  diApachekafkaOriginal,
  diJavaOriginal,
  diGoOriginal,
} from '@ng-icons/devicon/original';
import { CommonModule } from '@angular/common';

interface ProjectComponent {
  id: string;
  component_id: string;
  name: string;
  type: string;
  technology: string;
  framework: string;
  port: number;
  directory: string;
  status: string;
}

interface Connection {
  id: string;
  source: string;
  target: string;
  type: string;
  port: number;
}

interface ConnectionLine {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  iconX: number;
  iconY: number;
  angle: number;
  type: string;
  isBidirectional: boolean;
}

@Component({
  selector: 'app-development',
  imports: [CommonModule, NgIcon],
  templateUrl: './development.html',
  styleUrl: './development.scss',
  providers: [
    provideIcons({
      diAngularOriginal,
      diFastapiOriginal,
      diNodejsOriginal,
      diPythonOriginal,
      diReactOriginal,
      diNextjsOriginal,
      diVuejsOriginal,
      diSvelteOriginal,
      diDjangorestOriginal,
      diFlaskOriginal,
      diExpressOriginal,
      diNestjsOriginal,
      diPostgresqlOriginal,
      diMysqlOriginal,
      diMongodbOriginal,
      diSqliteOriginal,
      diRedisOriginal,
      diApachekafkaOriginal,
      diJavaOriginal,
      diGoOriginal,
    }),
  ],
})
export class Development implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>();
  private projectFacade = inject(ProjectFacade);
  private route = inject(ActivatedRoute);

  currentProject$ = this.projectFacade.currentProject$;
  currentArchitecture$ = this.projectFacade.currentArchitecture$;
  isLoading$ = this.projectFacade.loading$;
  loadingArchitecture$ = this.projectFacade.loadingArchitecture$;

  components: ProjectComponent[] = [];
  connections: Connection[] = [];
  projectId!: string;

  ngOnInit(): void {
    let route = this.route;
    while (route.parent) {
      route = route.parent;
      if (route.snapshot.params['projectId']) {
        this.projectId = route.snapshot.params['projectId'];
        this.projectFacade.loadProjectArchitecture(this.projectId as string);
        break;
      }
    }

    this.currentArchitecture$
      .pipe(takeUntil(this.destroy$))
      .subscribe((architecture) => {
        if (architecture) {
          this.components = architecture.components as any;
          this.connections = architecture.connections as any;
        }
      });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  getIcon(framework: string): string {
    const iconMap: { [key: string]: string } = {
      django: 'diDjangorestOriginal',
      flask: 'diFlaskOriginal',
      fastapi: 'diFastapiOriginal',
      express: 'diExpressOriginal',
      nestjs: 'diNestjsOriginal',
      react: 'diReactOriginal',
      nextjs: 'diNextjsOriginal',
      angular: 'diAngularOriginal',
      vue: 'diVuejsOriginal',
      svelte: 'diSvelteOriginal',
      postgresql: 'diPostgresqlOriginal',
      mysql: 'diMysqlOriginal',
      mongodb: 'diMongodbOriginal',
      sqlite: 'diSqliteOriginal',
      redis: 'diRedisOriginal',
      kafka: 'diApachekafkaOriginal',
      nodejs: 'diNodejsOriginal',
      python: 'diPythonOriginal',
      java: 'diJavaOriginal',
      go: 'diGoOriginal',
      vanilla: '',
      none: '',
    };
    return iconMap[framework.toLowerCase()] || '';
  }

  onDeleteComponent(componentId: string): void{
    this.projectFacade.deleteComponent(componentId);
    setTimeout(() => {this.projectFacade.loadProjectArchitecture(this.projectId)}, 1000)
  }

}
