# 🎬 Udyam Digital — 3-Minute Demo Script
### YTL Hackathon 2026 · Accel Business · Track A

---

## Pre-Demo Setup Checklist
- [ ] Backend running: `http://localhost:8000` (check `/health`)
- [ ] Frontend running: `http://localhost:3000`
- [ ] Browser at `http://localhost:3000` — full screen, zoom 110%
- [ ] KYC specimen `K01_gst_certificate.png` ready to upload from Desktop
- [ ] Order ID notepad ready for Tracker demo

---

## 0:00–0:25 — Hook: The Problem (25 seconds)

**[Stay on a blank slide or the partner portal]**

> *"Every year, Accel Business reaches out to thousands of small businesses — clinics, pharmacies, restaurants, manufacturers — with great connectivity products. But look at this data..."*

**[Show funnel numbers on screen or in slides]**

> *"5,000 leads. Only 368 activated. That's just 7.4%. The number-one reason? They couldn't be reached after 3 attempts — 805 businesses, just... gone. The second reason? The owner had no time for a site visit. These aren't bad leads. The process is broken."*

> *"Today we're showing you how Udyam Digital fixes that — a fully digital onboarding journey where an SMB owner can go from 'interested' to 'activated' in a single sitting, on their phone."*

---

## 0:25–1:10 — Module 1: Digi Saathi Advisor (45 seconds)

**[Click to Advisor tab]**

> *"Meet Digi Saathi — your AI business advisor. Watch what happens when I describe my business."*

**[Type in chat box:]** `I run a dental clinic with 8 staff in Kochi. We have one location and we have a GSTIN.`

> *"Digi Saathi is now collecting a structured profile — just 5 fields — using the LLM. Watch..."*

**[Wait for follow-up question from Digi Saathi, answer it. After profile complete:]**

> *"The LLM has extracted the profile and handed it to our rules engine — which looks up the product catalogue and applies eligibility rules. Prices NEVER come from the LLM. They come from the catalogue. No hallucinations."*

**[Show bundle card appearing]**

> *"And Digi Saathi explains it back — in plain language. Watch — I'll switch to Hindi."*

**[Click Hindi button, type:]** `मेरी clinic के लिए कौन सा plan सही रहेगा?`

> *"Same rules engine. Different language. The bundle prices are identical because they're from the catalogue, not the LLM."*

---

## 1:10–1:40 — Module 2: Quote Engine (30 seconds)

**[Click to Quote tab]**

> *"Now let's say the customer wants to customise their bundle. I'll set segment to Professional, Tier-1, 10 employees, has GSTIN."*

**[Click Generate Quote]**

> *"Instant pricing — no PDF, no waiting 3 days. And look — I can toggle add-ons on and off. When I remove Secure Wi-Fi, the total updates immediately."*

**[Toggle one item off]**

> *"If the customer says the price is too high, the advisor can say — 'just remove the Wi-Fi add-on and save ₹399 a month.' No more 'quote too complex' drop-off."*

**[Click "Accept & Proceed to KYC" — note the Order ID]**

> *"One click creates the order. Let's complete KYC."*

---

## 1:40–2:25 — Module 3: Smart KYC (45 seconds)

**[Click to KYC tab]**

> *"The KYC wizard starts with a consent screen — DPDP Act compliant, per-purpose itemised consent. Required vs optional are clearly separated."*

**[Tick the two required checkboxes, click Continue]**

> *"GSTIN verification — I'll enter `32TTNXB7384T1ZW`."*

**[Type GSTIN, click Verify]**

> *"Registry match — Balaji Dental Care LLP, Active. Cross to Udyam — I'll skip for now. Now document upload."*

**[Upload K01_gst_certificate.png for 'GST Certificate']**

> *"OCR runs locally — the image never leaves this server. Watch the cross-field validation..."*

**[Point to flags or green checkmark]**

> *"The system extracted the GSTIN from the certificate image and confirmed it matches what was entered. It also checked the business name against the registry."*

> *"This is what gives us an answer-key-ready KYC — we test against all 12 specimen applicants including K05, which is missing its Udyam certificate. Our size-guard catches that."*

---

## 2:25–2:50 — Module 4: Order Tracker (25 seconds)

**[Click to Tracker tab]**

> *"The customer never needs to call 'where is my connection'. Enter the order ID we just created..."*

**[Type the order ID, click Track]**

> *"Status: Accepted. Progress bar at 0%. Estimated activation date shown. Now watch the demo advance — this simulates what happens when our backend processes the order."*

**[Click "Advance to Next Step" twice]**

> *"KYC Submitted... KYC Verified. The customer gets a WhatsApp notification at every step. 3 follow-up calls becomes half a call."*

---

## 2:50–3:00 — Module 5: Partner Portal (10 seconds)

**[Click to Partners tab]**

> *"Finally — the partner back-office. 4,632 open leads, sorted by our AI propensity model. Top lead: Zenith Printers, score 76. Field agent calls this one first. That's how we turn field force from reactive to data-driven."*

> *"Thank you."*

---

## Judges Q&A — Anticipated Questions

| Question | Answer |
|----------|--------|
| "How do you ensure the LLM doesn't hallucinate prices?" | Prices are NEVER in the LLM context. The rules engine reads product_catalogue.csv and builds the bundle. The LLM only receives the bundle JSON and explains it in plain language. |
| "What happens if OCR fails?" | The system flags the document for manual agent review. There's also a size guard — files under 500 bytes are caught as blank/empty (handles K05's missing Udyam cert). |
| "Is this DPDP Act compliant?" | Yes — itemised per-purpose consent, Aadhaar masked immediately post-extraction, OCR runs locally (no image leaves server), grievance officer contact shown. |
| "What's the AUC of your propensity model?" | 0.628 on a held-out 20% test split, stratified by conversion. Features are pre-outcome only — no data leakage. Top feature: monthly telecom spend. |
| "How does it handle SMBs without GSTIN?" | Bundle A has an explicit no-GSTIN path — Micro segment gets Fibre + SIM + Website without GSTIN-gated products. The advisor offers GSTIN guidance post-activation to unlock more. |
| "What languages are supported?" | English and Hindi fully. The LLM (Gemini 1.5 Flash) handles language switching in the advisor. UI labels switch via i18n JSON files. Telugu can be added within the same framework. |

---

*Total demo time: 3 minutes · Prototype: fully functional · Data: 100% synthetic*  
*YTL Hackathon 2026 · Accel Business*
