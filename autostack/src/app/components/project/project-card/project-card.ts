import { Component, Input } from '@angular/core';
import { ProjectResult } from '../../../services/project/project-service';

@Component({
  selector: 'app-project-card',
  imports: [],
  templateUrl: './project-card.html',
  styleUrl: './project-card.scss'
})
export class ProjectCard {
  @Input() information!: ProjectResult
  BannerImage = 'assets/images/project-banner.jpg';
  imageLoaded = false;

  onImageLoad() {
    this.imageLoaded = true;
  }
}
