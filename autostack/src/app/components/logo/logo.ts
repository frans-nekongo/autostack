import { HttpClient } from '@angular/common/http';
import {
  Component,
  inject,
  Input,
  OnChanges,
  SimpleChanges,
} from '@angular/core';
import { DomSanitizer } from '@angular/platform-browser';

@Component({
  selector: 'app-logo',
  imports: [],
  templateUrl: './logo.html',
  styleUrl: './logo.scss',
})
export class Logo implements OnChanges {
  private httpClient = inject(HttpClient);
  private sanitiser = inject(DomSanitizer);

  @Input() name?: string;
  @Input() width?: string;
  @Input() height?: string;
  @Input() color?: string;

  svgIcon: any;
  ngOnChanges(): void {
    if (!this.name) {
      this.svgIcon = '';
      return;
    }

    this.httpClient
      .get(`assets/svg/${this.name}.svg`, { responseType: 'text' })
      .subscribe((value) => {
        this.svgIcon = this.sanitiser.bypassSecurityTrustHtml(
          this.modifySvg(value)
        );
      });
  }

  private modifySvg(svg: string): string {
    const parser = new DOMParser();
    const doc = parser.parseFromString(svg, 'image/svg+xml');
    const svgElement = doc.querySelector('svg');

    if (svgElement) {
      if (this.width) {
        svgElement.setAttribute('width', this.width);
      }
      if (this.height) {
        svgElement.setAttribute('height', this.height);
      }
      if (this.color) {
        svgElement.setAttribute('fill', this.color);
        // Also set currentColor for paths that inherit color
        svgElement
          .querySelectorAll('path, circle, rect, polygon, polyline')
          .forEach((el) => {
            if (
              !el.hasAttribute('fill') ||
              el.getAttribute('fill') === 'currentColor'
            ) {
              el.setAttribute('fill', this.color!);
            }
          });
      }
    }

    return new XMLSerializer().serializeToString(doc);
  }
}
