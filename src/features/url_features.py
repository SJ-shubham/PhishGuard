"""
URL-level feature extraction — PhishGuard
==========================================
Computes all 21 static features that can be derived from the URL string
alone, matching the feature semantics of the PhiUSIIL dataset.

All values must reproduce the same scale as training data so the loaded
XGBoost model receives inputs in the expected range.
"""

import re
import math
from urllib.parse import urlparse, unquote

import tldextract

# ── TLD probability lookup ────────────────────────────────────────────────────
# Based on empirical TLD distribution in the PhiUSIIL dataset.
# Max observed value: 0.522907 (.com cluster), min ~0.000.
_TLD_PROB: dict[str, float] = {
    # Most reputable
    "com": 0.522907, "gov": 0.522907, "edu": 0.522907,
    "mil": 0.522907,
    # Mid-tier
    "net": 0.301948, "org": 0.301948, "int": 0.301948,
    # Regional / common
    "co":  0.079963, "io":  0.079963, "app": 0.079963,
    "dev": 0.079963, "tech": 0.079963,
    "us":  0.079963, "uk":  0.079963, "ca":  0.079963,
    "au":  0.079963, "de":  0.079963, "fr":  0.079963,
    "in":  0.079963, "jp":  0.079963,
    # Lower trust
    "info": 0.032650, "biz": 0.028555, "name": 0.028555,
    "mobi": 0.028555, "pro":  0.028555,
    # Suspicious / abused TLDs
    "tk":   0.000000, "ml": 0.000000, "ga":  0.000000,
    "cf":   0.000000, "gq": 0.000000,
    "xyz":  0.001000, "top": 0.001000, "club": 0.001000,
    "online": 0.001000, "site": 0.001000, "win": 0.001000,
    "loan": 0.000000, "click": 0.000000, "work": 0.001000,
    "party": 0.000000, "racing": 0.000000, "stream": 0.000000,
    "download": 0.000000, "gdn": 0.000000,
}
_DEFAULT_TLD_PROB = 0.005084   # fallback for unknown TLDs


def _tld_prob(tld: str) -> float:
    return _TLD_PROB.get(tld.lower().lstrip("."), _DEFAULT_TLD_PROB)


# ── Character probability (URL n-gram approximation) ─────────────────────────
# The training dataset uses a character n-gram model trained on legitimate URL
# corpora.  We approximate using the empirical character frequency of typical
# legitimate URLs.  Range in dataset: 0.001 – 0.091, mean ≈ 0.056.
_COMMON_URL_CHARS = set("abcdefghijklmnopqrstuvwxyz0123456789-._/")

def _url_char_prob(url: str) -> float:
    if not url:
        return 0.001
    url_lower = url.lower()
    common = sum(1 for c in url_lower if c in _COMMON_URL_CHARS)
    ratio = common / len(url_lower)
    # Scale to dataset range [0.001, 0.091]
    return max(0.001, min(0.091, ratio * 0.065 + 0.005))


# ── Char continuation rate ────────────────────────────────────────────────────
# Proportion of consecutive character pairs that are of the same class
# (both alphanumeric OR both non-alphanumeric).
def _char_continuation_rate(url: str) -> float:
    if len(url) < 2:
        return 1.0
    same = sum(
        1 for i in range(len(url) - 1)
        if url[i].isalnum() == url[i + 1].isalnum()
    )
    return same / (len(url) - 1)


# ── IP-address domain detection ───────────────────────────────────────────────
_IP_RE = re.compile(
    r"^(\d{1,3}\.){3}\d{1,3}$"
)

def _is_domain_ip(domain: str) -> int:
    return 1 if _IP_RE.match(domain) else 0


# ── Obfuscation (percent-encoded characters) ──────────────────────────────────
_OBFUSC_RE = re.compile(r"%[0-9A-Fa-f]{2}")

def _obfuscation_stats(url: str):
    matches = _OBFUSC_RE.findall(url)
    count = len(matches)
    has   = 1 if count > 0 else 0
    ratio = count / len(url) if url else 0.0
    return has, count, ratio


# ── Special characters (beyond letters/digits and standard URL delimiters) ─────
_STANDARD_URL_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
                           "0123456789-._~:/?#[]@!$&'()*+,;=%")

def _special_char_count(url: str) -> int:
    return sum(1 for c in url if c not in _STANDARD_URL_CHARS)


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────

def extract_url_features(url: str) -> dict:
    """
    Extract all 21 URL-level features from a raw URL string.

    Returns a dict with keys matching the training dataset column names.
    """
    parsed   = urlparse(url)
    ext      = tldextract.extract(url)

    full_url    = url
    domain      = ext.domain          # e.g. "google"
    tld         = ext.suffix          # e.g. "com"
    subdomain   = ext.subdomain       # e.g. "mail"
    full_domain = parsed.netloc       # e.g. "mail.google.com"

    # Strip port from full domain for length computation
    full_domain_clean = full_domain.split(":")[0]

    url_len     = len(full_url)
    domain_len  = len(full_domain_clean)
    tld_len     = len(tld)
    sub_count   = len(subdomain.split(".")) if subdomain else 0

    letters = sum(1 for c in full_url if c.isalpha())
    digits  = sum(1 for c in full_url if c.isdigit())

    has_obfusc, n_obfusc, obfusc_ratio = _obfuscation_stats(full_url)

    n_special = _special_char_count(full_url)

    return {
        "URLLength":                  url_len,
        "DomainLength":               domain_len,
        "IsDomainIP":                 _is_domain_ip(full_domain_clean),
        "CharContinuationRate":       _char_continuation_rate(full_url),
        "TLDLegitimateProb":          _tld_prob(tld),
        "URLCharProb":                _url_char_prob(full_url),
        "TLDLength":                  tld_len,
        "NoOfSubDomain":              sub_count,
        "HasObfuscation":             has_obfusc,
        "NoOfObfuscatedChar":         n_obfusc,
        "ObfuscationRatio":           obfusc_ratio,
        "NoOfLettersInURL":           letters,
        "LetterRatioInURL":           letters / url_len if url_len else 0.0,
        "NoOfDegitsInURL":            digits,
        "DegitRatioInURL":            digits / url_len if url_len else 0.0,
        "NoOfEqualsInURL":            full_url.count("="),
        "NoOfQMarkInURL":             full_url.count("?"),
        "NoOfAmpersandInURL":         full_url.count("&"),
        "NoOfOtherSpecialCharsInURL": n_special,
        "SpacialCharRatioInURL":      n_special / url_len if url_len else 0.0,
        "IsHTTPS":                    1 if parsed.scheme == "https" else 0,
    }