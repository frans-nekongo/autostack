import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Production } from './production';

describe('Production', () => {
  let component: Production;
  let fixture: ComponentFixture<Production>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Production]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Production);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
