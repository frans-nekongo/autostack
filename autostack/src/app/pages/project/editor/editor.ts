import { Component } from '@angular/core';
import { MermaidEditor } from "../../../components/mermaid-editor/mermaid-editor";
import { ComponentMenu } from '../../../components/component-menu/component-menu';
import { ArchitectureCanvas } from '../../../components/architecture-canvas/architecture-canvas';

@Component({
  selector: 'app-editor',
  imports: [ComponentMenu, ArchitectureCanvas,],
  templateUrl: './editor.html',
  styleUrl: './editor.scss'
})
export class Editor {

}
