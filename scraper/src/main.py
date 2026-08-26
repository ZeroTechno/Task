import os
import re
import json
import time
import requests
import hashlib
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from typing import Optional
from pydantic import BaseModel, HttpUrl, ValidationError

CACHE_DIR = "cache"
OUTPUT_DIR = "output"
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "FlyRankInternship-A9/1.0 (+https://github.com/ZeroTechno/Task)"
}

# --- Pydantic Schema Definition ---
class BookSchema(BaseModel):
    title: str
    product_url: HttpUrl
    price_text: str
    price_gbp: float
    availability_text: str
    rating_text: Optional[str] = None
    description: Optional[str] = None
    source_page: HttpUrl
    fetched_at: str

def fetch_page(url: str, delay_seconds: float = 0.5) -> str:
    url_hash = hashlib.md5(url.encode("utf-8")).hexdigest()
    cache_path = os.path.join(CACHE_DIR, f"{url_hash}.html")

    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()

    time.sleep(delay_seconds)
    response = requests.get(url, headers=HEADERS, timeout=5)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch {url}, status code: {response.status_code}")

    content = response.text
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(content)
    return content

def discover_book_urls(start_url: str, max_pages: int = 3):
    current_url = start_url
    pages_crawled = 0
    book_urls = []

    while current_url and pages_crawled < max_pages:
        html = fetch_page(current_url)
        pages_crawled += 1
        soup = BeautifulSoup(html, "html.parser")

        articles = soup.select("article.product_pod h3 a")
        for a in articles:
            relative_link = a.get("href")
            absolute_link = urljoin(current_url, relative_link)
            book_urls.append((absolute_link, current_url))

        next_btn = soup.select_one("li.next a")
        if next_btn:
            next_href = next_btn.get("href")
            current_url = urljoin(current_url, next_href)
        else:
            current_url = None

    # De-duplicate while preserving order
    seen = set()
    unique_books = []
    for b_url, s_url in book_urls:
        if b_url not in seen:
            seen.add(b_url)
            unique_books.append((b_url, s_url))

    return unique_books

def extract_book_details(book_url: str, source_page: str) -> dict:
    html = fetch_page(book_url)
    soup = BeautifulSoup(html, "html.parser")

    product_main = soup.select_one("div.product_main")
    title = product_main.select_one("h1").get_text(strip=True) if product_main.select_one("h1") else None
    price_text = product_main.select_one("p.price_color").get_text(strip=True) if product_main.select_one("p.price_color") else None
    availability_text = product_main.select_one("p.availability").get_text(strip=True) if product_main.select_one("p.availability") else None
    
    rating_tag = product_main.select_one("p.star-rating")
    rating_text = None
    if rating_tag:
        classes = rating_tag.get("class", [])
        classes = [c for c in classes if c != "star-rating"]
        rating_text = classes[0] if classes else None

    desc_tag = soup.select_one("#product_description + p")
    description = desc_tag.get_text(strip=True) if desc_tag else None

    return {
        "title": title,
        "product_url": book_url,
        "price_text": price_text,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": datetime.now(timezone.utc).isoformat()
    }

def normalize_price(price_str: str) -> float:
    match = re.search(r"[\d.]+", price_str)
    return float(match.group()) if match else 0.0

if __name__ == "__main__":
    start_url = "https://books.toscrape.com/catalogue/page-1.html"
    book_items = discover_book_urls(start_url, max_pages=3)

    valid_records = []
    invalid_records = []

    for book_url, source_page in book_items:
        raw_data = extract_book_details(book_url, source_page)
        
        # Add normalized price
        raw_data["price_gbp"] = normalize_price(raw_data.get("price_text", ""))

        try:
            validated = BookSchema(**raw_data)
            # Dump using model_dump in Pydantic v2 (or dict() for v1)
            dumped = validated.model_dump() if hasattr(validated, "model_dump") else validated.dict()
            # Convert HttpUrl objects back to string for clean JSON serialization
            dumped["product_url"] = str(dumped["product_url"])
            dumped["source_page"] = str(dumped["source_page"])
            valid_records.append(dumped)
        except ValidationError as e:
            invalid_records.append({
                "record": raw_data,
                "error": str(e)
            })

    # Save to output files
    with open("output/books.json", "w", encoding="utf-8") as f:
        json.dump(valid_records, f, indent=2)

    with open("output/errors.json", "w", encoding="utf-8") as f:
        json.dump(invalid_records, f, indent=2)

    print(f"Validated books stored: {len(valid_records)}")
    print(f"Invalid records: {len(invalid_records)}")