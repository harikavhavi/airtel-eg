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


# ── LLM instance (shared across sessions) ────────────────────────────────────
_llm = None

def get_llm():
    global _llm
    api_key = os.getenv("GOOGLE_API_KEY", "").strip()
    # Check for placeholder or invalid prefix (Google Gemini API keys start with AIzaSy)
    if not api_key or "your_" in api_key or not api_key.startswith("AIzaSy"):
        return None
    if _llm is None:
        try:
            _llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                temperature=0.3,
                google_api_key=api_key,
            )
        except Exception as e:
            print(f"[Advisor] Failed to initialize Gemini model: {e}")
            return None
    return _llm


# ── In-memory session store (use Redis in production) ─────────────────────────
sessions: dict[str, list] = {}
guided_sessions: dict[str, dict] = {}


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


# ── Fallback Guided Advisor (when API key is missing or invalid) ──────────────
def run_guided_advisor(req: ChatRequest) -> ChatResponse:
    is_hi = req.language == "hi"
    sid = req.session_id
    if sid not in guided_sessions:
        guided_sessions[sid] = {
            "step": 0,
            "profile": {
                "business_type": "Professional office",
                "employee_count": 8,
                "num_sites": 1,
                "city": "Kochi",
                "has_gstin": True,
            }
        }

    state = guided_sessions[sid]
    step = state["step"]
    msg = req.message.strip().lower()

    # Step 0: Initial greeting / business type
    if step == 0:
        if any(w in msg for w in ["clinic", "retail", "shop", "office", "firm", "factory", "restaurant", "store", "dental"]):
            state["profile"]["business_type"] = req.message.strip()
            state["step"] = 1
            reply = (
                "बहुत बढ़िया! आपके व्यवसाय में कितने कर्मचारी या टीम सदस्य काम करते हैं?"
                if is_hi else
                "Great! How many employees or staff members work at your business?"
            )
        else:
            state["step"] = 1
            reply = (
                "नमस्ते! आप किस प्रकार का व्यवसाय चलाते हैं (जैसे क्लिनिक, खुदरा दुकान, कार्यालय, आदि)?"
                if is_hi else
                "Hello! What kind of business do you run (e.g. dental clinic, retail store, law office, small factory)?"
            )
        return ChatResponse(reply=reply, session_id=sid)

    # Step 1: Employee count
    elif step == 1:
        nums = re.findall(r'\b\d+\b', msg)
        if nums:
            state["profile"]["employee_count"] = max(1, int(nums[0]))
        else:
            state["profile"]["business_type"] = req.message.strip()
        state["step"] = 2
        reply = (
            "आपकी कितनी व्यावसायिक शाखाएं या साइटें हैं? (उदा. 1, 2, 3)"
            if is_hi else
            "How many business locations or sites do you currently operate?"
        )
        return ChatResponse(reply=reply, session_id=sid)

    # Step 2: Num sites
    elif step == 2:
        nums = re.findall(r'\b\d+\b', msg)
        if nums:
            state["profile"]["num_sites"] = max(1, int(nums[0]))
        state["step"] = 3
        reply = (
            "आपका व्यवसाय किस शहर में स्थित है?"
            if is_hi else
            "Which city is your business located in?"
        )
        return ChatResponse(reply=reply, session_id=sid)

    # Step 3: City
    elif step == 3:
        state["profile"]["city"] = req.message.strip().title()
        state["step"] = 4
        reply = (
            "क्या आपके पास अपने व्यवसाय के लिए GSTIN है? (हाँ / नहीं)"
            if is_hi else
            "Do you have a GSTIN registered for your business? (Yes / No)"
        )
        return ChatResponse(reply=reply, session_id=sid)

    # Step 4: GSTIN & Bundle generation
    elif step == 4:
        has_g = any(w in msg for w in ["yes", "y", "haan", "ha", "true", "हाँ", "ha"])
        state["profile"]["has_gstin"] = has_g
        state["step"] = 5

        bundle = build_bundle(state["profile"])
        prof = state["profile"]

        if is_hi:
            reply = (
                f"धन्यवाद! आपके {prof['business_type']} ({prof['city']}, {prof['employee_count']} कर्मचारी) के लिए "
                f"हमने सबसे उपयुक्त Accel Business प्लान तैयार किया है।\n\n"
                f"कुल मासिक शुल्क: ₹{bundle['total_monthly_inr']:,}/माह\n"
                f"{bundle['activation_note']}\n\n"
                "आप नीचे दिए गए बंडल कार्ड को देखकर 'View Full Quote' पर क्लिक करके आगे बढ़ सकते हैं।"
            )
        else:
            reply = (
                f"Thank you! Based on your profile for {prof['business_type']} in {prof['city']} "
                f"with {prof['employee_count']} staff, here is your tailored Accel Business bundle.\n\n"
                f"Total monthly plan: ₹{bundle['total_monthly_inr']:,}/month\n"
                f"{bundle['activation_note']}\n\n"
                "You can review your recommended items below and click 'View Full Quote' to customize or proceed to KYC."
            )

        return ChatResponse(
            reply=reply,
            session_id=sid,
            bundle=bundle,
            profile=prof,
        )

    # Step 5+: Follow-up questions
    else:
        bundle = build_bundle(state["profile"])
        if is_hi:
            reply = "यदि आपके कोई और प्रश्न हैं या आप कुछ बदलाव चाहते हैं, तो कृपया 'View Full Quote' पर क्लिक करें या हमारी टीम आपसे 2 घंटे के भीतर संपर्क करेगी।"
        else:
            reply = "If you'd like to adjust items or add-ons, you can toggle them in the Quote tab, or our team can assist you within 2 business hours."
        return ChatResponse(reply=reply, session_id=sid, bundle=bundle, profile=state["profile"])


# ── Routes ────────────────────────────────────────────────────────────────────
@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    llm = get_llm()

    # If no LLM available (e.g. invalid or missing API key), run guided fallback
    if llm is None:
        return run_guided_advisor(req)

    try:
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

    except Exception as e:
        print(f"[Advisor] Gemini LLM error: {e}. Switching to guided local advisor.")
        return run_guided_advisor(req)


@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    sessions.pop(session_id, None)
    guided_sessions.pop(session_id, None)
    return {"status": "cleared"}
