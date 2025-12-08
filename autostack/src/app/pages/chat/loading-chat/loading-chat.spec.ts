import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LoadingChat } from './loading-chat';

describe('LoadingChat', () => {
  let component: LoadingChat;
  let fixture: ComponentFixture<LoadingChat>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LoadingChat]
    })
    .compileComponents();

    fixture = TestBed.createComponent(LoadingChat);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
