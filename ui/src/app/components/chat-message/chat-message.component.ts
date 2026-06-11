import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { IonIcon, IonSpinner } from '@ionic/angular/standalone';

import { ChatMessage } from '../../models/chat.models';

@Component({
  selector: 'app-chat-message',
  standalone: true,
  imports: [CommonModule, IonIcon, IonSpinner],
  template: `
    <div class="msg" [class.user]="message.role === 'user'" [class.assistant]="message.role === 'assistant'">
      <div class="bubble">
        <div class="role">
          <ion-icon
            [name]="message.role === 'user' ? 'person-circle-outline' : 'sparkles-outline'"
          />
          <span>{{ message.role === 'user' ? 'You' : 'Foundry IQ' }}</span>
        </div>

        <ng-container *ngIf="message.pending; else content">
          <ion-spinner name="dots" />
        </ng-container>
        <ng-template #content>
          <div class="text">{{ message.content }}</div>
        </ng-template>

        <ng-container *ngIf="(message.citations?.length ?? 0) > 0">
          <div class="citations">
            <div class="cite-header">
              <ion-icon name="link-outline" />
              <span>Sources</span>
            </div>
            <a
              *ngFor="let c of message.citations"
              class="cite"
              [href]="c.url"
              target="_blank"
              rel="noopener"
            >
              <span class="cite-title">{{ c.title || c.url || 'Source' }}</span>
              <span class="cite-snip muted" *ngIf="c.snippet">{{ c.snippet }}</span>
            </a>
          </div>
        </ng-container>
      </div>
    </div>
  `,
  styles: [
    `
      .msg { display: flex; margin: 8px 0; }
      .msg.user { justify-content: flex-end; }
      .bubble {
        max-width: min(720px, 86%);
        padding: 12px 14px;
        border-radius: 14px;
        background: var(--app-bg-elevated);
        box-shadow: var(--app-shadow-card);
      }
      .msg.user .bubble {
        background: linear-gradient(135deg, var(--ion-color-primary), #6f57f6);
        color: #fff;
      }
      .role { display: flex; align-items: center; gap: 6px; font-size: 12px; opacity: 0.75; margin-bottom: 6px; font-weight: 600; }
      .text { font-size: 14.5px; line-height: 1.55; white-space: pre-wrap; }
      .citations { margin-top: 10px; border-top: 1px solid rgba(127,127,127,0.18); padding-top: 8px; }
      .cite-header { display: flex; align-items: center; gap: 6px; font-size: 12px; opacity: 0.75; margin-bottom: 6px; }
      .cite { display: block; padding: 6px 8px; border-radius: 8px; text-decoration: none; color: inherit; }
      .cite:hover { background: rgba(91, 61, 245, 0.06); }
      .cite-title { display: block; font-weight: 600; font-size: 13px; color: var(--ion-color-primary); }
      .msg.user .cite-title { color: #fff; text-decoration: underline; }
      .cite-snip { display: block; font-size: 12px; margin-top: 2px; }
    `,
  ],
})
export class ChatMessageComponent {
  @Input({ required: true }) message!: ChatMessage;
}
