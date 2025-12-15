import { Component, inject, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Subject, takeUntil } from 'rxjs';
import { GitInfo } from '../../../../services/project/project-service';
import { ProjectFacade } from '../../../../state/project/project.facade';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-version-control-project-settings',
  imports: [CommonModule],
  templateUrl: './version-control-project-settings.html',
  styleUrl: './version-control-project-settings.scss',
})
export class VersionControlProjectSettings implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>();
  private projectFacade = inject(ProjectFacade);
  private route = inject(ActivatedRoute);

  loading$ = this.projectFacade.loading$;
  currentProject$ = this.projectFacade.currentProject$;
  gitInfo!: GitInfo | null | undefined;
  projectId: string | null = null;

  ngOnInit(): void {
    let route = this.route;
    while (route.parent) {
      route = route.parent;
      if (route.snapshot.params['projectId']) {
        this.projectId = route.snapshot.params['projectId'];
        this.projectFacade.loadProject(this.projectId as string);
        this.projectFacade.loadProjectArchitecture(this.projectId as string);
        break;
      }
    }

    this.currentProject$.pipe(takeUntil(this.destroy$)).subscribe((project) => {
      if (project) {
        this.gitInfo = project.gitInfo;
      }
    });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  onInitialiseGit(): void {
    console.log(this.projectId);
    if (this.projectId) {
      this.projectFacade.initialiseGit(this.projectId);
    }
  }
}
