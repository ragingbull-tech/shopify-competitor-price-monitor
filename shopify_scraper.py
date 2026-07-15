from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import requests


REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 portfolio price monitor; contact=demo@example.com",
    "Accept": "application/json,text/javascript,*/*;q=0.8",
}


def robots_allows(url: str, user_agent: str = "*") -> bool:
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

    parser = RobotFileParser()
    parser.set_url(robots_url)
    parser.read()

    return parser.can_fetch(user_agent, url)


def parse_shopify_price(value: int | str | float) -> float:
    if isinstance(value, int):
        return round(value / 100, 2)

    price = float(value)

    if price >= 1000:
        return round(price / 100, 2)

    return round(price, 2)


def scrape_shopify_product(
    store_url: str,
    product_handle: str,
    competitor_name: str,
) -> list[dict]:
    base_url = store_url.rstrip("/") + "/"
    product_json_url = urljoin(base_url, f"products/{product_handle}.js")
    product_page_url = urljoin(base_url, f"products/{product_handle}")

    if not robots_allows(product_json_url):
        raise RuntimeError(f"robots.txt does not allow scraping: {product_json_url}")

    response = requests.get(product_json_url, headers=REQUEST_HEADERS, timeout=20)
    response.raise_for_status()

    product = response.json()
    observed_at = datetime.now(timezone.utc).isoformat()
    snapshots = []

    for variant in product.get("variants", []):
        variant_title = variant.get("title", "Default Title")
        title = product["title"]

        if variant_title and variant_title != "Default Title":
            title = f"{product['title']} - {variant_title}"

        snapshots.append(
            {
                "competitor": competitor_name,
                "title": title,
                "url": product_page_url,
                "price": parse_shopify_price(variant["price"]),
                "currency": "USD",
                "in_stock": bool(variant.get("available")),
                "stock_text": "In stock" if variant.get("available") else "Out of stock",
                "rating": None,
                "observed_at": observed_at,
            }
        )

    return snapshots


def scrape_shopify_products(store_url: str, competitor_name: str) -> list[dict]:
    base_url = store_url.rstrip("/") + "/"
    products_url = urljoin(base_url, "products.json")

    if not robots_allows(products_url):
        raise RuntimeError(f"robots.txt does not allow scraping: {products_url}")

    response = requests.get(products_url, headers=REQUEST_HEADERS, timeout=20)
    response.raise_for_status()

    data = response.json()
    observed_at = datetime.now(timezone.utc).isoformat()
    snapshots = []

    for product in data.get("products", []):
        product_title = product["title"]
        handle = product["handle"]
        product_url = urljoin(base_url, f"products/{handle}")

        for variant in product.get("variants", []):
            variant_title = variant.get("title", "Default Title")
            title = product_title

            if variant_title and variant_title != "Default Title":
                title = f"{product_title} - {variant_title}"

            snapshots.append(
                {
                    "competitor": competitor_name,
                    "title": title,
                    "url": product_url,
                    "price": float(variant["price"]),
                    "currency": "USD",
                    "in_stock": bool(variant.get("available")),
                    "stock_text": "In stock" if variant.get("available") else "Out of stock",
                    "rating": None,
                    "observed_at": observed_at,
                }
            )

    return snapshots
