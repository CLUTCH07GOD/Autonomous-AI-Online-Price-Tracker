from __future__ import annotations

import asyncio
import logging
import random
import time
from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from urllib.parse import urlparse

from bs4 import BeautifulSoup
import httpx
from scrapy.selector import Selector

from app.core.config import settings
from app.scrapers.price_parser import detect_currency, normalize_price as clean_price

logger = logging.getLogger(__name__)


class ScrapeState(StrEnum):
    FETCHING = "FETCHING"
    SCRAPING = "SCRAPING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    RETRYING = "RETRYING"
    PENDING = "PENDING"


@dataclass
class ScrapedProduct:
    title: str
    price: Decimal | None
    mrp: Decimal | None
    currency: str
    availability: str
    rating: float | None
    rating_count: int
    category: str | None
    image_url: str | None
    website: str


@dataclass
class ScrapeAttempt:
    state: ScrapeState
    html: str | None = None
    latency_ms: int | None = None
    retry_count: int = 0
    http_status: int | None = None
    error_message: str | None = None


def domain_key(url: str) -> str:
    host = urlparse(url).netloc.lower().replace("www.", "")
    if "amazon" in host:
        return "amazon"
    if "flipkart" in host:
        return "flipkart"
    if "myntra" in host:
        return "myntra"
    if "ajio" in host:
        return "ajio"
    if "reliancedigital" in host or "reliance" in host:
        return "reliance_digital"
    return host.split(".")[0]


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
]

BLOCK_MARKERS = (
    "captcha",
    "robot check",
    "automated access",
    "unusual traffic",
    "access denied",
    "verify you are a human",
    "enter the characters you see below",
)


def _request_headers() -> dict[str, str]:
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-IN,en-US;q=0.9,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Cache-Control": "no-cache",
        "Upgrade-Insecure-Requests": "1",
    }


def _looks_blocked(html: str, status: int | None) -> bool:
    if status in {401, 403, 429, 503}:
        return True
    lower = html[:10000].lower()
    return any(marker in lower for marker in BLOCK_MARKERS)


async def fetch_html(url: str, wait_selectors: list[str], timeout: int, max_retries: int = 3) -> ScrapeAttempt:
    last_error: Exception | None = None
    timeout_seconds = max(5, int(timeout / 1000))
    for attempt in range(max_retries):
        started = time.perf_counter()
        try:
            logger.info("[Scraper] state=%s attempt=%s url=%s", ScrapeState.FETCHING, attempt + 1, url)
            async with httpx.AsyncClient(timeout=timeout_seconds, follow_redirects=True) as client:
                response = await client.get(url, headers=_request_headers())
            html = response.text
            status = response.status_code
            latency_ms = int((time.perf_counter() - started) * 1000)

            if _looks_blocked(html, status):
                state = ScrapeState.BLOCKED if attempt == max_retries - 1 else ScrapeState.RETRYING
                if state == ScrapeState.RETRYING:
                    await asyncio.sleep(0.8 * (attempt + 1))
                    continue
                return ScrapeAttempt(
                    state=ScrapeState.BLOCKED,
                    html=html,
                    latency_ms=latency_ms,
                    retry_count=attempt,
                    http_status=status,
                    error_message="Anti-bot or rate-limit page detected",
                )

            if wait_selectors:
                selector = Selector(text=html)
                found = any(selector.css(css).get() for css in wait_selectors)
                logger.info("[Scraper] state=%s selector_found=%s url=%s", ScrapeState.SCRAPING, found, url)

            return ScrapeAttempt(
                state=ScrapeState.SUCCESS,
                html=html,
                latency_ms=latency_ms,
                retry_count=attempt,
                http_status=status,
            )
        except Exception as exc:
            last_error = exc
            logger.warning(
                "[Scraper] state=%s attempt=%s error=%r",
                ScrapeState.RETRYING if attempt < max_retries - 1 else ScrapeState.FAILED,
                attempt + 1,
                exc,
            )
            if attempt < max_retries - 1:
                await asyncio.sleep(0.8 * (2**attempt) + random.random())

    return ScrapeAttempt(
        state=ScrapeState.FAILED,
        retry_count=max_retries - 1,
        error_message=str(last_error) if last_error else "Unknown scrape failure",
    )


class EcommerceAdapter:
    website = "generic"
    wait_selectors: list[str] = []

    async def fetch_soup(self, url: str) -> tuple[BeautifulSoup, ScrapeAttempt]:
        attempt = await fetch_html(url, self.wait_selectors, settings.scraper_timeout_ms)
        if attempt.state != ScrapeState.SUCCESS or not attempt.html:
            raise RuntimeError(attempt.error_message or f"Scrape ended in {attempt.state}")
        return BeautifulSoup(attempt.html, "html.parser"), attempt

    async def scrape_product(self, url: str) -> tuple[ScrapedProduct, ScrapeAttempt]:
        if "demo" in url.lower() or "mock" in url.lower():
            # Generate mock details
            parsed = urlparse(url)
            path_part = parsed.path.strip("/")
            name = path_part.split("/")[-1] if path_part else "mock-product"
            title = name.replace("-", " ").replace("_", " ").title()
            if not title:
                title = "Mock Product"
            
            # Base price heuristic
            if "headphone" in url.lower():
                base = 2999
            elif "phone" in url.lower():
                base = 49999
            elif "laptop" in url.lower():
                base = 79999
            elif "watch" in url.lower():
                base = 12999
            elif "shoe" in url.lower() or "sneaker" in url.lower():
                base = 4999
            else:
                base = 999
                
            # Add a random fluctuation of ±5%
            price = Decimal(str(round(base * random.uniform(0.95, 1.05), 2)))
            mrp = Decimal(str(round(base * 1.2, 2)))
            
            scraped = ScrapedProduct(
                title=title,
                price=price,
                mrp=mrp,
                currency="INR",
                availability="In Stock",
                rating=4.2,
                rating_count=128,
                category="Mock Category",
                image_url=None,
                website=self.website,
            )
            attempt = ScrapeAttempt(
                state=ScrapeState.SUCCESS,
                html="<html>Mock HTML</html>",
                latency_ms=random.randint(50, 150),
                retry_count=0,
                http_status=200
            )
            logger.info(f"[Mock Scraper] Intercepted mock URL: {url} -> {price}")
            return scraped, attempt

        soup, attempt = await self.fetch_soup(url)
        return self.parse_product(soup), attempt

    async def scrape_price(self, url: str) -> Decimal | None:
        product, _ = await self.scrape_product(url)
        return product.price

    def parse_product(self, soup: BeautifulSoup) -> ScrapedProduct:
        title = soup.find(["h1", "title"])
        return ScrapedProduct(
            title=title.get_text(strip=True) if title else "Untitled product",
            price=None,
            mrp=None,
            currency=detect_currency(soup.get_text(" ", strip=True)[:2000]) or "INR",
            availability="Unknown",
            rating=None,
            rating_count=0,
            category=None,
            image_url=None,
            website=self.website,
        )
