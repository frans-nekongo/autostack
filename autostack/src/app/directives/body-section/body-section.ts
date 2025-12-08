import { Directive, TemplateRef } from '@angular/core';

@Directive({
  selector: '[appBodySection]'
})
export class BodySection {

  constructor(public templateRef: TemplateRef<unknown>) { }

}
