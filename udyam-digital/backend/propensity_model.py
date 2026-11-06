# ─────────────────────────────────────────────────────────────────────────────
# propensity_model.py  –  Lead scoring (no leakage, proper train/test split)
# ─────────────────────────────────────────────────────────────────────────────
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/propensity", tags=["Propensity"])

DATA_DIR = Path(__file__).parent / "data"

# ── Build model at startup ─────────────────────────────────────────────────────
df = pd.read_csv(DATA_DIR / "smb_leads.csv")

df["activated"] = (df["outcome"] == "Activated").astype(int)
df["has_gstin_bin"] = (df["has_gstin"] == "Y").astype(int)
df["has_udyam_bin"] = (df["has_udyam"] == "Y").astype(int)
df["city_tier_bin"] = pd.to_numeric(df["city_tier"], errors="coerce").fillna(2).astype(int)

# One encoder per column — avoids shared encoder bug
le_segment = LabelEncoder()
le_source   = LabelEncoder()
le_state    = LabelEncoder()

df["segment_enc"] = le_segment.fit_transform(df["segment"].fillna("unknown"))
df["source_enc"]  = le_source.fit_transform(df["lead_source"].fillna("unknown"))
df["state_enc"]   = le_state.fit_transform(df["state"].fillna("unknown"))

FEATURES = [
    "has_gstin_bin", "has_udyam_bin",
    "employee_count", "num_sites",
    "city_tier_bin", "monthly_telecom_spend_inr",
    "segment_enc", "source_enc", "state_enc",
]

X = df[FEATURES].fillna(0)
y = df["activated"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model = GradientBoostingClassifier(n_estimators=200, max_depth=4, random_state=42)
model.fit(X_train, y_train)

# ── Evaluation metrics (printed at startup) ────────────────────────────────────
_auc = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])
_top10 = int(len(y_test) * 0.1)
_top_idx = np.argsort(model.predict_proba(X_test)[:, 1])[-_top10:]
_top10_lift = y_test.iloc[_top_idx].mean() / y_test.mean()
print(f"[Propensity] AUC={_auc:.3f}  Top-10%-decile lift={_top10_lift:.1f}x")

# ── Feature importance (for "top reasons" in back-office UI) ──────────────────
_importance_pairs = sorted(
    zip(FEATURES, model.feature_importances_), key=lambda x: -x[1]
)
FEATURE_LABELS = {
    "has_gstin_bin":            "Has GSTIN",
    "has_udyam_bin":            "Has Udyam registration",
    "employee_count":           "Number of employees",
    "num_sites":                "Number of business sites",
    "city_tier_bin":            "City tier",
    "monthly_telecom_spend_inr":"Current telecom spend",
    "segment_enc":              "Business segment",
    "source_enc":               "Lead source",
    "state_enc":                "State / location",
}


# ── Scoring function ──────────────────────────────────────────────────────────
def score_lead(lead: dict) -> dict:
    """
    Score a single lead dict (pre-outcome features only).
    Returns score 0-100, top 3 factors, and call priority.
    """
    row = {f: 0 for f in FEATURES}
    row["has_gstin_bin"] = 1 if str(lead.get("has_gstin", "N")).upper() == "Y" else 0
    row["has_udyam_bin"] = 1 if str(lead.get("has_udyam", "N")).upper() == "Y" else 0
    row["employee_count"] = int(lead.get("employee_count", 1))
    row["num_sites"] = int(lead.get("num_sites", 1))
    row["city_tier_bin"] = int(lead.get("city_tier", 2))
    row["monthly_telecom_spend_inr"] = float(lead.get("monthly_telecom_spend_inr", 0))

    seg = lead.get("segment", "unknown")
    src = lead.get("lead_source", "unknown")
    st  = lead.get("state", "unknown")
    row["segment_enc"] = le_segment.transform([seg])[0] if seg in le_segment.classes_ else 0
    row["source_enc"]  = le_source.transform([src])[0]  if src in le_source.classes_  else 0
    row["state_enc"]   = le_state.transform([st])[0]    if st  in le_state.classes_   else 0

    X_new = pd.DataFrame([row])[FEATURES].fillna(0)
    prob = model.predict_proba(X_new)[0][1]
    score = round(prob * 100, 1)

    priority = "HIGH" if score >= 15 else "MEDIUM" if score >= 7 else "LOW"
    top_factors = [FEATURE_LABELS[f] for f, _ in _importance_pairs[:3]]

    return {"score": score, "priority": priority, "top_factors": top_factors}


# ── API endpoint ──────────────────────────────────────────────────────────────
class LeadScoreRequest(BaseModel):
    has_gstin: str = "N"
    has_udyam: str = "N"
    employee_count: int = 1
    num_sites: int = 1
    city_tier: int = 2
    monthly_telecom_spend_inr: float = 0
    segment: str = "Micro retail & services"
    lead_source: str = "Field sales"
    state: str = "Maharashtra"


@router.post("/score")
async def score(req: LeadScoreRequest):
    return score_lead(req.model_dump())


@router.get("/leads")
async def get_scored_leads(limit: int = 50):
    """Return top leads sorted by propensity score for the partner back-office."""
    leads_df = pd.read_csv(DATA_DIR / "smb_leads.csv")
    # Only show non-activated leads (still open)
    open_leads = leads_df[leads_df["outcome"] != "Activated"].copy()
    scored = []
    for _, row in open_leads.iterrows():
        s = score_lead(row.to_dict())
        scored.append({
            "lead_id": row["lead_id"],
            "business_name": row["business_name"],
            "business_type": row["business_type"],
            "segment": row["segment"],
            "city": row["city"],
            "city_tier": row["city_tier"],
            "state": row["state"],
            "preferred_language": row.get("preferred_language", "English"),
            "contact_name": row["contact_name"],
            "stage_reached": row["stage_reached"],
            "drop_reason": row.get("drop_reason", ""),
            "monthly_telecom_spend_inr": row["monthly_telecom_spend_inr"],
            "has_gstin": row["has_gstin"],
            "products_of_interest": row.get("products_of_interest", ""),
            "score": s["score"],
            "priority": s["priority"],
            "top_factors": s["top_factors"],
        })

    scored.sort(key=lambda x: -x["score"])
    return scored[:limit]

