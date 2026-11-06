# ─────────────────────────────────────────────────────────────────────────────
# advisor.py  –  GenAI advisor  (LLM profile extraction → rules engine → LLM explain)
# ─────────────────────────────────────────────────────────────────────────────
import json, re, os
from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from dotenv import load_dotenv

from catalogue import (
    CATALOGUE, city_tier, infer_segment,
    eligible_products, resolve_dependencies, get_unit_price,
)

load_dotenv()

router = APIRouter(prefix="/advisor", tags=["Advisor"])

# ── System prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are "Digi Saathi", a friendly business advisor for Accel Business — India's leading telecom.
Speak in the user's preferred language (default English; switch to Hindi or regional language if asked).

PHASE 1 — Profile collection (ask ONE question at a time, keep it short and friendly):
Collect these 5 fields: business_type, employee_count (number), num_sites (number), city, has_gstin (yes/no).
Once all 5 are collected, output ONLY this JSON block on its own line (no other text):
{"business_type": "...", "employee_count": N, "num_sites": N, "city": "...", "has_gstin": true/false}

PHASE 2 — Explanation (triggered after you receive a [BUNDLE] block):
Explain the recommended bundle to the owner in plain, warm language.
- Never mention product codes (P01, P02…).
- Never state a price yourself — use ONLY the prices from the [BUNDLE] block.
- If the user objects to price, say which optional add-ons can be removed to lower the cost.
- If the user asks a question you cannot answer, say "Our team will call you within 2 hours."

Keep all replies under 80 words unless explaining a bundle.
"""

# ── LLM instance (shared across sessions) ────────────────────────────────────
_llm = None

def get_llm():
    global _llm
    if _llm is None:
        _llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.3,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
        )
    return _llm


# ── In-memory session store (use Redis in production) ─────────────────────────
sessions: dict[str, list] = {}


# ── Build bundle from profile (rules engine — no LLM) ────────────────────────
def build_bundle(profile: dict) -> dict:
    has_gstin = bool(profile.get("has_gstin", False))
    city = str(profile.get("city", ""))
    employees = int(profile.get("employee_count", 1))
    sites = int(profile.get("num_sites", 1))

    tier = city_tier(city)
    segment = infer_segment(employees, sites)

    eligible = eligible_products(has_gstin, tier, employees, sites, segment)
    final_pids = resolve_dependencies(eligible)

    line_items = []
    for pid in sorted(final_pids):
        p = CATALOGUE[pid]
        price = get_unit_price(p, segment)
        line_items.append({
            "product_id": pid,
            "product_name": p["product_name"],
            "category": p["category"],
            "description": p["description"],
            "price_per_unit_inr": price,
            "setup_inr": int(p["one_time_setup_inr"]),
            "contract_months": int(p["min_contract_months"]),
            "install_days": int(p["typical_install_days"]),
        })

    # Fibre products need physical install; others can be same-day
    fibre_pids = {"P01", "P02", "P03", "P05", "P06"}
    has_fibre = any(item["product_id"] in fibre_pids for item in line_items)
    max_install = max((i["install_days"] for i in line_items), default=1)
    max_contract = max((i["contract_months"] for i in line_items), default=12)

    total_monthly = sum(i["price_per_unit_inr"] for i in line_items)
    total_setup = sum(i["setup_inr"] for i in line_items)

    return {
        "segment": segment,
        "city_tier": tier,
        "has_gstin": has_gstin,
        "line_items": line_items,
        "total_monthly_inr": total_monthly,
        "total_setup_inr": total_setup,
        "contract_months": max_contract,
        "activation_note": (
            f"Fibre installation takes up to {max_install} business days. "
            "SIM and cloud products activate the same day."
            if has_fibre
            else "All selected products can be activated within 1 business day."
        ),
        "no_gstin_tip": (
            "Some products (Cloud Telephony, Managed Firewall, etc.) need a GSTIN. "
            "We can help you get your GSTIN — ask us how!"
            if not has_gstin else ""
        ),
    }


def _extract_profile(text: str) -> dict | None:
    """Extract JSON profile block if the LLM has completed Phase 1."""
    match = re.search(r'\{[^{}]*"business_type"[^{}]*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return None


# ── API models ────────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    session_id: str
    message: str
    language: str = "en"


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    bundle: dict | None = None
    profile: dict | None = None


# ── Routes ────────────────────────────────────────────────────────────────────
@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    llm = get_llm()

    if req.session_id not in sessions:
        sessions[req.session_id] = [SystemMessage(content=SYSTEM_PROMPT)]

    history = sessions[req.session_id]
    lang_hint = f"[User language preference: {req.language}] " if req.language != "en" else ""
    history.append(HumanMessage(content=f"{lang_hint}{req.message}"))

    response = llm.invoke(history)
    history.append(AIMessage(content=response.content))

    # Check if LLM has emitted a profile JSON (Phase 1 complete)
    profile = _extract_profile(response.content)
    bundle = None

    if profile:
        bundle = build_bundle(profile)
        # Feed bundle back to LLM for plain-language Phase 2 explanation
        bundle_hint = (
            f"[BUNDLE] {json.dumps(bundle, ensure_ascii=False)}\n"
            "Now explain this bundle to the customer in plain language. "
            "Do NOT mention product codes. Use prices from the bundle only."
        )
        history.append(HumanMessage(content=bundle_hint))
        explanation = llm.invoke(history)
        history.append(AIMessage(content=explanation.content))
        return ChatResponse(
            reply=explanation.content,
            session_id=req.session_id,
            bundle=bundle,
            profile=profile,
        )

    return ChatResponse(reply=response.content, session_id=req.session_id)


@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    sessions.pop(session_id, None)
    return {"status": "cleared"}

