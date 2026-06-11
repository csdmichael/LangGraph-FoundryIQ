import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '../../environments/environment';
import {
  ChatRequest,
  ChatResponse,
  SamplePrompt,
} from '../models/chat.models';

@Injectable({ providedIn: 'root' })
export class ChatService {
  private readonly http = inject(HttpClient);
  private readonly base = environment.apiBaseUrl;

  getSamplePrompts(): Observable<SamplePrompt[]> {
    return this.http.get<SamplePrompt[]>(`${this.base}/prompts`);
  }

  sendChat(req: ChatRequest): Observable<ChatResponse> {
    return this.http.post<ChatResponse>(`${this.base}/chat`, req);
  }
}
