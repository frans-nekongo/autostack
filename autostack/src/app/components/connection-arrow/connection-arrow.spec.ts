import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ConnectionArrow } from './connection-arrow';

describe('ConnectionArrow', () => {
  let component: ConnectionArrow;
  let fixture: ComponentFixture<ConnectionArrow>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ConnectionArrow]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ConnectionArrow);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
