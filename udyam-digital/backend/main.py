# ─────────────────────────────────────────────────────────────────────────────
# main.py  –  FastAPI app entry point  (mounts all routers + CORS)
# ─────────────────────────────────────────────────────────────────────────────
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from advisor import router as advisor_router
from quote_engine import router as quote_router
from kyc_service import router as kyc_router
from tracker import router as tracker_router
from propensity_model import router as propensity_router

app = FastAPI(
    title="Udyam Digital — Accel Business",
    description="Digital-first SMB onboarding: Advisor, Quote, KYC, Order Tracker",
    version="1.0.0",
)

# Allow React dev server in development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(advisor_router)
app.include_router(quote_router)
app.include_router(kyc_router)
app.include_router(tracker_router)
app.include_router(propensity_router)


@app.get("/")
def root():
    return {
        "service": "Udyam Digital — Accel Business API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": [
            "/advisor/chat",
            "/quote/generate",
            "/kyc/gstin/{gstin}",
            "/kyc/udyam/{udyam_number}",
            "/kyc/extract_document",
            "/tracker/{order_id}",
            "/tracker/create",
            "/propensity/score",
            "/propensity/leads",
        ],
    }


@app.get("/health")
def health():
    return {"status": "ok"}

