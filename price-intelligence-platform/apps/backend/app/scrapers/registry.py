from __future__ import annotations

from app.scrapers.adapters import AjioAdapter, AmazonAdapter, FlipkartAdapter, MyntraAdapter, RelianceDigitalAdapter
from app.scrapers.base import EcommerceAdapter, domain_key

ADAPTERS: dict[str, EcommerceAdapter] = {
    "amazon": AmazonAdapter(),
    "flipkart": FlipkartAdapter(),
    "myntra": MyntraAdapter(),
    "ajio": AjioAdapter(),
    "reliance_digital": RelianceDigitalAdapter(),
}


def adapter_for_url(url: str) -> EcommerceAdapter:
    key = domain_key(url)
    if key not in ADAPTERS:
        raise ValueError(f"Unsupported website: {key}")
    return ADAPTERS[key]
