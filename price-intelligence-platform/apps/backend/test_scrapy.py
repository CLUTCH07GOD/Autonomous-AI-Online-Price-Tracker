import scrapy
from scrapy.crawler import CrawlerProcess

class ProductSpider(scrapy.Spider):
    name = "product_spider"
    start_urls = ["https://httpbin.org/html"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with open("debug_log.txt", "a") as f:
            f.write("ProductSpider __init__ called!\n")

    def start_requests(self):
        with open("debug_log.txt", "a") as f:
            f.write("ProductSpider start_requests called!\n")
        yield scrapy.Request(
            url=self.start_urls[0],
            callback=self.parse,
            dont_filter=True
        )

    def parse(self, response):
        with open("debug_log.txt", "a") as f:
            f.write(f"PARSE CALLED! HTML length: {len(response.text)}\n")

if __name__ == "__main__":
    with open("debug_log.txt", "w") as f:
        f.write("--- Starting debug run ---\n")
    process = CrawlerProcess()
    process.crawl(ProductSpider)
    process.start()
