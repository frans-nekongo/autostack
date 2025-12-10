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
import { Apollo } from 'apollo-angular';
import {
  catchError,
  map,
  Observable,
  of,
  Subject,
  switchMap,
  takeUntil,
} from 'rxjs';
import { ProjectFacade } from '../../../../state/project/project.facade';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import mermaid from 'mermaid';
import { ProjectService } from '../../../../services/project/project-service';

@Component({
  selector: 'app-general-project-settings',
  imports: [CommonModule, FormsModule],
  templateUrl: './general-project-settings.html',
  styleUrl: './general-project-settings.scss',
})
export class GeneralProjectSettings
  implements OnInit, OnDestroy, AfterViewInit
{
  @ViewChild('mermaidDiagram', { static: false }) mermaidDiagram!: ElementRef;
  private destroy$ = new Subject<void>();
  private projectFacade = inject(ProjectFacade);
  private projectService = inject(ProjectService);
  private route = inject(ActivatedRoute);
  private router = inject(Router);

  currentProject$ = this.projectFacade.currentProject$;
  canEdit: boolean = false;

  // Modal state
  showDeleteModal: boolean = false;
  deleteConfirmationText: string = '';
  isDeleting: boolean = false;
  deleteError: string = '';

  formData = {
    name: '',
    version: '',
    description: '',
  };

  originalData = {
    name: '',
    version: '',
    description: '',
  };

  ngOnInit(): void {
    this.route.params.subscribe((params) => {
      const projectId = params['projectId'];
      if (projectId) {
        this.projectFacade.loadProject(projectId);
        this.projectFacade.loadProjectArchitecture(projectId);
      }
    });

    this.currentProject$.pipe(takeUntil(this.destroy$)).subscribe((project) => {
      if (project) {
        this.formData = {
          name: project.name || '',
          version: project.version || '',
          description: project.description || '',
        };
        this.originalData = { ...this.formData };
      }
    });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  ngAfterViewInit(): void {
    this.renderMermaidDiagram();
  }

  private diagramCode: string = '';

  private async renderMermaidDiagram(): Promise<void> {
    try {
      this.projectFacade.currentProject$
        .pipe(
          takeUntil(this.destroy$),
          switchMap((selectedProject) => {
            if (!selectedProject || !selectedProject.id) {
              return of(null);
            }
            return this.projectService.fetchProjectArchitecture(
              selectedProject.id
            );
          }),
          catchError((error) => {
            return of(null);
          })
        )
        .subscribe({
          next: async (architectureResult: any) => {
            if (architectureResult) {
              this.diagramCode =
                this.projectService.generateC4Diagram(architectureResult);
              const element = this.mermaidDiagram.nativeElement;
              await this.renderDiagram(element, this.diagramCode);
              await mermaid.run({
                nodes: [element],
              });
            }
          },
          error: (error) => {
            console.error('Error loading architecture:', error);
          },
        });
    } catch (error) {
      console.error('Error rendering Mermaid diagram:', error);
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

  onCanEditSelect(option: boolean): void {
    this.canEdit = option;
  }

  openDeleteModal(): void {
    this.showDeleteModal = true;
    this.deleteConfirmationText = '';
    this.deleteError = '';
  }

  closeDeleteModal(): void {
    this.showDeleteModal = false;
    this.deleteConfirmationText = '';
    this.deleteError = '';
    this.isDeleting = false;
  }

  get isDeleteEnabled(): Observable<boolean> {
    return this.currentProject$.pipe(
      map(
        (currentProject) => this.deleteConfirmationText === currentProject?.name
      )
    );
  }

  deleteProject(): void {
    this.currentProject$.pipe(takeUntil(this.destroy$)).subscribe({
      next: (project) => {
        if (!project || !project.id) {
          this.deleteError = 'Project not found';
          return;
        }

        if (this.deleteConfirmationText !== project.name) {
          this.deleteError = 'Project name does not match';
          return;
        }

        this.isDeleting = true;
        this.deleteError = '';

        this.projectService
          .deleteProject(project.id)
          .pipe(takeUntil(this.destroy$))
          .subscribe({
            next: () => {
              this.closeDeleteModal();
              this.router.navigate(['/projects']);
            },
            error: (error) => {
              this.isDeleting = false;
              this.deleteError = 'Failed to delete project. Please try again.';
              console.error('Error deleting project:', error);
            },
          });
      },
      error: (error) => {
        this.deleteError = 'Error loading project details';
        console.error('Error:', error);
      },
    });
  }

  resetForm(): void {
    this.currentProject$.pipe(takeUntil(this.destroy$)).subscribe((project) => {
      if (project) {
        this.formData = {
          name: project.name || '',
          version: project.version || '',
          description: project.description || '',
        };
      }
    });
  }

  onSubmit(): void {
    if (!this.canEdit) return;

    // Get current project ID
    let projectId: string = '';
    this.currentProject$.pipe(takeUntil(this.destroy$)).subscribe((project) => {
      if (project) {
        projectId = project.id;

        // Prepare updates object with only changed values
        const updates: any = {};

        if (this.formData.name !== this.originalData.name) {
          updates.name = this.formData.name;
        }

        if (this.formData.version !== this.originalData.version) {
          updates.version = this.formData.version;
        }

        if (this.formData.description !== this.originalData.description) {
          updates.description = this.formData.description;
        }

        // Only update if there are changes
        if (Object.keys(updates).length > 0) {
          this.projectFacade.updateProject(projectId, updates);

          // Update original data with new values
          this.originalData = { ...this.formData };
        }

        // Exit edit mode
        this.canEdit = false;
      }
    });
  }

  onFormInputChange(field: keyof typeof this.formData, value: string): void {
    this.formData[field] = value;
  }

    hasFormChanges(): boolean {
    return (
      this.formData.name !== this.originalData.name ||
      this.formData.version !== this.originalData.version ||
      this.formData.description !== this.originalData.description
    );
  }
}
