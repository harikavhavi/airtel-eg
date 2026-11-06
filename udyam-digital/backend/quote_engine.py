# ─────────────────────────────────────────────────────────────────────────────
# quote_engine.py  –  Quote generation with full eligibility + dependency checks
# ─────────────────────────────────────────────────────────────────────────────
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

from catalogue import CATALOGUE, get_unit_price

router = APIRouter(prefix="/quote", tags=["Quote"])

FIBRE_PIDS = {"P01", "P02", "P03", "P05", "P06"}


class QuoteItem(BaseModel):
    product_id: str
    quantity: int = 1


class QuoteRequest(BaseModel):
    items: List[QuoteItem]
    city_tier: str          # "1" or "2"
    has_gstin: bool
    employee_count: int
    num_sites: int
    segment: str = "micro"  # micro | prof | multi | mfg


class LineItem(BaseModel):
    product_id: str
    product_name: str
    category: str
    quantity: int
    unit: str
    monthly_inr: int
    setup_inr: int
    contract_months: int
    install_days: int
    is_optional: bool = True   # core connectivity = False, set by frontend


class QuoteResponse(BaseModel):
    line_items: List[LineItem]
    total_monthly_inr: int
    total_setup_inr: int
    max_contract_months: int
    activation_note: str
    errors: List[str]


@router.post("/generate", response_model=QuoteResponse)
async def generate_quote(req: QuoteRequest):
    line_items = []
    total_monthly = 0
    total_setup = 0
    errors = []

    cart_ids = {item.product_id for item in req.items}

    for item in req.items:
        p = CATALOGUE.get(item.product_id)
        if not p:
            errors.append(f"Product {item.product_id} not found in catalogue")
            continue

        # ── Eligibility checks ──────────────────────────────────────────────
        if req.city_tier not in p["available_city_tiers"].split(";"):
            errors.append(f"'{p['product_name']}' is not available in Tier-{req.city_tier} cities")
            continue
        if p["requires_gstin"] == "Y" and not req.has_gstin:
            errors.append(f"'{p['product_name']}' requires a valid GSTIN — skipped")
            continue
        if req.employee_count < int(p["min_employees"]):
            errors.append(
                f"'{p['product_name']}' needs at least {p['min_employees']} employees "
                f"(you have {req.employee_count})"
            )
            continue
        if req.num_sites < int(p["min_sites"]):
            errors.append(
                f"'{p['product_name']}' needs at least {p['min_sites']} sites "
                f"(you have {req.num_sites})"
            )
            continue

        # ── Dependency check (requires_one_of) ─────────────────────────────
        req_one = p.get("requires_one_of", "").strip()
        if req_one:
            required_options = req_one.split("|")
            if not any(r in cart_ids for r in required_options):
                errors.append(
                    f"'{p['product_name']}' requires one of "
                    f"{[CATALOGUE[r]['product_name'] for r in required_options if r in CATALOGUE]} "
                    "in the bundle"
                )
                continue

        unit_price = get_unit_price(p, req.segment)
        monthly = unit_price * item.quantity
        setup = int(p["one_time_setup_inr"]) * item.quantity

        line_items.append(LineItem(
            product_id=item.product_id,
            product_name=p["product_name"],
            category=p["category"],
            quantity=item.quantity,
            unit=p["unit"],
            monthly_inr=monthly,
            setup_inr=setup,
            contract_months=int(p["min_contract_months"]),
            install_days=int(p["typical_install_days"]),
        ))
        total_monthly += monthly
        total_setup += setup

    if not line_items:
        return QuoteResponse(
            line_items=[],
            total_monthly_inr=0,
            total_setup_inr=0,
            max_contract_months=12,
            activation_note="No eligible products found. Please check your inputs.",
            errors=errors,
        )

    max_install = max(li.install_days for li in line_items)
    max_contract = max(li.contract_months for li in line_items)
    has_fibre = any(item.product_id in FIBRE_PIDS for item in req.items)

    activation_note = (
        f"Fibre/leased-line installation takes up to {max_install} business days. "
        "SIM and cloud products go live the same day."
        if has_fibre
        else "All products can be activated within 1 business day."
    )

    return QuoteResponse(
        line_items=line_items,
        total_monthly_inr=total_monthly,
        total_setup_inr=total_setup,
        max_contract_months=max_contract,
        activation_note=activation_note,
        errors=errors,
    )

