import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';
import { NgIcon, provideIcons } from "@ng-icons/core";
import { heroCog8Tooth } from '@ng-icons/heroicons/outline';

@Component({
  selector: 'app-project-settings-sidebar',
  imports: [NgIcon, RouterModule, ],
  templateUrl: './project-settings-sidebar.html',
  styleUrl: './project-settings-sidebar.scss',
  providers: [provideIcons({ heroCog8Tooth })]
})
export class ProjectSettingsSidebar {

}
