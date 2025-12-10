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
        // Set fill on the root SVG element
        svgElement.setAttribute('fill', this.color);

        // Override ALL fill attributes on child elements
        svgElement
          .querySelectorAll(
            'path, circle, rect, polygon, polyline, ellipse, line'
          )
          .forEach((el) => {
            // Remove the condition - just set the color on everything
            el.setAttribute('fill', this.color!);
          });
      }
    }

    return new XMLSerializer().serializeToString(doc);
  }
}
