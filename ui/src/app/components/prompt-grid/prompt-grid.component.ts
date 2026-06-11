import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { IonCard, IonCardContent, IonIcon, IonBadge } from '@ionic/angular/standalone';

import { SamplePrompt } from '../../models/chat.models';

@Component({
  selector: 'app-prompt-grid',
  standalone: true,
  imports: [CommonModule, IonCard, IonCardContent, IonIcon, IonBadge],
  template: `
    <div class="prompt-grid" [attr.data-device]="device">
      <ion-card
        *ngFor="let p of prompts; trackBy: trackById"
        class="prompt-card surface-card"
        button="true"
        (click)="picked.emit(p)"
      >
        <ion-card-content>
          <div class="row">
            <div class="icon-bubble">
              <ion-icon [name]="p.icon || 'sparkles-outline'" />
            </div>
            <ion-badge color="light" class="category">{{ p.category }}</ion-badge>
          </div>
          <div class="title">{{ p.title }}</div>
          <div class="prompt muted">{{ p.prompt }}</div>
        </ion-card-content>
      </ion-card>
    </div>
  `,
  styles: [
    `
      .prompt-grid {
        display: grid;
        gap: 12px;
      }
      /* Mobile: 1 column */
      .prompt-grid[data-device='mobile'] { grid-template-columns: 1fr; }
      /* Tablet/iPad: 2 columns */
      .prompt-grid[data-device='tablet'] { grid-template-columns: 1fr 1fr; gap: 14px; }
      /* Desktop: dense 2-column inside the side rail */
      .prompt-grid[data-device='desktop'] { grid-template-columns: 1fr 1fr; gap: 14px; }

      .prompt-card { margin: 0; cursor: pointer; transition: transform 0.15s ease, box-shadow 0.15s ease; }
      .prompt-card:hover { transform: translateY(-2px); box-shadow: 0 14px 32px rgba(16,24,40,0.10); }
      .row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
      .icon-bubble {
        width: 36px; height: 36px; border-radius: 10px;
        background: rgba(91, 61, 245, 0.12);
        color: var(--ion-color-primary);
        display: flex; align-items: center; justify-content: center;
      }
      .icon-bubble ion-icon { font-size: 20px; }
      .category { font-size: 11px; }
      .title { font-weight: 700; font-size: 14px; margin-bottom: 4px; }
      .prompt { font-size: 12.5px; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
    `,
  ],
})
export class PromptGridComponent {
  @Input() prompts: SamplePrompt[] = [];
  @Input() device: 'mobile' | 'tablet' | 'desktop' = 'mobile';
  @Output() picked = new EventEmitter<SamplePrompt>();

  trackById(_: number, p: SamplePrompt): number {
    return p.id;
  }
}
