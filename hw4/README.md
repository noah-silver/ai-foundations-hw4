# Campus Customs

A Yale-apparel storefront with an AI shopping assistant ("The Outfitter"). Built for
*AI Foundations for Managers*, HW4.

- **Front end:** React + Vite + TypeScript (`frontend/`)
- **Back end:** FastAPI + a PydanticAI agent on `gpt-5.6-luna` via the Portkey gateway (`backend/`)
- **Data:** a SQLite database and product images (provided separately — see below)

The shopper can browse products, create an account and log in, and chat with the Outfitter,
which answers from the live database (prices, colors, per-size stock), shows matching product
cards on the page, and remembers a signed-in shopper's conversation.

For a full description of how the system works, see [`output/harness.md`](output/harness.md).

## Layout

```
hw4/
├── frontend/          # Vite React TypeScript app
├── backend/           # FastAPI app + PydanticAI agent
│   ├── main.py        # API routes (products, accounts, chat)
│   ├── agent.py       # builds the agent (Portkey/OpenAI, tools, prompt)
│   ├── tools.py       # catalogue/inventory tools
│   ├── models.py      # Pydantic types
│   └── prompts/prompt.md  # agent voice + safety rules
├── output/            # harness.md, design.md, usability.md, app_check.html, audit_trail.json
├── requirements.txt   # Python dependencies
├── .env.example       # copy to .env and add your key
└── data/              # NOT in git — place the data pack here (see below)
```

## Prerequisites

- Python 3.11+
- Node.js 18+ and npm

## 1. Place the data pack

The database and product images are **not** in this repo. Put the provided data pack in a
`data/` folder at the root of `hw4/` so it looks like:

```
hw4/data/campus_customs.db
hw4/data/products/<product images>.jpg
```

## 2. Add your API key

```bash
cp .env.example .env
# then edit .env and set PORTKEY_API_KEY to your real key
```

`.env` is gitignored, so your key is never committed.

## 3. Run the back end

From the `hw4/` folder:

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cd backend
uvicorn main:app --reload --port 8000
```

The API runs on http://localhost:8000 (it serves the catalogue, accounts, chat, and product
images).

## 4. Run the front end

In a second terminal, from the `hw4/frontend/` folder:

```bash
npm install
npm run dev
```

Open http://localhost:5173. The Vite dev server proxies `/api` and `/images` to the backend on
port 8000, so start the backend first.

## Notes

- Chat requires a valid `PORTKEY_API_KEY`; browsing products and accounts work without it.
- Every agent run is appended to `output/audit_trail.json` (append-only).
- The three seed user accounts in the database can't be logged into (legacy hash format) —
  create a new account to try login.
