import sys
import json
import time
import random
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging

# Enable Scrapy logging to stderr so it doesn't pollute stdout (which is for JSON)
configure_logging(install_root_handler=False)
import logging
logging.basicConfig(level=logging.WARNING, stream=sys.stderr)

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

def _looks_blocked(html: str, status: int | None) -> bool:
    if status in {401, 403, 429, 503}:
        return True
    lower = html[:10000].lower()
    return any(marker in lower for marker in BLOCK_MARKERS)

class ProductSpider(scrapy.Spider):
    name = "product_spider"

    def __init__(self, url, extra_headers=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.url = url
        self.extra_headers = extra_headers or {}
        self.result = {
            "state": "FAILED",
            "html": None,
            "http_status": None,
            "latency_ms": None,
            "error_message": "Not started"
        }

    def start_requests(self):
        self.start_time = time.perf_counter()
        yield scrapy.Request(
            url=self.url,
            headers=self.extra_headers,
            callback=self.parse,
            errback=self.handle_error,
            dont_filter=True
        )

    def parse(self, response):
        latency = int((time.perf_counter() - self.start_time) * 1000)
        html = response.text
        status = response.status
        
        if _looks_blocked(html, status):
            self.result = {
                "state": "BLOCKED",
                "html": html,
                "http_status": status,
                "latency_ms": latency,
                "error_message": "Anti-bot or rate-limit page detected"
            }
        else:
            self.result = {
                "state": "SUCCESS",
                "html": html,
                "http_status": status,
                "latency_ms": latency,
                "error_message": None
            }

    def handle_error(self, failure):
        latency = int((time.perf_counter() - self.start_time) * 1000)
        status = None
        html = None
        if hasattr(failure.value, "response") and failure.value.response:
            status = failure.value.response.status
            html = failure.value.response.text

        self.result = {
            "state": "FAILED",
            "html": html,
            "http_status": status,
            "latency_ms": latency,
            "error_message": str(failure.value)
        }

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"state": "FAILED", "error_message": "Missing URL argument"}))
        sys.exit(1)

    url = sys.argv[1]
    timeout_ms = 30000
    if len(sys.argv) >= 3:
        try:
            timeout_ms = int(sys.argv[2])
        except ValueError:
            pass

    settings_dict = {
        'USER_AGENT': random.choice(USER_AGENTS),
        'REQUEST_FINGERPRINTER_IMPLEMENTATION': '2.7',
        'ROBOTSTXT_OBEY': False,
        'DOWNLOAD_TIMEOUT': timeout_ms / 1000.0,
        'CONCURRENT_REQUESTS': 1,
        'LOG_LEVEL': 'WARNING',
        'COOKIES_ENABLED': True,
    }

    extra_headers = {
        "Accept-Language": "en-IN,en-US;q=0.9,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Cache-Control": "no-cache",
        "Upgrade-Insecure-Requests": "1",
    }

    shared_result = {}
    
    class CustomProductSpider(ProductSpider):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.shared_res = shared_result
        
        def parse(self, response):
            super().parse(response)
            self.shared_res.update(self.result)
            
        def handle_error(self, failure):
            super().handle_error(failure)
            self.shared_res.update(self.result)

    process = CrawlerProcess(settings=settings_dict)
    process.crawl(CustomProductSpider, url=url, extra_headers=extra_headers)
    process.start()

    if not shared_result:
        shared_result = {
            "state": "FAILED",
            "html": None,
            "http_status": None,
            "latency_ms": None,
            "error_message": "Crawl completed without yielding result"
        }

    print(json.dumps(shared_result))

if __name__ == "__main__":
    main()
