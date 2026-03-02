"""
Content-level feature extraction — PhishGuard
==============================================
Fetches a URL and extracts 28 content-based features from the HTML response,
matching the feature semantics of the PhiUSIIL dataset.

All features default to 0 when the page cannot be reached (an unreachable
or error-returning URL is itself a phishing signal handled by the heuristic
engine; zeros let the ML model still produce a useful probability).
"""

import re
import socket
from difflib import SequenceMatcher
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup
import tldextract


# ── Request configuration ─────────────────────────────────────────────────────
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}
_TIMEOUT = 8          # seconds per request
_MAX_HTML = 500_000   # cap HTML at 500 KB to keep parsing fast


# ── Keyword lists ─────────────────────────────────────────────────────────────
_BANK_KEYWORDS  = {"bank", "banking", "credit", "debit", "account", "loan",
                   "financial", "finance", "invest", "mortgage", "wire", "transfer"}
_PAY_KEYWORDS   = {"pay", "payment", "checkout", "purchase", "order", "buy",
                   "shop", "cart", "invoice", "billing", "transaction", "paypal",
                   "stripe", "venmo", "zelle", "cash"}
_CRYPTO_KEYWORDS = {"bitcoin", "btc", "ethereum", "eth", "crypto", "blockchain",
                    "nft", "wallet", "mining", "defi", "binance", "coinbase",
                    "token", "altcoin", "litecoin"}
_SOCIAL_DOMAINS = {"facebook.com", "twitter.com", "x.com", "instagram.com",
                   "linkedin.com", "youtube.com", "tiktok.com", "pinterest.com",
                   "reddit.com", "snapchat.com", "whatsapp.com", "telegram.org"}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _fetch(url: str) -> tuple[requests.Response | None, str]:
    """Fetch URL, return (response, html_text). Returns (None, '') on error."""
    try:
        resp = requests.get(
            url, headers=_HEADERS, timeout=_TIMEOUT,
            allow_redirects=True, verify=False
        )
        html = resp.text[:_MAX_HTML]
        return resp, html
    except Exception:
        return None, ""


def _get_domain(url: str) -> str:
    ext = tldextract.extract(url)
    return f"{ext.domain}.{ext.suffix}".lower()


def _text_match_score(a: str, b: str) -> float:
    """Return SequenceMatcher ratio * 100, capped to [0, 100]."""
    if not a or not b:
        return 0.0
    ratio = SequenceMatcher(None, a.lower(), b.lower()).ratio()
    return round(min(ratio * 100, 100.0), 6)


def _check_robots(base_url: str) -> int:
    """Return 1 if robots.txt is accessible, 0 otherwise."""
    parsed = urlparse(base_url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    try:
        r = requests.get(robots_url, headers=_HEADERS, timeout=4, verify=False)
        return 1 if r.status_code == 200 and len(r.text) > 10 else 0
    except Exception:
        return 0


def _redirect_type(response: requests.Response, original_domain: str) -> tuple[int, int]:
    """
    Analyse the redirect history.
    Returns (NoOfURLRedirect, NoOfSelfRedirect) — both binary (0 or 1).
    """
    if not response.history:
        return 0, 0
    url_redirect  = 0
    self_redirect = 0
    for r in response.history:
        redir_domain = _get_domain(r.url)
        if redir_domain != original_domain:
            url_redirect = 1
        else:
            self_redirect = 1
    return url_redirect, self_redirect


def _count_external_refs(soup: BeautifulSoup, page_domain: str) -> tuple[int, int, int]:
    """
    Count (self_refs, empty_refs, external_refs) from meaningful link elements.

    Only inspects tags that semantically carry URLs:
      <a href>, <link href>, <img src>, <script src>, <iframe src>, <form action>
    This avoids inflated counts from inline JS or data attributes.
    """
    self_ref = 0
    empty_ref = 0
    ext_ref = 0

    _EMPTY = {"", "#", "javascript:void(0)", "javascript:;", "javascript:", "/"}

    # (tag_name, attribute) pairs that carry real URLs
    _LINK_SELECTORS = [
        ("a",      "href"),
        ("link",   "href"),
        ("img",    "src"),
        ("script", "src"),
        ("iframe", "src"),
        ("form",   "action"),
    ]

    for tag_name, attr in _LINK_SELECTORS:
        for tag in soup.find_all(tag_name):
            val = tag.get(attr, None)
            if val is None:
                continue
            val = val.strip()
            if val in _EMPTY or val.startswith("data:"):
                empty_ref += 1
                continue
            if not val.startswith("http"):
                # relative URL — belongs to same domain
                self_ref += 1
                continue
            link_domain = _get_domain(val)
            if link_domain == page_domain or not link_domain:
                self_ref += 1
            else:
                ext_ref += 1

    return self_ref, empty_ref, ext_ref


def _has_social_net(soup: BeautifulSoup) -> int:
    for a in soup.find_all("a", href=True):
        href = a["href"].lower()
        if any(s in href for s in _SOCIAL_DOMAINS):
            return 1
    return 0


def _has_keyword(text: str, keywords: set) -> int:
    text_lower = text.lower()
    return 1 if any(k in text_lower for k in keywords) else 0


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

# ── Median content feature values for legitimate sites (from PhiUSIIL dataset) ─
# Used as neutral defaults when a JS-rendered SPA is detected.
# Source: median of label=1 rows across all 28 content features.
_SPA_DEFAULTS = {
    "LineOfCode":            1105,
    "LargestLineLength":     3066,
    "HasTitle":              1,
    "DomainTitleMatchScore": 100.0,
    "URLTitleMatchScore":    100.0,
    "HasFavicon":            1,
    "Robots":                0,
    "IsResponsive":          1,
    "NoOfURLRedirect":       0,
    "NoOfSelfRedirect":      0,
    "HasDescription":        1,
    "NoOfPopup":             0,
    "NoOfiFrame":            1,
    "HasExternalFormSubmit": 0,
    "HasSocialNet":          1,
    "HasSubmitButton":       1,
    "HasHiddenFields":       1,
    "HasPasswordField":      0,
    "Bank":                  0,
    "Pay":                   0,
    "Crypto":                0,
    "HasCopyrightInfo":      1,
    "NoOfImage":             25,
    "NoOfCSS":               6,
    "NoOfJS":                14,
    "NoOfSelfRef":           76,
    "NoOfEmptyRef":          1,
    "NoOfExternalRef":       46,
}

def _is_spa(lines: list[str], html: str) -> bool:
    """
    Detect a JavaScript-rendered Single Page Application.

    Criteria:
      - The server responded (html is non-empty)
      - Very few line breaks (≤ 5 lines) — minified shell
      - At least one line is very long (> 5 000 chars) — minified JS/CSS bundle
        OR the raw HTML is large despite few lines (> 20 KB)

    Reason: True phishing pages never serve 100KB minified JavaScript bundles.
    Only legitimate SPA frameworks (React, Next.js, Vue, Angular) produce this.
    """
    if len(lines) > 5:
        return False
    longest = max((len(l) for l in lines), default=0)
    return longest > 5_000 or len(html) > 20_000


def extract_content_features(url: str) -> dict:
    """
    Fetch `url` and extract all 28 content-level features.

    - Non-reachable URLs: return all-zero defaults (phishing signal).
    - JS SPA pages (≤5 lines, large HTML): return legitimate-median defaults
      because plain HTTP cannot see rendered content.  True phishing pages
      never ship 20KB+ minified JS bundles.
    - Normal HTML pages: full extraction.
    """
    defaults = {
        "LineOfCode": 0, "LargestLineLength": 0,
        "HasTitle": 0, "DomainTitleMatchScore": 0.0, "URLTitleMatchScore": 0.0,
        "HasFavicon": 0, "Robots": 0, "IsResponsive": 0,
        "NoOfURLRedirect": 0, "NoOfSelfRedirect": 0,
        "HasDescription": 0, "NoOfPopup": 0, "NoOfiFrame": 0,
        "HasExternalFormSubmit": 0, "HasSocialNet": 0,
        "HasSubmitButton": 0, "HasHiddenFields": 0, "HasPasswordField": 0,
        "Bank": 0, "Pay": 0, "Crypto": 0,
        "HasCopyrightInfo": 0,
        "NoOfImage": 0, "NoOfCSS": 0, "NoOfJS": 0,
        "NoOfSelfRef": 0, "NoOfEmptyRef": 0, "NoOfExternalRef": 0,
    }

    # Suppress SSL warnings (we still check SSL in the heuristic engine)
    requests.packages.urllib3.disable_warnings()

    page_domain   = _get_domain(url)
    response, html = _fetch(url)

    if not html:
        return defaults

    # ── Raw HTML metrics ──────────────────────────────────────────────────────
    lines = html.splitlines()
    loc   = len(lines)
    largest_line = max((len(l) for l in lines), default=0)

    # ── SPA detection ─────────────────────────────────────────────────────────
    # If the page is a JavaScript-rendered SPA (React/Next.js/Vue etc.), the
    # raw HTML is a minimal shell.  We cannot extract meaningful content
    # features from it, so we substitute the median values observed in
    # legitimate sites from the training dataset.  This prevents the model
    # from treating every modern JS app as a phishing page.
    if _is_spa(lines, html):
        # Still try to extract a few features that ARE present in the shell
        soup_shell = BeautifulSoup(html, "html.parser")
        spa_feats  = dict(_SPA_DEFAULTS)  # start from legitimate medians

        # Override with actual values that are available in the shell
        title_tag = soup_shell.find("title")
        if title_tag and title_tag.get_text(strip=True):
            spa_feats["HasTitle"] = 1
        viewport = soup_shell.find("meta", attrs={"name": re.compile(r"viewport", re.I)})
        spa_feats["IsResponsive"] = 1 if viewport else _SPA_DEFAULTS["IsResponsive"]
        desc = soup_shell.find("meta", attrs={"name": re.compile(r"description", re.I)})
        spa_feats["HasDescription"] = 1 if (desc and desc.get("content", "").strip()) else _SPA_DEFAULTS["HasDescription"]
        spa_feats["Robots"] = _check_robots(url)

        # Keep actual redirect info
        if response is not None:
            no_url_redir, no_self_redir = _redirect_type(response, page_domain)
            spa_feats["NoOfURLRedirect"] = no_url_redir
            spa_feats["NoOfSelfRedirect"] = no_self_redir

        return spa_feats


    soup = BeautifulSoup(html, "html.parser")
    page_text = soup.get_text(" ", strip=True).lower()

    # Title
    title_tag = soup.find("title")
    title_text = title_tag.get_text(strip=True) if title_tag else ""
    has_title  = 1 if title_text else 0

    # Domain & URL title match (0–100 scale, same as dataset)
    domain_match = _text_match_score(page_domain.split(".")[0], title_text)
    url_match    = _text_match_score(url, title_text)

    # Favicon
    fav = soup.find("link", rel=lambda r: r and any(
        "icon" in x.lower() for x in (r if isinstance(r, list) else [r])
    ))
    has_favicon = 1 if fav else 0

    # Robots.txt
    robots = _check_robots(url)

    # Responsive (viewport meta)
    viewport = soup.find("meta", attrs={"name": re.compile(r"viewport", re.I)})
    is_responsive = 1 if viewport else 0

    # Redirects
    no_url_redir = no_self_redir = 0
    if response is not None:
        no_url_redir, no_self_redir = _redirect_type(response, page_domain)

    # Meta description
    desc = soup.find("meta", attrs={"name": re.compile(r"description", re.I)})
    has_desc = 1 if (desc and desc.get("content", "").strip()) else 0

    # Popups
    n_popup = len(re.findall(r"window\.open\s*\(", html))

    # iFrames
    n_iframe = len(soup.find_all("iframe"))

    # External form submit
    has_ext_form = 0
    for form in soup.find_all("form"):
        action = form.get("action", "")
        if action and action.startswith("http"):
            action_domain = _get_domain(action)
            if action_domain and action_domain != page_domain:
                has_ext_form = 1
                break

    # Social networks
    has_social = _has_social_net(soup)

    # Submit / hidden / password fields
    has_submit   = 1 if soup.find("input", {"type": re.compile(r"submit", re.I)}) \
                         or soup.find("button", {"type": re.compile(r"submit", re.I)}) else 0
    has_hidden   = 1 if soup.find("input", {"type": re.compile(r"hidden",  re.I)}) else 0
    has_password = 1 if soup.find("input", {"type": re.compile(r"password", re.I)}) else 0

    # Keyword flags
    bank   = _has_keyword(page_text + " " + title_text, _BANK_KEYWORDS)
    pay    = _has_keyword(page_text + " " + title_text, _PAY_KEYWORDS)
    crypto = _has_keyword(page_text + " " + title_text, _CRYPTO_KEYWORDS)

    # Copyright
    has_copyright = 1 if re.search(r"(?:©|&copy;|\bcopyright\b)", html, re.I) else 0

    # Resource counts
    n_img = len(soup.find_all("img"))
    n_css = len(soup.find_all("link", rel=lambda r: r and "stylesheet" in
                               (r if isinstance(r, list) else [r]))) \
            + len(soup.find_all("style"))
    n_js  = len(soup.find_all("script"))

    # Reference counts
    self_ref, empty_ref, ext_ref = _count_external_refs(soup, page_domain)

    return {
        "LineOfCode":           loc,
        "LargestLineLength":    largest_line,
        "HasTitle":             has_title,
        "DomainTitleMatchScore": domain_match,
        "URLTitleMatchScore":   url_match,
        "HasFavicon":           has_favicon,
        "Robots":               robots,
        "IsResponsive":         is_responsive,
        "NoOfURLRedirect":      no_url_redir,
        "NoOfSelfRedirect":     no_self_redir,
        "HasDescription":       has_desc,
        "NoOfPopup":            n_popup,
        "NoOfiFrame":           n_iframe,
        "HasExternalFormSubmit": has_ext_form,
        "HasSocialNet":         has_social,
        "HasSubmitButton":      has_submit,
        "HasHiddenFields":      has_hidden,
        "HasPasswordField":     has_password,
        "Bank":                 bank,
        "Pay":                  pay,
        "Crypto":               crypto,
        "HasCopyrightInfo":     has_copyright,
        "NoOfImage":            n_img,
        "NoOfCSS":              n_css,
        "NoOfJS":               n_js,
        "NoOfSelfRef":          self_ref,
        "NoOfEmptyRef":         empty_ref,
        "NoOfExternalRef":      ext_ref,
    }
