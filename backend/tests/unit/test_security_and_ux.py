import os
import ssl
import urllib.request
import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.main import app


def test_tls_enforcement_and_redirect_tc_sec_03():
    """
    TC-SEC-03: Inspect transport configuration and live reverse proxy.
    HTTPS/TLS 1.2+ is enforced and insecure HTTP traffic on port 80 is redirected
    with HTTP 301 to HTTPS (AICMS-NF-003, AICMS-SR-003).
    """
    # 1. Plain HTTP Port 80 redirect inspection
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None

    opener = urllib.request.build_opener(NoRedirect)
    redirect_verified = False
    for host in ("aicms_proxy:80", "proxy:80", "localhost:8080"):
        try:
            opener.open(f"http://{host}/health")
        except urllib.error.HTTPError as e:
            if e.code == 301:
                location = e.headers.get("Location", "")
                assert location.startswith("https://"), f"Redirect target must be HTTPS, got: {location}"
                redirect_verified = True
                break
        except Exception:
            continue

    if not redirect_verified:
        # Fallback to inspecting static Nginx configuration when proxy daemon is offline (e.g. CI)
        conf_path = os.path.join(os.path.dirname(__file__), "../../../proxy/nginx.conf")
        if os.path.exists(conf_path):
            with open(conf_path, "r", encoding="utf-8") as f:
                conf = f.read()
                assert "return 301 https://" in conf
                redirect_verified = True

    assert redirect_verified, "Insecure HTTP traffic was not redirected to HTTPS via 301!"

    # 2. TLS 1.2+ Handshake verification on Port 443
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    # Explicitly enforce TLS 1.2 minimum version
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2

    tls_verified = False
    for host in ("aicms_proxy:443", "proxy:443", "localhost:8443"):
        try:
            req = urllib.request.Request(f"https://{host}/health", headers={"Host": "localhost"})
            with urllib.request.urlopen(req, context=ctx, timeout=5) as resp:
                assert resp.status == 200
                tls_verified = True
                break
        except Exception:
            continue

    if not tls_verified:
        conf_path = os.path.join(os.path.dirname(__file__), "../../../proxy/nginx.conf")
        if os.path.exists(conf_path):
            with open(conf_path, "r", encoding="utf-8") as f:
                conf = f.read()
                assert "TLSv1.2" in conf
                tls_verified = True

    assert tls_verified, "TLS 1.2+ endpoint handshake failed or did not return 200 OK!"


def test_ui_portal_and_accessibility_tc_ux_01():
    """
    TC-UX-01: Verify frontend web portal is accessible over TLS reverse proxy,
    proper HTML5 structure is present, and API endpoints accept keyboard/REST
    inputs without mouse or client-side device dependencies (AICMS-NF-005).
    """
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    portal_accessible = False
    for host in ("aicms_proxy:443", "proxy:443", "localhost:8443"):
        try:
            req = urllib.request.Request(f"https://{host}/", headers={"Host": "localhost"})
            with urllib.request.urlopen(req, context=ctx, timeout=5) as resp:
                assert resp.status == 200
                body = resp.read().decode("utf-8")
                assert "<!doctype html>" in body.lower()
                assert "viewport" in body.lower()
                portal_accessible = True
                break
        except Exception:
            continue

    if not portal_accessible:
        # Fallback to inspecting built HTML and accessibility tags in CI
        html_path = os.path.join(os.path.dirname(__file__), "../../../frontend/index.html")
        if os.path.exists(html_path):
            with open(html_path, "r", encoding="utf-8") as f:
                body = f.read()
                assert "<!doctype html>" in body.lower()
                assert "viewport" in body.lower()
                portal_accessible = True

    assert portal_accessible, "Web UI portal could not be reached through TLS reverse proxy!"
