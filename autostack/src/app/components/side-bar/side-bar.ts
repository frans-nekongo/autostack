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
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-side-bar',
  imports: [NgIcon, CommonModule, ],
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
  private router = inject(Router);

  projects: ProjectResult[] = [];
  isLoading = false;
  error: string | null = null;

  projects$ = this.projectFacade.projects$;
  isLoading$ = this.projectFacade.loading$;
  error$ = this.projectFacade.error$;
  projectsCount$ = this.projectFacade.projectsCount$;

  ngOnInit(): void {
    this.projectFacade.loadProjects();
  }

  onSelectProject(project: ProjectResult):void {
    this.projectFacade.setCurrentProject(project.id);
    this.router.navigate(['/project', project.id]);
  }
}
