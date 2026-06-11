import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./pages/chat/chat.page').then((m) => m.ChatPage),
  },
  { path: '**', redirectTo: '' },
];
