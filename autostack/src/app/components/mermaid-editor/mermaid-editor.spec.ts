import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MermaidEditor } from './mermaid-editor';

describe('MermaidEditor', () => {
  let component: MermaidEditor;
  let fixture: ComponentFixture<MermaidEditor>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MermaidEditor]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MermaidEditor);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
