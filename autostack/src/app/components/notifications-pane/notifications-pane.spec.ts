import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NotificationsPane } from './notifications-pane';

describe('NotificationsPane', () => {
  let component: NotificationsPane;
  let fixture: ComponentFixture<NotificationsPane>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NotificationsPane]
    })
    .compileComponents();

    fixture = TestBed.createComponent(NotificationsPane);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
