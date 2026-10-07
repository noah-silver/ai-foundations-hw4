import { authToken } from './auth'
import type { Product } from './api'

export type ChatRole = 'user' | 'assistant'

export interface ChatMessage {
  role: ChatRole
  content: string
  products?: Product[]
}

function authHeaders(): Record<string, string> {
  const token = authToken()
  return token ? { Authorization: `Bearer ${token}` } : {}
}

/**
 * Send a message to the PydanticAI agent.
 *
 * Logged-in shoppers have their history loaded and saved server-side, so we don't
 * resend it. Guests pass their running history so the agent still has context.
 */
export async function sendChatMessage(
  message: string,
  history: ChatMessage[],
  productId?: string | null,
): Promise<ChatMessage> {
  const loggedIn = Boolean(authToken())
  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders() },
    body: JSON.stringify({
      message,
      history: loggedIn ? [] : history.map((m) => ({ role: m.role, content: m.content })),
      product_id: productId ?? null,
    }),
  })
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || 'The Outfitter is unavailable right now.')
  return { role: 'assistant', content: data.reply, products: data.products ?? [] }
}

/** Erase a signed-in shopper's saved conversation on the server. No-op for guests. */
export async function clearServerHistory(): Promise<void> {
  if (!authToken()) return
  await fetch('/api/chat/history', { method: 'DELETE', headers: authHeaders() }).catch(() => {})
}

/** Restore a signed-in shopper's saved conversation. Returns [] for guests or on error. */
export async function loadChatHistory(): Promise<ChatMessage[]> {
  if (!authToken()) return []
  try {
    const res = await fetch('/api/chat/history', { headers: authHeaders() })
    if (!res.ok) return []
    const data = await res.json()
    return (data.messages ?? []) as ChatMessage[]
  } catch {
    return []
  }
}
