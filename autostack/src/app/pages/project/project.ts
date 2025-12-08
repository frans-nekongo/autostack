import { Component, inject, OnDestroy, OnInit } from '@angular/core';
import { Router, RouterOutlet } from '@angular/router';
import { NgIcon, provideIcons } from "@ng-icons/core";
import { heroArrowLeft } from '@ng-icons/heroicons/outline';
import { ProjectFacade } from '../../state/project/project.facade';
import { Subject, takeUntil } from 'rxjs';
import { RouterModule } from "@angular/router";
import { ProjectResult, ProjectService } from '../../services/project/project-service';

@Component({
  selector: 'app-project',
  imports: [RouterOutlet, NgIcon, RouterModule],
  templateUrl: './project.html',
  styleUrl: './project.scss',
  providers: [provideIcons({heroArrowLeft})]
})
export class Project implements OnInit, OnDestroy{
  private destory$ = new Subject<void>()
  private projectFacade = inject(ProjectFacade);
  private projectService = inject(ProjectService);
  private router = inject(Router)

  project$ = this.projectFacade.project$;
  project!: ProjectResult;


  ngOnInit(): void {
    this.projectFacade.project$.pipe(takeUntil(this.destory$)).subscribe((selectedProject) => {
      if (selectedProject) {
        this.project = selectedProject;
      }
    })
  }

  ngOnDestroy(): void {
    
  }

  onBack(): void {
    this.router.navigate(['/'])
  }
}
