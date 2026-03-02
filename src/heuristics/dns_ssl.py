"""
DNS Resolution & SSL Validation — PhishGuard
=============================================
Layer 3 dynamic checks:
  - DNS: verify the domain actually resolves (flags dead/fake domains)
  - SSL: verify a valid TLS handshake on port 443 (flags self-signed or missing certs)

Both checks use socket-level operations with tight timeouts so they
never block the prediction pipeline for more than a few seconds.
"""

import socket
import ssl
from dataclasses import dataclass
from urllib.parse import urlparse

import tldextract


_DNS_TIMEOUT = 4    # seconds
_SSL_TIMEOUT = 5    # seconds


@dataclass
class DNSResult:
    resolves:    bool          # True if DNS lookup succeeded
    ip_address:  str           # Resolved IP (empty if failed)
    error:       str           # Error message if failed


@dataclass
class SSLResult:
    valid:         bool        # True if TLS handshake succeeded with valid cert
    error:         str         # Error message if failed
    is_https:      bool        # Whether the URL uses HTTPS at all


def _extract_hostname(url: str) -> str:
    """Extract bare hostname from URL (strip port)."""
    parsed = urlparse(url)
    host   = parsed.hostname or ""
    return host


def check_dns(url: str) -> DNSResult:
    """
    Attempt to resolve the URL's hostname via DNS.

    A failure means the domain does not exist or is unreachable —
    a strong phishing/dead-link signal.
    """
    hostname = _extract_hostname(url)
    if not hostname:
        return DNSResult(resolves=False, ip_address="", error="No hostname extracted")

    try:
        socket.setdefaulttimeout(_DNS_TIMEOUT)
        infos = socket.getaddrinfo(hostname, None)
        ip = infos[0][4][0] if infos else ""
        return DNSResult(resolves=True, ip_address=ip, error="")
    except socket.gaierror as e:
        return DNSResult(resolves=False, ip_address="", error=str(e))
    except Exception as e:
        return DNSResult(resolves=False, ip_address="", error=str(e))
    finally:
        socket.setdefaulttimeout(None)


def check_ssl(url: str) -> SSLResult:
    """
    Attempt a TLS handshake against the domain on port 443.

    Rules:
      - If URL is HTTP (not HTTPS) → is_https=False, valid=False
      - If handshake succeeds with a valid certificate → valid=True
      - If certificate is invalid, expired, or connection refused → valid=False

    Note: we deliberately do NOT follow redirects here — we test the
    raw domain the URL points at.
    """
    parsed    = urlparse(url)
    is_https  = parsed.scheme == "https"
    hostname  = _extract_hostname(url)

    if not is_https:
        return SSLResult(valid=False, error="URL uses HTTP, not HTTPS",
                         is_https=False)

    if not hostname:
        return SSLResult(valid=False, error="No hostname", is_https=True)

    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=_SSL_TIMEOUT) as sock:
            with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                # If we got here, handshake succeeded and cert is valid
                return SSLResult(valid=True, error="", is_https=True)
    except ssl.SSLCertVerificationError as e:
        return SSLResult(valid=False, error=f"Cert verification failed: {e}",
                         is_https=True)
    except ssl.SSLError as e:
        return SSLResult(valid=False, error=f"SSL error: {e}", is_https=True)
    except ConnectionRefusedError:
        return SSLResult(valid=False, error="Connection refused on port 443",
                         is_https=True)
    except socket.timeout:
        return SSLResult(valid=False, error="SSL handshake timed out",
                         is_https=True)
    except Exception as e:
        return SSLResult(valid=False, error=str(e), is_https=True)
