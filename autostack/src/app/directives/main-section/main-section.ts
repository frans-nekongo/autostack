import { Directive, TemplateRef } from '@angular/core';

@Directive({
  selector: '[appMainSection]'
})
export class MainSection {

  constructor(public templateRef: TemplateRef<unknown>) { }

}
