#!/usr/bin/env python3
"""Check the visitor-analytics backend the same way check-backend.py checks leads.

Reads js/config.js and confirms, using only the public publishable key:
  * `agartha_events` exists and accepts the columns js/analytics.js sends
  * the publishable key can INSERT an event (a real pageview row) ...
  * ... but is still refused any READ (row-level security is insert-only)

Unlike check-backend.py this DOES write one row (events are disposable, unlike
leads), then leaves it — it is a real, harmless pageview to /__healthcheck.
Run it after deploying to prove the tracker's write path is live.

    python scripts/check-analytics.py
"""

import json
import os
import re
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Columns js/analytics.js posts for a pageview.
PAYLOAD_COLUMNS = ["event_type", "path", "referrer", "referrer_host", "session_id",
                   "visitor_id", "is_new_visitor", "device", "browser", "screen_w",
                   "lang", "utm_source", "utm_medium", "utm_campaign"]


def config():
    text = open(os.path.join(ROOT, "js", "config.js"), encoding="utf-8").read()
    url = re.search(r'url:\s*"([^"]+)"', text).group(1)
    key = re.search(r'key:\s*"([^"]+)"', text).group(1)
    return url, key


def call(url, key, path, method="GET", body=None, prefer="return=minimal"):
    req = urllib.request.Request(
        url + path, method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"apikey": key, "Authorization": "Bearer " + key,
                 "Content-Type": "application/json", "Prefer": prefer})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except Exception as e:
        return None, str(e)


def main():
    url, key = config()
    print(f"project: {url}")
    print(f"key:     {key[:16]}… (publishable)")
    failures = []

    # 1. Reads must come back empty — the key is insert-only.
    status, body = call(url, key, "/rest/v1/agartha_events?select=*&limit=2")
    if status is None:
        failures.append(f"cannot reach the project: {body}")
    elif status == 200 and body.strip() in ("[]", ""):
        print("reads:   blocked by RLS (empty result) — correct")
    elif status in (401, 403):
        print(f"reads:   refused with HTTP {status} — correct")
    else:
        failures.append(f"the publishable key could READ events: HTTP {status} {body[:200]}")

    # 2. A column that does not exist must be rejected by name (PGRST204).
    status, body = call(url, key, "/rest/v1/agartha_events", "POST",
                        {"definitely_not_a_column": "probe"})
    if status == 400 and "PGRST204" in body:
        print("table:   agartha_events reachable, schema cache live")
    elif status is None:
        failures.append(f"cannot reach the table: {body}")
    else:
        failures.append(f"unexpected reply to the bogus-column probe: HTTP {status} {body[:200]}")

    # 3. The real payload shape must INSERT (events are meant to be written).
    probe = {c: None for c in PAYLOAD_COLUMNS}
    probe["event_type"] = "pageview"
    probe["path"] = "/__healthcheck"
    probe["device"] = "desktop"
    probe["is_new_visitor"] = False
    probe["screen_w"] = 0
    status, body = call(url, key, "/rest/v1/agartha_events", "POST", probe)
    if status in (200, 201, 204):
        print(f"insert:  all {len(PAYLOAD_COLUMNS)} event columns accepted — write path live")
    elif status == 400 and "PGRST204" in body:
        failures.append(f"a column analytics.js posts is missing: {body[:200]}")
    else:
        failures.append(f"the pageview probe did not insert: HTTP {status} {body[:200]}")

    if failures:
        print("\nPROBLEM(S):")
        for f in failures:
            print("  " + f)
        return 1
    print("\nAnalytics backend healthy: the tracker can log events, nobody else can read them.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
