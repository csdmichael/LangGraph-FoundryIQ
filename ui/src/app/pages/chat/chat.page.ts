import { Component, ElementRef, OnInit, ViewChild, computed, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import {
  IonContent,
  IonHeader,
  IonToolbar,
  IonTitle,
  IonButtons,
  IonButton,
  IonIcon,
  IonMenu,
  IonMenuButton,
  IonFooter,
  IonTextarea,
  MenuController,
} from '@ionic/angular/standalone';

import { ChatMessageComponent } from '../../components/chat-message/chat-message.component';
import { ProfileCardComponent } from '../../components/profile-card/profile-card.component';
import { PromptGridComponent } from '../../components/prompt-grid/prompt-grid.component';
import { ChatService } from '../../services/chat.service';
import { DeviceService } from '../../services/device.service';
import { ChatMessage, SamplePrompt } from '../../models/chat.models';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    IonContent,
    IonHeader,
    IonToolbar,
    IonTitle,
    IonButtons,
    IonButton,
    IonIcon,
    IonMenu,
    IonMenuButton,
    IonFooter,
    IonTextarea,
    ChatMessageComponent,
    ProfileCardComponent,
    PromptGridComponent,
  ],
  templateUrl: './chat.page.html',
  styleUrl: './chat.page.scss',
})
export class ChatPage implements OnInit {
  private readonly chatService = inject(ChatService);
  private readonly menuCtrl = inject(MenuController);
  readonly deviceService = inject(DeviceService);

  @ViewChild('scrollContainer', { static: false }) scrollContainer?: ElementRef<HTMLElement>;

  readonly messages = signal<ChatMessage[]>([]);
  readonly samplePrompts = signal<SamplePrompt[]>([]);
  readonly threadId = signal<string | null>(null);
  readonly sending = signal(false);
  draft = '';

  readonly device = computed(() => this.deviceService.device());
  readonly isMobile = computed(() => this.device() === 'mobile');
  readonly isTablet = computed(() => this.device() === 'tablet');
  readonly isDesktop = computed(() => this.device() === 'desktop');

  ngOnInit(): void {
    this.chatService.getSamplePrompts().subscribe({
      next: (prompts) => this.samplePrompts.set(prompts),
      error: (err) => console.error('Failed to load prompts', err),
    });
  }

  pickPrompt(prompt: SamplePrompt): void {
    this.draft = prompt.prompt;
    if (this.isMobile()) {
      // On phone the prompts live in the side menu — close it after pick
      this.menuCtrl.close('side-menu').catch(() => undefined);
    }
    this.send();
  }

  newConversation(): void {
    this.messages.set([]);
    this.threadId.set(null);
    this.draft = '';
  }

  send(): void {
    const prompt = this.draft.trim();
    if (!prompt || this.sending()) return;

    const userMsg: ChatMessage = {
      role: 'user',
      content: prompt,
      ts: new Date().toISOString(),
    };
    const placeholder: ChatMessage = {
      role: 'assistant',
      content: '',
      pending: true,
    };

    this.messages.update((m) => [...m, userMsg, placeholder]);
    this.draft = '';
    this.sending.set(true);
    queueMicrotask(() => this.scrollToBottom());

    const history = this.messages()
      .slice(0, -2) // exclude the just-added user+placeholder
      .filter((m) => !m.pending)
      .map((m) => ({ role: m.role, content: m.content }));

    this.chatService
      .sendChat({
        prompt,
        thread_id: this.threadId(),
        history,
      })
      .subscribe({
        next: (resp) => {
          this.messages.update((m) => {
            const copy = [...m];
            copy[copy.length - 1] = {
              role: 'assistant',
              content: resp.answer || '(no response)',
              citations: resp.citations,
              ts: resp.timestamp,
            };
            return copy;
          });
          if (resp.thread_id) this.threadId.set(resp.thread_id);
          this.sending.set(false);
          queueMicrotask(() => this.scrollToBottom());
        },
        error: (err) => {
          this.messages.update((m) => {
            const copy = [...m];
            copy[copy.length - 1] = {
              role: 'assistant',
              content:
                'Sorry — the Foundry agent could not be reached. ' +
                (err?.error?.detail || err?.message || ''),
            };
            return copy;
          });
          this.sending.set(false);
        },
      });
  }

  onKey(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.send();
    }
  }

  private scrollToBottom(): void {
    const el = this.scrollContainer?.nativeElement;
    if (el) el.scrollTop = el.scrollHeight;
  }
}
