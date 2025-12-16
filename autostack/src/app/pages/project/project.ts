import { Component, inject, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute, Router, RouterOutlet } from '@angular/router';
import { NgIcon, provideIcons } from '@ng-icons/core';
import { heroArrowLeft } from '@ng-icons/heroicons/outline';
import { ProjectFacade } from '../../state/project/project.facade';
import { Subject, takeUntil } from 'rxjs';
import { RouterModule } from '@angular/router';
import {
  ProjectResult,
  ProjectService,
} from '../../services/project/project-service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-project',
  imports: [RouterOutlet, NgIcon, RouterModule, CommonModule],
  templateUrl: './project.html',
  styleUrl: './project.scss',
  providers: [provideIcons({ heroArrowLeft })],
})
export class Project implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>();
  private projectFacade = inject(ProjectFacade);
  private router = inject(Router);
  private route = inject(ActivatedRoute);

  currentProject$ = this.projectFacade.currentProject$;
  currentArchitecture$ = this.projectFacade.currentArchitecture$;
  isLoading$ = this.projectFacade.loading$;
  loadingArchitecture$ = this.projectFacade.loadingArchitecture$;

  ngOnInit(): void {
    this.route.params.subscribe((params) => {
      const projectId = params['projectId'];
      if (projectId) {
        this.projectFacade.loadProject(projectId);
      }
    });

    this.currentArchitecture$
      .pipe(takeUntil(this.destroy$))
      .subscribe((architecture) => {
        if (architecture) {
          console.log(architecture);
        }
      });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  onBack(): void {
    this.router.navigate(['/']);
  }
}
