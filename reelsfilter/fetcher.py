import httpx
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def fetch_metadata(url: str) -> dict:
    """Fetch og:title and og:description from a Facebook Reel URL.

    Facebook often blocks scraping, so we fall back gracefully to the
    raw URL when no useful metadata is returned.
    """
    title = ""
    description = ""

    try:
        response = httpx.get(url, headers=HEADERS, follow_redirects=True, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        og_title = soup.find("meta", property="og:title")
        og_desc = soup.find("meta", property="og:description")

        title = og_title["content"].strip() if og_title and og_title.get("content") else ""
        description = og_desc["content"].strip() if og_desc and og_desc.get("content") else ""
    except Exception:
        pass  # Facebook blocks are expected; classifier will work from URL alone

    return {"url": url, "title": title, "description": description}
