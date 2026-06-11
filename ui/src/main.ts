import { bootstrapApplication } from '@angular/platform-browser';
import { RouteReuseStrategy, provideRouter } from '@angular/router';
import {
  IonicRouteStrategy,
  provideIonicAngular,
} from '@ionic/angular/standalone';
import { provideHttpClient, withFetch } from '@angular/common/http';

import { AppComponent } from './app/app.component';
import { routes } from './app/app.routes';

bootstrapApplication(AppComponent, {
  providers: [
    { provide: RouteReuseStrategy, useClass: IonicRouteStrategy },
    provideIonicAngular({
      mode: 'md', // consistent look across web/desktop; iPad gets iOS via per-platform CSS
    }),
    provideRouter(routes),
    provideHttpClient(withFetch()),
  ],
}).catch((err) => console.error(err));
