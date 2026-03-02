"""
Risk Fusion Engine — PhishGuard
================================
Fuses signals from all intelligence layers into a single 0-100 risk score.

Scoring weights:
  ML base (trust-calibrated) → 0–60
  Brand impersonation        → +30
  IP-based URL (registered)  → +30
  IP-in-subdomain            → +25   (e.g. 192.168.0.1.evil.com)
  Suspicious TLD             → +20
  Domain age < 180d          → +20
  SSL failure                → +15
  Content indicators         → +20
  Phishing keywords          → +15   (login, verify, secure, account…)
  DNS failure                → +15
  Punycode/IDN domain        → +20
  ─────────────────────────────────
  RAW_MAX = 150  (realistic normalization cap — scores > 150 are capped at 100)

Trust Calibration
-----------------
When multiple network heuristics are clean (SSL valid, DNS resolves, old domain,
clean TLD, no IP anywhere, no brand impersonation), high ML P(phish) for complex
legitimate sites is weighted DOWN. This replaces the crude whitelist approach.

  n_clean      = count of clean signals (max 6)
  trust_factor = 1.0 - (n_clean / 6) * 0.6
  → 0 clean signals: trust_factor = 1.0   (full ML weight)
  → 6 clean signals: trust_factor = 0.4   (40% ML weight — genuine legitimate site)
"""

from dataclasses import dataclass, field

from src.heuristics.brand        import BrandResult
from src.heuristics.dns_ssl      import DNSResult, SSLResult
from src.heuristics.whois_age    import WhoisResult
from src.heuristics.path_analysis import (
    PathResult, TLDResult,
    IPSubdomainResult, KeywordResult, PunycodeResult,
)


@dataclass
class HeuristicSignals:
    """All raw heuristic outputs — preserved for explainability."""
    brand:        BrandResult        = None
    dns:          DNSResult          = None
    ssl:          SSLResult          = None
    whois:        WhoisResult        = None
    path:         PathResult         = None
    tld:          TLDResult          = None
    ip_subdomain: IPSubdomainResult  = None
    keywords:     KeywordResult      = None
    punycode:     PunycodeResult     = None
    # From ML feature dict
    is_ip_url:    bool               = False


@dataclass
class FusionResult:
    """Final fused score with full score breakdown."""
    ml_base:            float = 0.0   # trust-calibrated ML contribution (0–60)
    trust_factor:       float = 1.0   # 0.4–1.0
    brand_penalty:      float = 0.0   # 0 or +30
    ip_penalty:         float = 0.0   # 0 or +30  (registered domain is IP)
    ip_sub_penalty:     float = 0.0   # 0 or +25  (IP embedded in subdomain)
    tld_penalty:        float = 0.0   # 0 or +20
    domain_age_penalty: float = 0.0   # 0 or +20
    ssl_penalty:        float = 0.0   # 0 or +15
    content_penalty:    float = 0.0   # 0 or +20
    keyword_penalty:    float = 0.0   # 0–15
    dns_penalty:        float = 0.0   # 0 or +15
    punycode_penalty:   float = 0.0   # 0 or +20

    raw_score:    float = 0.0
    final_score:  float = 0.0

    signals: HeuristicSignals = field(default_factory=HeuristicSignals)

    def breakdown(self) -> dict:
        """Return score breakdown as a clean dict for API/display."""
        return {
            "ml_base":            round(self.ml_base, 2),
            "trust_factor":       round(self.trust_factor, 2),
            "brand_impersonation": round(self.brand_penalty, 2),
            "ip_based_url":        round(self.ip_penalty, 2),
            "ip_in_subdomain":     round(self.ip_sub_penalty, 2),
            "suspicious_tld":      round(self.tld_penalty, 2),
            "domain_age":          round(self.domain_age_penalty, 2),
            "ssl_failure":         round(self.ssl_penalty, 2),
            "content_indicators":  round(self.content_penalty, 2),
            "keyword_signals":     round(self.keyword_penalty, 2),
            "dns_failure":         round(self.dns_penalty, 2),
            "punycode_idn":        round(self.punycode_penalty, 2),
            "raw_total":           round(self.raw_score, 2),
            "final_score":         round(self.final_score, 2),
        }


# ── Weight constants ──────────────────────────────────────────────────────────
_ML_MAX        = 60.0
_W_BRAND       = 30.0
_W_IP          = 30.0   # registered domain IS an IP
_W_IP_SUB      = 25.0   # IP embedded in subdomain
_W_TLD         = 20.0
_W_DOMAIN_AGE  = 20.0
_W_SSL         = 15.0
_W_CONTENT     = 20.0
_W_KEYWORDS    = 15.0
_W_DNS_FAIL    = 15.0
_W_PUNYCODE    = 20.0
_RAW_MAX       = 150.0  # realistic normalization cap


def fuse(
    ml_phishing_prob: float,
    url_features: dict,
    content_features: dict,
    signals: HeuristicSignals,
) -> FusionResult:
    """
    Combine ML probability and all heuristic signals into a final risk score.

    Parameters
    ----------
    ml_phishing_prob : float
        Raw P(phishing) from XGBoost, 0.0–1.0.
    url_features : dict
        Output of extract_url_features().
    content_features : dict
        Output of extract_content_features().
    signals : HeuristicSignals
        All heuristic results (brand, dns, ssl, whois, path, tld, ip_subdomain,
        keywords, punycode).

    Returns
    -------
    FusionResult with final_score in [0, 100].
    """
    result = FusionResult(signals=signals)

    # ── Trust calibration ─────────────────────────────────────────────────────
    # Count how many network heuristics are "clean" (legitimate signals).
    # The more clean signals, the more we discount the ML base — this is how
    # we avoid false positives without a whitelist.
    ssl_ok    = bool(signals.ssl  and signals.ssl.valid  and signals.ssl.is_https)
    dns_ok    = bool(signals.dns  and signals.dns.resolves)
    old_dom   = bool(signals.whois and not signals.whois.is_new
                     and not signals.whois.is_unknown)
    clean_tld = bool(signals.tld  and not signals.tld.is_suspicious_tld)
    no_ip     = (url_features.get("IsDomainIP", 0) == 0
                 and not (signals.ip_subdomain and signals.ip_subdomain.has_ip_in_subdomain))
    no_brand  = bool(not signals.brand or not signals.brand.is_impersonation)

    n_clean      = sum([ssl_ok, dns_ok, old_dom, clean_tld, no_ip, no_brand])
    trust_factor = 1.0 - (n_clean / 6) * 0.6   # range: 1.0 (all bad) → 0.4 (all clean)

    result.trust_factor = round(trust_factor, 3)

    # ── Layer 1: ML base (0 – 60, scaled by trust) ────────────────────────────
    result.ml_base = round(min(ml_phishing_prob * _ML_MAX * trust_factor,
                               _ML_MAX * trust_factor), 2)

    # ── Layer 2: Brand impersonation (+30) ────────────────────────────────────
    if signals.brand and signals.brand.is_impersonation:
        result.brand_penalty = _W_BRAND

    # ── Layer 2: Registered-domain is an IP (+30) ─────────────────────────────
    if url_features.get("IsDomainIP", 0) == 1:
        result.ip_penalty = _W_IP

    # ── Layer 2: IP embedded in subdomain (+25) ───────────────────────────────
    if signals.ip_subdomain and signals.ip_subdomain.has_ip_in_subdomain:
        result.ip_sub_penalty = _W_IP_SUB

    # ── Layer 2: Suspicious TLD (+20) ─────────────────────────────────────────
    if signals.tld and signals.tld.is_suspicious_tld:
        result.tld_penalty = _W_TLD

    # ── Layer 3: Domain age < 180 days (+20) ──────────────────────────────────
    if signals.whois:
        if signals.whois.is_new:
            result.domain_age_penalty = _W_DOMAIN_AGE
        elif signals.whois.is_unknown and not url_features.get("IsHTTPS", 0):
            result.domain_age_penalty = _W_DOMAIN_AGE * 0.5

    # ── Layer 3: SSL/TLS failure (+15) ────────────────────────────────────────
    if signals.ssl and not signals.ssl.valid:
        result.ssl_penalty = _W_SSL

    # ── Layer 3: DNS failure (+15) ────────────────────────────────────────────
    if signals.dns and not signals.dns.resolves:
        result.dns_penalty = _W_DNS_FAIL

    # ── Layer 4: Content indicators (+20) ─────────────────────────────────────
    has_pw    = content_features.get("HasPasswordField", 0) == 1
    has_ext_f = content_features.get("HasExternalFormSubmit", 0) == 1
    has_pop   = content_features.get("NoOfPopup", 0) > 0
    if has_pw and has_ext_f:
        result.content_penalty = _W_CONTENT
    elif (has_pw or has_ext_f) and has_pop:
        result.content_penalty = _W_CONTENT * 0.5

    # ── Layer 4: Phishing keywords in domain / path (+15) ─────────────────────
    # Scale by keyword count: 1 keyword = 40%, 2 = 70%, 3+ = 100%
    if signals.keywords and signals.keywords.has_suspicious_keywords:
        kw_count = signals.keywords.keyword_count
        kw_ratio = min(1.0, 0.4 + (kw_count - 1) * 0.3)
        result.keyword_penalty = round(_W_KEYWORDS * kw_ratio, 2)

    # ── Layer 4: Punycode / IDN homograph (+20) ───────────────────────────────
    if signals.punycode and signals.punycode.has_punycode:
        result.punycode_penalty = _W_PUNYCODE

    # ── Normalise to 0–100 ────────────────────────────────────────────────────
    result.raw_score = round(
        result.ml_base + result.brand_penalty + result.ip_penalty +
        result.ip_sub_penalty + result.tld_penalty + result.domain_age_penalty +
        result.ssl_penalty + result.content_penalty + result.keyword_penalty +
        result.dns_penalty + result.punycode_penalty,
        2,
    )
    result.final_score = round(min(result.raw_score / _RAW_MAX * 100, 100.0), 2)

    return result
