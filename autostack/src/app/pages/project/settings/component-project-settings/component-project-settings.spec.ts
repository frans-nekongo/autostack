import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ComponentProjectSettings } from './component-project-settings';

describe('ComponentProjectSettings', () => {
  let component: ComponentProjectSettings;
  let fixture: ComponentFixture<ComponentProjectSettings>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ComponentProjectSettings]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ComponentProjectSettings);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
