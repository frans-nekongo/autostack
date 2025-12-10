import { Component } from '@angular/core';
import { ProjectSettingsSidebar } from "../../../components/project/project-settings-sidebar/project-settings-sidebar";
import { RouterModule } from "@angular/router";

@Component({
  selector: 'app-project-settings',
  imports: [ProjectSettingsSidebar, RouterModule],
  templateUrl: './settings.html',
  styleUrl: './settings.scss'
})
export class ProjectSettings {

}
