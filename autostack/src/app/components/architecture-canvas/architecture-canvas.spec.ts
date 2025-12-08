import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ArchitectureCanvas } from './architecture-canvas';

describe('ArchitectureCanvas', () => {
  let component: ArchitectureCanvas;
  let fixture: ComponentFixture<ArchitectureCanvas>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ArchitectureCanvas]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ArchitectureCanvas);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
