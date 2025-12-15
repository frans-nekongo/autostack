import { CommonModule } from '@angular/common';
import {
  Component,
  ContentChild,
  EventEmitter,
  Input,
  Output,
  TemplateRef,
} from '@angular/core';
import { NgIcon } from '@ng-icons/core';

export type SideModalSize = 'sm' | 'md' | 'lg' | 'xl';

@Component({
  selector: 'app-side-pane',
  imports: [CommonModule, NgIcon],
  templateUrl: './side-pane.html',
  styleUrl: './side-pane.scss',
})
export class SidePane {
  @Input() isOpen = false;
  @Input() title?: string;
  @Input() position = 'right';
  @Input() size: SideModalSize = 'md';
  @Input() showCloseButton = true;
  @Input() closeOnBackdropClick = true;
  @Input() customWidth?: string;
  @Output() closeModal = new EventEmitter<void>();

  @ContentChild('header') headerTemplate?: TemplateRef<unknown>;
  @ContentChild('body') bodyTemplate?: TemplateRef<unknown>;
  @ContentChild('footer') footerTemplate?: TemplateRef<unknown>;

  get modalClasses(): string {
    const baseClasses =
      'flex flex-col gap-6 items-start absolute top-0 h-full bg-white p-6 pointer-events-auto shadow-lg';

    // Position classes
    const positionClasses =
      this.position === 'right'
        ? 'right-0 rounded-l-lg shadow-[-4px_0_6px_-1px_rgba(0,0,0,0.1)] animate-slide-in-right'
        : 'left-0 rounded-r-lg shadow-[4px_0_6px_-1px_rgba(0,0,0,0.1)] animate-slide-in-left';

    // Size classes
    const sizeClasses = this.getSizeClasses();

    return `${baseClasses} ${positionClasses} ${sizeClasses}`;
  }

  get animationClass(): string {
    return this.position === 'right'
      ? 'animate-slide-in-right'
      : 'animate-slide-in-left';
  }

  private getSizeClasses(): string {
    if (this.customWidth) {
      return '';
    }

    const sizeMap = {
      sm: 'w-80',
      md: 'w-96',
      lg: 'w-1/3',
      xl: 'w-1/2',
    };

    return sizeMap[this.size];
  }

  get customWidthStyle(): { [key: string]: string } | null {
    return this.customWidth ? { width: this.customWidth } : null;
  }

  onClose(): void {
    this.closeModal.emit();
  }

  onBackdropClick(): void {
    if (this.closeOnBackdropClick) {
      this.onClose();
    }
  }

  onModalClick(event: Event): void {
    event.stopPropagation();
  }
}
