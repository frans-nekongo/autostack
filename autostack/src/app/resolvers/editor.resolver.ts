// editor.resolver.ts
import { Injectable } from '@angular/core';
import { Resolve } from '@angular/router';

@Injectable({ providedIn: 'root' })
export class EditorResolver implements Resolve<boolean> {
  resolve(): Promise<boolean> {
    return new Promise(resolve => {
      setTimeout(() => resolve(true), 50);
    });
  }
}

