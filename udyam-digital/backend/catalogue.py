# ─────────────────────────────────────────────────────────────────────────────
# catalogue.py  –  shared product-catalogue loader & eligibility helpers
# ─────────────────────────────────────────────────────────────────────────────
import csv
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

TIER1_CITIES = {
    "mumbai", "delhi", "bengaluru", "bangalore", "chennai",
    "hyderabad", "kolkata", "pune", "ahmedabad", "surat",
}


def load_catalogue() -> dict:
    """Return {product_id: row_dict} from product_catalogue.csv."""
    cat = {}
    with open(DATA_DIR / "product_catalogue.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            cat[row["product_id"]] = row
    return cat


CATALOGUE: dict = load_catalogue()


def city_tier(city: str) -> str:
    return "1" if city.strip().lower() in TIER1_CITIES else "2"


def infer_segment(employees: int, sites: int) -> str:
    if employees <= 5 and sites == 1:
        return "micro"
    if employees <= 20 and sites <= 2:
        return "prof"
    if sites >= 3:
        return "multi"
    return "mfg"


def get_unit_price(p: dict, segment: str) -> int:
    """
    Defined pricing rule:
    micro → price_min  (most price-sensitive)
    mfg   → price_max  (enterprise)
    others → midpoint
    """
    lo = int(p["price_min_inr_per_month"])
    hi = int(p["price_max_inr_per_month"])
    if segment == "micro":
        return lo
    if segment == "mfg":
        return hi
    return (lo + hi) // 2


def eligible_products(
    has_gstin: bool,
    tier: str,
    employees: int,
    sites: int,
    segment: str,
) -> list[str]:
    """Return list of product_ids that pass ALL eligibility rules."""
    result = []
    for pid, p in CATALOGUE.items():
        if tier not in p["available_city_tiers"].split(";"):
            continue
        if p["requires_gstin"] == "Y" and not has_gstin:
            continue
        if employees < int(p["min_employees"]):
            continue
        if sites < int(p["min_sites"]):
            continue
        if segment not in p["target_segments"].split(";"):
            continue
        result.append(pid)
    return result


def resolve_dependencies(selected: list[str]) -> list[str]:
    """Remove products whose requires_one_of dependency is not in the bundle."""
    sel_set = set(selected)
    for pid in list(sel_set):
        req = CATALOGUE[pid].get("requires_one_of", "")
        if req:
            options = req.split("|")
            if not any(r in sel_set for r in options):
                sel_set.discard(pid)
    return list(sel_set)

