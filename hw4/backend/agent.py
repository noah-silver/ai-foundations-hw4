"""The Outfitter: a PydanticAI chat agent for the Campus Customs shop.

The agent runs on gpt-5.6-luna through the Portkey gateway (matching HW2/HW3). Its
system prompt lives in prompts/prompt.md, its tools in tools.py, and its types in
models.py. It answers only from the catalogue and inventory via its tools, so it never
invents products, prices, colors, or stock.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

from openai import AsyncOpenAI
from pydantic_ai import Agent, ModelRetry, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from models import ChatReply, Customer, ProductDetails, ProductSummary, SizeAvailability
from tools import ChatDeps, who_is_chatting
from tools import check_size_stock as _check_size_stock
from tools import get_product_details as _get_product_details
from tools import search_catalogue as _search_catalogue

HERE = Path(__file__).resolve().parent
PROMPT_PATH = HERE / "prompts" / "prompt.md"
ROOT = HERE.parent.parent  # course root, where .env lives

PORTKEY_BASE_URL = "https://api.portkey.ai/v1"
MODEL_NAME = "gpt-5.6-luna"


def render_system_prompt(customer: Customer | None, current_product_name: str | None,
                         current_product_id: str | None) -> str:
    """The full system prompt: the base voice/safety/tool rules plus this request's live
    customer and page context.

    We render and inject this ourselves (see main.py) rather than relying on PydanticAI's own
    system-prompt handling, because when a message_history is supplied the agent does not
    re-apply dynamic system prompts — so customer and page context would otherwise be lost on
    every turn after the first.
    """
    parts = [PROMPT_PATH.read_text(encoding="utf-8").rstrip(), "\n## Who you're helping right now\n"]
    if customer and customer.logged_in:
        who = customer.first_name or customer.name or "there"
        parts.append(
            f"You are chatting with {who}, a signed-in customer (email {customer.email}). "
            "You may greet them by first name. Don't read their email back to them."
        )
    else:
        parts.append("You are chatting with a guest who is not signed in.")
    if current_product_id and current_product_name:
        parts.append(
            f'The shopper is currently viewing "{current_product_name}" (product_id '
            f'{current_product_id}). If they say "this", "it", or "this one" without naming a '
            "product, they mean this one — look it up before answering."
        )
    return "\n".join(parts)


def load_portkey_key() -> str:
    """Load PORTKEY_API_KEY from the environment or a .env file, without printing it.

    Checks hw4/.env first (so a standalone clone works), then the course-root .env.
    """
    key = os.environ.get("PORTKEY_API_KEY")
    if key:
        return key
    candidates = [HERE.parent / ".env", ROOT / ".env"]  # hw4/.env, then course-root/.env
    for env_path in candidates:
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                if line.startswith("PORTKEY_API_KEY="):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if key:
                        os.environ["PORTKEY_API_KEY"] = key
                        return key
    raise RuntimeError(
        "PORTKEY_API_KEY was not found. Create hw4/.env from .env.example and add your key."
    )


def build_agent() -> Agent[ChatDeps, ChatReply]:
    key = load_portkey_key()
    client = AsyncOpenAI(
        api_key=key,
        base_url=PORTKEY_BASE_URL,
        default_headers={"x-portkey-api-key": key, "x-portkey-provider": "openai"},
    )
    model = OpenAIChatModel(MODEL_NAME, provider=OpenAIProvider(openai_client=client))
    # No system_prompt here: main.py injects the rendered prompt (base + customer + page
    # context) into message_history so it survives multi-turn conversations.
    agent = Agent(
        model,
        deps_type=ChatDeps,
        output_type=ChatReply,
        retries=2,
    )

    @agent.output_validator
    def require_ids_for_listed_products(ctx: RunContext[ChatDeps], output: ChatReply) -> ChatReply:
        # Make the model surface product cards whenever it's clearly showing products, so the
        # storefront grid isn't left empty.
        if not output.product_ids:
            # (a) it searched and found matches but returned none, or (b) it quoted a price.
            if ctx.deps.last_search_ids:
                raise ModelRetry(
                    "Your search found products but you returned no product_ids. Put the ids of "
                    "the products you're showing into product_ids so the page can display them."
                )
            if re.search(r"\$\d", output.reply):
                raise ModelRetry(
                    "You listed specific products but left product_ids empty. Resend the same "
                    "answer with each mentioned product's product_id in product_ids."
                )
        return output

    @agent.tool
    def search_catalogue(
        ctx: RunContext[ChatDeps],
        query: str,
        limit: int = 8,
        max_price: float | None = None,
        min_price: float | None = None,
    ) -> list[ProductSummary]:
        """Search products by keyword across name, type, description, colors, and tags. Pass
        max_price/min_price (USD) for budget questions like "under $70". Results come back
        in-stock first, each with an in_stock flag."""
        return _search_catalogue(ctx.deps, query, limit, max_price, min_price)

    @agent.tool
    def get_product_details(ctx: RunContext[ChatDeps], product_id: str) -> ProductDetails:
        """Description, price, colors, and per-size stock for one product. Use for price and
        'what sizes/colors' questions. The price and quantities come straight from the database."""
        details = _get_product_details(ctx.deps, product_id)
        if details is None:
            raise ModelRetry(f"No product has id '{product_id}'. Use search_catalogue to find the right id first.")
        return details

    @agent.tool
    def check_size_stock(ctx: RunContext[ChatDeps], product_id: str, size: str) -> SizeAvailability:
        """Whether one product is available in one size, with the exact quantity. Use for
        'do you have X in size M?' questions. Relay its message when a size is out of stock."""
        result = _check_size_stock(ctx.deps, product_id, size)
        if result is None:
            raise ModelRetry(f"No product has id '{product_id}'. Use search_catalogue to find the right id first.")
        return result

    @agent.tool
    def get_customer(ctx: RunContext[ChatDeps]) -> Customer:
        """Who you're chatting with: their name and email if signed in, or a guest marker.
        Use it to greet a returning customer by name."""
        return who_is_chatting(ctx.deps)

    return agent
