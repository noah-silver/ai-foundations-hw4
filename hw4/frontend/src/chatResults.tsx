import { createContext, useContext, useMemo, useState, type ReactNode } from 'react'
import type { Product } from './api'

/**
 * Shared state for products the chat agent has surfaced. The chat widget writes to it when a
 * reply includes products; the /shop page reads from it and renders them as cards. This is how
 * a chat search "updates the page" instead of only filling the chat bubble.
 */
interface ChatResultsValue {
  products: Product[]
  query: string
  setResults: (products: Product[], query: string) => void
}

const ChatResultsContext = createContext<ChatResultsValue | null>(null)

export function ChatResultsProvider({ children }: { children: ReactNode }) {
  const [products, setProducts] = useState<Product[]>([])
  const [query, setQuery] = useState('')

  const value = useMemo<ChatResultsValue>(
    () => ({
      products,
      query,
      setResults: (next, q) => {
        setProducts(next)
        setQuery(q)
      },
    }),
    [products, query],
  )

  return <ChatResultsContext.Provider value={value}>{children}</ChatResultsContext.Provider>
}

export function useChatResults(): ChatResultsValue {
  const ctx = useContext(ChatResultsContext)
  if (!ctx) throw new Error('useChatResults must be used within ChatResultsProvider')
  return ctx
}
