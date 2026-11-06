# 📊 Udyam Digital — 10-Slide Business Case
### Accel Business · YTL Hackathon 2026 · Track A

---

## Slide 1 — The Opportunity

### 6 Crore+ MSMEs. Only 7.4% Converting.

| Metric | Today | Potential |
|--------|-------|-----------|
| Total MSME businesses in India | 6.3 crore | — |
| SMB leads in pilot dataset | 5,000 | — |
| Leads that activate | **368 (7.4%)** | 1,000 (20%) |
| Revenue lost per quarter (missed activations) | ₹43L/month MRR | — |
| Average cost per activation | ₹15,000 | ₹5,000 |

> **The gap:** 92.6% of interested SMBs walk away before activating — not because they don't want connectivity, but because the journey is too hard.

---

## Slide 2 — Root Cause Analysis

### Why SMBs Drop Out (from 5,000-lead dataset)

| Drop Reason | Leads Lost | % of Base | Our Fix |
|-------------|-----------|-----------|---------|
| Unreachable after 3 attempts | 805 | **16.1%** | WhatsApp/chat async channel |
| Owner had no time for a visit | 531 | **10.6%** | Self-serve — no visit needed |
| Not interested on first call | 470 | **9.4%** | Tailored AI bundle = instant relevance |
| Price too high | 414 | **8.3%** | Transparent bundled pricing shows value |
| Locked in with current provider | 325 | **6.5%** | Contract lock-in incentive + switching deal |
| Quote too complex | 206 | **4.1%** | Plain-language quote with toggles |

**Combined opportunity:** Top 3 reasons alone = **36.1% of base** — fixable with digital self-serve.

---

## Slide 3 — Our Solution: 4-Module Digital Journey

```
SMB Owner
   │
   ▼
[1] DIGI SAATHI (GenAI Advisor)
    • Multilingual (EN + HI + regional)
    • 5 questions → structured profile
    • Rules engine → personalised bundle
    • LLM explains in plain language
   │
   ▼
[2] TRANSPARENT QUOTE ENGINE
    • Instant pricing — no PDF, no waiting
    • Toggle add-ons on/off
    • Eligibility checks built in
    • One-click order creation
   │
   ▼
[3] SMART KYC (10-minute digital verification)
    • GSTIN + Udyam registry lookup
    • OCR document extraction (local — no data leaves)
    • Cross-field validation catches errors automatically
    • DPDP Act compliant consent screen
   │
   ▼
[4] ORDER TRACKER + PARTNER PORTAL
    • Real-time status (no more "where is my connection?")
    • Field force sees AI-scored leads sorted by propensity
    • Automated WhatsApp updates at every milestone
```

**Result:** SMB goes from "interested" to "activated" in **1 sitting** (SIM/cloud) or **≤3 days** (fibre).

---

## Slide 4 — Target Segments (Prioritised by Data)

| Segment | Market Share | Conversion | ARPU/mo | Priority | Reason |
|---------|-------------|-----------|---------|---------|--------|
| **Professional offices** | 25% | **11%** | ₹6,216 | 🥇 **Phase 1** | High conversion, volume, GSTIN penetration |
| **Small multi-site** | 15% | **11%** | ₹13,334 | 🥈 Phase 2 | High bundle value, needs SD-WAN |
| **Small manufacturers** | 5% | **12%** | ₹14,729 | 🥉 Phase 2 | Highest conversion, complex needs |
| **Micro retail & services** | 55% | **4%** | ₹2,196 | 📈 Phase 3 | Huge volume, needs low-friction path |

**Launch city selection:** Mumbai + Bengaluru (Tier-1, highest GSTIN density, highest telecom spend).

---

## Slide 5 — Recommended Bundles

### Bundle A — "Digital Starter" (Micro, ₹1,597–2,196/mo)
> Kirana, salon, pharmacy | 1–5 employees, 1 site
- Biz Fibre 100 + Business Postpaid 299 + Website & Domain
- **With GSTIN:** + Cloud POS & Billing (₹599/mo) → unlocks upsell
- **No-GSTIN path:** Still activates — GSTIN guidance offered post-activation

### Bundle B — "Pro Office" (Professional, ₹6,216/mo)
> Clinic, CA firm, coaching centre | 5–20 employees
- Biz Fibre 300 + 2 Postpaid SIMs + 5 Cloud Email + Endpoint Security + Secure Wi-Fi + Cloud Telephony

### Bundle C — "Multi-Site Connect" (Multi-site, ₹13,334/mo)
> Restaurant chain, 3–10 store retailer | 20–50 employees, 3+ sites
- 3× Biz Fibre 300 + 4G/5G Failover + 4 SIMs + Cloud CCTV + Managed SD-WAN + Cloud Email

### Bundle D — "Manufacturing Power" (Mfg, ₹14,729/mo)
> Auto-parts, textile unit | 25+ employees, GSTIN required
- Internet Leased Line 20 + 5 SIMs + Machine Monitoring IoT + Managed Firewall + Endpoint Security

---

## Slide 6 — Technology Architecture

```
                    ┌─────────────────────────────────────┐
                    │         USER CHANNELS                │
                    │  Web App   WhatsApp   Field Tablet   │
                    └────────────────┬────────────────────┘
                                     │ HTTPS / TLS 1.3
                    ┌────────────────▼────────────────────┐
                    │         REACT FRONTEND (PWA)         │
                    │  Advisor · Quote · KYC · Tracker    │
                    └────────────────┬────────────────────┘
                                     │ REST API
                    ┌────────────────▼────────────────────┐
                    │          FASTAPI BACKEND             │
                    ├──────────┬──────────┬───────────────┤
                    │  Advisor │  Quote   │  KYC Service  │
                    │  (Phase  │  Engine  │  (Tesseract   │
                    │  1→JSON  │  Rules   │   Local OCR)  │
                    │  →Rules  │  Engine) │               │
                    │  →Phase2)│          │               │
                    ├──────────┴──────────┴───────────────┤
                    │   Order Tracker  │  Propensity ML   │
                    │   (SQLite FSM)   │  (GBM, AUC 0.63) │
                    └────────┬─────────┴──────────────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
      Gemini 1.5 Flash  Product CSVs   GSTIN/Udyam
      (LLM — no PII)   (25 products)  Registries
```

**Key design decisions:**
- Prices from rules engine only — LLM **never** states a price
- OCR runs locally — no document leaves the server
- LLM receives redacted profile only — no Aadhaar/GSTIN in LLM context

---

## Slide 7 — Business Case (ROI)

### CAC: ₹15,000 → ₹5,000 (~67% reduction)

| Model | Activations/Quarter | CAC | Quarterly Acq. Cost | Monthly MRR |
|-------|--------------------|----|--------------------|-----------:|
| **Today** (field sales) | 368 (7.4%) | ₹15,000 | ₹55.2L | ₹25.4L |
| **Year 1 Target** (12%) | 600 | ₹8,000 | ₹48L | ₹41.4L |
| **Year 3 Target** (20%) | 1,000 | ₹5,000 | ₹50L | ₹55L |

### Cost Assumptions (Year 3 Target)
```
1,000 fully digital activations × ₹3,000     = ₹30L
4,000 partial-touch (1 field call) × ₹5,000  = ₹20L
                                 Total CAC   = ₹50L / 1,000 = ₹5,000 per activation

Platform infra (cloud hosting):              ~₹2L/month
LLM API cost (5,000 sessions × ₹2):         ~₹1L/month
```

### Payback Period
- Average bundle: ₹5,500/month × 40% contribution margin = **₹2,200/month**
- CAC payback: ₹5,000 ÷ ₹2,200 = **~2.3 months**

### Churn Impact
- Current 6-month churn: 15% → Target: 8% (better onboarding = stickier customers)
- At 1,000 activations/quarter: 7% churn reduction = **₹3.8L MRR saved annually**

---

## Slide 8 — Metrics & Targets

| KPI | Current Baseline | Year 1 Pilot Target | Year 3 Scale Target |
|-----|-----------------|--------------------|--------------------|
| Lead-to-activation rate | **7.4%** | 12% | 20% |
| Avg days to activate | **17.6 days** | SIM/cloud: same day | Fibre: ≤3 days |
| Cost per activation | **₹15,000** | ₹8,000 | ₹5,000 |
| Follow-up calls per customer | **3.0** | ≤1.0 | ≤0.5 |
| KYC completion rate | **68%** | ≥85% | ≥90% |
| 6-month churn | **15%** | ≤10% | ≤8% |
| NPS score | **6.86** | ≥7.5 | ≥8.0 |

### Funnel Improvement Model
```
Current:  5,000 → 3,406 → 1,974 → 861 → 588 → 368 (7.4%)
Target:   5,000 → 4,500 → 3,000 → 2,000 → 1,800 → 1,000 (20%)

Lever                Before  After   Driver
Reached/contacted:    68%     90%    WhatsApp async removes "unreachable"
Needs → Quote:        44%     67%    AI advisor + instant quote
KYC completion:       68%     90%    Digital OCR + auto-fill
Quote → Activate:     63%     56%    (conservative — lower than baseline)
```

---

## Slide 9 — Rollout Plan

### Phase 1: Proof of Concept (Month 1–3)
- **Cities:** Mumbai + Bengaluru (Tier-1, highest GSTIN density)
- **Segment:** Professional offices only (best conversion-to-volume ratio)
- **Channels:** Web app + field agent tablet
- **Target:** 500 digital leads, 60 activations (12%)
- **Success gate:** KYC auto-approval ≥85%, NPS ≥7.5

### Phase 2: Expansion (Month 4–6)
- **Cities:** Add Delhi, Hyderabad, Pune, Chennai, Ahmedabad (5 Tier-1 cities)
- **Segments:** Add multi-site and micro (with no-GSTIN path)
- **Channels:** Add WhatsApp bot + partner portal for channel partners
- **Target:** 2,000 digital leads, 240 activations

### Phase 3: Scale (Month 7–12)
- **Cities:** 20 Tier-2 cities (Jaipur, Lucknow, Bhopal, Coimbatore, etc.)
- **Channels:** Add voice bot (IVR → AI handoff), regional language expansion
- **Target:** 10,000 leads/month, 2,000 activations (20%)

### Phase 4: National (Year 2+)
- **DigiLocker integration** — eliminate physical document upload
- **Aadhaar e-KYC** — 2-minute verification
- **Franchise/DSA portal** — extend to 5,000+ channel partners nationally

---

## Slide 10 — Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| LLM hallucinates prices | Medium | High | **Prices come from rules engine ONLY** — LLM never states a figure; architecture enforces this |
| OCR fails on poor-quality photos | High | Medium | Fallback: manual upload + agent review queue; file-size guard catches blanks |
| Field force resistance | High | High | Partner portal shows field team their own leads scored higher with digital assist; commission structure preserved |
| GSTIN/Udyam registry downtime | Low | High | Local CSV cache; graceful degradation to manual entry with flag |
| Data breach / API key leak | Low | Very High | Local OCR, PII masking in logs, secrets in env vars, no PII in LLM context |
| Low adoption by micro segment | High | Medium | No-GSTIN path enabled; WhatsApp bot (lower friction than web); vernacular language support |
| Regulatory change (DPDP rules) | Low | Medium | Modular consent layer easily updated; privacy officer review quarterly |

---

*All numbers sourced from the provided smb_leads.csv (5,000 records), product_catalogue.csv (25 products), and mock registries.*  
*All assumptions are explicitly stated. Synthetic data only.*  
*YTL Hackathon 2026 · Accel Business · Track A*

