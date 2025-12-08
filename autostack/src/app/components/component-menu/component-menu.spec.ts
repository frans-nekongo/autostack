import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ComponentMenu } from './component-menu';

describe('ComponentMenu', () => {
  let component: ComponentMenu;
  let fixture: ComponentFixture<ComponentMenu>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ComponentMenu]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ComponentMenu);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
