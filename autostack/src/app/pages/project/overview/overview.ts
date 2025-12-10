import {
  Component,
  inject,
  OnDestroy,
  OnInit,
  AfterViewInit,
  ElementRef,
  ViewChild,
} from '@angular/core';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { catchError, of, Subject, switchMap, takeUntil } from 'rxjs';
import { ProjectFacade } from '../../../state/project/project.facade';
import mermaid from 'mermaid';
import { Apollo, gql } from 'apollo-angular';
import { provideIcons, NgIcon } from '@ng-icons/core';
import { diVscodePlain } from '@ng-icons/devicon/plain';
import { ProjectService } from '../../../services/project/project-service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-overview',
  imports: [RouterModule, NgIcon, CommonModule],
  templateUrl: './overview.html',
  styleUrl: './overview.scss',
  providers: [provideIcons({ diVscodePlain })],
})
export class Overview implements OnInit, OnDestroy, AfterViewInit {
  @ViewChild('mermaidDiagram', { static: false }) mermaidDiagram!: ElementRef;
  @ViewChild('mermaidDiagramLarge') mermaidDiagramLarge!: ElementRef;

  private destory$ = new Subject<void>();
  private projectFacade = inject(ProjectFacade);
  private projectService = inject(ProjectService);
  private router = inject(Router);
  private route = inject(ActivatedRoute);

  currentProject$ = this.projectFacade.currentProject$;
  currentArchitecture$ = this.projectFacade.currentArchitecture$;
  isLoading$ = this.projectFacade.loading$;
  loadingArchitecture$ = this.projectFacade.loadingArchitecture$;

  architectureComponents$ = this.projectFacade.architectureComponents$;
  architectureTechnologies$ = this.projectFacade.architectureTechnologies$;
  architectureConnections$ = this.projectFacade.architectureConnections$;

  isLoading = false;
  error: string | null = null;

  isModalOpen = false;

  private diagramCode: string = '';

  ngOnInit(): void {
    // Initialize Mermaid
    mermaid.initialize({
      startOnLoad: false,
      theme: 'default',
      securityLevel: 'loose',
    });

    this.route.params.subscribe((params) => {
      const projectId = params['projectId'];
      if (projectId) {
        this.projectFacade.loadProject(projectId);
        this.projectFacade.loadProjectArchitecture(projectId);
      }
    });
  }

  ngAfterViewInit(): void {
    this.renderMermaidDiagram();
  }

  private async renderMermaidDiagram(): Promise<void> {
    try {
      this.isLoading = true;

      this.projectFacade.currentProject$
        .pipe(
          takeUntil(this.destory$),
          // Use switchMap to properly chain the observables
          switchMap((selectedProject) => {
            if (!selectedProject || !selectedProject.id) {
              this.isLoading = false;
              return of(null);
            }
            return this.projectService.fetchProjectArchitecture(
              selectedProject.id
            );
          }),
          catchError((error) => {
            console.error('Error fetching project architecture:', error);
            this.error = 'Failed to load architecture. Please try again later.';
            this.isLoading = false;
            return of(null);
          })
        )
        .subscribe({
          next: async (architectureResult: any) => {
            this.isLoading = false;

            if (architectureResult) {
              // Generate the C4 diagram
              this.diagramCode =
                this.projectService.generateC4Diagram(architectureResult);

              // Render the diagram
              const element = this.mermaidDiagram.nativeElement;
              await this.renderDiagram(element, this.diagramCode);

              // Initialize mermaid rendering
              await mermaid.run({
                nodes: [element],
              });

              // Add click event listener
              element.addEventListener('click', () => {
                this.navigateToEditor();
              });

              // Make it clickable
              element.style.cursor = 'pointer';
            }
          },
          error: (error) => {
            console.error('Error in subscription:', error);
            this.isLoading = false;
            this.error = 'An unexpected error occurred.';
          },
        });
    } catch (error) {
      console.error('Error rendering Mermaid diagram:', error);
      this.isLoading = false;
    }
  }

  private async renderDiagram(
    element: HTMLElement,
    code: string
  ): Promise<void> {
    try {
      element.innerHTML = code;
      await mermaid.run({
        nodes: [element],
      });
    } catch (error) {
      console.error('Error rendering diagram:', error);
    }
  }

  private navigateToEditor(): void {
    this.router.navigate(['/editor']);
  }

  ngOnDestroy(): void {
    this.destory$.next();
    this.destory$.complete();
  }

  onNavigateToEditor(): void {
    this.router.navigate(['/project/editor']);
  }

  openInVSCode() {
    this.projectFacade.currentProject$
      .pipe(takeUntil(this.destory$))
      .subscribe((selectedProject) => {
        if (selectedProject) {
          const projectPath = selectedProject.metadata?.directory as string;
          const encodedPath = encodeURIComponent(projectPath);
          window.location.href = `vscode://file/${encodedPath}`;
        }
      });
  }

  openModal() {
    this.isModalOpen = true;
    setTimeout(async () => {
      if (this.mermaidDiagramLarge && this.diagramCode) {
        await this.renderDiagram(
          this.mermaidDiagramLarge.nativeElement,
          this.diagramCode
        );
      }
    }, 0);
  }

  closeModal() {
    this.isModalOpen = false;
  }
}
