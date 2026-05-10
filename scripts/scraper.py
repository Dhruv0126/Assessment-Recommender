import json
from pathlib import Path

import requests
from bs4 import BeautifulSoup


def scrape_shl_catalog(seed_url: str = "https://www.shl.com/solutions/products/product-catalog/") -> list[dict]:
    """
    Starter scraper template.
    The SHL catalog HTML structure can change, so treat this as a customizable baseline.
    """
    resp = requests.get(seed_url, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    assessments: list[dict] = []
    cards = soup.select("a")  # Replace with precise selectors after inspecting page structure.
    for card in cards:
        href = card.get("href")
        text = card.get_text(" ", strip=True)
        if not href or not text:
            continue
        if "assessment" not in text.lower() and "test" not in text.lower():
            continue

        url = href if href.startswith("http") else f"https://www.shl.com{href}"
        assessments.append(
            {
                "name": text[:120],
                "description": "",
                "skills_measured": [],
                "duration": None,
                "category": None,
                "url": url,
                "test_type": "N/A",
            }
        )

    # Deduplicate by URL
    unique = {a["url"]: a for a in assessments}
    return list(unique.values())


if __name__ == "__main__":
    output = Path("data/shl_catalog.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    data = scrape_shl_catalog()
    output.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Saved {len(data)} raw catalog entries to {output}")
