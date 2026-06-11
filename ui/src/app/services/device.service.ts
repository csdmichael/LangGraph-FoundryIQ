import { Injectable } from '@angular/core';
import { signal } from '@angular/core';
import { Platform } from '@ionic/angular/standalone';

export type DeviceClass = 'mobile' | 'tablet' | 'desktop';

@Injectable({ providedIn: 'root' })
export class DeviceService {
  readonly device = signal<DeviceClass>('desktop');

  constructor(private readonly platform: Platform) {
    this.recompute();
    this.platform.resize.subscribe(() => this.recompute());
  }

  private recompute(): void {
    const width = this.platform.width();
    if (width < 768) {
      this.device.set('mobile');
    } else if (width < 1200) {
      this.device.set('tablet');
    } else {
      this.device.set('desktop');
    }
  }
}
