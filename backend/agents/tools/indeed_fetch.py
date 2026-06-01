import json
import logging
import re
from html import unescape

from bs4 import BeautifulSoup
from curl_cffi import requests as curl_requests

logger = logging.getLogger(__name__)

INDEED_JK_PATTERN = re.compile(r"jk=([a-f0-9]+)", re.I)


def is_indeed_url(url: str) -> bool:
    return "indeed." in url.lower()


def extract_indeed_jk(url: str) -> str | None:
    match = INDEED_JK_PATTERN.search(url)
    return match.group(1) if match else None


def indeed_viewjob_url(jk: str) -> str:
    return f"https://www.indeed.com/viewjob?jk={jk}"


def parse_indeed_html(html: str) -> str | None:
    """Extract job text from Indeed HTML."""
    soup = BeautifulSoup(html, "lxml")
    parts: list[str] = []

    title_el = soup.select_one(
        "h1.jobsearch-JobInfoHeader-title, [data-testid='jobsearch-JobInfoHeader-title'], h1"
    )
    if title_el:
        parts.append(f"Job Title: {title_el.get_text(strip=True)}")

    company_el = soup.select_one(
        "[data-testid='inlineHeader-companyName'], "
        "[data-testid='company-name'], "
        ".jobsearch-CompanyInfoWithoutHeaderImage"
    )
    if company_el:
        parts.append(f"Company: {company_el.get_text(strip=True)}")

    location_el = soup.select_one(
        "[data-testid='inlineHeader-companyLocation'], [data-testid='text-location']"
    )
    if location_el:
        parts.append(f"Location: {location_el.get_text(strip=True)}")

    desc_el = soup.select_one("#jobDescriptionText")
    if desc_el:
        parts.append(desc_el.get_text("\n", strip=True))

    if len(parts) >= 2:
        return "\n\n".join(parts)

    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
        except json.JSONDecodeError:
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            if isinstance(item, dict) and item.get("@type") == "JobPosting":
                chunks = [item.get("title"), item.get("description")]
                text = "\n\n".join(unescape(c) for c in chunks if c)
                if len(text) > 80:
                    return text

    component = soup.select_one(".jobsearch-JobComponent")
    if component:
        text = component.get_text("\n", strip=True)
        if len(text) > 80:
            return text

    return None


IMPERSONATE_PROFILES = ("chrome131", "chrome120", "chrome124", "safari17_0")

DEFAULT_HEADERS = {
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://www.indeed.com/",
}


def _http_get_indeed(fetch_url: str, timeout: int) -> curl_requests.Response | None:
    """Try several TLS fingerprints; Indeed often 403s Playwright and some profiles."""
    last_status = None
    for profile in IMPERSONATE_PROFILES:
        try:
            response = curl_requests.get(
                fetch_url,
                impersonate=profile,
                timeout=timeout,
                allow_redirects=True,
                headers=DEFAULT_HEADERS,
            )
            last_status = response.status_code
            if response.status_code == 200:
                return response
            if response.status_code == 403:
                logger.debug("Indeed 403 with profile %s, retrying", profile)
                continue
            logger.warning("Indeed HTTP %s with profile %s", response.status_code, profile)
            return response
        except Exception as e:
            logger.debug("Indeed fetch error with profile %s: %s", profile, e)
            continue
    if last_status:
        logger.warning("Indeed returned HTTP %s for %s after all profiles", last_status, fetch_url)
    return None


def fetch_indeed_description(url: str, timeout: int = 30) -> str | None:
    """
    Fetch Indeed job page via curl_cffi (Chrome TLS fingerprint).
    Playwright is blocked with 403; this path works for public viewjob pages.
    """
    jk = extract_indeed_jk(url)
    if not jk:
        logger.warning("Indeed URL missing jk parameter: %s", url)
        return None

    fetch_url = indeed_viewjob_url(jk)
    response = _http_get_indeed(fetch_url, timeout)
    if not response:
        return None

    if response.status_code == 403:
        logger.warning("Indeed returned 403 for %s (all profiles)", fetch_url)
        return None

    if response.status_code >= 400:
        logger.warning("Indeed returned HTTP %s for %s", response.status_code, fetch_url)
        return None

    text = parse_indeed_html(response.text)
    if text:
        logger.info("Indeed fetch OK for jk=%s (%d chars)", jk, len(text))
    else:
        logger.warning("Indeed page fetched but no job content parsed for jk=%s", jk)
    return text
