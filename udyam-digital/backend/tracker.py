# ─────────────────────────────────────────────────────────────────────────────
# tracker.py  –  Order state machine + SQLite persistence
# ─────────────────────────────────────────────────────────────────────────────
import sqlite3, uuid
from datetime import date, timedelta
from pathlib import Path
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/tracker", tags=["Tracker"])

DB_PATH = Path(__file__).parent / "orders.db"

STATES = [
    "ACCEPTED",
    "KYC_SUBMITTED",
    "KYC_VERIFIED",
    "ORDER_PLACED",
    "INSTALLATION_SCHEDULED",
    "TECH_VISIT_DONE",
    "ACTIVATED",
]

STATE_MESSAGES = {
    "ACCEPTED":               "✅ Quote accepted! Please complete your KYC documents.",
    "KYC_SUBMITTED":          "📄 Documents received. Under review — usually done within 1 business day.",
    "KYC_VERIFIED":           "✅ KYC verified! We are setting up your services.",
    "ORDER_PLACED":           "🔧 Order placed with our installation team.",
    "INSTALLATION_SCHEDULED": "📅 Engineer visit scheduled. You will receive an SMS with the time slot.",
    "TECH_VISIT_DONE":        "🛠️ Installation complete. Activating your services now.",
    "ACTIVATED":              "🎉 You're live! Welcome to Accel Business. Call 1800-XXX-XXXX for support.",
}

# ── DB helpers ────────────────────────────────────────────────────────────────
def _get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    db = _get_db()
    db.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id          TEXT PRIMARY KEY,
            lead_id           TEXT DEFAULT '',
            business_name     TEXT DEFAULT '',
            current_state     TEXT NOT NULL DEFAULT 'ACCEPTED',
            created_date      TEXT NOT NULL,
            max_install_days  INTEGER NOT NULL DEFAULT 5,
            total_monthly_inr INTEGER DEFAULT 0,
            segment           TEXT DEFAULT 'micro'
        )
    """)
    db.commit()
    db.close()


init_db()   # Run once at startup


# ── Pydantic models ───────────────────────────────────────────────────────────
class CreateOrderRequest(BaseModel):
    lead_id: str = ""
    business_name: str = ""
    max_install_days: int = 5
    total_monthly_inr: int = 0
    segment: str = "micro"


class OrderStatusResponse(BaseModel):
    order_id: str
    business_name: str
    current_state: str
    message: str
    progress_pct: int
    steps_completed: list[str]
    steps_remaining: list[str]
    estimated_activation: str
    support_number: str = "1800-XXX-XXXX"


# ── Routes ────────────────────────────────────────────────────────────────────
@router.post("/create")
async def create_order(req: CreateOrderRequest):
    """Create a new order and return its ID."""
    order_id = "ORD-" + uuid.uuid4().hex[:8].upper()
    created = str(date.today())
    db = _get_db()
    db.execute(
        """INSERT INTO orders
           (order_id, lead_id, business_name, current_state, created_date,
            max_install_days, total_monthly_inr, segment)
           VALUES (?, ?, ?, 'ACCEPTED', ?, ?, ?, ?)""",
        (order_id, req.lead_id, req.business_name, created,
         req.max_install_days, req.total_monthly_inr, req.segment),
    )
    db.commit()
    db.close()
    return {"order_id": order_id, "state": "ACCEPTED", "message": STATE_MESSAGES["ACCEPTED"]}


@router.get("/{order_id}", response_model=OrderStatusResponse)
async def get_order_status(order_id: str):
    db = _get_db()
    row = db.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,)).fetchone()
    db.close()

    if not row:
        return OrderStatusResponse(
            order_id=order_id,
            business_name="",
            current_state="NOT_FOUND",
            message="Order not found. Please check your order ID.",
            progress_pct=0,
            steps_completed=[],
            steps_remaining=STATES,
            estimated_activation="—",
        )

    state = row["current_state"]
    idx = STATES.index(state) if state in STATES else 0
    created = date.fromisoformat(row["created_date"])
    eta = created + timedelta(days=row["max_install_days"])

    return OrderStatusResponse(
        order_id=order_id,
        business_name=row["business_name"],
        current_state=state,
        message=STATE_MESSAGES.get(state, "Status unknown"),
        progress_pct=int(idx / (len(STATES) - 1) * 100),
        steps_completed=STATES[: idx + 1],
        steps_remaining=STATES[idx + 1 :],
        estimated_activation=str(eta),
    )


@router.post("/{order_id}/advance")
async def advance_order(order_id: str):
    """Advance order to next state — used in the demo to simulate progress."""
    db = _get_db()
    row = db.execute("SELECT current_state FROM orders WHERE order_id = ?", (order_id,)).fetchone()
    if not row:
        db.close()
        return {"error": "Order not found"}

    idx = STATES.index(row["current_state"]) if row["current_state"] in STATES else 0
    if idx < len(STATES) - 1:
        new_state = STATES[idx + 1]
        db.execute("UPDATE orders SET current_state = ? WHERE order_id = ?", (new_state, order_id))
        db.commit()
    else:
        new_state = STATES[-1]
    db.close()
    return {"order_id": order_id, "new_state": new_state, "message": STATE_MESSAGES[new_state]}

