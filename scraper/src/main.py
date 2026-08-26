import os
import time
import requests
import hashlib
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "FlyRankInternship-A9/1.0 (+https://github.com/ZeroTechno/Task)"
}

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
            book_urls.append(absolute_link)

        next_btn = soup.select_one("li.next a")
        if next_btn:
            next_href = next_btn.get("href")
            current_url = urljoin(current_url, next_href)
        else:
            current_url = None

    unique_urls = list(dict.fromkeys(book_urls))
    return unique_urls

def extract_book_details(book_url: str, source_page: str) -> dict:
    html = fetch_page(book_url)
    soup = BeautifulSoup(html, "html.parser")

    # Scope selectors specifically to the product area
    product_main = soup.select_one("div.product_main")
    
    title = product_main.select_one("h1").get_text(strip=True) if product_main.select_one("h1") else None
    price_text = product_main.select_one("p.price_color").get_text(strip=True) if product_main.select_one("p.price_color") else None
    availability_text = product_main.select_one("p.availability").get_text(strip=True) if product_main.select_one("p.availability") else None
    
    # Rating class extraction (e.g., class="star-rating Three")
    rating_tag = product_main.select_one("p.star-rating")
    rating_text = None
    if rating_tag:
        classes = rating_tag.get("class", [])
        classes = [c for c in classes if c != "star-rating"]
        rating_text = classes[0] if classes else None

    # Description is under #product_description + p
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

if __name__ == "__main__":
    start_url = "https://books.toscrape.com/catalogue/page-1.html"
    urls = discover_book_urls(start_url, max_pages=3)
    
    raw_records = []
    for url in urls:
        record = extract_book_details(url, source_page=start_url)
        raw_records.append(record)
        
    print("--- Stage 3 Sample Raw Record ---")
    print(raw_records[0])
    print(f"detail_pages = {len(raw_records)}")