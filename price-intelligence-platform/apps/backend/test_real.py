import sys
import asyncio

# Set SelectorEventLoop on Windows before importing Twisted/Scrapy
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# 1. Install the reactor before importing or using other Scrapy/Twisted components
from scrapy.utils.reactor import install_reactor
try:
    install_reactor('twisted.internet.asyncioreactor.AsyncioSelectorReactor')
except Exception as e:
    print("install_reactor warning:", e)

import logging
logging.basicConfig(level=logging.DEBUG)

import time
import random
from dataclasses import dataclass
from enum import StrEnum
import scrapy
from scrapy.crawler import CrawlerRunner

class ScrapeState(StrEnum):
    FETCHING = "FETCHING"
    SCRAPING = "SCRAPING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    RETRYING = "RETRYING"
    PENDING = "PENDING"

@dataclass
class ScrapeAttempt:
    state: ScrapeState
    html: str | None = None
    latency_ms: int | None = None
    retry_count: int = 0
    http_status: int | None = None
    error_message: str | None = None

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
]

BLOCK_MARKERS = (
    "captcha",
    "robot check",
    "automated access",
    "unusual traffic",
    "access denied",
    "verify you are a human",
)

def _looks_blocked(html: str, status: int | None) -> bool:
    if status in {401, 403, 429, 503}:
        return True
    lower = html[:10000].lower()
    return any(marker in lower for marker in BLOCK_MARKERS)

class HtmlSpider(scrapy.Spider):
    name = "html_spider"

    def __init__(self, url: str, attempt: ScrapeAttempt, extra_headers: dict | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = url
        self.attempt = attempt
        self.extra_headers = extra_headers or {}
        self.logger.info(f"HtmlSpider initialized with url: {self.url}")

    def start_requests(self):
        self.logger.info(f"HtmlSpider.start_requests called for {self.url}")
        yield scrapy.Request(
            url=self.url,
            headers=self.extra_headers,
            callback=self.parse,
            errback=self.handle_error,
            dont_filter=True
        )

    def parse(self, response):
        self.logger.info(f"HtmlSpider.parse called with status {response.status}")
        self.attempt.html = response.text
        self.attempt.http_status = response.status
        if _looks_blocked(self.attempt.html, response.status):
            self.attempt.state = ScrapeState.BLOCKED
            self.attempt.error_message = "Anti-bot or rate-limit page detected"
        else:
            self.attempt.state = ScrapeState.SUCCESS

    def handle_error(self, failure):
        self.logger.info(f"HtmlSpider.handle_error called with failure: {failure}")
        self.attempt.state = ScrapeState.FAILED
        self.attempt.error_message = str(failure.value)
        if hasattr(failure.value, "response") and failure.value.response:
            self.attempt.http_status = failure.value.response.status
            self.attempt.html = failure.value.response.text

async def fetch_html(url: str, wait_selectors: list[str], timeout: int, max_retries: int = 3) -> ScrapeAttempt:
    last_error: Exception | None = None
    
    settings_dict = {
        'TWISTED_REACTOR': 'twisted.internet.asyncioreactor.AsyncioSelectorReactor',
        'USER_AGENT': random.choice(USER_AGENTS),
        'REQUEST_FINGERPRINTER_IMPLEMENTATION': '2.7',
        'ROBOTSTXT_OBEY': False,
        'DOWNLOAD_TIMEOUT': timeout / 1000.0,
        'CONCURRENT_REQUESTS': 1,
        'LOG_LEVEL': 'INFO',
    }
    
    extra_headers = {
        "Accept-Language": "en-IN,en-US;q=0.9,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Cache-Control": "no-cache",
        "Upgrade-Insecure-Requests": "1",
    }

    from scrapy.crawler import AsyncCrawlerRunner
    runner = AsyncCrawlerRunner(settings=settings_dict)

    for attempt_idx in range(max_retries):
        started = time.perf_counter()
        attempt = ScrapeAttempt(state=ScrapeState.FETCHING, retry_count=attempt_idx)
        print(f"Attempt {attempt_idx + 1} starting...")
        try:
            await runner.crawl(HtmlSpider, url=url, attempt=attempt, extra_headers=extra_headers)
            attempt.latency_ms = int((time.perf_counter() - started) * 1000)
            
            if attempt.state == ScrapeState.SUCCESS:
                return attempt
            elif attempt.state == ScrapeState.BLOCKED:
                print("Blocked by anti-bot.")
                if attempt_idx < max_retries - 1:
                    await asyncio.sleep(0.8 * (attempt_idx + 1) + random.random())
                    continue
                return attempt
            else:
                raise RuntimeError(attempt.error_message or "Unknown Scrapy failure")
        except Exception as exc:
            last_error = exc
            attempt.state = ScrapeState.FAILED
            attempt.error_message = str(exc)
            attempt.latency_ms = int((time.perf_counter() - started) * 1000)
            print(f"Attempt {attempt_idx + 1} raised error: {exc}")
            if attempt_idx < max_retries - 1:
                await asyncio.sleep(0.8 * (2**attempt_idx) + random.random())

    return ScrapeAttempt(
        state=ScrapeState.FAILED,
        retry_count=max_retries - 1,
        error_message=str(last_error) if last_error else "Unknown scrape failure"
    )

async def main():
    url = "https://www.amazon.in/dp/B0CX9F1N8J"
    print("Testing Scrapy fetch for:", url)
    attempt = await fetch_html(url, [], 30000, max_retries=1)
    print("Scrape State:", attempt.state)
    print("HTTP Status:", attempt.http_status)
    print("Latency MS:", attempt.latency_ms)
    print("Error message:", attempt.error_message)
    if attempt.html:
        print("HTML length:", len(attempt.html))
        print("First 500 chars:")
        print(attempt.html[:500])

if __name__ == "__main__":
    asyncio.run(main())
