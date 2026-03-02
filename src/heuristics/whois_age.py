"""
WHOIS Domain Age Analysis — PhishGuard
=======================================
Newly registered domains are a strong phishing signal.
Attackers register throwaway domains hours before a campaign.

Threshold: domains < 180 days old are considered suspicious.
If WHOIS lookup fails or returns no creation date, the domain is
treated as unverifiable (partial risk added).
"""

import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urlparse

import tldextract
import whois


_WHOIS_TIMEOUT    = 8     # seconds before we give up
_SUSPICIOUS_DAYS  = 180   # domains younger than this are flagged


@dataclass
class WhoisResult:
    age_days:      int     # -1 = unknown / lookup failed
    is_new:        bool    # True if domain < 180 days old
    is_unknown:    bool    # True if WHOIS failed or no creation date
    creation_date: str     # ISO string or "unknown"
    error:         str


def _extract_registered_domain(url: str) -> str:
    ext = tldextract.extract(url)
    return f"{ext.domain}.{ext.suffix}"


def _normalise_date(raw) -> datetime | None:
    """Handle whois returning a list or a single datetime."""
    if raw is None:
        return None
    if isinstance(raw, list):
        raw = raw[0]
    if isinstance(raw, datetime):
        # Make timezone-aware if naive
        if raw.tzinfo is None:
            raw = raw.replace(tzinfo=timezone.utc)
        return raw
    return None


def _do_whois(domain: str, result_holder: list):
    """Run whois lookup and store result in list (for threading)."""
    try:
        w = whois.whois(domain)
        result_holder.append(w)
    except Exception as e:
        result_holder.append(e)


def check_domain_age(url: str) -> WhoisResult:
    """
    Perform a WHOIS lookup and return the domain's age in days.

    Uses a thread-based timeout so a slow WHOIS server never blocks
    the prediction pipeline for more than _WHOIS_TIMEOUT seconds.
    """
    domain = _extract_registered_domain(url)

    # Run WHOIS in a daemon thread with a timeout
    result_holder: list = []
    thread = threading.Thread(
        target=_do_whois, args=(domain, result_holder), daemon=True
    )
    thread.start()
    thread.join(timeout=_WHOIS_TIMEOUT)

    if not result_holder:
        return WhoisResult(
            age_days=-1, is_new=False, is_unknown=True,
            creation_date="unknown", error="WHOIS lookup timed out"
        )

    raw = result_holder[0]

    if isinstance(raw, Exception):
        return WhoisResult(
            age_days=-1, is_new=False, is_unknown=True,
            creation_date="unknown", error=str(raw)
        )

    creation = _normalise_date(getattr(raw, "creation_date", None))

    if creation is None:
        return WhoisResult(
            age_days=-1, is_new=False, is_unknown=True,
            creation_date="unknown", error="No creation date in WHOIS"
        )

    now      = datetime.now(timezone.utc)
    age_days = (now - creation).days
    is_new   = age_days < _SUSPICIOUS_DAYS

    return WhoisResult(
        age_days=age_days,
        is_new=is_new,
        is_unknown=False,
        creation_date=creation.strftime("%Y-%m-%d"),
        error=""
    )
