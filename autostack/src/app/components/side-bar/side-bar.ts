import { Component, inject, OnInit } from '@angular/core';
import { NgIcon, provideIcons } from '@ng-icons/core';
import { heroBell, heroCog8Tooth, heroPlus } from '@ng-icons/heroicons/outline';
import {
  saxAirdropOutline,
  saxDirectNormalOutline,
} from '@ng-icons/iconsax/outline';
import { saxDirectNormalBulk } from '@ng-icons/iconsax/bulk';
import { Logo } from '../logo/logo';
import { ProjectFacade } from '../../state/project/project.facade';
import {
  ProjectResult,
  ProjectService,
} from '../../services/project/project-service';
import { UserService } from '../../services/user/user-service';
import { Router } from '@angular/router';
import { Apollo } from 'apollo-angular';
import { FormGroup } from '@angular/forms';
import { catchError, of, Subject } from 'rxjs';

@Component({
  selector: 'app-side-bar',
  imports: [NgIcon],
  templateUrl: './side-bar.html',
  styleUrl: './side-bar.scss',
  providers: [
    provideIcons({
      heroCog8Tooth,
      heroBell,
      heroPlus,
      saxAirdropOutline,
      saxDirectNormalBulk,
    }),
  ],
})
export class SideBar implements OnInit {
  private projectFacade = inject(ProjectFacade);
  private projectService = inject(ProjectService);
  private userService = inject(UserService);
  private router = inject(Router);
  prompt: string = '';
  private apollo = inject(Apollo);
  private destroy$ = new Subject<void>();

  projects: ProjectResult[] = [];
  isLoading = false;
  error: string | null = null;

  ngOnInit(): void {
    this.loadProjects();
  }

  loadProjects(): void {
    this.isLoading = true;
    this.error = null;

    this.projectService
      .fetchAllProjects()
      .pipe(
        catchError((error) => {
          console.error('Error fetching projects:', error);
          this.error = 'Failed to load projects. Please try again later.';
          this.isLoading = false;
          return of(null);
        })
      )
      .subscribe({
        next: (projectResult: any) => {
          this.isLoading = false;
          console.log(projectResult);

          if (projectResult) {
            this.projects = projectResult.map((project: any) =>
              this.transformProjectResult(project)
            );
          } else {
            this.error = 'No projects found.';
          }
        },
        error: (error) => {
          console.error('Error in subscription:', error);
          this.isLoading = false;
          this.error = 'An unexpected error occurred.';
        },
      });
  }

  private transformProjectResult(projectResult: ProjectResult): ProjectResult {
    return {
      id: projectResult.id,
      name: projectResult.name,
      author: projectResult.author,
      description: projectResult.description || 'No description available',
      version: projectResult.version,
      status: projectResult.status,
      metadata: projectResult.metadata,
      gitInfo: {
        ...projectResult.gitInfo,
      },
    };
  }

  onSelect(project: ProjectResult) {
    const {
      id,
      name,
      author,
      description,
      version,
      status,
      metadata,
      gitInfo,
    } = project;
    this.projectFacade.setProject(
      id as string,
      name,
      author,
      description,
      version,
      status,
      metadata,
      gitInfo
    );
    this.router.navigate(['/project']);
  }
}
