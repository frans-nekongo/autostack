import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VersionControlProjectSettings } from './version-control-project-settings';

describe('VersionControlProjectSettings', () => {
  let component: VersionControlProjectSettings;
  let fixture: ComponentFixture<VersionControlProjectSettings>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [VersionControlProjectSettings]
    })
    .compileComponents();

    fixture = TestBed.createComponent(VersionControlProjectSettings);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
