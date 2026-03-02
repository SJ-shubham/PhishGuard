"""
PhishGuard — URL Analyzer
==========================
Run from the project root:

  Single URL:
    python -X utf8 test_predict.py https://example.com

  Interactive mode (loop):
    python -X utf8 test_predict.py

  Default test batch:
    python -X utf8 test_predict.py --batch
"""

import sys
import os
import re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.predictor import predict
from src.explainer import save_waterfall_plot, save_heatmap_plot
from src.report    import generate_report

_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs", "shap")
_REPORT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs", "reports")

# ── ANSI colours ──────────────────────────────────────────────────────────────
RESET  = "\033[0m"
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
DIM    = "\033[2m"

_LEVEL_COLOR = {
    "Low":      GREEN,
    "Medium":   YELLOW,
    "High":     RED,
    "Critical": RED + BOLD,
}

# ── Built-in test batch ───────────────────────────────────────────────────────
_BATCH = [
    # Legitimate sites
    ("https://www.google.com",              "Legitimate"),
    ("https://www.github.com",              "Legitimate"),
    ("https://www.wikipedia.org",           "Legitimate"),
    ("https://www.kaggle.com",              "Legitimate"),
    ("https://www.geeksforgeeks.org",       "Legitimate"),
    # Classic phishing
    ("http://paypa1-secure-login.tk/verify","Phishing"),
    ("http://192.168.1.1/admin/login",      "Phishing"),
    ("http://g00gle-verify.xyz/update",     "Phishing"),
    # IP in subdomain
    ("http://192.168.0.1.secure-login-update.com/verify", "Phishing"),
    # Punycode / IDN
    ("http://xn--google-7hd.com",           "Phishing"),
]

# ── Display ───────────────────────────────────────────────────────────────────

def _bar(score: float, width: int = 30) -> str:
    filled = int(round(score / 100 * width))
    empty  = width - filled
    if score < 30:
        color = GREEN
    elif score < 50:
        color = YELLOW
    else:
        color = RED
    return f"{color}{'█' * filled}{'░' * empty}{RESET}"


def _print_result(result, expected: str = ""):
    cv = _LEVEL_COLOR.get(result.risk_level, RESET)
    feats = result.features
    bd    = result.score_breakdown
    hf    = result.heuristic_flags

    print()
    print(f"  {DIM}{'─' * 68}{RESET}")
    print(f"  URL      : {CYAN}{result.url}{RESET}")
    if expected:
        marker = GREEN + "OK" + RESET if (
            (expected == "Phishing") == result.is_phishing
        ) else RED + "WRONG" + RESET
        print(f"  Expected : {expected}  ({marker})")

    print(f"  Score    : {_bar(result.risk_score)}  {cv}{result.risk_score:.1f}/100{RESET}")
    print(f"  Risk     : {cv}{result.risk_level}  —  {result.verdict}{RESET}")
    print(f"  ML raw   : P(phish)={result.phishing_prob:.4f}  P(legit)={result.legitimate_prob:.4f}"
          f"  {DIM}(raw model output, before heuristic adjustment){RESET}")
    print(f"  Time     : {result.elapsed_sec}s")

    # ── Score breakdown ───────────────────────────────────────────────────────
    print()
    print(f"  {DIM}Score breakdown (raw/{150} -> normalized 0-100):{RESET}")
    print(f"  {DIM}Trust factor: {bd.get('trust_factor', 1.0):.2f}  (1.0=full ML weight, 0.4=all signals clean){RESET}")
    breakdown_items = [
        ("ML base (calibrated)", bd.get("ml_base", 0),            "/60"),
        ("Brand impersonation",  bd.get("brand_impersonation", 0), "/30"),
        ("IP-based URL",         bd.get("ip_based_url", 0),        "/30"),
        ("IP in subdomain",      bd.get("ip_in_subdomain", 0),     "/25"),
        ("Suspicious TLD",       bd.get("suspicious_tld", 0),      "/20"),
        ("Domain age",           bd.get("domain_age", 0),          "/20"),
        ("SSL failure",          bd.get("ssl_failure", 0),         "/15"),
        ("DNS failure",          bd.get("dns_failure", 0),         "/15"),
        ("Keyword signals",      bd.get("keyword_signals", 0),     "/15"),
        ("Punycode/IDN",         bd.get("punycode_idn", 0),        "/20"),
        ("Content indicators",   bd.get("content_indicators", 0),  "/20"),
    ]
    for label, val, cap in breakdown_items:
        color = RED if val > 0 else DIM
        print(f"    {label:<25} {color}{val:>6.2f}{RESET}{DIM}{cap}{RESET}")
    print(f"    {'Raw total':<25} {bd.get('raw_total', 0):>6.2f}/150")
    print(f"    {'Final score':<25} {bd.get('final_score', 0):>6.2f}/100")

    # ── Heuristic signals ─────────────────────────────────────────────────────
    print()
    print(f"  {DIM}Heuristic signals:{RESET}")
    signal_items = [
        ("DNS resolves",      hf.get("dns_resolves")),
        ("SSL valid",         hf.get("ssl_valid")),
        ("HTTPS",             hf.get("is_https")),
        ("Brand impersonation", hf.get("brand_impersonation")),
        ("Suspicious TLD",    hf.get("suspicious_tld")),
        ("Domain is new",     hf.get("domain_is_new")),
        ("Domain age (days)", hf.get("domain_age_days")),
        ("Domain created",    hf.get("domain_created")),
        ("Path suspicious",   hf.get("path_is_suspicious")),
        ("Path flags",        hf.get("path_flags")),
        ("IP in subdomain",   hf.get("ip_in_subdomain")),
        ("Suspicious keywords", hf.get("suspicious_keywords")),
        ("Found keywords",    hf.get("found_keywords")),
        ("Has punycode",      hf.get("has_punycode")),
    ]
    if hf.get("brand_impersonation"):
        signal_items += [
            ("  -> Matched brand", hf.get("brand_matched")),
            ("  -> Edit distance", hf.get("brand_distance")),
        ]
    if hf.get("ip_in_subdomain") and hf.get("detected_ip"):
        signal_items.append(("  -> Detected IP", hf.get("detected_ip")))
    if hf.get("has_punycode") and hf.get("punycode_parts"):
        signal_items.append(("  -> Punycode parts", hf.get("punycode_parts")))
    if not hf.get("ssl_valid") and hf.get("ssl_error"):
        signal_items.append(("  -> SSL error", hf.get("ssl_error")))
    for label, val in signal_items:
        if val is None:
            continue
        if isinstance(val, bool):
            color = (RED if val else GREEN) if label in (
                "Brand impersonation", "Suspicious TLD", "Domain is new",
                "Path suspicious", "IP in subdomain", "Suspicious keywords",
                "Has punycode",
            ) else (GREEN if val else RED)
            txt = f"{color}{val}{RESET}"
        else:
            txt = str(val)
        print(f"    {label:<25} {txt}")

    # ── Key ML features ───────────────────────────────────────────────────────
    print()
    print(f"  {DIM}Key ML features:{RESET}")
    show = [
        ("IsHTTPS",           feats.get("IsHTTPS")),
        ("IsDomainIP",        feats.get("IsDomainIP")),
        ("TLDLegitimateProb", round(feats.get("TLDLegitimateProb", 0), 4)),
        ("NoOfExternalRef",   feats.get("NoOfExternalRef")),
        ("NoOfSelfRef",       feats.get("NoOfSelfRef")),
        ("IsResponsive",      feats.get("IsResponsive")),
        ("HasDescription",    feats.get("HasDescription")),
        ("HasPasswordField",  feats.get("HasPasswordField")),
        ("HasSocialNet",      feats.get("HasSocialNet")),
        ("HasSubmitButton",   feats.get("HasSubmitButton")),
        ("HasCopyrightInfo",  feats.get("HasCopyrightInfo")),
        ("LineOfCode",        feats.get("LineOfCode")),
    ]
    for name, val in show:
        flag = GREEN + "1" + RESET if val == 1 else (
               RED   + "0" + RESET if val == 0 else str(val)
        )
        print(f"    {name:<25} {flag}")

    # ── SHAP attribution ──────────────────────────────────────────────────────
    shap_exp = result.shap_explanation
    if shap_exp:
        print()
        print(f"  {DIM}SHAP attribution (log-odds space):{RESET}")
        print(f"    Base value  : {shap_exp.base_value:+.4f}  (avg model output)")
        print(f"    Final value : {shap_exp.prediction_value:+.4f}")
        print()
        print(f"    {RED}Top phishing signals{RESET} (push P(legitimate) down):")
        for feat, val in shap_exp.top_risk_features[:6]:
            bar_w = int(abs(val) / 0.5 * 20)
            bar   = RED + "█" * min(bar_w, 20) + RESET
            print(f"      {feat:<28} {val:+.4f}  {bar}")
        print()
        print(f"    {GREEN}Top legitimate signals{RESET} (push P(legitimate) up):")
        for feat, val in shap_exp.top_safe_features[:6]:
            bar_w = int(abs(val) / 0.5 * 20)
            bar   = GREEN + "█" * min(bar_w, 20) + RESET
            print(f"      {feat:<28} {val:+.4f}  {bar}")


def _safe_filename(url: str) -> str:
    """Turn a URL into a safe filename stem."""
    name = re.sub(r"https?://", "", url)
    name = re.sub(r"[^\w\-.]", "_", name)
    return name[:60]


def _analyze(url: str, expected: str = ""):
    url = url.strip()
    # Auto-add scheme if missing
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    print(f"\n  Analyzing {CYAN}{url}{RESET} ...")
    try:
        result = predict(url)
        _print_result(result, expected)

        # Save SHAP plots if explanation is available
        wf_path = None
        if result.shap_explanation:
            stem    = _safe_filename(url)
            wf_path = os.path.join(_OUTPUT_DIR, f"{stem}_waterfall.png")
            hm_path = os.path.join(_OUTPUT_DIR, f"{stem}_heatmap.png")
            os.makedirs(_OUTPUT_DIR, exist_ok=True)
            save_waterfall_plot(result.shap_explanation, url, wf_path)
            save_heatmap_plot(result.shap_explanation, url, hm_path)
            print(f"\n  {DIM}SHAP plots saved:{RESET}")
            print(f"    Waterfall -> {wf_path}")
            print(f"    Heatmap   -> {hm_path}")

        # Generate PDF report
        report_path = generate_report(result, output_dir=_REPORT_DIR, shap_image=wf_path)
        print(f"\n  {DIM}PDF report saved:{RESET}")
        print(f"    {report_path}")

    except Exception as e:
        print(f"\n  {RED}Error: {e}{RESET}\n")


# ── Entrypoints ───────────────────────────────────────────────────────────────

def run_single(url: str):
    print()
    print("=" * 72)
    print("  PhishGuard — URL Analyzer")
    print("=" * 72)
    _analyze(url)
    print("=" * 72)
    print()


def run_batch():
    print()
    print("=" * 72)
    print("  PhishGuard — Default Test Batch")
    print("=" * 72)
    for url, expected in _BATCH:
        _analyze(url, expected)
    print("=" * 72)
    print()


def run_interactive():
    print()
    print("=" * 72)
    print("  PhishGuard — Interactive URL Analyzer")
    print("  Type a URL and press Enter.  Type 'exit' to quit.")
    print("=" * 72)
    while True:
        try:
            raw = input("\n  URL > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  Exiting.")
            break
        if not raw or raw.lower() in ("exit", "quit", "q"):
            print("  Exiting.")
            break
        _analyze(raw)


# ── Entry ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        run_interactive()
    elif args[0] == "--batch":
        run_batch()
    else:
        run_single(args[0])
