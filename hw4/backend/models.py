"""Pydantic types for the chat agent and the chat API.

Two groups of types:
- Tool return types (`ProductSummary`, `SizeStock`, `ProductDetails`, `SizeAvailability`):
  what the agent's product/stock tools hand back. These are structured so the agent reads
  real values straight from the database instead of inventing prices or quantities.
- Chat/API types (`ChatReply`, `ChatTurn`, `ChatRequest`, `ChatResponse`): the agent's
  output and the shapes exchanged between the website and FastAPI.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ProductSummary(BaseModel):
    """A lightweight product hit from a catalogue search (enough to recommend and pick one)."""

    product_id: str = Field(description="Stable id; pass this to get_product_details or check_size_stock.")
    name: str
    garment_type: str
    colors: list[str]
    price: float = Field(description="Price in USD, straight from the catalogue.")
    in_stock: bool = Field(description="True if any size has stock. Prefer in-stock items.")


class SizeStock(BaseModel):
    """Stock for one size of a product."""

    size: str
    quantity: int = Field(description="Units on hand for this size, from the inventory table.")
    available: bool = Field(description="True if quantity > 0; False means this size is out of stock.")


class ProductDetails(BaseModel):
    """Everything needed to answer description, price, color, and stock questions for one product."""

    product_id: str
    name: str
    garment_type: str
    description: str
    colors: list[str]
    price: float = Field(description="Price in USD, straight from the catalogue.")
    sizes: list[SizeStock] = Field(description="Per-size stock, ordered XS→XXL.")
    in_stock: bool = Field(description="True if any size has stock; False if the whole product is sold out.")


class Customer(BaseModel):
    """Who the agent is chatting with. Guests have logged_in=False and no name/email."""

    logged_in: bool
    first_name: str | None = None
    name: str | None = None
    email: str | None = None


class SizeAvailability(BaseModel):
    """A targeted answer to 'is this product available in this size?'."""

    product_id: str
    name: str
    size: str
    quantity: int
    available: bool = Field(description="False means this exact size is out of stock.")
    message: str = Field(description="A plain-language status the agent can relay, e.g. 'Sold out in size M'.")


class ChatReply(BaseModel):
    """What the PydanticAI agent returns."""

    reply: str = Field(description="The friendly answer to show the shopper.")
    product_ids: list[str] = Field(
        default_factory=list,
        description="product_id values to show as cards, in display order. Empty if none apply.",
    )


class ChatTurn(BaseModel):
    """One prior message in a conversation (role is 'user' or 'assistant')."""

    role: str
    content: str


class ChatRequest(BaseModel):
    """A chat message from the website. Guests also send their running history."""

    message: str
    history: list[ChatTurn] = Field(default_factory=list)
    product_id: str | None = Field(
        default=None,
        description="The product the shopper is currently viewing, if any, so 'this'/'it' resolves.",
    )


class ChatResponse(BaseModel):
    """The API's reply: the agent's text plus hydrated product cards."""

    reply: str
    products: list[dict] = Field(default_factory=list)


class ToolCall(BaseModel):
    """One tool the agent invoked during a run (for the audit trail)."""

    name: str
    args: dict = Field(default_factory=dict)


class AuditEntry(BaseModel):
    """One record of an agent run, appended to output/audit_trail.json."""

    timestamp: str = Field(description="UTC ISO-8601 time the run finished.")
    user_id: int | None = Field(default=None, description="Account id, or null for a guest.")
    is_guest: bool
    user_message: str = Field(description="The shopper's message that triggered the run.")
    tool_calls: list[ToolCall] = Field(default_factory=list, description="Tools the agent called, in order.")
    product_ids: list[str] = Field(default_factory=list, description="Products the agent chose to show.")
    num_results: int = 0
    status: str = Field(description="'ok' or 'error'.")
    error: str | None = None
    duration_ms: int | None = None
    model: str
