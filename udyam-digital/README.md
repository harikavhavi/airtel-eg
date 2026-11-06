# 🚀 Udyam Digital — Project Setup Guide
### YTL Hackathon 2026 · Accel Business SMB Onboarding

---

## Quick Start (Local Development)

### Prerequisites
- Python 3.12+ (venv already created at `backend/venv/`)
- Node.js 20+ (node_modules already installed at `frontend/node_modules/`)
- Tesseract OCR installed on your system
- A **Google Gemini API key** (free at [aistudio.google.com](https://aistudio.google.com))

### 1. Install Tesseract OCR (required for KYC document processing)
**Windows:** Download installer from https://github.com/UB-Mannheim/tesseract/wiki  
**Mac:** `brew install tesseract`  
**Linux:** `sudo apt install tesseract-ocr`

### 2. Set your Google API Key

Edit `backend/.env` and replace `your_google_api_key_here`:
```
GOOGLE_API_KEY=AIzaSy...your_real_key_here
```

### 3. One-click Start (Windows)

**Option A — Double-click:**
```
udyam-digital\start.bat
```

**Option B — PowerShell:**
```powershell
cd "C:\Users\harik\Downloads\AIRTEL eg\udyam-digital"
.\start.ps1
```

This opens **two terminal windows** — backend on port 8000, frontend on port 3000.

### 4. Manual Start (if one-click fails)

**Terminal 1 — Backend:**
```powershell
cd backend
.\venv\Scripts\uvicorn main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```powershell
cd frontend
npm run dev
```

| URL | Purpose |
|-----|---------|
| http://localhost:3000 | **React app (open this in browser)** |
| http://localhost:8000/docs | FastAPI Swagger UI (all endpoints) |

---

## Project Structure

```
udyam-digital/
├── backend/
│   ├── main.py               # FastAPI app entry point
│   ├── advisor.py            # GenAI advisor (LangChain + Gemini)
│   ├── quote_engine.py       # Quote generation with eligibility checks
│   ├── kyc_service.py        # KYC OCR + registry lookup + cross-validation
│   ├── tracker.py            # Order state machine (SQLite)
│   ├── propensity_model.py   # ML propensity scoring (GBM)
│   ├── catalogue.py          # Shared product catalogue helpers
│   └── data/
│       ├── product_catalogue.csv
│       ├── smb_leads.csv
│       ├── mock_gstin_registry.csv
│       ├── mock_udyam_registry.csv
│       └── kyc_documents/    (K01–K12 specimen docs)
├── frontend/
│   └── src/
│       ├── App.jsx
│       └── pages/
│           ├── Advisor.jsx       # Digi Saathi chat interface
│           ├── Quote.jsx         # Quote card with toggles
│           ├── KYC.jsx           # KYC wizard (consent → lookup → upload)
│           ├── Tracker.jsx       # Order status timeline
│           └── PartnerPortal.jsx # Back-office with propensity scores
├── docker-compose.yml
└── README.md
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/advisor/chat` | Send message to Digi Saathi advisor |
| DELETE | `/advisor/session/{id}` | Clear advisor session |
| POST | `/quote/generate` | Generate quote with eligibility checks |
| GET | `/kyc/gstin/{gstin}` | GSTIN registry lookup + validation |
| GET | `/kyc/udyam/{udyam}` | Udyam registry lookup + validation |
| POST | `/kyc/extract_document` | OCR document + cross-field validation |
| POST | `/tracker/create` | Create a new order |
| GET | `/tracker/{order_id}` | Get order status |
| POST | `/tracker/{order_id}/advance` | Advance order state (demo) |
| POST | `/propensity/score` | Score a single lead |
| GET | `/propensity/leads` | Get all open leads sorted by score |

---

## KYC Validation Matrix

The system checks all of the following across the 12 test applicants (K01–K12):

| Check | What is validated |
|-------|-------------------|
| GSTIN format | 15 chars, state code 01-38, PAN pattern, checksum |
| GSTIN registry | Active / Cancelled / Suspended status |
| GSTIN × certificate | Number on cert must match entered number |
| GSTIN × business name | Trade name in registry must appear on certificate |
| Udyam format | UDYAM-XX-DD-XXXXXXX pattern |
| Udyam × certificate | Number on cert must match entered number |
| Udyam × GSTIN | Business name consistency across both registries |
| Address proof date | Must be ≤ 90 days old from 2026-07-15 |
| Signatory name | Name on ID must match declared signatory name |
| Missing documents | Empty/tiny file detected (e.g. K05 missing Udyam cert) |

---

## Propensity Model Performance

Trained on 5,000 SMB leads (80/20 split, stratified):
- **Features used:** has_gstin, has_udyam, employee_count, num_sites, city_tier, monthly_telecom_spend, segment, lead_source, state
- **No leakage:** drop_reason, stage_dates, bundle data excluded
- **Model:** Gradient Boosting (200 trees, depth 4)
- **AUC = 0.628** on held-out 20% test set (baseline conversion 7.4%)
- Top-decile lift printed at backend startup

---

## Data Privacy (DPDP Act 2023)

- Per-purpose itemised consent before any document upload
- OCR runs locally (Tesseract) — no image sent to external API
- Aadhaar numbers masked (`XXXX XXXX 1234`) immediately after extraction; images not retained
- All identifiers masked in application logs
- Grievance contact: privacy@accel.in

---

## Demo Script (3 minutes)

```
0:00-0:30  Show funnel: "Only 7.4% of 5,000 SMB leads activated"
0:30-1:15  Advisor tab: type business type → get Hindi bundle recommendation
1:15-1:45  Quote tab: show toggles, transparent pricing, activation note
1:45-2:30  KYC tab: upload a specimen doc → watch OCR flag a planted error
2:30-2:50  Tracker tab: create sample order → advance through states
2:50-3:00  Partners tab: show propensity-sorted lead queue with scores
```

---

*All data is synthetic. Prepared for YTL Hackathon 2026.*
