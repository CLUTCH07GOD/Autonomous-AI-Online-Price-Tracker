from __future__ import annotations

import json
import logging
import re

from bs4 import BeautifulSoup

from app.scrapers.base import EcommerceAdapter, ScrapedProduct, clean_price
from app.scrapers.price_parser import detect_currency

logger = logging.getLogger(__name__)


def json_ld_product(soup: BeautifulSoup) -> dict | None:
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(re.sub(r"[\x00-\x1F\x7F-\x9F]", "", tag.string or ""))
        except Exception:
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            if isinstance(item, dict) and item.get("@type") in {"Product", "ProductGroup"}:
                return item
    return None


class JsonLdCommerceAdapter(EcommerceAdapter):
    website = "generic"

    def parse_product(self, soup: BeautifulSoup) -> ScrapedProduct:
        data = json_ld_product(soup) or {}
        offers = data.get("offers") or {}
        if isinstance(offers, list):
            offers = offers[0] if offers else {}
        aggregate = data.get("aggregateRating") or {}
        image = data.get("image")
        if isinstance(image, list):
            image = image[0] if image else None
        availability = str(offers.get("availability") or "")

        title = data.get("name") or (soup.title.get_text(strip=True) if soup.title else "Product")
        price = clean_price(str(offers.get("price") or ""))

        logger.info(f"[JsonLD] Parsed: title='{title[:60]}', price={price}")

        return ScrapedProduct(
            title=title,
            price=price,
            mrp=None,
            currency=offers.get("priceCurrency") or detect_currency(str(offers.get("price") or "")) or "INR",
            availability="In Stock" if "instock" in availability.lower() or "limited" in availability.lower() else "Out of Stock",
            rating=float(aggregate.get("ratingValue")) if aggregate.get("ratingValue") else None,
            rating_count=int(float(aggregate.get("ratingCount", 0))) if aggregate.get("ratingCount") else 0,
            category=data.get("category"),
            image_url=image,
            website=self.website,
        )


class AmazonAdapter(EcommerceAdapter):
    website = "amazon"
    wait_selectors = ["#productTitle", "#title", "[data-feature-name='title']", ".a-price .a-offscreen"]

    def parse_product(self, soup: BeautifulSoup) -> ScrapedProduct:
        title_el = soup.select_one("#productTitle") or soup.select_one("#title")
        if not title_el:
            raise ValueError("Anti-bot detected or page changed: Missing product title")
        title = title_el.get_text(strip=True)

        price_selectors = [
            ".priceToPay .a-offscreen",
            "#corePrice_feature_div .a-offscreen",
            ".a-price .a-offscreen",
            ".priceToPay",
            ".a-price-whole",
            "#priceblock_ourprice",
            "#priceblock_dealprice"
        ]
        price_el = None
        for sel in price_selectors:
            el = soup.select_one(sel)
            if el and el.get_text(strip=True):
                price_el = el
                break
        price = clean_price(price_el.get_text(strip=True) if price_el else None)

        mrp_selectors = [
            ".basisPrice .a-offscreen",
            ".a-text-price .a-offscreen",
            "#priceblock_mrp"
        ]
        mrp_el = None
        for sel in mrp_selectors:
            el = soup.select_one(sel)
            if el and el.get_text(strip=True):
                mrp_el = el
                break
        mrp = clean_price(mrp_el.get_text(strip=True) if mrp_el else None)

        image_el = (
            soup.select_one("#landingImage")
            or soup.select_one("#imgBlkFront")
            or soup.select_one("#main-image-container img")
        )
        image_url = image_el.get("src") if image_el else None

        rating_el = soup.select_one("#averageCustomerReviews .a-icon-alt") or soup.select_one(".a-icon-star .a-icon-alt")
        rating = None
        if rating_el:
            match = re.search(r"(\d+\.?\d*)", rating_el.get_text())
            if match:
                rating = float(match.group(1))

        rating_count_el = soup.select_one("#acrCustomerReviewText")
        rating_count = 0
        if rating_count_el:
            match = re.search(r"([\d,]+)", rating_count_el.get_text())
            if match:
                rating_count = int(match.group(1).replace(",", ""))

        availability_el = soup.select_one("#availability")
        availability = "In Stock"
        if availability_el:
            text = availability_el.get_text().lower()
            if "out of stock" in text or "currently unavailable" in text:
                availability = "Out of Stock"

        return ScrapedProduct(
            title=title,
            price=price,
            mrp=mrp,
            currency=(detect_currency(price_el.get_text(strip=True)) if price_el else None) or "INR",
            availability=availability,
            rating=rating,
            rating_count=rating_count,
            category=None,
            image_url=image_url,
            website=self.website,
        )


class FlipkartAdapter(EcommerceAdapter):
    website = "flipkart"
    wait_selectors = ["h1", "._30jeq3", ".Nx9bqj", "[data-id]"]

    def parse_product(self, soup: BeautifulSoup) -> ScrapedProduct:
        title_el = soup.select_one(".B_NuCI") or soup.select_one("h1")
        if not title_el:
            raise ValueError("Anti-bot detected or page changed: Missing product title")
        title = title_el.get_text(strip=True)

        price_el = soup.select_one("._30jeq3._16Jk6d") or soup.select_one(".Nx9bqj.CxhGGd") or soup.select_one("._30jeq3")
        price = clean_price(price_el.get_text(strip=True) if price_el else None)

        mrp_el = soup.select_one("._3I9_wc._27999z") or soup.select_one(".yRaY8j.A98u7W") or soup.select_one("._3I9_wc")
        mrp = clean_price(mrp_el.get_text(strip=True) if mrp_el else None)

        image_el = soup.select_one("img._396cs4._2amPTt._3qG0Vb") or soup.select_one("img.DByuf4") or soup.select_one("img._2r_T1I")
        image_url = image_el.get("src") if image_el else None

        rating_el = soup.select_one("._3LWZlK") or soup.select_one(".XQDdHH")
        rating = float(rating_el.get_text()) if rating_el else None

        rating_count_el = soup.select_one("._2wp97r") or soup.select_one(".Wphh3N")
        rating_count = 0
        if rating_count_el:
            match = re.search(r"([\d,]+)", rating_count_el.get_text())
            if match:
                rating_count = int(match.group(1).replace(",", ""))

        availability = "In Stock"
        if soup.select_one("._1dq9fB") or "this item is currently out of stock" in soup.get_text().lower():
            availability = "Out of Stock"

        return ScrapedProduct(
            title=title,
            price=price,
            mrp=mrp,
            currency=(detect_currency(price_el.get_text(strip=True)) if price_el else None) or "INR",
            availability=availability,
            rating=rating,
            rating_count=rating_count,
            category=None,
            image_url=image_url,
            website=self.website,
        )


class MyntraAdapter(EcommerceAdapter):
    website = "myntra"
    wait_selectors = [".pdp-title", ".pdp-name", ".pdp-price"]

    def parse_product(self, soup: BeautifulSoup) -> ScrapedProduct:
        title_brand = soup.select_one(".pdp-title")
        title_name = soup.select_one(".pdp-name")
        if not title_brand or not title_name:
            raise ValueError("Anti-bot detected or page changed: Missing product title")
        title = f"{title_brand.get_text(strip=True)} - {title_name.get_text(strip=True)}"

        price_el = soup.select_one(".pdp-price")
        price = clean_price(price_el.get_text(strip=True) if price_el else None)

        mrp_el = soup.select_one(".pdp-mrp")
        mrp = clean_price(mrp_el.get_text(strip=True) if mrp_el else None)

        # Myntra images are often lazy-loaded or in scripts, try to find the first large image
        image_url = None
        scripts = soup.find_all("script")
        for s in scripts:
            if "pdpData" in s.get_text():
                match = re.search(r'"image":\s*"([^"]+)"', s.get_text())
                if match:
                    image_url = match.group(1)
                    break
        
        if not image_url:
            image_el = soup.select_one(".image-grid-image")
            if image_el:
                style = image_el.get("style")
                if style and "background-image" in style:
                    match = re.search(r'url\("?([^")]+)"?\)', style)
                    if match:
                        image_url = match.group(1)

        rating_el = soup.select_one(".index-overallRating .index-averageRating")
        rating = float(rating_el.get_text()) if rating_el else None

        return ScrapedProduct(
            title=title,
            price=price,
            mrp=mrp,
            currency=(detect_currency(price_el.get_text(strip=True)) if price_el else None) or "INR",
            availability="In Stock",
            rating=rating,
            rating_count=0,
            category=None,
            image_url=image_url,
            website=self.website,
        )


class AjioAdapter(EcommerceAdapter):
    website = "ajio"
    wait_selectors = [".prod-header", ".brand-name", ".prod-sp"]

    def parse_product(self, soup: BeautifulSoup) -> ScrapedProduct:
        brand = soup.select_one(".brand-name")
        name = soup.select_one(".prod-header")
        if not brand or not name:
            raise ValueError("Anti-bot detected or page changed: Missing product title")
        title = f"{brand.get_text(strip=True)} - {name.get_text(strip=True)}"

        price_el = soup.select_one(".prod-sp")
        price = clean_price(price_el.get_text(strip=True) if price_el else None)

        mrp_el = soup.select_one(".prod-cp")
        mrp = clean_price(mrp_el.get_text(strip=True) if mrp_el else None)

        image_el = soup.select_one(".img-container img")
        image_url = image_el.get("src") if image_el else None

        return ScrapedProduct(
            title=title,
            price=price,
            mrp=mrp,
            currency=(detect_currency(price_el.get_text(strip=True)) if price_el else None) or "INR",
            availability="In Stock",
            rating=None,
            rating_count=0,
            category=None,
            image_url=image_url,
            website=self.website,
        )


class RelianceDigitalAdapter(EcommerceAdapter):
    website = "reliance_digital"
    wait_selectors = [".pdp__title", ".pdp__offerPrice", "h1"]

    def parse_product(self, soup: BeautifulSoup) -> ScrapedProduct:
        title_el = soup.select_one(".pdp__title")
        if not title_el:
            raise ValueError("Anti-bot detected or page changed: Missing product title")
        title = title_el.get_text(strip=True)

        price_el = soup.select_one(".pdp__offerPrice")
        price = clean_price(price_el.get_text(strip=True) if price_el else None)

        mrp_el = soup.select_one(".pdp__mrp")
        mrp = clean_price(mrp_el.get_text(strip=True) if mrp_el else None)

        image_el = soup.select_one("#mainImg") or soup.select_one(".pdp__mainImage")
        image_url = "https://www.reliancedigital.in" + image_el.get("src") if image_el and image_el.get("src") else None

        return ScrapedProduct(
            title=title,
            price=price,
            mrp=mrp,
            currency=(detect_currency(price_el.get_text(strip=True)) if price_el else None) or "INR",
            availability="In Stock",
            rating=None,
            rating_count=0,
            category=None,
            image_url=image_url,
            website=self.website,
        )
