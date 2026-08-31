#!/usr/bin/env python3
"""Front-end security checks that generic scanners do not cover.

Semgrep and Trivy look at code and dependencies. Neither knows that this site
loads five scripts from a CDN, that a floating version range there means a
future release runs unreviewed on the admin page, or that a Content-Security-
Policy went missing from vercel.json. This checks the things specific to how
this site is actually served.

    python3 scripts/check-security.py

Exits non-zero on any finding, so CI fails.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = sorted(ROOT.glob("*.html"))

REQUIRED_HEADERS = {
    "X-Content-Type-Options",
    "X-Frame-Options",
    "Referrer-Policy",
    "Strict-Transport-Security",
    "Permissions-Policy",
}
# A CSP in either enforcing or report-only form satisfies the CSP requirement.
CSP_KEYS = {"Content-Security-Policy", "Content-Security-Policy-Report-Only"}

findings = []


def check_cdn_scripts():
    """Every external script must be version-pinned and carry SRI."""
    for page in PAGES:
        for tag in re.findall(r"<script\b[^>]*>", page.read_text()):
            src = re.search(r'src="(https?://[^"]+)"', tag)
            if not src:
                continue
            url = src.group(1)
            name = page.name
            # a floating major range means a future release lands unreviewed
            if re.search(r"@\d+/", url) or re.search(r"@(latest|next)\b", url):
                findings.append(f"{name}: unpinned CDN version -> {url}")
            if "integrity=" not in tag:
                findings.append(f"{name}: no SRI on {url}")
            elif "crossorigin=" not in tag:
                # SRI without CORS makes the browser refuse the script outright
                findings.append(f"{name}: integrity without crossorigin -> {url}")


def check_headers():
    cfg = json.loads((ROOT / "vercel.json").read_text())
    have = {h["key"] for rule in cfg.get("headers", []) for h in rule["headers"]}
    for key in sorted(REQUIRED_HEADERS - have):
        findings.append(f"vercel.json: missing security header {key}")
    if not (have & CSP_KEYS):
        findings.append("vercel.json: no Content-Security-Policy in any form")


def check_link_safety():
    """target=_blank without rel=noopener hands the opener to the new page."""
    for page in PAGES:
        for tag in re.findall(r'<a\b[^>]*target="_blank"[^>]*>', page.read_text()):
            if "noopener" not in tag:
                href = re.search(r'href="([^"]*)"', tag)
                findings.append(f"{page.name}: target=_blank without noopener -> "
                                f"{href.group(1) if href else tag[:60]}")


def check_no_service_key():
    """The publishable key is meant to be public; a service key never is."""
    for f in list(ROOT.glob("*.html")) + list((ROOT / "js").glob("*.js")):
        text = f.read_text()
        if "service_role" in text:
            findings.append(f"{f.name}: contains 'service_role' — never ship a service key")
        # a Supabase JWT-style secret has three base64 segments
        if re.search(r"eyJ[A-Za-z0-9_-]{20,}\.eyJ[A-Za-z0-9_-]{20,}\.", text):
            findings.append(f"{f.name}: looks like an embedded JWT")


def main() -> int:
    check_cdn_scripts()
    check_headers()
    check_link_safety()
    check_no_service_key()

    if findings:
        print(f"{len(findings)} finding(s):\n", file=sys.stderr)
        for f in findings:
            print(f"  {f}", file=sys.stderr)
        return 1
    print(f"clean — {len(PAGES)} pages: CDN scripts pinned with SRI, "
          f"security headers present, no unsafe _blank links, no service key")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
