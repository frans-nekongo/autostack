import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ChatSideBar } from './chat-side-bar';

describe('ChatSideBar', () => {
  let component: ChatSideBar;
  let fixture: ComponentFixture<ChatSideBar>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ChatSideBar]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ChatSideBar);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
