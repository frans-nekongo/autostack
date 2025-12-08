import { Component, ContentChild, Input } from '@angular/core';
import { TopSection } from '../../directives/top-section/top-section';
import { MainTopSection } from '../../directives/main-top-section/main-top-section';
import { BodySection } from '../../directives/body-section/body-section';
import { LeftSection } from '../../directives/left-section/left-section';
import { RightSection } from '../../directives/right-section/right-section';
import { CommonModule } from '@angular/common';
import { Header } from "../../components/header/header";

@Component({
  selector: 'app-main-layout',
  imports: [CommonModule, ],
  templateUrl: './main-layout.html',
  styleUrl: './main-layout.scss',
})
export class MainLayout {
  @ContentChild(TopSection) topSection!: TopSection;
  @ContentChild(MainTopSection) mainTopSection!: MainTopSection;
  @ContentChild(LeftSection) leftSection!: LeftSection;
  @ContentChild(RightSection) rightSection!: RightSection;
  @ContentChild(BodySection) bodySection!: BodySection;

  @Input() leftWidth: number = 50;
  @Input() rightWidth: number = 50;

  get gridCols(): string {
    if (this.leftSection && this.rightSection) {
      return `1fr ${this.leftWidth}% ${this.rightWidth}%`;
    } else if (this.leftSection) {
      return '1fr';
    } else if (this.rightSection) {
      return '1fr';
    }

    return '1fr';
  }
}
