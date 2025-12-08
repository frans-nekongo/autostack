import { Directive, TemplateRef } from '@angular/core';

@Directive({
  selector: '[appLeftSection]'
})
export class LeftSection {

  constructor(public templateRef: TemplateRef<unknown>) { }

}
