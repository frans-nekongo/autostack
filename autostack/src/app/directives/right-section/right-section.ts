import { Directive, TemplateRef } from '@angular/core';

@Directive({
  selector: '[appRightSection]'
})
export class RightSection {

  constructor(public templateRef: TemplateRef<unknown>) { }
}
