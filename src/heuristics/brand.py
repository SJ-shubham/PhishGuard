"""
Brand Impersonation Detection — PhishGuard
===========================================
Uses Levenshtein edit distance to detect typosquatting and homoglyph
substitution attacks (e.g. paypa1, g00gle, micr0soft).

Returns a BrandResult with:
  - is_impersonation : bool
  - matched_brand    : str   (which brand is being impersonated)
  - edit_distance    : int   (how many character changes away)
  - normalised_domain: str   (domain after homoglyph substitution)
"""

import re
import tldextract
import Levenshtein


# ── Known brands attackers most commonly impersonate ─────────────────────────
KNOWN_BRANDS = {
    # Finance & payments
    "paypal", "chase", "citibank", "bankofamerica", "wellsfargo",
    "barclays", "hsbc", "sbi", "hdfc", "icici", "axis",
    "americanexpress", "visa", "mastercard", "stripe",
    # Big tech
    "google", "microsoft", "apple", "amazon", "facebook", "instagram",
    "twitter", "netflix", "spotify", "dropbox", "adobe", "linkedin",
    "github", "yahoo", "outlook", "gmail", "hotmail", "icloud",
    # E-commerce
    "ebay", "walmart", "target", "flipkart", "aliexpress", "etsy",
    # Collaboration
    "zoom", "slack", "discord", "notion", "whatsapp", "telegram",
    "skype", "teams",
    # Other high-value targets
    "docusign", "fedex", "dhl", "ups", "usps", "netflix",
    "coinbase", "binance", "robinhood", "venmo", "zelle",
}

# ── Homoglyph substitution map ────────────────────────────────────────────────
# Maps lookalike characters back to their ASCII originals.
_HOMOGLYPH_MAP = str.maketrans({
    "0": "o", "1": "l", "3": "e", "4": "a", "5": "s",
    "6": "g", "7": "t", "8": "b", "9": "g", "@": "a",
    "!": "i", "$": "s", "|": "i",
})

# Levenshtein distance thresholds
_DISTANCE_EXACT      = 0   # exact match = real brand, not impersonation
_DISTANCE_MAX        = 2   # max edit distance to still flag as impersonation
                           # (3 was too loose — "kaggle"→"google" distance=3 false-positived)
_MIN_BRAND_LEN       = 4   # ignore very short brands (avoid over-triggering)


def _normalise(domain: str) -> str:
    """Apply homoglyph substitution and lowercase."""
    return domain.lower().translate(_HOMOGLYPH_MAP)


def _extract_domain_name(url: str) -> str:
    """Return the bare domain name (without TLD or subdomains)."""
    ext = tldextract.extract(url)
    return ext.domain.lower()


class BrandResult:
    def __init__(self, is_impersonation: bool, matched_brand: str,
                 edit_distance: int, normalised_domain: str):
        self.is_impersonation  = is_impersonation
        self.matched_brand     = matched_brand
        self.edit_distance     = edit_distance
        self.normalised_domain = normalised_domain

    def __repr__(self):
        if self.is_impersonation:
            return (f"BrandResult(impersonation=True, brand={self.matched_brand!r}, "
                    f"distance={self.edit_distance}, normalised={self.normalised_domain!r})")
        return "BrandResult(impersonation=False)"


def check_brand_impersonation(url: str) -> BrandResult:
    """
    Check whether the URL's domain is impersonating a known brand.

    Algorithm:
      1. Extract bare domain name (e.g. 'paypa1' from 'paypa1-secure.tk')
      2. Apply homoglyph normalisation ('paypa1' -> 'paypal')
      3. Compute Levenshtein distance against every known brand
      4a. dist == 0 AND original changed during normalisation
          -> homoglyph attack (e.g. paypa1, g00gle, micr0s0ft) -- FLAGGED
      4b. dist == 0 AND original unchanged -> this IS the real brand -- not flagged
      4c. 1 <= dist <= 2 -> typosquat attack -- FLAGGED

    Returns BrandResult.
    """
    raw_domain  = _extract_domain_name(url)
    norm_domain = _normalise(raw_domain)

    best_brand    = ""
    best_distance = 999

    for brand in KNOWN_BRANDS:
        if len(brand) < _MIN_BRAND_LEN:
            continue
        dist = Levenshtein.distance(norm_domain, brand)
        if dist < best_distance:
            best_distance = dist
            best_brand    = brand

    # Homoglyph attack: normalisation changed the string AND it now matches a
    # brand exactly (e.g. paypa1 -> paypal, g00gle -> google).
    if best_distance == _DISTANCE_EXACT:
        if raw_domain != norm_domain:
            # Characters were substituted to reach a brand name → attack
            return BrandResult(True, best_brand, best_distance, norm_domain)
        # raw == norm == brand: this literally is the brand (e.g. real paypal.com)
        return BrandResult(False, best_brand, best_distance, norm_domain)

    # Typosquat: 1–2 character edits away from a known brand
    if best_distance <= _DISTANCE_MAX:
        return BrandResult(True, best_brand, best_distance, norm_domain)

    return BrandResult(False, "", best_distance, norm_domain)
