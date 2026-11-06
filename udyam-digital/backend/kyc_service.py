# ─────────────────────────────────────────────────────────────────────────────
# kyc_service.py  –  Smart KYC: registry lookups, OCR, and cross-field validation
# ─────────────────────────────────────────────────────────────────────────────
import csv, re, io
from datetime import datetime, date
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form
from pydantic import BaseModel
from PIL import Image
import pytesseract

router = APIRouter(prefix="/kyc", tags=["KYC"])

TODAY = date(2026, 7, 15)   # "today" per README
DATA_DIR = Path(__file__).parent / "data"

# ── Load registries at startup ────────────────────────────────────────────────
GSTIN_DB: dict = {}
UDYAM_DB: dict = {}

with open(DATA_DIR / "mock_gstin_registry.csv", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        GSTIN_DB[row["gstin"]] = row

with open(DATA_DIR / "mock_udyam_registry.csv", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        UDYAM_DB[row["udyam_number"]] = row

# ── GSTIN checksum (mod-36 Luhn-like) ────────────────────────────────────────
_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def _gstin_checksum(gstin: str) -> bool:
    total = 0
    for i, ch in enumerate(gstin[:-1]):
        val = _CHARS.index(ch)
        val = val * 2 if i % 2 else val
        total += val // 36 + val % 36
    check = (36 - (total % 36)) % 36
    return _CHARS[check] == gstin[-1]


# ── Format validators ─────────────────────────────────────────────────────────
def validate_gstin_format(gstin: str) -> tuple[bool, str]:
    """
    15-char GSTIN: state code (01-38) + PAN (5L+4D+1L) + entity + Z + checksum.
    4th char of PAN (gstin[5]) = 'X' is accepted for this mock dataset (per README).
    """
    if len(gstin) != 15:
        return False, "GSTIN must be exactly 15 characters"
    sc = gstin[:2]
    if not sc.isdigit() or not (1 <= int(sc) <= 38):
        return False, f"Invalid state code '{sc}'"
    pan = gstin[2:12]
    if not re.match(r"^[A-Z]{5}[0-9]{4}[A-Z]$", pan):
        return False, "Invalid PAN pattern within GSTIN"
    if not _gstin_checksum(gstin):
        return False, "GSTIN checksum verification failed"
    return True, "OK"


def validate_udyam_format(udyam: str) -> tuple[bool, str]:
    """UDYAM-XX-00-XXXXXXX  (district code 00 accepted per README)."""
    if not re.match(r"^UDYAM-[A-Z]{2}-\d{2}-\d{7}$", udyam):
        return False, "Invalid format — expected UDYAM-ST-00-XXXXXXX"
    return True, "OK"


# ── Reliable document-date parser ─────────────────────────────────────────────
def _parse_doc_date(text: str) -> date | None:
    """
    Find the most recent plausible issue date in OCR text.
    Prefers dates labelled with 'date', 'dated', 'issued', 'dt'.
    """
    labelled = re.findall(
        r'(?:date|dated|issued?|dt\.?)\s*[:\-]?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})',
        text, re.IGNORECASE
    )
    candidates = labelled or re.findall(r'\b(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4})\b', text)
    parsed = []
    for ds in candidates:
        ds_norm = ds.replace("-", "/")
        for fmt in ("%d/%m/%Y", "%m/%d/%Y"):
            try:
                parsed.append(datetime.strptime(ds_norm, fmt).date())
                break
            except ValueError:
                continue
    plausible = [d for d in parsed if d <= TODAY]
    return max(plausible) if plausible else None


# ── Registry lookup endpoints ─────────────────────────────────────────────────
@router.get("/gstin/{gstin}")
async def lookup_gstin(gstin: str):
    g = gstin.strip().upper()
    valid, msg = validate_gstin_format(g)
    if not valid:
        return {"status": "invalid_format", "message": msg}

    rec = GSTIN_DB.get(g)
    if not rec:
        return {"status": "not_found", "message": "GSTIN not found in registry"}

    if rec["status"] != "Active":
        return {
            "status": "inactive",
            "message": f"GSTIN status is '{rec['status']}' — cannot proceed",
            "legal_name": rec["legal_name"],
        }

    return {
        "status": "active",
        "legal_name": rec["legal_name"],
        "trade_name": rec["trade_name"],
        "constitution": rec["constitution"],
        "address": rec["principal_place_of_business"],
        "state": rec["state"],
        "registration_date": rec["registration_date"],
    }


@router.get("/udyam/{udyam_number}")
async def lookup_udyam(udyam_number: str):
    u = udyam_number.strip().upper()
    valid, msg = validate_udyam_format(u)
    if not valid:
        return {"status": "invalid_format", "message": msg}

    rec = UDYAM_DB.get(u)
    if not rec:
        return {"status": "not_found", "message": "Udyam number not found in registry"}

    return {
        "status": "found",
        "enterprise_name": rec["enterprise_name"],
        "enterprise_type": rec["enterprise_type"],
        "major_activity": rec["major_activity"],
        "state": rec["state"],
        "city": rec["city"],
        "date_of_registration": rec["date_of_registration"],
    }


# ── Document OCR & cross-field validation ────────────────────────────────────
@router.post("/extract_document")
async def extract_document(
    doc_type: str = Form(...),
    gstin_entered: str = Form(""),
    udyam_entered: str = Form(""),
    signatory_name_entered: str = Form(""),
    file: UploadFile = File(...),
):
    """
    OCR a KYC document and run all cross-field validations.
    NOTE: OCR runs locally (Tesseract). No image or raw text leaves this service.
    """
    raw_bytes = await file.read()

    # Guard: empty or trivially small file = missing document
    if len(raw_bytes) < 500:
        return {
            "doc_type": doc_type,
            "status": "error",
            "flags": ["⚠️ Document appears to be empty or unreadable — please re-upload."],
            "extracted_fields": {},
        }

    image = Image.open(io.BytesIO(raw_bytes))
    raw_text = pytesseract.image_to_string(image)

    flags: list[str] = []
    fields: dict = {}

    # ── Address proof ─────────────────────────────────────────────────────────
    if doc_type == "address_proof":
        doc_date = _parse_doc_date(raw_text)
        if doc_date:
            age = (TODAY - doc_date).days
            fields["document_date"] = str(doc_date)
            fields["days_old"] = age
            if age > 90:
                flags.append(
                    f"⚠️ Address proof is {age} days old (maximum 90 days allowed). "
                    f"Please provide a document dated after {date(2026, 4, 16)}."
                )
            else:
                fields["date_valid"] = True
        else:
            flags.append("⚠️ Could not find a valid issue date in this document.")

    # ── GST certificate ───────────────────────────────────────────────────────
    elif doc_type == "gstin_certificate":
        gstin_pat = r"\b[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][0-9A-Z]{3}\b"
        matches = re.findall(gstin_pat, raw_text)
        if matches:
            on_cert = matches[0]
            fields["gstin_on_certificate"] = on_cert

            # 1. GSTIN on certificate vs entered GSTIN
            if gstin_entered and on_cert != gstin_entered.strip().upper():
                flags.append(
                    f"⚠️ GSTIN mismatch: certificate shows {on_cert} but you entered "
                    f"{gstin_entered.upper()}"
                )

            # 2. Registry status
            rec = GSTIN_DB.get(on_cert)
            if rec:
                fields["registry_legal_name"] = rec["legal_name"]
                if rec["status"] != "Active":
                    flags.append(
                        f"⚠️ GSTIN '{on_cert}' is '{rec['status']}' in the registry — "
                        "cannot proceed with this GSTIN."
                    )
                # 3. Business name on certificate vs registry
                name_words = {w for w in rec["legal_name"].lower().split() if len(w) > 3}
                cert_lower = raw_text.lower()
                if name_words and not any(w in cert_lower for w in name_words):
                    flags.append(
                        "⚠️ Business name on the certificate may not match the registry "
                        f"record ('{rec['legal_name']}') — manual review recommended."
                    )
            else:
                flags.append(f"⚠️ GSTIN '{on_cert}' not found in registry.")
        else:
            flags.append("⚠️ Could not extract a GSTIN from this certificate.")

    # ── Udyam certificate ─────────────────────────────────────────────────────
    elif doc_type == "udyam_certificate":
        udyam_pat = r"UDYAM-[A-Z]{2}-\d{2}-\d{7}"
        matches = re.findall(udyam_pat, raw_text)
        if matches:
            on_cert = matches[0]
            fields["udyam_on_certificate"] = on_cert

            if udyam_entered and on_cert != udyam_entered.strip().upper():
                flags.append(
                    f"⚠️ Udyam number mismatch: certificate shows {on_cert}, "
                    f"you entered {udyam_entered.upper()}"
                )

            # Cross-check: Udyam business name vs GSTIN trade name
            u_rec = UDYAM_DB.get(on_cert)
            if u_rec and gstin_entered:
                g_rec = GSTIN_DB.get(gstin_entered.strip().upper())
                if g_rec:
                    u_words = {w for w in u_rec["enterprise_name"].lower().split() if len(w) > 3}
                    g_name = g_rec["trade_name"].lower()
                    if u_words and not any(w in g_name for w in u_words):
                        flags.append(
                            f"⚠️ Business name mismatch: Udyam registry shows "
                            f"'{u_rec['enterprise_name']}' but GSTIN registry shows "
                            f"'{g_rec['trade_name']}' — please verify."
                        )
        else:
            flags.append("⚠️ Could not find a Udyam registration number in this certificate.")

    # ── Signatory ID ──────────────────────────────────────────────────────────
    elif doc_type == "signatory_id":
        if len(raw_text.strip()) < 50:
            flags.append("⚠️ Document appears illegible or blank — please re-upload a clearer photo.")

        # Name match
        if signatory_name_entered:
            name_words = {w for w in signatory_name_entered.lower().split() if len(w) > 2}
            ocr_lower = raw_text.lower()
            if not any(w in ocr_lower for w in name_words):
                flags.append(
                    f"⚠️ Signatory name '{signatory_name_entered}' not clearly found in the ID — "
                    "please ensure you uploaded the correct document."
                )

        # Mask Aadhaar — do NOT store full number or retain image
        aadhaar = re.findall(r'\b\d{4}\s\d{4}\s\d{4}\b', raw_text)
        if aadhaar:
            fields["masked_aadhaar"] = "XXXX XXXX " + aadhaar[0][-4:]

    return {
        "doc_type": doc_type,
        "status": "flagged" if flags else "ok",
        "flags": flags,
        "extracted_fields": fields,
        "raw_text_preview": raw_text[:200].strip(),  # limited preview for debugging
    }

