import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ProjectSettingsSidebar } from './project-settings-sidebar';

describe('ProjectSettingsSidebar', () => {
  let component: ProjectSettingsSidebar;
  let fixture: ComponentFixture<ProjectSettingsSidebar>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ProjectSettingsSidebar]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ProjectSettingsSidebar);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
