import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GeneralProjectSettings } from './general-project-settings';

describe('GeneralProjectSettings', () => {
  let component: GeneralProjectSettings;
  let fixture: ComponentFixture<GeneralProjectSettings>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GeneralProjectSettings]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GeneralProjectSettings);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
