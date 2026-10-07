# Design

How Campus Customs is styled to feel like a real storefront, and why each choice helps a
shopper stay and buy. Concrete changes, grouped by the elements the brief called out. The core
system lives in `frontend/src/index.css`.

## Fonts & type hierarchy

- **Two-typeface system:** a high-contrast serif (**Cormorant Garamond**) for headlines and
  product names, and a clean sans (**Inter**) for body, labels, and UI. The serif reads as
  heritage/Ivy; the sans keeps prices, sizes, and buttons legible. The pairing signals "an
  established shop," not a generic template.
- **A real scale, not just bigger/smaller:** fluid `clamp()` sizes for H1/H2 so headlines stay
  dramatic on desktop and controlled on mobile; small uppercase **eyebrow** labels
  (letter-spaced gold) sit above headings to orient the eye.
- **Gold accent rule** under section and page headings gives each block a clear "start here"
  marker, so a scanning shopper always knows where a new section begins.

Why it helps: clear hierarchy lets a shopper find the price, the name, and the call to action in
a glance — less friction, faster path to a product page.

## Color

- **Disciplined palette:** deep navy (`--navy`), warm cream/paper backgrounds, and a single
  metallic **gold** accent, with a restrained red/green only for sold-out / in-stock status.
  Restraint reads as premium; one accent color keeps calls to action obvious.
- **Depth, not flatness:** layered backgrounds (navy hero, cream page, paper cards), soft
  shadows that deepen on hover (`--shadow-lift`), and a radial gold highlight washed across the
  hero so it feels lit rather than printed.

Why it helps: a confident, consistent palette builds trust ("this is a legit store"), and the
lone gold accent funnels attention to buttons and links that move a shopper forward.

## Hierarchy & layout

- **Sticky header with a promo ribbon** ("Kickoff Weekend… free shipping over $100") keeps
  navigation and an incentive on screen at all times.
- **Storefront rhythm on the home page:** hero → featured "Kickoff Lineup" → value pillars →
  rivalry call-out, each a distinct band, so the page tells a story instead of dumping a grid.
- **Product grid** uses square, consistent image frames so differently-shaped garments line up
  tidily — a tidy grid reads as curated inventory.

Why it helps: a guided page keeps a visitor scrolling (and discovering product) rather than
bouncing off a wall of thumbnails.

## Motion

All motion is subtle, fast, and wrapped in `@media (prefers-reduced-motion: no-preference)` so
it never fights accessibility.

- **Entrance:** hero text fades up in a short stagger; product cards fade up as the grid
  mounts; pillars ease in. The page feels alive on arrival.
- **Micro-interactions:** buttons lift on hover and settle on click; links transition to gold;
  the brand mark tilts on hover; focus-visible rings in gold for keyboard users.
- **Chat:** the panel slides up when opened, each message pops in, and the launcher gives a few
  gold attention-pulses shortly after load to invite a first question.

Why it helps: motion gives feedback (things feel responsive and real) and the launcher pulse
nudges shoppers toward the assistant, which is the fastest route to the right product.

## Product presentation

- **Framed, contained images** on a clean white field so every garment is presented the same
  way.
- **Hover storytelling:** the image gently zooms, a dark gradient with **"View details →"**
  rises from the bottom, the card lifts with a deeper shadow, and the title shifts toward the
  brand blue — the whole card invites the click.
- **Honest status up front:** a **Sold out** badge on the card and per-size availability on the
  detail page (with "Only N left" urgency) so shoppers trust what they see.

Why it helps: product is the thing being sold, so making each card feel tactile and clickable —
and truthful about stock — both increases click-through and reduces the frustration of chasing
unavailable items.

## Chat feel

- The Outfitter reads as a **boutique concierge**: serif title, a soft subtitle ("Ask about
  fits, colors, and sizes"), navy header with a gold underline.
- **Conversational polish:** user and assistant bubbles are visually distinct, messages animate
  in, a three-dot "thinking" indicator shows the agent is working, and **starter suggestion
  chips** remove the blank-box problem.
- **In-context product cards** inside the chat (image, name, price) that are clickable straight
  to the product page, so a recommendation is one tap from the buy decision.

Why it helps: a chat that feels like a knowledgeable shop assistant — not a raw text box —
earns more questions, and every answer puts real, clickable product in front of the shopper.

## Accessibility & consistency

- Reduced-motion users get a calm, static site. Keyboard users get visible gold focus rings.
- One set of design tokens (colors, fonts, radius, shadows, easing) drives every component, so
  the home page, product pages, forms, and chat all feel like one store.
