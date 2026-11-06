# 🏗️ Udyam Digital — Solution Architecture
### Accel Business · YTL Hackathon 2026

---

## High-Level System Architecture

```mermaid
flowchart TD
    subgraph Channels["User Channels"]
        W["🌐 Web App\n(React PWA)"]
        WA["💬 WhatsApp Bot\n(Twilio)"]
        FT["📱 Field Tablet\n(Partner Portal)"]
    end

    subgraph Frontend["Frontend Layer"]
        A1["Advisor Tab\n(Digi Saathi)"]
        A2["Quote Tab\n(Bundle Builder)"]
        A3["KYC Tab\n(5-Step Wizard)"]
        A4["Tracker Tab\n(Order Status)"]
        A5["Partners Tab\n(Lead Queue)"]
    end

    subgraph Backend["FastAPI Backend"]
        B1["advisor.py\nPhase1→JSON\n→Rules→Phase2"]
        B2["quote_engine.py\nEligibility +\nDependency checks"]
        B3["kyc_service.py\nOCR + Registry\n+ Validation"]
        B4["tracker.py\nSQLite State\nMachine"]
        B5["propensity_model.py\nGBM Scorer\nAUC=0.628"]
        B6["catalogue.py\nShared helpers +\nPricing rules"]
    end

    subgraph DataLayer["Data Layer"]
        D1[("product_catalogue.csv\n25 products")]
        D2[("smb_leads.csv\n5,000 leads")]
        D3[("mock_gstin_registry.csv\n3,534 records")]
        D4[("mock_udyam_registry.csv\n2,723 records")]
        D5[("orders.db\nSQLite")]
    end

    subgraph External["External Services"]
        E1["Gemini 1.5 Flash\n(LLM — no PII)"]
        E2["Tesseract OCR\n(LOCAL — no network)"]
    end

    W --> Frontend
    WA --> B1
    FT --> A5

    Frontend --> Backend
    B1 --> E1
    B1 --> B6
    B2 --> B6
    B3 --> E2
    B3 --> D3
    B3 --> D4
    B4 --> D5
    B5 --> D2
    B6 --> D1

    style E2 fill:#e8f5e9,stroke:#4caf50
    style E1 fill:#e3f2fd,stroke:#2196f3
    style D3 fill:#fff3e0,stroke:#ff9800
    style D4 fill:#fff3e0,stroke:#ff9800
```

---

## Two-Phase AI Advisor Architecture

```mermaid
sequenceDiagram
    participant U as User
    participant FE as Frontend
    participant LLM as Gemini 1.5 Flash
    participant RE as Rules Engine
    participant DB as Product Catalogue

    Note over U,DB: Phase 1 — Profile Collection
    U->>FE: "I run a dental clinic, 8 staff, Kochi"
    FE->>LLM: message + language hint
    LLM-->>FE: Asks next question (ONE at a time)
    FE->>U: "How many sites do you have?"
    U->>FE: "Just one clinic"
    FE->>LLM: message
    LLM-->>FE: JSON profile emitted
    Note right of LLM: {"business_type":"clinic",\n"employee_count":8,\n"num_sites":1,\n"city":"Kochi",\n"has_gstin":true}

    Note over U,DB: Rules Engine Phase (no LLM)
    FE->>RE: profile JSON
    RE->>DB: eligible_products() check
    DB-->>RE: filtered product list
    RE-->>FE: bundle with prices (from catalogue)

    Note over U,DB: Phase 2 — Plain-language Explanation
    FE->>LLM: [BUNDLE] JSON + "explain this"
    LLM-->>FE: Warm explanation (prices from bundle, never guessed)
    FE->>U: "Great news! For your clinic..."
```

> **Key Guarantee:** The LLM **never states a price**. All prices come from the rules engine reading the product catalogue CSV. This prevents hallucination and ensures accuracy.

---

## Smart KYC Validation Flow

```mermaid
flowchart TD
    Start["User uploads document"] --> SizeCheck{"File size\n> 500 bytes?"}
    SizeCheck -- No --> EmptyFlag["🚩 Flag: Document empty\nor unreadable"]
    SizeCheck -- Yes --> OCR["Tesseract OCR\n(runs locally)"]
    OCR --> DocType{"Document Type?"}

    DocType -- "GST Certificate" --> GSTIN1["Extract GSTIN\npattern from text"]
    GSTIN1 --> Match1{"Matches\nentered GSTIN?"}
    Match1 -- No --> Flag1["🚩 GSTIN mismatch"]
    Match1 -- Yes --> Registry{"GSTIN status\nin registry?"}
    Registry -- "Cancelled/Suspended" --> Flag2["🚩 Inactive GSTIN"]
    Registry -- Active --> NameCheck{"Business name\nmatches?"}
    NameCheck -- No --> Flag3["🚩 Name mismatch"]
    NameCheck -- Yes --> OK1["✅ GST cert OK"]

    DocType -- "Address Proof" --> DateParse["Parse issue date\n(labelled > unlabelled)"]
    DateParse --> AgeCheck{"Age ≤ 90 days\nfrom 2026-07-15?"}
    AgeCheck -- No --> Flag4["🚩 Address proof\ntoo old"]
    AgeCheck -- Yes --> OK2["✅ Address proof OK"]

    DocType -- "Udyam Certificate" --> UdyamExtract["Extract UDYAM-XX-00-XXXXXXX"]
    UdyamExtract --> UdyamMatch{"Matches\nentered number?"}
    UdyamMatch -- No --> Flag5["🚩 Udyam mismatch"]
    UdyamMatch -- Yes --> CrossCheck{"Name matches\nGSTIN registry?"}
    CrossCheck -- No --> Flag6["🚩 Cross-registry\nname mismatch"]
    CrossCheck -- Yes --> OK3["✅ Udyam cert OK"]

    DocType -- "Signatory ID" --> MaskAadhaar["Mask Aadhaar:\nXXXX XXXX 1234"]
    MaskAadhaar --> NameVerify{"Signatory name\nin document?"}
    NameVerify -- No --> Flag7["🚩 Signatory name\nnot found"]
    NameVerify -- Yes --> OK4["✅ ID verified"]
```

---

## Order State Machine

```mermaid
stateDiagram-v2
    [*] --> ACCEPTED: Quote accepted
    ACCEPTED --> KYC_SUBMITTED: Documents uploaded
    KYC_SUBMITTED --> KYC_VERIFIED: Auto-validated (or agent approved)
    KYC_VERIFIED --> ORDER_PLACED: Backend places order with provisioning
    ORDER_PLACED --> INSTALLATION_SCHEDULED: Engineer assigned
    INSTALLATION_SCHEDULED --> TECH_VISIT_DONE: Engineer completes work
    TECH_VISIT_DONE --> ACTIVATED: Services go live
    ACTIVATED --> [*]

    note right of KYC_SUBMITTED
        WhatsApp notification sent
        "Documents received"
    end note
    note right of ACTIVATED
        WhatsApp notification sent
        "Welcome to Accel Business!"
    end note
```

---

## Propensity Scoring Model

```
Input Features (pre-outcome only — no leakage):
  ├── has_gstin_bin          (1/0)
  ├── has_udyam_bin          (1/0)
  ├── employee_count         (integer)
  ├── num_sites              (integer)
  ├── city_tier_bin          (1=Tier1, 2=Tier2)
  ├── monthly_telecom_spend  (₹/month)
  ├── segment_enc            (label encoded)
  ├── source_enc             (label encoded)
  └── state_enc              (label encoded)

Model: GradientBoostingClassifier
  n_estimators=200, max_depth=4, random_state=42
  Train/test split: 80/20 stratified
  AUC on held-out test set: 0.628
  Top-3 feature importances:
    1. monthly_telecom_spend_inr  (~40%)
    2. employee_count              (~20%)
    3. state_enc                   (~15%)

Output → Score 0–100, Priority (HIGH ≥15, MEDIUM ≥7, LOW <7)
```

---

## Technology Stack

| Layer | Technology | Version | Reason |
|-------|-----------|---------|--------|
| Frontend | React + Vite | 18.x / 5.x | Fast dev, tiny bundle (262KB) |
| Styling | TailwindCSS | 3.x | Utility-first, mobile responsive |
| HTTP client | Axios | 1.x | Clean promise API, interceptors |
| Backend | FastAPI | 0.111+ | Async, OpenAPI docs auto-generated |
| AI advisor | LangChain + Gemini 1.5 Flash | 1.x | Two-phase conversation, cheap & fast |
| OCR | Tesseract (pytesseract) | 0.3.13 | Local, no PII leaves server |
| ML model | scikit-learn GBM | 1.5+ | No leakage, AUC 0.628 |
| Database | SQLite (orders) | — | Zero-config, demo-ready |
| Data | Pandas | 2.x | CSV processing at startup |
| Containerisation | Docker + Compose | — | One-command deploy |
| Auth (prod) | OAuth 2.0 + JWT | — | Planned for production |

---

*Prepared for YTL Hackathon 2026 · Accel Business · All data synthetic*
