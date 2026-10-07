# Usability improvements

Usability improvements for Campus Customs: on the front end and in the agent/backend. The first
two of each were the original set; a clear-chat control (front-end #3) was added afterward. Each
note says what we added and why it helps a shopper or the business.

## Front-end

### 1. Starter suggestion chips in the chat

**What:** When the chat is empty (just the greeting), it now shows a row of clickable starter
prompts — "Show me your hoodies", "Gifts for a Yale dad", "What crewnecks do you have?",
"Anything under $50?". Clicking one sends it immediately.
(`frontend/src/components/ChatWidget.tsx`)

**Why it helps:** A blank chat box is a cold start — many shoppers don't realize the Outfitter
can search by category, gift recipient, or budget. The chips teach what's possible in one
glance and turn a click into a first query, so more visitors actually engage the assistant
instead of bouncing. For the business, that means more guided product discovery and fewer
dead-end sessions.

### 2. Guest chat that survives a page reload

**What:** A guest's conversation is now saved to the browser's `localStorage` and restored when
the page reloads, so refreshing or reopening the site no longer wipes the chat. (Signed-in
shoppers already have their history saved server-side; this closes the gap for everyone else.)
We fixed a subtle mount-time race so the saved chat is loaded on the very first render.

**Why it helps:** Shoppers often reload, follow a link, or come back a minute later. Losing the
whole conversation — the products the Outfitter found, the back-and-forth about sizes — is
frustrating and makes people start over. Persisting it keeps their place and keeps the
recommended products one scroll away, which protects momentum toward a purchase.

### 3. Clear-chat / start-over control

**What:** A **Clear** button in the chat header (shown whenever there's a conversation) resets
the chat to the greeting, which brings the starter suggestion chips back. It also erases the
saved copy so a reopen or reload stays fresh — `localStorage` for guests, and a
`DELETE /api/chat/history` call for signed-in shoppers.
(`frontend/src/components/ChatWidget.tsx`, `backend/main.py`)

**Why it helps:** Shoppers switch tasks — done hunting for a hoodie, now shopping for a gift.
Without a reset, the old conversation (and its product context) lingers and the helpful starter
chips never return. A one-click clear lets them start a clean line of questions, and restoring
the chips re-exposes what the Outfitter can do. For signed-in shoppers it also gives them
control over their stored history, which is good for trust.

## Agent / back-end

### 3. Smarter product search: budget filter + in-stock-first ranking

**What:** `search_catalogue` now takes optional `max_price` / `min_price`, and the agent is told
to use them for budget questions ("hoodies under $70") instead of eyeballing prices. Results are
also ranked **in-stock first** and each carries an `in_stock` flag, and the prompt tells the
agent to prefer available items and to say so when something is sold out.
(`backend/tools.py`, `backend/agent.py`, `backend/prompts/prompt.md`)

**Why it helps:** Budget filtering at the database level makes "under $X" answers exact rather
than approximate, so shoppers trust the numbers. In-stock-first ranking means the Outfitter
leads with things the shopper can actually buy today, instead of recommending a sold-out item
and sending them to a dead end. For the business, that steers demand toward sellable inventory
and reduces "it was out of stock" disappointment.

### 4. Chat query analytics for the business

**What:** Every chat question is logged to a new `chat_queries` table (the query text, how many
products it surfaced, the user if signed in, and a timestamp). A `GET /api/insights/top-queries`
endpoint summarizes the most-asked questions and — importantly — the ones that returned **zero**
matches. (`backend/main.py`)

**Why it helps:** This turns the chatbot into a demand sensor. The most-asked queries show what
shoppers want; the **no-result** queries are a gap list — things people ask for that the shop
doesn't carry or can't be found by the current search (e.g. "umbrellas", a specific team). That
directly informs buying, merchandising, and search-tuning decisions. (In production this
endpoint would be gated to staff accounts; it reads aggregate data, never message contents of
other customers.)

## How to see them

- Chips & guest persistence: open **Ask the Outfitter**, note the starter chips; send a message,
  reload the page, and the conversation is still there.
- Clear chat: after a conversation, click **Clear** in the chat header — it resets to the
  greeting and the starter chips reappear.
- Budget/in-stock search: ask "what hoodies do you have under $60?" — only sub-$60, in-stock
  items come back.
- Analytics: after some chats, `curl http://localhost:8000/api/insights/top-queries`.
