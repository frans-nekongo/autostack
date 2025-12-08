import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ProjectCardSkeleton } from './project-card-skeleton';

describe('ProjectCardSkeleton', () => {
  let component: ProjectCardSkeleton;
  let fixture: ComponentFixture<ProjectCardSkeleton>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ProjectCardSkeleton]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ProjectCardSkeleton);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
