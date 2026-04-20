from __future__ import annotations

import hashlib
import re

PII_PATTERNS: dict[str, str] = {
    "email": r"[\w\.-]+@[\w\.-]+\.\w+",
    "phone_vn": r"(?:\+84|0)[ \.-]?\d{3}[ \.-]?\d{3}[ \.-]?\d{3,4}", # Matches 090 123 4567, 090.123.4567, etc.
    "cccd": r"\b\d{12}\b",
    "credit_card": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
    # TODO: Add more patterns (e.g., Passport, Vietnamese address keywords)
    "passport": r"\b[A-Z][0-9]{7}\b",
    "address_vn": r"\b(?:Phường|Quận|Thành phố|Đường|Ngõ|Ngách|Hẻm|Xã|Huyện|Tỉnh)[A-Za-z0-9\s,]+\b",
    "ip_address": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    "mac_address": r"\b(?:[0-9A-Fa-f]{2}[:\-]){5}[0-9A-Fa-f]{2}\b",
    "dob": r"\b(?:0?[1-9]|[12]\d|3[01])[\/\-](?:0?[1-9]|1[0-2])[\/\-](?:19|20)\d{2}\b",  # DD/MM/YYYY or DD-MM-YYYY
    "bank_account_vn": r"\b\d{9,14}\b",  # Vietnamese bank accounts (9–14 digits)
    "full_name_vn": r"\b(?:Nguyễn|Trần|Lê|Phạm|Huỳnh|Hoàng|Phan|Vũ|Võ|Đặng|Bùi|Đỗ|Hồ|Ngô|Dương|Lý)\s+[A-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝĐ][a-zàáâãèéêìíòóôõùúýđ]+(?:\s+[A-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝĐ][a-zàáâãèéêìíòóôõùúýđ]+)*\b",
    "license_plate_vn": r"\b\d{2}[A-Z]{1,2}[- ]?\d{4,5}\b",  # e.g. 51A-12345
}


def scrub_text(text: str) -> str:
    safe = text
    for name, pattern in PII_PATTERNS.items():
        safe = re.sub(pattern, f"[REDACTED_{name.upper()}]", safe)
    return safe


def summarize_text(text: str, max_len: int = 80) -> str:
    safe = scrub_text(text).strip().replace("\n", " ")
    return safe[:max_len] + ("..." if len(safe) > max_len else "")


def hash_user_id(user_id: str) -> str:
    return hashlib.sha256(user_id.encode("utf-8")).hexdigest()[:12]
