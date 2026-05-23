from __future__ import annotations

import logging
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session, selectinload

from app.models.alert import Alert
from app.models.intelligence import ScrapeSnapshot
from app.models.price import PriceHistory, ProductLink
from app.models.product import Product
from app.models.website import Website
from app.scrapers.base import ScrapeAttempt, ScrapeState, domain_key
from app.scrapers.registry import adapter_for_url
from app.services.notification_service import create_price_drop_notifications

logger = logging.getLogger(__name__)

DEFAULT_WEBSITES = {
    "amazon": ("Amazon", "https://www.amazon.in"),
    "flipkart": ("Flipkart", "https://www.flipkart.com"),
    "myntra": ("Myntra", "https://www.myntra.com"),
    "ajio": ("Ajio", "https://www.ajio.com"),
    "reliance_digital": ("Reliance Digital", "https://www.reliancedigital.in"),
}


def _call_procedure(db: Session, sql: str, params: dict | None = None) -> None:
    db.execute(text(sql), params or {})


def _snapshot_payload(url: str, scraped: object | None) -> dict:
    if not scraped:
        return {"url": url}
    return {
        "url": url,
        "title": scraped.title,
        "price": float(scraped.price) if scraped.price is not None else None,
        "mrp": float(scraped.mrp) if scraped.mrp is not None else None,
        "currency": scraped.currency,
        "availability": scraped.availability,
        "rating": scraped.rating,
        "rating_count": scraped.rating_count,
        "category": scraped.category,
        "image_url": scraped.image_url,
        "website": scraped.website,
    }


def ensure_website(db: Session, key: str) -> Website:
    website = db.scalar(select(Website).where(Website.adapter_key == key))
    if website:
        return website
    name, base_url = DEFAULT_WEBSITES.get(key, (key.title(), f"https://{key}.com"))
    website = Website(name=name, base_url=base_url, adapter_key=key)
    db.add(website)
    db.flush()
    return website


async def add_product_from_url(db: Session, url: str, owner_id: int | None = None, target_price: Decimal | None = None) -> Product:
    # --- Check for duplicate URL ---
    existing_link = db.scalar(select(ProductLink).where(ProductLink.url == url))
    if existing_link:
        logger.info(f"URL already tracked: {url} → product_id={existing_link.product_id}")
        return db.scalar(
            select(Product).where(Product.id == existing_link.product_id).options(selectinload(Product.links))
        )

    adapter = adapter_for_url(url)
    key = domain_key(url)
    logger.info(f"[Pipeline] URL: {url} | Platform: {key} | Adapter: {adapter.__class__.__name__}")
    website = ensure_website(db, key)

    # --- Scrape ---
    scraped = None
    attempt = ScrapeAttempt(state=ScrapeState.FETCHING)
    scrape_status = ScrapeState.SUCCESS.value
    error_msg = None
    try:
        scraped, attempt = await adapter.scrape_product(url)
        logger.info(
            f"[Pipeline] Extraction OK: title='{scraped.title[:60]}', "
            f"price={scraped.price}, availability='{scraped.availability}', "
            f"image={'yes' if scraped.image_url else 'no'}"
        )
    except Exception as exc:
        import traceback
        logger.error(f"[Pipeline] Scraping FAILED for {url}:\n{traceback.format_exc()}")
        error_msg = str(exc)
        scrape_status = ScrapeState.BLOCKED.value if "Anti-bot" in error_msg or "rate-limit" in error_msg else ScrapeState.FAILED.value
        attempt.error_message = error_msg
        attempt.state = ScrapeState(scrape_status)

    # --- Create product ---
    product = Product(
        owner_id=owner_id,
        title=scraped.title if scraped else "Fetching Product Data...",
        category=(scraped.category if scraped else None) or "General",
        image_url=scraped.image_url if scraped else None,
        currency=scraped.currency if scraped else "INR",
        current_best_price=scraped.price if scraped else None,
        lowest_price=scraped.price if scraped else None,
        highest_price=scraped.price if scraped else None,
        mrp=scraped.mrp if scraped else None,
        rating=scraped.rating if scraped else None,
        rating_count=(scraped.rating_count if scraped else 0) or 0,
    )
    db.add(product)
    db.flush()

    # --- Create product link ---
    link = ProductLink(
        product_id=product.id,
        website_id=website.id,
        url=url,
        last_price=scraped.price if scraped else None,
        availability=scraped.availability if scraped else None,
        last_checked_at=datetime.now(timezone.utc),
        scrape_status=scrape_status,
        error_message=error_msg,
    )
    db.add(link)
    db.flush()

    # --- Scraper log ---
    _call_procedure(
        db,
        "CALL log_scrape_result(:product_link_id, :website_id, :status, :http_status, :latency_ms, :retry_count, :error_message)",
        {
            "product_link_id": link.id,
            "website_id": website.id,
            "status": scrape_status,
            "http_status": attempt.http_status,
            "latency_ms": attempt.latency_ms,
            "retry_count": attempt.retry_count,
            "error_message": error_msg,
        },
    )

    db.add(
        ScrapeSnapshot(
            product_id=product.id,
            product_link_id=link.id,
            website_id=website.id,
            status=scrape_status,
            http_status=attempt.http_status,
            latency_ms=attempt.latency_ms,
            error_message=error_msg,
            payload=_snapshot_payload(url, scraped),
            raw_html=attempt.html,
        )
    )

    # --- Price history entry ---
    if scraped and scraped.price is not None:
        _call_procedure(
            db,
            "CALL record_price_snapshot(:product_id, :product_link_id, :website_id, :price, :mrp, :availability)",
            {
                "product_id": product.id,
                "product_link_id": link.id,
                "website_id": website.id,
                "price": scraped.price,
                "mrp": scraped.mrp,
                "availability": scraped.availability,
            },
        )

    # --- Alert ---
    if target_price and owner_id:
        _call_procedure(
            db,
            "CALL create_alert(:user_id, :product_id, :target_price, :percentage_drop, :lowest_in_days, :channel_email, :channel_telegram, :priority)",
            {
                "user_id": owner_id,
                "product_id": product.id,
                "target_price": target_price,
                "percentage_drop": None,
                "lowest_in_days": None,
                "channel_email": 1,
                "channel_telegram": 0,
                "priority": "normal",
            },
        )

    db.commit()
    logger.info(f"[Pipeline] Product #{product.id} committed to DB successfully")
    return db.scalar(select(Product).where(Product.id == product.id).options(selectinload(Product.links)))


async def refresh_product_prices(db: Session, product_id: int) -> Product:
    product = db.scalar(select(Product).where(Product.id == product_id).options(selectinload(Product.links)))
    if not product:
        raise ValueError("Product not found")
    old_best = product.current_best_price
    prices: list[Decimal] = []
    for link in product.links:
        if not link.is_active:
            continue
        adapter = adapter_for_url(link.url)
        link.scrape_status = ScrapeState.FETCHING.value
        db.flush()
        attempt = ScrapeAttempt(state=ScrapeState.FETCHING)
        try:
            scraped, attempt = await adapter.scrape_product(link.url)
            link.scrape_status = ScrapeState.SUCCESS.value
            link.error_message = None
        except Exception as exc:
            logger.error(f"[Refresh] Failed for link #{link.id}: {repr(exc)}")
            link.scrape_status = ScrapeState.BLOCKED.value if "Anti-bot" in str(exc) or "rate-limit" in str(exc) else ScrapeState.FAILED.value
            link.error_message = str(exc)
            _call_procedure(
                db,
                "CALL log_scrape_result(:product_link_id, :website_id, :status, :http_status, :latency_ms, :retry_count, :error_message)",
                {
                    "product_link_id": link.id,
                    "website_id": link.website_id,
                    "status": link.scrape_status,
                    "http_status": attempt.http_status,
                    "latency_ms": attempt.latency_ms,
                    "retry_count": attempt.retry_count,
                    "error_message": link.error_message,
                },
            )
            db.add(
                ScrapeSnapshot(
                    product_id=product.id,
                    product_link_id=link.id,
                    website_id=link.website_id,
                    status=link.scrape_status,
                    http_status=attempt.http_status,
                    latency_ms=attempt.latency_ms,
                    error_message=link.error_message,
                    payload=_snapshot_payload(link.url, None),
                    raw_html=attempt.html,
                )
            )
            continue
        link.last_price = scraped.price
        link.availability = scraped.availability
        link.last_checked_at = datetime.now(timezone.utc)

        # Update product fields with latest data
        product.title = scraped.title or product.title
        product.image_url = scraped.image_url or product.image_url
        product.rating = scraped.rating or product.rating
        product.mrp = scraped.mrp or product.mrp

        if scraped.price is not None:
            prices.append(scraped.price)
            product.lowest_price = min(product.lowest_price, scraped.price) if product.lowest_price else scraped.price
            product.highest_price = max(product.highest_price, scraped.price) if product.highest_price else scraped.price
            _call_procedure(
                db,
                "CALL record_price_snapshot(:product_id, :product_link_id, :website_id, :price, :mrp, :availability)",
                {
                    "product_id": product.id,
                    "product_link_id": link.id,
                    "website_id": link.website_id,
                    "price": scraped.price,
                    "mrp": scraped.mrp,
                    "availability": scraped.availability,
                },
            )
        _call_procedure(
            db,
            "CALL log_scrape_result(:product_link_id, :website_id, :status, :http_status, :latency_ms, :retry_count, :error_message)",
            {
                "product_link_id": link.id,
                "website_id": link.website_id,
                "status": ScrapeState.SUCCESS.value,
                "http_status": attempt.http_status,
                "latency_ms": attempt.latency_ms,
                "retry_count": attempt.retry_count,
                "error_message": None,
            },
        )
        db.add(
            ScrapeSnapshot(
                product_id=product.id,
                product_link_id=link.id,
                website_id=link.website_id,
                status=ScrapeState.SUCCESS.value,
                http_status=attempt.http_status,
                latency_ms=attempt.latency_ms,
                error_message=None,
                payload=_snapshot_payload(link.url, scraped),
                raw_html=attempt.html,
            )
        )
    product.current_best_price = min(prices) if prices else product.current_best_price
    db.flush()
    if old_best and product.current_best_price and product.current_best_price < old_best:
        create_price_drop_notifications(db, product, old_best, product.current_best_price)
    db.commit()
    return product


def delete_product(db: Session, product_id: int, owner_id: int | None = None) -> bool:
    """Delete a product and all related records. Returns True if deleted."""
    product = db.scalar(select(Product).where(Product.id == product_id))
    if not product:
        return False
    if owner_id is not None and product.owner_id != owner_id:
        return False
    logger.info(f"[Delete] Removing product #{product_id}: {product.title}")
    db.delete(product)
    db.commit()
    return True


def product_stats(db: Session, product_id: int) -> dict:
    row = db.execute(
        select(
            func.min(PriceHistory.price),
            func.max(PriceHistory.price),
            func.avg(PriceHistory.price),
            func.count(PriceHistory.id),
        ).where(PriceHistory.product_id == product_id)
    ).one()
    product = db.get(Product, product_id)
    return {"current": product.current_best_price if product else None, "lowest": row[0], "highest": row[1], "average": row[2], "samples": row[3]}
