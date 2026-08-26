# The Polite Scraper (Books to Scrape)

A straightforward, resilient web scraping pipeline built with Python, BeautifulSoup, and Pydantic. It fetches the first 3 catalogue pages (60 books total) from Books to Scrape, cleans and normalizes messy text values into structured data, validates each record against a strict schema, and finishes every run with a status report.

---

## Target Classification
* **Target Website:** Books to Scrape (`https://books.toscrape.com/`)
* **Why this target:** It is a free, publicly available sandbox environment designed specifically for practicing web scraping.
* **Scope:** 3 catalogue pages, capturing exactly 60 unique book detail pages.
* **Fields Collected:** Title, product URL, raw price text, numeric price in GBP, availability, rating, description, source page URL, and fetch timestamp.
* **Robots.txt Check:** Requested `https://books.toscrape.com/robots.txt` and received a `404 Not Found` (no robots file present).
* **Ethics Declaration:** I will not reuse this code on another site without checking its rules and terms first.

---

## Politeness & Scraping Rules

To make sure this scraper behaves like a polite guest on the server, it follows these rules:

* **Custom User-Agent:** Sends `FlyRankInternship-A9/1.0 (+https://github.com/ZeroTechno/Task)` with every request so server administrators can see who is requesting the pages.
* **Rate Limiting:** Pauses for at least 500 ms between network requests so the target server is never flooded.
* **Request Timeout:** Cuts off hanging connections after 5 seconds instead of waiting indefinitely.
* **Local Disk Cache:** Saves downloaded HTML into `cache/` by URL hash. Subsequent runs load from local disk to avoid unnecessary network traffic while testing.
* **Sensible Retries:** Retries transient connection drops or 5xx server errors once, but immediately skips 404s and 403s.

---

## Data Schema

Each extracted record is normalized and validated against this Pydantic schema before saving:

Field | Type | Required | Notes
`title` | string | Yes | Book title
`product_url` | HttpUrl (string) | Yes | Canonical link to the book page
`price_text` | string | Yes | Original raw text (e.g., `£51.77`)
`price_gbp` | float | Yes | Cleaned numeric price (e.g., `51.77`)
`availability_text` | string | Yes | Stock availability line from the page
`rating_text` | string / null | No | Star rating class name (`Three`, `Four`, etc.)
`description` | string / null | No | Product description, or `null` if missing
`source_page` | HttpUrl (string) | Yes | Catalogue page URL where the link was found (provenance)
`fetched_at` | string (ISO 8601) | Yes | UTC timestamp of when the record was pulled

---

## How to Run

1. **Install dependencies:**
   ```bash
   pip3 install requests beautifulsoup4 pydantic

2. **Run the pipeline:**
   ```bash
   python3 src/main.py

The Good records will be written to `output/books.json`, failing records go to `output/errors.json`, and run stats are saved to `output/run-report.json`.

---

## Verified Run Report

Output generated from `output/run-report.json` after running with 1 deliberate test failure:

```json
{
  "start_time": "2026-08-26T12:22:55.452708+00:00",
  "end_time": "2026-08-26T12:22:57.238977+00:00",
  "duration_seconds": 1.79,
  "catalogue_pages": 3,
  "total_targets_attempted": 61,
  "valid_records_stored": 60,
  "invalid_records": 0,
  "failed_pages": 1,
  "cache_hits": 63,
  "pages_fetched": 0
}

---

## Notes & Limitations

* **No Headless Browser Needed:** Because the site renders all its data directly in static server-side HTML, simple HTTP requests using `requests` are enough. Running Playwright or Selenium here would add heavy CPU and memory overhead without any benefit.
* **HTML Fragility:** The scraper relies on static CSS classes (like `div.product_main` and `p.star-rating`). If the sandbox website updates its markup structure, selectors will need to be updated.

---

## Scraping Ethics

* Always use an official API first if the service provides one.
* Never scrape behind authentication, bypass paywalls, or circumvent anti-bot barriers.
* Collect only the specific fields needed, cache during development, and keep request rates respectful.