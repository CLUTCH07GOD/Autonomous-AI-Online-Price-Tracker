from __future__ import annotations

from decimal import Decimal, InvalidOperation
import re


def normalize_price(raw_text: str | None, locale_hint: str = "AUTO") -> Decimal | None:
    """
    Convert localized price strings to Decimal using separator heuristics from
    the scraper reference repo. Returns None when no numeric price is present.
    """
    if not raw_text:
        return None

    cleaned = re.sub(r"[^\d,\.]", "", raw_text)
    if not cleaned:
        return None

    if locale_hint == "AUTO":
        if "," in cleaned and "." in cleaned:
            locale_hint = "EU" if cleaned.rfind(",") > cleaned.rfind(".") else "US"
        elif "," in cleaned:
            parts = cleaned.split(",")
            locale_hint = "EU" if len(parts[-1]) == 2 else "US"
        else:
            locale_hint = "US"

    normalized = cleaned.replace(".", "").replace(",", ".") if locale_hint == "EU" else cleaned.replace(",", "")
    try:
        return Decimal(normalized).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        return None


_CURRENCY_SYMBOLS = {
    "R$": "BRL",
    "C$": "CAD",
    "A$": "AUD",
    "$": "USD",
    "€": "EUR",
    "£": "GBP",
    "₹": "INR",
    "¥": "JPY",
    "₽": "RUB",
    "₩": "KRW",
    "฿": "THB",
    "CHF": "CHF",
}


def detect_currency(raw_text: str | None) -> str | None:
    if not raw_text:
        return None
    for symbol, code in _CURRENCY_SYMBOLS.items():
        if symbol in raw_text:
            return code
    match = re.search(r"\b(USD|EUR|GBP|INR|JPY|RUB|AUD|CAD|SGD|MXN|BRL|CHF|CNY|KRW|THB)\b", raw_text, re.IGNORECASE)
    return match.group(1).upper() if match else None


def normalize_and_detect(raw_text: str | None, locale_hint: str = "AUTO") -> tuple[Decimal | None, str | None]:
    return normalize_price(raw_text, locale_hint), detect_currency(raw_text)
