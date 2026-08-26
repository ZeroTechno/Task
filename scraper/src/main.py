import os
import time
import requests
import hashlib

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

# Identifying polite User-Agent
HEADERS = {
    "User-Agent": "FlyRankInternship-A9/1.0 (+https://github.com/ZeroTechno/Task)"
}

def fetch_page(url: str, delay_seconds: float = 0.5) -> str:
    # Hash URL to make a unique, clean filename for caching
    url_hash = hashlib.md5(url.encode("utf-8")).hexdigest()
    cache_path = os.path.join(CACHE_DIR, f"{url_hash}.html")

    # 1. Read from cache if already downloaded
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            content = f.read()
        print(f"CACHE HIT: {url} ({len(content)} bytes)")
        return content

    # 2. Be polite: pause before hitting the live server
    time.sleep(delay_seconds)

    # 3. Network fetch with a 5-second timeout
    response = requests.get(url, headers=HEADERS, timeout=5)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch {url}, status code: {response.status_code}")

    content = response.text
    print(f"FETCH: {url} ({len(content)} bytes)")

    # 4. Save to cache directory
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(content)

    return content

if __name__ == "__main__":
    test_url = "https://books.toscrape.com/catalogue/page-1.html"
    print("Testing Stage 1 Fetch & Cache...")
    fetch_page(test_url)
    fetch_page(test_url)