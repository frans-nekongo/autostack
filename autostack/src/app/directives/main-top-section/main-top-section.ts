import { Directive, TemplateRef } from '@angular/core';

@Directive({
  selector: '[appMainTopSection]'
})
export class MainTopSection {

  constructor(public templateRef: TemplateRef<unknown>) { }

}
