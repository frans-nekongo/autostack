import { Component, inject, OnInit } from '@angular/core';
import { Logo } from '../logo/logo';
import { NgIcon, provideIcons } from '@ng-icons/core';
import { saxNotificationBold } from '@ng-icons/iconsax/bold';
import { heroSparklesSolid } from '@ng-icons/heroicons/solid';
import { ActivatedRoute, NavigationEnd, Router } from '@angular/router';
import { filter, map, Observable, of, switchMap } from 'rxjs';
import { ProjectFacade } from '../../state/project/project.facade';
import { ChatFacade } from '../../state/chat/chat.facade';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-header',
  imports: [Logo, NgIcon, CommonModule],
  templateUrl: './header.html',
  styleUrl: './header.scss',
  providers: [provideIcons({ saxNotificationBold, heroSparklesSolid })],
})
export class Header implements OnInit {
  private router = inject(Router);
  private route = inject(ActivatedRoute);
  private projectFacade = inject(ProjectFacade);
  private chatFacade = inject(ChatFacade);

  colour = '#F8F8F8';
  pageTitle$!: Observable<string>;

  ngOnInit() {
    this.pageTitle$ = this.router.events.pipe(
      filter((event) => event instanceof NavigationEnd),
      map(() => {
        let route = this.route;
        while (route.firstChild) {
          route = route.firstChild;
        }
        return route;
      }),
      switchMap((route) => {
        const staticTitle = route.snapshot.data['title'] || '';
        const routePath = route.snapshot.routeConfig?.path || '';

        // Check if we're on a chat detail page
        if (routePath === ':chatid') {
          return this.chatFacade.currentChat$.pipe(
            map((chat) => chat?.chatTitle || 'Chat')
          );
        }

        // Check if we're on a project page
        if (route.parent?.snapshot.routeConfig?.path === 'project/:projectId') {
          return this.projectFacade.currentProject$.pipe(
            map((project) => project?.name || 'Project')
          );
        }

        // Return static title for other routes
        return of(staticTitle);
      })
    );
  }
}
