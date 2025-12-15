import { ComponentFixture, TestBed } from '@angular/core/testing';

import { OperationDetail } from './operation-detail';

describe('OperationDetail', () => {
  let component: OperationDetail;
  let fixture: ComponentFixture<OperationDetail>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [OperationDetail]
    })
    .compileComponents();

    fixture = TestBed.createComponent(OperationDetail);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
