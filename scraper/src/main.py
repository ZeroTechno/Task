import os
import time
import requests
import hashlib
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
        raise Exception(f"Failed to fetch {url}, status: {response.status_code}")

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

        # Extract all book links from the page
        articles = soup.select("article.product_pod h3 a")
        for a in articles:
            relative_link = a.get("href")
            absolute_link = urljoin(current_url, relative_link)
            book_urls.append(absolute_link)

        # Find "next" page link
        next_btn = soup.select_one("li.next a")
        if next_btn:
            next_href = next_btn.get("href")
            current_url = urljoin(current_url, next_href)
        else:
            current_url = None

    unique_urls = list(dict.fromkeys(book_urls))
    print(f"catalogue_pages = {pages_crawled}, discovered = {len(book_urls)}, unique_urls = {len(unique_urls)}")
    return unique_urls

if __name__ == "__main__":
    start_url = "https://books.toscrape.com/catalogue/page-1.html"
    urls = discover_book_urls(start_url, max_pages=3)
