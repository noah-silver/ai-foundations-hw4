"""Campus Customs API: catalogue, inventory, accounts, and the chat agent.

Run from the backend/ folder:
    uvicorn main:app --reload --port 8000
"""

import json
import secrets
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, field_validator
from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    SystemPromptPart,
    TextPart,
    ToolCallPart,
    UserPromptPart,
)

from agent import MODEL_NAME, build_agent, render_system_prompt
from auth import hash_password, verify_password
from models import AuditEntry, ChatRequest, ChatResponse, ChatTurn, Customer, ToolCall
from tools import ChatDeps, product_name

AUDIT_PATH = Path(__file__).resolve().parent.parent / "output" / "audit_trail.json"

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DB_PATH = DATA_DIR / "campus_customs.db"
SIZE_ORDER = ["XS", "S", "M", "L", "XL", "XXL"]

app = FastAPI(title="Campus Customs API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

# Session tokens live only in memory for this class project: a real shop would
# persist them (or use JWTs) so logins survive a server restart.
SESSIONS: dict[str, int] = {}

# The PydanticAI agent is built once, on first chat request (it loads the API key).
_AGENT = None


def get_agent():
    global _AGENT
    if _AGENT is None:
        _AGENT = build_agent()
    return _AGENT

# catalogue.image_file_path is relative to data/ (e.g. "products/x.jpg"),
# so mounting data/products at /images gives /images/x.jpg.
app.mount("/images", StaticFiles(directory=DATA_DIR / "products"), name="images")


def get_conn() -> sqlite3.Connection:
    # Read-only so the site can never modify the shop's data.
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def get_write_conn() -> sqlite3.Connection:
    # Read/write connection, used only for creating and reading user accounts.
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_analytics_table() -> None:
    # Business analytics: a log of what shoppers ask the chatbot and how many matches came back.
    with get_write_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                num_results INTEGER NOT NULL,
                user_id INTEGER,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        conn.commit()


ensure_analytics_table()


def log_query(query: str, num_results: int, user_id: int | None) -> None:
    with get_write_conn() as conn:
        conn.execute(
            "INSERT INTO chat_queries (query, num_results, user_id) VALUES (?, ?, ?)",
            (query, num_results, user_id),
        )
        conn.commit()


def public_user(row: sqlite3.Row) -> dict:
    # Never expose password_hash to the client.
    return {
        "id": row["id"],
        "name": row["name"],
        "email": row["email"],
        "first_name": row["first_name"],
        "last_name": row["last_name"],
    }


def product_from_row(row: sqlite3.Row) -> dict:
    return {
        "product_id": row["product_id"],
        "name": row["name"],
        "garment_type": row["garment_type"],
        "description": row["description"],
        "colors": json.loads(row["colors"]),
        "search_tags": json.loads(row["search_tags"]),
        "image_url": "/images/" + Path(row["image_file_path"]).name,
        "price": row["price"],
        "total_stock": row["total_stock"],
    }


PRODUCT_QUERY = """
    SELECT c.*, COALESCE(SUM(i.quantity), 0) AS total_stock
    FROM catalogue c
    LEFT JOIN inventory i ON i.product_id = c.product_id
"""


@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    # The site itself is served by Vite; send visits to the API root over to it.
    return RedirectResponse("http://localhost:5173/")


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/products")
def list_products() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(PRODUCT_QUERY + " GROUP BY c.product_id ORDER BY c.name").fetchall()
    return [product_from_row(r) for r in rows]


@app.get("/api/products/{product_id}")
def get_product(product_id: str) -> dict:
    with get_conn() as conn:
        row = conn.execute(
            PRODUCT_QUERY + " WHERE c.product_id = ? GROUP BY c.product_id", (product_id,)
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Product not found")
        sizes = conn.execute(
            "SELECT size, quantity FROM inventory WHERE product_id = ?", (product_id,)
        ).fetchall()

    product = product_from_row(row)
    product["inventory"] = sorted(
        ({"size": s["size"], "quantity": s["quantity"]} for s in sizes),
        key=lambda s: SIZE_ORDER.index(s["size"]) if s["size"] in SIZE_ORDER else len(SIZE_ORDER),
    )
    return product


# --- Accounts -------------------------------------------------------------


class SignupRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str

    @field_validator("first_name", "last_name")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("This field is required.")
        return v.strip()

    @field_validator("password")
    @classmethod
    def strong_enough(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters.")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


def issue_token(user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    SESSIONS[token] = user_id
    return token


def current_user(authorization: str | None = Header(default=None)) -> dict:
    # Expect "Authorization: Bearer <token>".
    token = authorization.removeprefix("Bearer ").strip() if authorization else ""
    user_id = SESSIONS.get(token)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Not signed in.")
    with get_write_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=401, detail="Not signed in.")
    return public_user(row)


@app.post("/api/signup")
def signup(req: SignupRequest) -> dict:
    email = req.email.lower()
    full_name = f"{req.first_name} {req.last_name}"
    with get_write_conn() as conn:
        exists = conn.execute("SELECT 1 FROM users WHERE email = ?", (email,)).fetchone()
        if exists:
            raise HTTPException(status_code=409, detail="An account with that email already exists.")
        cur = conn.execute(
            """
            INSERT INTO users (name, email, password_hash, first_name, last_name)
            VALUES (?, ?, ?, ?, ?)
            """,
            (full_name, email, hash_password(req.password), req.first_name, req.last_name),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM users WHERE id = ?", (cur.lastrowid,)).fetchone()
    return {"token": issue_token(row["id"]), "user": public_user(row)}


@app.post("/api/login")
def login(req: LoginRequest) -> dict:
    with get_write_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (req.email.lower(),)).fetchone()
    # Verify even when the user is missing? We still return the same error either way
    # so the response doesn't reveal which emails have accounts.
    if row is None or not verify_password(req.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    return {"token": issue_token(row["id"]), "user": public_user(row)}


@app.post("/api/logout")
def logout(authorization: str | None = Header(default=None)) -> dict:
    token = authorization.removeprefix("Bearer ").strip() if authorization else ""
    SESSIONS.pop(token, None)
    return {"status": "ok"}


@app.get("/api/me")
def me(user: dict = Depends(current_user)) -> dict:
    return {"user": user}


# --- Chat -----------------------------------------------------------------


def optional_user(authorization: str | None = Header(default=None)) -> dict | None:
    """Like current_user, but returns None instead of raising when not signed in."""
    token = authorization.removeprefix("Bearer ").strip() if authorization else ""
    user_id = SESSIONS.get(token)
    if user_id is None:
        return None
    with get_write_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return public_user(row) if row else None


def hydrate_products(product_ids: list[str]) -> list[dict]:
    """Turn agent-chosen product_ids into full product cards, in order, skipping unknowns."""
    cards: list[dict] = []
    seen: set[str] = set()
    with get_conn() as conn:
        for pid in product_ids:
            if pid in seen:
                continue
            seen.add(pid)
            row = conn.execute(
                PRODUCT_QUERY + " WHERE c.product_id = ? GROUP BY c.product_id", (pid,)
            ).fetchone()
            if row is not None:
                cards.append(product_from_row(row))
    return cards


def to_message_history(turns: list[ChatTurn]) -> list[ModelMessage]:
    """Rebuild PydanticAI message history from stored (role, content) turns."""
    history: list[ModelMessage] = []
    for turn in turns:
        if turn.role == "user":
            history.append(ModelRequest(parts=[UserPromptPart(content=turn.content)]))
        elif turn.role == "assistant":
            history.append(ModelResponse(parts=[TextPart(content=turn.content)]))
    return history


def load_history(user_id: int) -> list[ChatTurn]:
    with get_write_conn() as conn:
        rows = conn.execute(
            "SELECT role, content FROM chat_messages WHERE user_id = ? ORDER BY id", (user_id,)
        ).fetchall()
    return [ChatTurn(role=r["role"], content=r["content"]) for r in rows]


def save_message(user_id: int, role: str, content: str, products: list[dict] | None) -> None:
    with get_write_conn() as conn:
        conn.execute(
            "INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, ?, ?, ?)",
            (user_id, role, content, json.dumps(products) if products else None),
        )
        conn.commit()


@app.get("/api/chat/history")
def chat_history(user: dict = Depends(current_user)) -> dict:
    """Prior conversation for a signed-in shopper, so the widget can restore it."""
    with get_write_conn() as conn:
        rows = conn.execute(
            "SELECT role, content, products_json FROM chat_messages WHERE user_id = ? ORDER BY id",
            (user["id"],),
        ).fetchall()
    return {
        "messages": [
            {
                "role": r["role"],
                "content": r["content"],
                "products": json.loads(r["products_json"]) if r["products_json"] else [],
            }
            for r in rows
        ]
    }


def append_audit_entry(entry: AuditEntry) -> None:
    """Append one run to output/audit_trail.json. Append-only: the existing entries are read,
    the new one added, and the file replaced atomically — it is never wiped between runs."""
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    existing: list = []
    if AUDIT_PATH.exists():
        try:
            loaded = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
            if isinstance(loaded, list):
                existing = loaded
        except (json.JSONDecodeError, OSError):
            existing = []  # unreadable file: start fresh rather than crash, but don't delete it below
    existing.append(entry.model_dump())
    tmp = AUDIT_PATH.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(existing, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(AUDIT_PATH)  # atomic swap, so a crash can't truncate the trail


def extract_tool_calls(messages: list[ModelMessage]) -> list[ToolCall]:
    """Pull the tools the agent called (name + args) out of a run's messages."""
    calls: list[ToolCall] = []
    for message in messages:
        for part in getattr(message, "parts", []):
            if isinstance(part, ToolCallPart):
                if part.tool_name == "final_result":
                    continue  # PydanticAI's internal structured-output call, not a shop tool
                args = part.args
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except json.JSONDecodeError:
                        args = {"raw": args}
                calls.append(ToolCall(name=part.tool_name, args=args if isinstance(args, dict) else {"value": args}))
    return calls


@app.delete("/api/chat/history")
def clear_chat_history(user: dict = Depends(current_user)) -> dict:
    """Erase a signed-in shopper's saved conversation so the chat starts fresh."""
    with get_write_conn() as conn:
        conn.execute("DELETE FROM chat_messages WHERE user_id = ?", (user["id"],))
        conn.commit()
    return {"status": "ok"}


@app.post("/api/chat")
async def chat(req: ChatRequest, user: dict | None = Depends(optional_user)) -> ChatResponse:
    message = req.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    # Logged-in shoppers get real persisted history; guests use what the browser sent.
    prior = load_history(user["id"]) if user else req.history
    customer = (
        Customer(logged_in=True, first_name=user["first_name"], name=user["name"], email=user["email"])
        if user
        else None
    )
    deps = ChatDeps(customer=customer, current_product_id=req.product_id)

    # Inject the system prompt (base + customer + page context) as the first message, because
    # PydanticAI won't re-apply its own system prompt once a message_history is supplied.
    viewing = product_name(deps, req.product_id) if req.product_id else None
    system = render_system_prompt(customer, viewing, req.product_id)
    history_msgs: list[ModelMessage] = [ModelRequest(parts=[SystemPromptPart(content=system)])]
    history_msgs += to_message_history(prior)

    def now_iso() -> str:
        return datetime.now(timezone.utc).isoformat(timespec="seconds")

    started = time.perf_counter()
    try:
        result = await get_agent().run(message, message_history=history_msgs, deps=deps)
    except Exception as exc:
        # A content-filtered prompt (the provider blocked it) is a safety refusal, not an outage:
        # log it and reply politely instead of erroring.
        filtered = "content_filter" in str(exc) or "content management policy" in str(exc)
        append_audit_entry(
            AuditEntry(
                timestamp=now_iso(), user_id=user["id"] if user else None, is_guest=user is None,
                user_message=message, status="filtered" if filtered else "error", error=str(exc)[:300],
                duration_ms=round((time.perf_counter() - started) * 1000), model=MODEL_NAME,
            )
        )
        if filtered:
            return ChatResponse(
                reply="I'm sorry, but I can't help with that. I'm here to help you shop Campus "
                "Customs apparel — want help finding something for game day?",
                products=[],
            )
        raise HTTPException(status_code=502, detail="The Outfitter is unavailable right now. Please try again.")

    reply = result.output.reply
    products = hydrate_products(result.output.product_ids)

    if user:
        save_message(user["id"], "user", message, None)
        save_message(user["id"], "assistant", reply, products)

    # Business analytics: record what was asked and how many products it surfaced.
    log_query(message, len(products), user["id"] if user else None)

    # Audit trail: an append-only record of the agent loop (tools called, products shown).
    append_audit_entry(
        AuditEntry(
            timestamp=now_iso(), user_id=user["id"] if user else None, is_guest=user is None,
            user_message=message, tool_calls=extract_tool_calls(result.all_messages()),
            product_ids=result.output.product_ids, num_results=len(products), status="ok",
            duration_ms=round((time.perf_counter() - started) * 1000), model=MODEL_NAME,
        )
    )

    return ChatResponse(reply=reply, products=products)


@app.get("/api/insights/top-queries")
def top_queries(limit: int = 10) -> dict:
    """Business view of chat demand: most-asked questions and ones that returned nothing.

    Note: exposes aggregate shopper demand; in production this would be gated to staff accounts.
    """
    with get_write_conn() as conn:
        asked = conn.execute(
            """
            SELECT lower(trim(query)) AS q, COUNT(*) AS times, AVG(num_results) AS avg_results
            FROM chat_queries
            GROUP BY q ORDER BY times DESC, q LIMIT ?
            """,
            (limit,),
        ).fetchall()
        no_results = conn.execute(
            """
            SELECT lower(trim(query)) AS q, COUNT(*) AS times
            FROM chat_queries WHERE num_results = 0
            GROUP BY q ORDER BY times DESC, q LIMIT ?
            """,
            (limit,),
        ).fetchall()
        total = conn.execute("SELECT COUNT(*) AS n FROM chat_queries").fetchone()["n"]
    return {
        "total_queries": total,
        "top_asked": [{"query": r["q"], "times": r["times"], "avg_results": round(r["avg_results"], 1)} for r in asked],
        "no_result_queries": [{"query": r["q"], "times": r["times"]} for r in no_results],
    }
