import { CommonModule } from '@angular/common';
import { Component, inject, OnInit, ViewChild, ElementRef, AfterViewInit, OnDestroy } from '@angular/core';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import mermaid from 'mermaid';
import { FormsModule } from '@angular/forms';
import { SafeHtmlPipe } from '../../pipes/safe-html/safe-html-pipe';

// CodeMirror imports
import { EditorView, basicSetup } from 'codemirror';
import { EditorState } from '@codemirror/state';
import { javascript } from '@codemirror/lang-javascript';
import { StreamLanguage, LanguageSupport } from '@codemirror/language';
import { tags as t } from '@lezer/highlight';
import { HighlightStyle, syntaxHighlighting } from '@codemirror/language';

@Component({
  selector: 'app-mermaid-editor',
  imports: [CommonModule, FormsModule],
  templateUrl: './mermaid-editor.html',
  styleUrl: './mermaid-editor.scss'
})
export class MermaidEditor implements OnInit, AfterViewInit, OnDestroy {
  @ViewChild('editorContainer', { static: true }) editorContainer!: ElementRef<HTMLDivElement>;
  @ViewChild('resizer', { static: true }) resizer!: ElementRef<HTMLDivElement>;
  @ViewChild('leftPanel', { static: true }) leftPanel!: ElementRef<HTMLDivElement>;
  @ViewChild('rightPanel', { static: true }) rightPanel!: ElementRef<HTMLDivElement>;
  
  private sanitizer: DomSanitizer = inject(DomSanitizer);
  private renderCounter: number = 0;
  private editorView: EditorView | null = null;
  private isResizing = false;

  mermaidCode: string = `C4Container
    title Container Diagram
    
    Container_Boundary(microservices, "microservices") {
        Container(api, "API Service", "Node.js", "REST API")
        Container(db, "Database", "PostgreSQL", "Data storage")
    }`;
  renderedSvg: SafeHtml = '';
  errorMessage: string = '';
  
  ngOnInit(): void {
    mermaid.initialize({
      startOnLoad: false,
      theme: 'default',
      flowchart: { useMaxWidth: true },
      securityLevel: 'loose'
    });
  }

  ngAfterViewInit(): void {
    this.initializeCodeMirror();
    this.initializeResizer();
    this.renderDiagram();
  }

  ngOnDestroy(): void {
    if (this.editorView) {
      this.editorView.destroy();
    }
    this.removeResizeListeners();
  }

  private initializeCodeMirror(): void {
    // Custom Mermaid language definition
    const mermaidLanguage = StreamLanguage.define({
      name: 'mermaid',
      startState: () => ({}),
      token: (stream, state) => {
        // Keywords - Only C4Container supported
        if (stream.match(/\b(C4Container|title|Container_Boundary|Container|Person|System|Rel|UpdateElementStyle|UpdateRelStyle)\b/)) {
          return 'keyword';
        }
        
        // Directions
        if (stream.match(/\b(TD|TB|BT|RL|LR|T|B|L|R)\b/)) {
          return 'builtin';
        }
        
        // Arrows and connections
        if (stream.match(/-->|---|-\.-|==>|===/)) {
          return 'operator';
        }
        
        // Node definitions with brackets
        if (stream.match(/\[[^\]]+\]/)) {
          return 'string';
        }
        
        // Node definitions with parentheses
        if (stream.match(/\([^)]+\)/)) {
          return 'string';
        }
        
        // Node definitions with curly braces
        if (stream.match(/\{[^}]+\}/)) {
          return 'string';
        }
        
        // Node definitions with double quotes
        if (stream.match(/"[^"]*"/)) {
          return 'string';
        }
        
        // Node IDs
        if (stream.match(/\b[A-Za-z_][A-Za-z0-9_]*\b/)) {
          return 'variable';
        }
        
        // Comments
        if (stream.match(/%%.*$/)) {
          return 'comment';
        }
        
        stream.next();
        return null;
      }
    });

    // Custom highlighting theme for Mermaid
    const mermaidHighlightStyle = HighlightStyle.define([
      { tag: t.keyword, color: '#0969da', fontWeight: 'bold' }, // Blue for keywords
      // { tag: t.builtin, color: '#d73a49', fontWeight: 'bold' }, // Red for directions
      { tag: t.operator, color: '#cf222e' }, // Red for arrows
      { tag: t.string, color: '#0a3069', fontWeight: '500' }, // Dark blue for node labels
      { tag: t.variableName, color: '#8250df' }, // Purple for node IDs
      { tag: t.comment, color: '#656d76', fontStyle: 'italic' }, // Gray for comments
    ]);

    const state = EditorState.create({
      doc: this.mermaidCode,
      extensions: [
        basicSetup,
        new LanguageSupport(mermaidLanguage),
        syntaxHighlighting(mermaidHighlightStyle),
        EditorView.theme({
          '&': {
            height: '100%',
            fontSize: '14px',
            fontFamily: 'ui-monospace, SFMono-Regular, "SF Mono", Consolas, "Liberation Mono", Menlo, monospace'
          },
          '.cm-content': {
            padding: '16px',
            lineHeight: '1.6'
          },
          '.cm-focused': {
            outline: 'none'
          },
          '.cm-editor': {
            height: '100%'
          },
          '.cm-scroller': {
            height: '100%'
          },
          '.cm-line': {
            padding: '0 4px'
          }
        }),
        EditorView.updateListener.of((update) => {
          if (update.docChanged) {
            this.mermaidCode = update.state.doc.toString();
            this.renderDiagram();
          }
        })
      ]
    });

    this.editorView = new EditorView({
      state,
      parent: this.editorContainer.nativeElement
    });
  }

  private initializeResizer(): void {
    const resizer = this.resizer.nativeElement;
    const leftPanel = this.leftPanel.nativeElement;
    const rightPanel = this.rightPanel.nativeElement;

    const startResize = (e: MouseEvent) => {
      this.isResizing = true;
      document.addEventListener('mousemove', this.doResize.bind(this));
      document.addEventListener('mouseup', this.stopResize.bind(this));
      e.preventDefault();
    };

    resizer.addEventListener('mousedown', startResize);
  }

  private doResize(e: MouseEvent): void {
    if (!this.isResizing) return;

    const container = this.leftPanel.nativeElement.parentElement;
    const containerRect = container!.getBoundingClientRect();
    const newLeftWidth = ((e.clientX - containerRect.left) / containerRect.width) * 100;

    // Constrain between 20% and 80%
    const constrainedWidth = Math.min(Math.max(newLeftWidth, 20), 80);

    this.leftPanel.nativeElement.style.width = `${constrainedWidth}%`;
    this.rightPanel.nativeElement.style.width = `${100 - constrainedWidth}%`;
  }

  private stopResize(): void {
    this.isResizing = false;
    document.removeEventListener('mousemove', this.doResize);
    document.removeEventListener('mouseup', this.stopResize);
  }

  private removeResizeListeners(): void {
    document.removeEventListener('mousemove', this.doResize);
    document.removeEventListener('mouseup', this.stopResize);
  }

  private validateC4ContainerDiagram(code: string): boolean {
    const lines = code.split('\n').map(line => line.trim()).filter(line => line.length > 0);
    
    // Check if first non-empty line starts with C4Container
    const firstLine = lines.find(line => !line.startsWith('%%'));
    if (!firstLine || !firstLine.toLowerCase().startsWith('c4container')) {
      return false;
    }
    
    // Check if there's a Container_Boundary with "microservices"
    const hasMicroservicesBoundary = lines.some(line => {
      const boundaryMatch = line.match(/Container_Boundary\s*\([^,]+,\s*['"](.*?)['"][^)]*\)/);
      return boundaryMatch && boundaryMatch[1].toLowerCase().includes('microservices');
    });
    
    return hasMicroservicesBoundary;
  }

    renderDiagram(): void {
      this.errorMessage = '';
      if (!this.mermaidCode.trim()) {
        this.renderedSvg = '';
        return;
      }

      // Validate that the diagram is a C4Container diagram
      if (!this.validateC4ContainerDiagram(this.mermaidCode)) {
        this.errorMessage = 'Unsupported diagram type. Only C4Container diagrams are supported.';
        this.renderedSvg = this.sanitizer.bypassSecurityTrustHtml(
          '<div class="text-center p-8"><div class="text-red-600 text-lg font-semibold">Diagram Unsupported</div><div class="text-gray-600 mt-2">Only C4Container diagrams with Container_Boundary("microservices") are supported.</div></div>'
        );
        return;
      }

      const uniqueId = `mermaid-temp-${this.renderCounter++}`;
      
      mermaid.render(uniqueId, this.mermaidCode)
        .then(({ svg }) => {
          this.renderedSvg = this.sanitizer.bypassSecurityTrustHtml(svg);
        })
        .catch((error) => {
          this.errorMessage = 'Invalid Mermaid syntax: ' + error.message;
          this.renderedSvg = '';
        });
    }

  // Method to update editor content programmatically if needed
  updateEditorContent(newContent: string): void {
    if (this.editorView) {
      const transaction = this.editorView.state.update({
        changes: {
          from: 0,
          to: this.editorView.state.doc.length,
          insert: newContent
        }
      });
      this.editorView.dispatch(transaction);
    }
  }
}