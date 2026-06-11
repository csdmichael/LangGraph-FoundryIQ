import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import {
  IonCard,
  IonCardContent,
  IonAvatar,
  IonIcon,
  IonChip,
  IonLabel,
} from '@ionic/angular/standalone';

@Component({
  selector: 'app-profile-card',
  standalone: true,
  imports: [
    CommonModule,
    IonCard,
    IonCardContent,
    IonAvatar,
    IonIcon,
    IonChip,
    IonLabel,
  ],
  template: `
    <ion-card class="profile-card surface-card">
      <ion-card-content>
        <div class="profile-row">
          <ion-avatar class="avatar">
            <div class="avatar-fallback">MY</div>
          </ion-avatar>
          <div class="who">
            <div class="name">{{ name }}</div>
            <div class="title">{{ title }}</div>
          </div>
        </div>

        <div class="links">
          <a [href]="githubUrl" target="_blank" rel="noopener" class="link">
            <ion-icon name="logo-github" />
            <span>GitHub</span>
          </a>
          <a [href]="linkedinUrl" target="_blank" rel="noopener" class="link">
            <ion-icon name="logo-linkedin" />
            <span>LinkedIn</span>
          </a>
        </div>

        <ion-chip color="primary" outline="true" class="meta">
          <ion-icon name="sparkles-outline" />
          <ion-label>LangGraph × Foundry IQ</ion-label>
        </ion-chip>
      </ion-card-content>
    </ion-card>
  `,
  styles: [
    `
      .profile-card { margin: 0; }
      .profile-row { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
      .avatar {
        width: 56px; height: 56px;
        background: linear-gradient(135deg, var(--ion-color-primary), #8b6cff);
        display: flex; align-items: center; justify-content: center;
        color: #fff; font-weight: 700; font-size: 18px;
      }
      .avatar-fallback { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; }
      .who .name { font-weight: 700; font-size: 16px; }
      .who .title { color: var(--app-text-muted); font-size: 13px; }
      .links { display: flex; gap: 8px; flex-wrap: wrap; margin: 8px 0 4px; }
      .link {
        display: inline-flex; align-items: center; gap: 6px;
        padding: 6px 10px; border-radius: 999px;
        background: rgba(91, 61, 245, 0.08);
        color: var(--ion-color-primary);
        text-decoration: none; font-size: 13px; font-weight: 600;
      }
      .link ion-icon { font-size: 16px; }
      .meta { margin-top: 4px; }
    `,
  ],
})
export class ProfileCardComponent {
  @Input() name = 'Michael Yaacoub';
  @Input() title = 'Sr. Solution Engineer';
  @Input() githubUrl = 'https://github.com/csdmichael';
  @Input() linkedinUrl = 'https://www.linkedin.com/in/michael-yaacoub-7a46436/';
}
