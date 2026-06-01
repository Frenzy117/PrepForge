import asyncio
import logging
import socket
from ipaddress import ip_address, IPv4Address, IPv6Address, IPv4Network, IPv6Network

from langchain_core.tools import tool
from langchain_mistralai import ChatMistralAI
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright

from backend.agents.prompts.templates import jobReaderTemplate
from backend.agents.tools.indeed_fetch import fetch_indeed_description, is_indeed_url
from backend.config import get_settings

logger = logging.getLogger(__name__)

# Non-Indeed job boards (Playwright)
JOB_CONTENT_SELECTORS = [
    "#jobDescriptionText",
    ".jobsearch-JobComponent",
    "[data-testid='jobsearch-JobComponent']",
    ".jobsearch-ViewJobLayout--jobDisplay",
    "main",
]

CHROME_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/121.0.0.0 Safari/537.36"
)

CONSENT_SELECTORS = [
    "#onetrust-accept-btn-handler",
    "button:has-text('Accept all')",
    "button:has-text('Accept All')",
    "button:has-text('Accept')",
    "[data-testid='accept-cookies']",
]

INDEED_BLOCKED_MSG = (
    "Indeed blocked automated access to this URL. "
    "Open the posting in your browser, copy the job description, and use **Paste description** instead."
)


def _headless() -> bool:
    return get_settings().playwright_headless


def _scrape_timeout_ms() -> int:
    return get_settings().playwright_scrape_timeout_ms


def normalize_job_url(url: str) -> str:
    from backend.agents.tools.indeed_fetch import extract_indeed_jk, indeed_viewjob_url

    url = url.strip()
    jk = extract_indeed_jk(url)
    if jk and is_indeed_url(url):
        return indeed_viewjob_url(jk)
    return url


def _is_private_ip(host: str) -> bool:
    """Return True if the host resolves to a private/loopback IP."""
    try:
        infos = socket.getaddrinfo(host, None)
    except Exception:
        # If we cannot resolve, treat as unsafe to be conservative
        return True
    for info in infos:
        addr = info[4][0]
        try:
            ip = ip_address(addr)
            if ip.is_private or ip.is_loopback or ip.is_reserved or ip.is_link_local:
                return True
        except Exception:
            continue
    return False


def is_safe_url(url: str) -> bool:
    """Basic safety checks for URLs to mitigate SSRF and malicious hosts.

    - only allow http/https
    - host must not resolve to private or loopback IPs
    - reject obvious non-URLs
    """
    from urllib.parse import urlparse

    try:
        parsed = urlparse(url)
    except Exception:
        return False
    if parsed.scheme not in ("http", "https"):
        return False
    host = parsed.hostname
    if not host:
        return False
    # reject localhost and private IPs
    if host in ("localhost", "127.0.0.1", "::1"):
        return False
    if _is_private_ip(host):
        return False
    return True


def summarize_job_description(description: str | None) -> str:
    """Summarize raw job description text with the job reader LLM."""
    if not description or not description.strip():
        return "Job posting unavailable or contains no job details"

    llm = ChatMistralAI(
        model="mistral-medium-2508",
        api_key=get_settings().mistral_api_key,
    )
    prompt = jobReaderTemplate.invoke({"description": description.strip()})
    return llm.invoke(prompt).content


async def _dismiss_consent(page) -> None:
    for selector in CONSENT_SELECTORS:
        try:
            button = page.locator(selector).first
            if await button.is_visible(timeout=1500):
                await button.click(timeout=2000)
                await page.wait_for_timeout(800)
                return
        except Exception:
            continue


async def _extract_via_js(page) -> str | None:
    text = await page.evaluate(
        """() => {
            const parts = [];
            const title = document.querySelector(
                'h1.jobsearch-JobInfoHeader-title, [data-testid="jobsearch-JobInfoHeader-title"]'
            );
            const company = document.querySelector(
                '[data-testid="inlineHeader-companyName"], [data-testid="company-name"]'
            );
            const desc = document.querySelector('#jobDescriptionText')
                || document.querySelector('.jobsearch-JobComponent');

            if (title) parts.push('Job Title: ' + title.innerText.trim());
            if (company) parts.push('Company: ' + company.innerText.trim());
            if (desc) parts.push(desc.innerText.trim());
            if (parts.length) return parts.join('\\n\\n');
            return null;
        }"""
    )
    return (text or "").strip() or None


async def _extract_from_selectors(page) -> str | None:
    for selector in JOB_CONTENT_SELECTORS:
        try:
            locator = page.locator(selector).first
            if await locator.count() == 0:
                continue
            await locator.wait_for(state="attached", timeout=8000)
            text = await locator.text_content()
            cleaned = (text or "").strip()
            if len(cleaned) > 80:
                return cleaned
        except PlaywrightTimeoutError:
            continue
        except Exception as e:
            logger.debug("Selector %s failed: %s", selector, e)
    return None


async def _scrape_with_playwright(url: str) -> str | None:
    """Playwright fetch for non-Indeed boards (Indeed returns 403 to headless browsers)."""
    timeout = _scrape_timeout_ms()
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=_headless(),
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        )
        try:
            context = await browser.new_context(
                user_agent=CHROME_USER_AGENT,
                viewport={"width": 1280, "height": 900},
                locale="en-US",
            )
            page = await context.new_page()
            page.set_default_timeout(timeout)

            response = await page.goto(url, wait_until="domcontentloaded", timeout=timeout)
            if response and response.status == 403:
                logger.warning("HTTP 403 for %s", url)
                return None
            if response and response.status >= 400:
                logger.warning("HTTP %s for %s", response.status, url)

            await _dismiss_consent(page)
            await page.wait_for_timeout(1500)

            text = await _extract_via_js(page)
            if text and len(text) > 80:
                return text
            return await _extract_from_selectors(page)
        finally:
            await browser.close()


async def scrape_job_description(url: str) -> str | None:
    """Fetch job posting text. Indeed uses HTTP; other sites use Playwright."""
    url = normalize_job_url(url)

    # Basic safety check: reject URLs that look unsafe (SSRF, private hosts)
    try:
        if not is_safe_url(url):
            logger.warning("Rejected unsafe job URL: %s", url)
            return None
    except Exception:
        logger.warning("Error validating job URL: %s", url)
        return None

    if is_indeed_url(url):
        return await asyncio.to_thread(fetch_indeed_description, url)

    try:
        return await _scrape_with_playwright(url)
    except PlaywrightTimeoutError as e:
        logger.warning("Playwright timeout scraping %s: %s", url, e)
        return None
    except Exception as e:
        logger.warning("Failed to scrape job URL %s: %s", url, e)
        return None


async def scrape_and_summarize(url: str) -> str:
    """Scrape a job URL and return a structured summary."""
    description = await scrape_job_description(url)
    if not description:
        if is_indeed_url(url):
            return INDEED_BLOCKED_MSG
        return (
            f"Could not fetch job posting from URL: {url}. "
            "Try pasting the job description instead."
        )
    return summarize_job_description(description)


@tool
async def get_job_summary(job_link: str) -> str:
    """
    Extracts structured information from a job posting at the provided URL.

    Args:
        job_link: The URL of the job posting.

    Returns:
        A structured summary of the job posting's key details.
    """
    return await scrape_and_summarize(job_link)
