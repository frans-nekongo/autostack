import { Directive, TemplateRef } from '@angular/core';

@Directive({
  selector: '[appTopSection]'
})
export class TopSection {

  constructor(public templateRef: TemplateRef<unknown>) { }

}
