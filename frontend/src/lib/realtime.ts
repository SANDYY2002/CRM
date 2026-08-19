import type { Message } from './api';

export function connectConversation(
  conversationId: number,
  handlers: { onMessage?: (message: Message) => void; onTyping?: (isTyping: boolean) => void },
) {
  const token = localStorage.getItem('crm_access_token');
  if (!token) return () => undefined;

  const base = import.meta.env.VITE_WS_URL || 'ws://127.0.0.1:8000';
  const socket = new WebSocket(`${base}/ws/conversations/${conversationId}/?token=${encodeURIComponent(token)}`);

  socket.onmessage = (event) => {
    try {
      const payload = JSON.parse(event.data);
      if (payload.type === 'message' && payload.message) handlers.onMessage?.(payload.message as Message);
      if (payload.type === 'typing') handlers.onTyping?.(Boolean(payload.is_typing));
    } catch {
      // Ignore malformed realtime payloads.
    }
  };

  return () => socket.close();
}
