import { useEffect, useRef, useState, type FormEvent } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { clearServerHistory, loadChatHistory, sendChatMessage, type ChatMessage } from '../chat'
import { formatPrice, type Product } from '../api'
import { useAuth } from '../auth'
import { useChatResults } from '../chatResults'

const GREETING: ChatMessage = {
  role: 'assistant',
  content: 'Good afternoon, and welcome to Campus Customs. Looking for something to wear to the Bowl?',
}

// Shown in the empty chat so shoppers discover what they can ask.
const SUGGESTIONS = ['Show me your hoodies', 'Gifts for a Yale dad', 'What crewnecks do you have?', 'Anything under $50?']

const GUEST_STORAGE_KEY = 'cc_guest_chat'

function loadGuestChat(): ChatMessage[] {
  try {
    const saved = JSON.parse(localStorage.getItem(GUEST_STORAGE_KEY) || 'null')
    return Array.isArray(saved) && saved.length ? saved : [GREETING]
  } catch {
    return [GREETING]
  }
}

function ProductCards({ products }: { products: Product[] }) {
  return (
    <div className="chat-cards">
      {products.map((p) => (
        <Link key={p.product_id} to={`/products/${p.product_id}`} className="chat-card">
          <img src={p.image_url} alt={p.name} loading="lazy" />
          <span className="chat-card-name">{p.name}</span>
          <span className="chat-card-price">{formatPrice(p.price)}</span>
        </Link>
      ))}
    </div>
  )
}

export default function ChatWidget() {
  const { user } = useAuth()
  const { setResults } = useChatResults()
  const navigate = useNavigate()
  const location = useLocation()
  const [open, setOpen] = useState(false)
  // Lazy-init from localStorage so a guest's saved chat is present on the very first render
  // (initializing to the greeting here would let the save-effect clobber it before restore).
  const [messages, setMessages] = useState<ChatMessage[]>(loadGuestChat)
  const [input, setInput] = useState('')
  const [thinking, setThinking] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  // If the shopper is on a product page, pass that product so "this"/"it" resolves.
  const productMatch = location.pathname.match(/^\/products\/(.+)$/)
  const currentProductId = productMatch ? decodeURIComponent(productMatch[1]) : null

  // Restore conversation: signed-in shoppers from the DB, guests from localStorage (so a page
  // reload doesn't wipe their chat). Reset to the greeting when neither has anything saved.
  useEffect(() => {
    let active = true
    if (user) {
      loadChatHistory().then((saved) => {
        if (active) setMessages(saved.length ? saved : [GREETING])
      })
    } else {
      setMessages(loadGuestChat())
    }
    return () => {
      active = false
    }
  }, [user])

  // Persist a guest's conversation across reloads (logged-in history lives in the DB instead).
  useEffect(() => {
    if (!user) localStorage.setItem(GUEST_STORAGE_KEY, JSON.stringify(messages))
  }, [messages, user])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, thinking, open])

  async function sendText(text: string) {
    const trimmed = text.trim()
    if (!trimmed || thinking) return
    const history = [...messages, { role: 'user' as const, content: trimmed }]
    setMessages(history)
    setInput('')
    setThinking(true)
    try {
      const reply = await sendChatMessage(trimmed, history, currentProductId)
      setMessages((m) => [...m, reply])
      if (reply.products && reply.products.length > 0) {
        setResults(reply.products, trimmed)
        const onlyCurrent =
          reply.products.length === 1 && reply.products[0].product_id === currentProductId
        if (!onlyCurrent) navigate('/shop')
      }
    } catch (err) {
      setMessages((m) => [
        ...m,
        { role: 'assistant', content: err instanceof Error ? err.message : 'Something went wrong. Please try again.' },
      ])
    } finally {
      setThinking(false)
    }
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    void sendText(input)
  }

  async function handleClear() {
    if (thinking) return
    localStorage.removeItem(GUEST_STORAGE_KEY) // clear a guest's saved chat
    await clearServerHistory() // and a signed-in shopper's saved chat on the server
    setMessages([GREETING])
    setInput('')
  }

  const showSuggestions = messages.length <= 1 && !thinking

  return (
    <div className="chat">
      {open && (
        <section className="chat-panel" aria-label="Chat with Campus Customs">
          <header className="chat-header">
            <div>
              <p className="chat-title">The Outfitter</p>
              <p className="chat-sub">Ask about fits, colors, and sizes</p>
            </div>
            <div className="chat-header-actions">
              {messages.length > 1 && (
                <button className="chat-clear" onClick={() => void handleClear()} disabled={thinking}>
                  Clear
                </button>
              )}
              <button className="chat-close" onClick={() => setOpen(false)} aria-label="Close chat">
                ×
              </button>
            </div>
          </header>
          <div className="chat-body">
            {messages.map((m, i) => (
              <div key={i} className={`chat-msg-wrap ${m.role}`}>
                <div className={`chat-msg ${m.role}`}>{m.content}</div>
                {m.products && m.products.length > 0 && <ProductCards products={m.products} />}
              </div>
            ))}
            {showSuggestions && (
              <div className="chat-suggestions">
                {SUGGESTIONS.map((s) => (
                  <button key={s} className="chat-suggestion" onClick={() => void sendText(s)}>
                    {s}
                  </button>
                ))}
              </div>
            )}
            {thinking && (
              <div className="chat-msg assistant thinking" aria-label="Thinking">
                <span />
                <span />
                <span />
              </div>
            )}
            <div ref={bottomRef} />
          </div>
          <form className="chat-input" onSubmit={handleSubmit}>
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question…"
              aria-label="Message"
              autoFocus
            />
            <button type="submit" disabled={!input.trim() || thinking}>
              Send
            </button>
          </form>
        </section>
      )}
      <button className="chat-launcher" onClick={() => setOpen((o) => !o)} aria-expanded={open}>
        {open ? 'Close' : 'Ask the Outfitter'}
      </button>
    </div>
  )
}
