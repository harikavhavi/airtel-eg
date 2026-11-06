# 🔒 Udyam Digital — Data Privacy & Security Note
### Accel Business · YTL Hackathon 2026 · Track A

---

## Regulatory Framework

Designed for full compliance with the **Digital Personal Data Protection (DPDP) Act, 2023** and applicable TRAI telecom subscriber verification rules.

---

## Data Collected & Purpose Limitation

| Data Type | Purpose | Retention |
|-----------|---------|-----------|
| Business profile (type, size, city, employee count) | Bundle eligibility & recommendation | Session only — deleted after activation confirmed |
| GSTIN / Udyam registration number | Regulatory identity verification | Per applicable regulation (minimum required period) |
| KYC documents (photos/scans) | Regulatory compliance — subscriber verification | Per applicable regulation; securely deleted thereafter |
| Signatory Aadhaar / PAN | One-time identity verification | **Aadhaar image deleted immediately post-OCR**; only masked number (`XXXX XXXX 1234`) retained |
| Order status & communication records | Service tracking & support | 5 years |
| NPS & satisfaction feedback | Service improvement | 3 years, anonymised before analysis |

> **Data Minimisation Principle:** The advisor collects only 5–7 fields needed for eligibility. OCR extracts only required fields — full document text is never stored.

---

## Consent Design (DPDP Act Compliant)

### Itemised, Per-Purpose Consent
Before any document upload, users see a **three-item consent screen** (implemented in `KYC.jsx`):

| Consent Item | Type | Can Withdraw? |
|--------------|------|---------------|
| Identity & KYC verification | **Required** | No (service cannot proceed) |
| Order & service management | **Required** | No (service cannot proceed) |
| Marketing communications (SMS/WhatsApp offers) | **Optional** | Yes — anytime via account settings |

- Consent is **not bundled** — each purpose is separate and clearly described
- A **light privacy notice** is shown before the advisor asks for any contact detail
- Withdrawal of optional consent is effective immediately
- **Grievance contact** shown on consent screen: `privacy@accel.in`

---

## Security Controls

| Control | Implementation |
|---------|----------------|
| **Data at rest** | AES-256 encrypted object storage |
| **Data in transit** | TLS 1.3 enforced end-to-end |
| **OCR processing** | Runs **locally** via Tesseract — no document image or raw OCR text is sent to any external API or cloud service |
| **LLM interaction** | PII fields (GSTIN, Aadhaar, name) are **redacted** before any text is passed to the Gemini API |
| **Log masking** | Aadhaar, GSTIN, and Udyam numbers are automatically masked in all application logs |
| **Access control** | KYC document access restricted to verified KYC team only (RBAC) |
| **Retention enforcement** | Automated deletion scheduler triggers on retention period expiry |
| **Third-party sharing** | No document data shared with any third party except mandatory regulatory bodies |

---

## Data Flow Diagram

```
User Browser ──(TLS 1.3)──► React Frontend
                                │
                        (redacted data only)
                                │
                                ▼
                        FastAPI Backend
                        ├── Tesseract OCR (local, no network call)
                        ├── GSTIN/Udyam registry lookup (local CSV)
                        └── Gemini API ──► (profile only, no PII)
```

> **Key assurance:** The KYC document image never leaves the local server. Only extracted, masked fields are stored.

---

## User Rights (DPDP Act, Section 11–14)

| Right | How to Exercise |
|-------|-----------------|
| Right to access personal data | Email `privacy@accel.in` with verified business ID |
| Right to correction | Same channel — corrections processed within 7 days |
| Right to erasure | Processed within 30 days; regulatory-retention data noted |
| Right to grievance redressal | Grievance Officer responds within **30 days** |

**Grievance Officer:** Data Protection Officer, Accel Business  
**Contact:** privacy@accel.in  
**Response SLA:** 30 calendar days from receipt of verified request

---

## Future Roadmap (Privacy-Enhancing Technologies)

- **DigiLocker integration** — eliminates physical document upload entirely; consent via DigiLocker's own framework
- **Aadhaar e-KYC** — replaces image upload with UIDAI-authenticated pull (Aadhaar image never enters our system)
- **Federated analytics** — lead scoring model retrained on anonymised, aggregated data only

---

*All data in the prototype is 100% synthetic. No real personal data was used in development or testing.*  
*Prepared for YTL Hackathon 2026 — Accel Business Team*
