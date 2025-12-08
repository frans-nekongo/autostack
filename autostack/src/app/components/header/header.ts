import { Component, inject, OnDestroy, OnInit } from '@angular/core';
import { Logo } from '../logo/logo';
import { NgIcon, provideIcons } from '@ng-icons/core';
import { saxNotificationBold } from '@ng-icons/iconsax/bold';
import { heroSparklesSolid } from '@ng-icons/heroicons/solid';
import { ActivatedRoute, NavigationEnd, Router } from '@angular/router';

@Component({
  selector: 'app-header',
  imports: [Logo, NgIcon],
  templateUrl: './header.html',
  styleUrl: './header.scss',
  providers: [provideIcons({ saxNotificationBold, heroSparklesSolid })],
})
export class Header {

  colour = '#F8F8F8';
  pageTitle = '';

  
}
