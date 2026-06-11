import { Component } from '@angular/core';
import { IonApp, IonRouterOutlet } from '@ionic/angular/standalone';
import { addIcons } from 'ionicons';
import {
  send,
  sendOutline,
  sparklesOutline,
  shieldCheckmarkOutline,
  briefcaseOutline,
  analyticsOutline,
  peopleOutline,
  gitNetworkOutline,
  bookOutline,
  cloudUploadOutline,
  schoolOutline,
  documentTextOutline,
  rocketOutline,
  logoGithub,
  logoLinkedin,
  personCircleOutline,
  chatbubblesOutline,
  closeOutline,
  menuOutline,
  refreshOutline,
  linkOutline,
} from 'ionicons/icons';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [IonApp, IonRouterOutlet],
  template: `<ion-app><ion-router-outlet /></ion-app>`,
})
export class AppComponent {
  constructor() {
    addIcons({
      send,
      'send-outline': sendOutline,
      'sparkles-outline': sparklesOutline,
      'shield-checkmark-outline': shieldCheckmarkOutline,
      'briefcase-outline': briefcaseOutline,
      'analytics-outline': analyticsOutline,
      'people-outline': peopleOutline,
      'git-network-outline': gitNetworkOutline,
      'book-outline': bookOutline,
      'cloud-upload-outline': cloudUploadOutline,
      'school-outline': schoolOutline,
      'document-text-outline': documentTextOutline,
      'rocket-outline': rocketOutline,
      'logo-github': logoGithub,
      'logo-linkedin': logoLinkedin,
      'person-circle-outline': personCircleOutline,
      'chatbubbles-outline': chatbubblesOutline,
      'close-outline': closeOutline,
      'menu-outline': menuOutline,
      'refresh-outline': refreshOutline,
      'link-outline': linkOutline,
    });
  }
}
