import { ChangeDetectorRef, Component, OnDestroy, OnInit } from '@angular/core';
import { DemoService } from '../../services/demo/demo-service';
import { Subscription } from 'rxjs';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-demo',
  imports: [CommonModule],
  templateUrl: './demo.html',
  styleUrl: './demo.scss'
})
export class Demo implements OnInit, OnDestroy {
  private subscription: Subscription | undefined;
  responses: any[] = [];
  loading = false;
  error: string | null = null;
  
  constructor(private demoService: DemoService, private changeDetectorRef: ChangeDetectorRef) {}
  
  ngOnInit(): void {
    
  }

  getData() {
    // Reset state
    this.responses = [];
    this.error = null;
    this.loading = true;

    const requestId = `testing-${Date.now()}`;

    // Call the service
    this.subscription = this.demoService.getDemoData(requestId).subscribe({
      next: (response) => {
        this.responses = [...this.responses, response];
        this.changeDetectorRef.detectChanges();
      },
      error: (err) => {
        this.loading = false;
        this.error = err.message || 'Failed to get demo data';
        this.changeDetectorRef.detectChanges();
        console.error('Error:', err);
      },
      complete: () => {
        this.loading = false;
        this.changeDetectorRef.detectChanges();
        console.log('Stream completed');
      }
    });

    console.log(this.responses)
  }
  
  ngOnDestroy(): void {
    if (this.subscription) {
      this.subscription.unsubscribe();
    }
  }
}