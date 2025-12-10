import { Component, inject, OnInit } from '@angular/core';
import { ProjectFacade } from '../../../state/project/project.facade';
import { BehaviorSubject, catchError, combineLatest, map, Observable, of } from 'rxjs';
import {
  ProjectService,
  ProjectResult,
} from '../../../services/project/project-service';
import { NgIcon, provideIcons } from '@ng-icons/core';
import { Router } from '@angular/router';
import { heroChevronDown } from '@ng-icons/heroicons/outline';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';


type SortOption = 'name-asc' | 'name-desc' | 'date-asc' | 'date-desc';

@Component({
  selector: 'app-projects-page',
  imports: [NgIcon, CommonModule, FormsModule],
  templateUrl: './projects-page.html',
  styleUrl: './projects-page.scss',
  providers: [provideIcons({ heroChevronDown })],
})
export class ProjectsPage implements OnInit {
  private projectFacade = inject(ProjectFacade);
  private router = inject(Router);

  projects$ = this.projectFacade.projects$;
  isLoading$ = this.projectFacade.loading$;
  error$ = this.projectFacade.error$;
  projectsCount$ = this.projectFacade.projectsCount$;

  private searchTerm$ = new BehaviorSubject<string>('');
  private sortOption$ = new BehaviorSubject<SortOption>('date-desc');

  // Filtered and sorted projects observable
  filteredProjects$: Observable<ProjectResult[]>;
  

  searchTerm = '';
  sortOption: SortOption = 'date-desc';
  sortOptions = [
    { value: 'date-desc', label: 'Last Modified (Newest)' },
    { value: 'date-asc', label: 'Last Modified (Oldest)' },
    { value: 'name-asc', label: 'Name (A-Z)' },
    { value: 'name-desc', label: 'Name (Z-A)' },
  ];
  isDropdownOpen = false;

  constructor() {
    // Combine projects with search and sort to create filtered list
    this.filteredProjects$ = combineLatest([
      this.projectFacade.projects$,
      this.searchTerm$,
      this.sortOption$,
    ]).pipe(
      map(([projects, searchTerm, sortOption]) => {
        let filtered = this.filterProjects(projects, searchTerm);
        return this.sortProjects(filtered, sortOption);
      })
    );
  }

  ngOnInit(): void {
    this.projectFacade.loadProjects();
  }

  private filterProjects(
    projects: ProjectResult[],
    searchTerm: string
  ): ProjectResult[] {
    if (!searchTerm.trim()) {
      return projects;
    }

    const term = searchTerm.toLowerCase().trim();
    return projects.filter(
      (project) =>
        project.name.toLowerCase().includes(term) ||
        (project.description?.toLowerCase() || '').includes(term) ||
        (project.author?.toLowerCase() || '').includes(term)
    );
  }

  private sortProjects(
    projects: ProjectResult[],
    sortOption: SortOption
  ): ProjectResult[] {
    const projectsCopy = [...projects];

    switch (sortOption) {
      case 'name-asc':
        return projectsCopy.sort((a, b) => a.name.localeCompare(b.name));

      case 'name-desc':
        return projectsCopy.sort((a, b) => b.name.localeCompare(a.name));

      case 'date-asc':
        return projectsCopy.sort((a, b) => {
          const dateA = new Date(a.metadata?.lastModified || 0);
          const dateB = new Date(b.metadata?.lastModified || 0);
          return dateA.getTime() - dateB.getTime();
        });

      case 'date-desc':
      default:
        return projectsCopy.sort((a, b) => {
          const dateA = new Date(a.metadata?.lastModified || 0);
          const dateB = new Date(b.metadata?.lastModified || 0);
          return dateB.getTime() - dateA.getTime();
        });
    }
  }

  private searchProjects(projects: any[]): any[] {
    if (!this.searchTerm.trim()) {
      return projects;
    }

    const term = this.searchTerm.toLowerCase().trim();
    return projects.filter(
      (project) =>
        project.name.toLowerCase().includes(term) ||
        project.description.toLowerCase().includes(term)
    );
  }


  onSortChange(sortValue: string): void {
    this.sortOption = sortValue as SortOption;
    this.sortOption$.next(this.sortOption);
    this.closeDropdown();
  }

  onSearchChange(searchValue: string): void {
    this.searchTerm = searchValue;
    this.searchTerm$.next(searchValue);
  }

  onSelect(project: ProjectResult): void {
    // Set current project and navigate with project ID
    this.projectFacade.setCurrentProject(project.id);
    this.router.navigate(['/project', project.id]);
  }

  formatRelativeTime(dateString: string): string {
    const targetDate = new Date(dateString);
    const now = new Date();

    const diffMs = Math.abs(now.getTime() - targetDate.getTime());
    const diffMinutes = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    const targetYear = targetDate.getFullYear();
    const currentYear = now.getFullYear();
    const isSameYear = targetYear === currentYear;

    const monthNames = [
      'Jan',
      'Feb',
      'Mar',
      'Apr',
      'May',
      'Jun',
      'Jul',
      'Aug',
      'Sep',
      'Oct',
      'Nov',
      'Dec',
    ];

    const formatDay = (day: number): string => {
      return day < 10 ? `0${day}` : `${day}`;
    };

    if (diffMinutes < 60) {
      return `${diffMinutes} minute${diffMinutes !== 1 ? 's' : ''}`;
    }

    if (diffHours < 24) {
      return `${diffHours} hour${diffHours !== 1 ? 's' : ''}`;
    }

    if (diffDays < 7) {
      return `${diffDays} day${diffDays !== 1 ? 's' : ''}`;
    }

    if (diffDays < 30) {
      const weeks = Math.floor(diffDays / 7);
      return `${weeks} week${weeks !== 1 ? 's' : ''}`;
    }

    const monthDiff = Math.abs(
      (targetYear - currentYear) * 12 + (targetDate.getMonth() - now.getMonth())
    );

    if (monthDiff < 1) {
      const weeks = Math.floor(diffDays / 7);
      return `${weeks} week${weeks !== 1 ? 's' : ''}`;
    }

    if (isSameYear) {
      const month = monthNames[targetDate.getMonth()];
      const day = formatDay(targetDate.getDate());
      return `${month} ${day}`;
    }

    const month = monthNames[targetDate.getMonth()];
    const day = formatDay(targetDate.getDate());
    const year = targetDate.getFullYear();
    return `${day} ${month} ${year}`;
  }

  get currentSortLabel(): string {
    return (
      this.sortOptions.find((opt) => opt.value === this.sortOption)?.label ||
      'Sort'
    );
  }


  toggleDropdown(): void {
    this.isDropdownOpen = !this.isDropdownOpen;
  }

  closeDropdown(): void {
    this.isDropdownOpen = false;
  }

  onRefresh(): void {
    this.projectFacade.loadProjects();
  }


}
