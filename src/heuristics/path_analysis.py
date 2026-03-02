"""
Suspicious Path & TLD Analysis — PhishGuard
============================================
Static heuristics that fire purely on URL structure — no network needed.

PathResult flags:
  - long_path           : path longer than 75 chars
  - many_params         : more than 4 query parameters
  - random_token        : random-looking alphanumeric segment (token, UUID)
  - encoded_chars       : excessive %XX encoding in path/query
  - deep_path           : more than 4 nested directories
  - suspicious_extension: .exe .zip .bat .ps1 etc. in the path

TLDResult flags:
  - is_suspicious_tld   : TLD is commonly abused for phishing

IPSubdomainResult:
  - has_ip_in_subdomain : IPv4 address embedded as subdomain
    (e.g. 192.168.0.1.secure-site.com — evades IsDomainIP check)

KeywordResult:
  - has_suspicious_keywords : phishing keywords found in domain/path
  - found_keywords          : list of matched keywords
  - keyword_count           : total count

PunycodeResult:
  - has_punycode  : xn-- IDN domain found (potential homograph attack)
  - punycode_parts: which hostname labels are encoded
"""

import re
from dataclasses import dataclass, field
from urllib.parse import urlparse, parse_qs

import tldextract


# ── Suspicious TLD list ───────────────────────────────────────────────────────
SUSPICIOUS_TLDS = {
    "tk", "ml", "ga", "cf", "gq",
    "xyz", "top", "click", "loan", "online", "site", "win",
    "party", "racing", "stream", "download", "gdn", "accountant",
    "date", "faith", "review", "trade", "webcam", "cricket",
    "science", "work", "ninja", "space", "pw", "cc",
}

# ── Phishing keywords commonly found in phishing domains / paths ──────────────
_PHISHING_KEYWORDS = {
    # Auth flows
    "login", "signin", "sign-in", "logon", "log-in", "logout",
    "signup", "register",
    # Verification / confirmation
    "verify", "verification", "validate", "validation",
    "confirm", "confirmation", "authenticate", "auth",
    # Security theatre words
    "secure", "security", "ssl", "safe", "protected",
    # Account / credential
    "account", "accounts", "credential", "credentials",
    "password", "passwd", "pwd", "recover", "recovery",
    # Action pressure words
    "update", "upgrade", "renew", "restore", "reactivate",
    "suspend", "suspended", "limited", "limit", "locked",
    "unlock", "unblock", "alert",
    # Financial / banking
    "bank", "banking", "payment", "pay", "billing", "invoice",
    "checkout", "wallet", "upi", "netbanking",
    # Support lures
    "support", "helpdesk", "service", "customer",
    # Webmail / phishing paths
    "webscr", "cmd",
    # Action words in path
    "activate", "access",
}

# ── Regex patterns ─────────────────────────────────────────────────────────────
_RANDOM_TOKEN_RE = re.compile(
    r"(?:"
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
    r"|[0-9a-zA-Z]{20,}"
    r"|[0-9]{6,}"
    r")",
    re.IGNORECASE,
)
_ENCODED_CHAR_RE  = re.compile(r"%[0-9A-Fa-f]{2}")
# Matches an IPv4 address appearing anywhere in the hostname
_IP_IN_HOST_RE    = re.compile(
    r"(?:^|\.)(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(?:\.|$)"
)
# Word splitter for keyword detection
_WORD_SPLIT_RE    = re.compile(r"[^a-z0-9]")

_SUSPICIOUS_EXTS = {
    ".exe", ".zip", ".bat", ".ps1", ".vbs", ".js",
    ".msi", ".dmg", ".pkg", ".deb", ".rpm", ".sh",
    ".apk", ".rar", ".7z", ".tar", ".gz",
}

_LONG_PATH_CHARS  = 75
_MAX_PARAMS       = 4
_MAX_DEPTH        = 4
_ENCODED_RATIO    = 0.1


# ── Result dataclasses ────────────────────────────────────────────────────────

@dataclass
class PathResult:
    long_path:             bool = False
    many_params:           bool = False
    random_token:          bool = False
    encoded_chars:         bool = False
    deep_path:             bool = False
    suspicious_extension:  bool = False
    flags:                 list = field(default_factory=list)

    @property
    def is_suspicious(self) -> bool:
        return any([self.long_path, self.many_params, self.random_token,
                    self.encoded_chars, self.deep_path, self.suspicious_extension])


@dataclass
class TLDResult:
    tld:               str
    is_suspicious_tld: bool


@dataclass
class IPSubdomainResult:
    has_ip_in_subdomain: bool
    detected_ip:         str = ""


@dataclass
class KeywordResult:
    has_suspicious_keywords: bool
    found_keywords:          list = field(default_factory=list)
    keyword_count:           int  = 0


@dataclass
class PunycodeResult:
    has_punycode:    bool
    punycode_parts:  list = field(default_factory=list)


# ── Check functions ───────────────────────────────────────────────────────────

def check_path(url: str) -> PathResult:
    """Analyse URL path and query string for suspicious patterns."""
    parsed = urlparse(url)
    path   = parsed.path or ""
    query  = parsed.query or ""
    flags  = []

    long_path = len(path) > _LONG_PATH_CHARS
    if long_path:
        flags.append(f"long_path({len(path)} chars)")

    params      = parse_qs(query)
    many_params = len(params) > _MAX_PARAMS
    if many_params:
        flags.append(f"many_params({len(params)})")

    random_token = bool(_RANDOM_TOKEN_RE.search(path + "/" + query))
    if random_token:
        flags.append("random_token")

    encoded_count = len(_ENCODED_CHAR_RE.findall(url))
    encoded_chars = encoded_count / max(len(url), 1) > _ENCODED_RATIO
    if encoded_chars:
        flags.append(f"encoded_chars({encoded_count})")

    depth     = len([p for p in path.split("/") if p])
    deep_path = depth > _MAX_DEPTH
    if deep_path:
        flags.append(f"deep_path(depth={depth})")

    path_lower = path.lower()
    susp_ext   = any(path_lower.endswith(ext) for ext in _SUSPICIOUS_EXTS)
    if susp_ext:
        flags.append("suspicious_extension")

    return PathResult(
        long_path=long_path, many_params=many_params,
        random_token=random_token, encoded_chars=encoded_chars,
        deep_path=deep_path, suspicious_extension=susp_ext,
        flags=flags,
    )


def check_tld(url: str) -> TLDResult:
    """Check whether the URL's TLD is in the commonly-abused list."""
    ext = tldextract.extract(url)
    tld = ext.suffix.lower().lstrip(".")
    top = tld.split(".")[-1]
    is_susp = top in SUSPICIOUS_TLDS or tld in SUSPICIOUS_TLDS
    return TLDResult(tld=tld, is_suspicious_tld=is_susp)


def check_ip_subdomain(url: str) -> IPSubdomainResult:
    """
    Detect an IPv4 address embedded inside the subdomain portion of a URL.

    Attackers use this to make phishing URLs look like they target a known
    host, e.g.  http://192.168.0.1.secure-login-update.com/verify

    This is different from IsDomainIP (which checks if the *registered*
    domain is a bare IP address like http://192.168.1.1/admin).
    """
    hostname = urlparse(url).hostname or ""
    match    = _IP_IN_HOST_RE.search(hostname)
    if match:
        return IPSubdomainResult(has_ip_in_subdomain=True,
                                 detected_ip=match.group(1))
    return IPSubdomainResult(has_ip_in_subdomain=False)


def check_keywords(url: str) -> KeywordResult:
    """
    Detect phishing-indicative keywords in the domain (subdomain + sld)
    and the URL path.

    Only inspects the hostname and path — not the TLD or scheme — to
    avoid false-positives (e.g. 'secure' in 'secure.example.com' is
    suspicious; 'secure' in 'security.gov' hostname is less so but we
    still score it because the full context matters).
    """
    parsed   = urlparse(url)
    hostname = (parsed.hostname or "").lower()
    path     = (parsed.path or "").lower()

    ext        = tldextract.extract(url)
    # Only check subdomain + domain label (not the TLD itself)
    search_str = f"{ext.subdomain}.{ext.domain}".lower() + " " + path
    words      = set(_WORD_SPLIT_RE.split(search_str))

    found = sorted(words & _PHISHING_KEYWORDS)
    return KeywordResult(
        has_suspicious_keywords = len(found) > 0,
        found_keywords          = found,
        keyword_count           = len(found),
    )


def check_punycode(url: str) -> PunycodeResult:
    """
    Detect Punycode / Internationalized Domain Name (IDN) labels.

    xn-- prefixed labels are used in homograph attacks:
    e.g.  http://xn--google-7hd.com  (looks like goog|e.com)
    Any presence of xn-- in the hostname is an immediate red flag.
    """
    hostname     = (urlparse(url).hostname or "").lower()
    labels       = hostname.split(".")
    puny_labels  = [l for l in labels if l.startswith("xn--")]
    return PunycodeResult(
        has_punycode   = len(puny_labels) > 0,
        punycode_parts = puny_labels,
    )

