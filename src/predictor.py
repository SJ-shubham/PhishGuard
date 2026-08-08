"""
PhishGuard — Predictor
======================
Loads the trained XGBoost model and exposes a single `predict(url)` call that:
  1. Extracts 21 URL-level features (no network required)
  2. Extracts 28 content-level features (fetches the page)
  3. Runs all heuristic checks in parallel:
       - Brand impersonation (Levenshtein)
       - DNS resolution
       - SSL/TLS validation
       - WHOIS domain age
       - Suspicious path & TLD
  4. Fuses ML probability + heuristic signals into a weighted 0-100 risk score
  5. Applies a trusted-domain whitelist cap as a final safety net

Risk score -> 0 (definitely legitimate) to 100 (definitely phishing).
Label convention: model class 0 = phishing, class 1 = legitimate.
So  P(phishing) = predict_proba[:, 0].
"""

import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field

import joblib
import numpy as np

from src.features.url_features      import extract_url_features
from src.features.content_features  import extract_content_features

from src.heuristics.brand           import check_brand_impersonation
from src.heuristics.dns_ssl         import check_dns, check_ssl
from src.heuristics.whois_age       import check_domain_age
from src.heuristics.path_analysis   import (
    check_path, check_tld,
    check_ip_subdomain, check_keywords, check_punycode,
)

from src.fusion    import fuse, HeuristicSignals
from src.explainer import explain, ExplanationResult


# ── Paths ─────────────────────────────────────────────────────────────────────
_BASE        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MODEL_PATH  = os.path.join(_BASE, "models", "phishguard_model.pkl")
_FEAT_PATH   = os.path.join(_BASE, "models", "feature_list.pkl")

# ── Load model once at import ─────────────────────────────────────────────────
_model: object = joblib.load(_MODEL_PATH)
_features: list[str] = joblib.load(_FEAT_PATH)


# ── Verdict thresholds ────────────────────────────────────────────────────────
def _verdict(score: float) -> tuple[str, str]:
    """Map risk score (0-100) to (risk_level, verdict_label)."""
    if score < 30:
        return "Low",      "Safe to Visit"
    if score < 50:
        return "Medium",   "Caution Advised"
    if score < 75:
        return "High",     "Not Safe to Visit"
    return     "Critical", "Block Immediately"


# ── Result dataclass ──────────────────────────────────────────────────────────
@dataclass
class PredictionResult:
    url:              str
    risk_score:       float               # 0-100 (fused final score)
    phishing_prob:    float               # 0.0-1.0  (raw ML model output)
    legitimate_prob:  float               # 0.0-1.0
    risk_level:       str                 # Low / Medium / High / Critical
    verdict:          str                 # human-readable decision
    is_phishing:      bool
    features:         dict = field(default_factory=dict)   # all 49 extracted values
    score_breakdown:  dict = field(default_factory=dict)   # per-signal contribution
    heuristic_flags:  dict = field(default_factory=dict)   # raw heuristic outputs
    shap_explanation: ExplanationResult | None = None      # SHAP feature attribution
    elapsed_sec:      float = 0.0


# ── Parallel heuristic runner ─────────────────────────────────────────────────

def _run_heuristics(url: str) -> HeuristicSignals:
    """
    Run all five heuristic checks concurrently and assemble a HeuristicSignals.

    Network checks (DNS, SSL, WHOIS) each have their own timeouts so the total
    wall-clock cost is bounded by max(individual_timeouts) ~ 8 seconds, not
    the sum of all timeouts.
    """
    signals = HeuristicSignals()

    tasks = {
        "brand":        lambda: check_brand_impersonation(url),
        "dns":          lambda: check_dns(url),
        "ssl":          lambda: check_ssl(url),
        "whois":        lambda: check_domain_age(url),
        "path":         lambda: check_path(url),
        "tld":          lambda: check_tld(url),
        "ip_subdomain": lambda: check_ip_subdomain(url),
        "keywords":     lambda: check_keywords(url),
        "punycode":     lambda: check_punycode(url),
    }

    with ThreadPoolExecutor(max_workers=9) as executor:
        future_to_name = {executor.submit(fn): name for name, fn in tasks.items()}
        for future in as_completed(future_to_name):
            name = future_to_name[future]
            try:
                result = future.result()
                setattr(signals, name, result)
            except Exception:
                pass  # leave that signal as None; fusion handles None gracefully

    return signals


def _build_heuristic_flags(signals: HeuristicSignals) -> dict:
    """Flatten heuristic results into a display-friendly dict."""
    flags = {}

    if signals.brand:
        flags["brand_impersonation"] = signals.brand.is_impersonation
        if signals.brand.is_impersonation:
            flags["brand_matched"]  = signals.brand.matched_brand
            flags["brand_distance"] = signals.brand.edit_distance

    if signals.dns:
        flags["dns_resolves"] = signals.dns.resolves
        if signals.dns.ip_address:
            flags["ip_address"] = signals.dns.ip_address
        if not signals.dns.resolves:
            flags["dns_error"] = signals.dns.error

    if signals.ssl:
        flags["ssl_valid"]  = signals.ssl.valid
        flags["is_https"]   = signals.ssl.is_https
        if not signals.ssl.valid:
            flags["ssl_error"] = signals.ssl.error

    if signals.whois:
        flags["domain_age_days"]    = signals.whois.age_days
        flags["domain_is_new"]      = signals.whois.is_new
        flags["domain_age_unknown"] = signals.whois.is_unknown
        flags["domain_created"]     = signals.whois.creation_date

    if signals.path:
        flags["path_flags"]          = signals.path.flags
        flags["path_is_suspicious"]  = signals.path.is_suspicious

    if signals.tld:
        flags["tld"]                 = signals.tld.tld
        flags["suspicious_tld"]      = signals.tld.is_suspicious_tld

    if signals.ip_subdomain:
        flags["ip_in_subdomain"]     = signals.ip_subdomain.has_ip_in_subdomain
        if signals.ip_subdomain.has_ip_in_subdomain:
            flags["detected_ip"]     = signals.ip_subdomain.detected_ip

    if signals.keywords:
        flags["suspicious_keywords"] = signals.keywords.has_suspicious_keywords
        if signals.keywords.has_suspicious_keywords:
            flags["found_keywords"]  = signals.keywords.found_keywords
            flags["keyword_count"]   = signals.keywords.keyword_count

    if signals.punycode:
        flags["has_punycode"]        = signals.punycode.has_punycode
        if signals.punycode.has_punycode:
            flags["punycode_parts"]  = signals.punycode.punycode_parts

    return flags


# ── Public API ────────────────────────────────────────────────────────────────

def predict(url: str) -> PredictionResult:
    """
    Full prediction pipeline for a single URL.

    Steps
    -----
    1. Extract URL + content features
    2. Run XGBoost model -> P(phishing)
    3. Run all heuristics concurrently (brand, DNS, SSL, WHOIS, path, TLD,
       IP-in-subdomain, keyword, punycode)
    4. Fuse ML probability + heuristic signals -> trust-calibrated 0-100 score
    5. Return PredictionResult with full breakdown

    Parameters
    ----------
    url : str
        Raw URL including scheme, e.g. "https://example.com/path"
    """
    t0 = time.time()

    # ── Step 1: feature extraction ────────────────────────────────────────────
    url_feats     = extract_url_features(url)
    content_feats = extract_content_features(url)
    all_feats     = {**url_feats, **content_feats}

    # ── Step 2: ML model ──────────────────────────────────────────────────────
    vector  = np.array([[all_feats[col] for col in _features]], dtype=float)
    proba   = _model.predict_proba(vector)[0]   # [P(phishing), P(legitimate)]
    p_phish = float(proba[0])
    p_legit = float(proba[1])

    # ── Step 2b: SHAP attribution ─────────────────────────────────────────────
    try:
        shap_exp = explain(_model, vector, _features)
    except Exception:
        shap_exp = None

    # ── Step 3: heuristic checks (parallel) ──────────────────────────────────
    signals = _run_heuristics(url)

    # ── Step 4: risk fusion ───────────────────────────────────────────────────
    fusion = fuse(p_phish, url_feats, content_feats, signals)
    risk   = fusion.final_score

    level, verdict_label = _verdict(risk)

    # ── Step 5: assemble result ───────────────────────────────────────────────
    return PredictionResult(
        url             = url,
        risk_score      = risk,
        phishing_prob   = p_phish,
        legitimate_prob = p_legit,
        risk_level      = level,
        verdict         = verdict_label,
        is_phishing     = risk >= 50,
        features        = all_feats,
        score_breakdown = fusion.breakdown(),
        heuristic_flags = _build_heuristic_flags(signals),
        shap_explanation= shap_exp,
        elapsed_sec     = round(time.time() - t0, 2),
    )