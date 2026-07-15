from datetime import datetime, timezone
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://books.toscrape.com/"
COMPETITOR_NAME = "Books to Scrape"


def parse_price(price_text: str) -> float:
    cleaned = price_text.replace("£", "").replace("Â", "").strip()
    return float(cleaned)


def parse_rating(rating_classes: list[str]) -> int | None:
    ratings = {
        "Zero": 0,
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5,
    }

    for class_name in rating_classes:
        if class_name in ratings:
            return ratings[class_name]

    return None


def scrape_page(url: str = BASE_URL) -> list[dict]:
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    response.encoding = "utf-8"

    soup = BeautifulSoup(response.text, "html.parser")
    observed_at = datetime.now(timezone.utc).isoformat()
    snapshots = []

    for card in soup.select(".product_pod"):
        title_link = card.select_one("h3 a")
        price = card.select_one(".price_color")
        stock = card.select_one(".availability")
        rating = card.select_one(".star-rating")

        stock_text = stock.get_text(strip=True)

        snapshots.append(
            {
                "competitor": COMPETITOR_NAME,
                "title": title_link["title"].strip(),
                "url": urljoin(url, title_link["href"]),
                "price": parse_price(price.get_text(strip=True)),
                "currency": "GBP",
                "in_stock": "in stock" in stock_text.lower(),
                "stock_text": stock_text,
                "rating": parse_rating(rating.get("class", [])),
                "observed_at": observed_at,
            }
        )

    return snapshots
