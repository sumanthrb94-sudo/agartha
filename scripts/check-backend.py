#!/usr/bin/env python3
"""Check the lead-capture backend without writing a row.

Reads the same config the site uses (js/config.js) and confirms:
  * the Supabase project answers and the publishable key authenticates
  * `agartha_leads` exists and accepts exactly the columns the forms send
  * row-level security still refuses to hand that key any data back

Every probe is deliberately made to fail at type-coercion time, so nothing
lands in the table.

    python scripts/check-backend.py
"""

import json
import os
import re
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The columns js/main.js posts for a lead.
PAYLOAD_COLUMNS = ["form_type", "source_page", "first_name", "last_name",
                   "email", "phone", "preferred_date", "message"]


def config():
    text = open(os.path.join(ROOT, "js", "config.js"), encoding="utf-8").read()
    url = re.search(r'url:\s*"([^"]+)"', text).group(1)
    key = re.search(r'key:\s*"([^"]+)"', text).group(1)
    return url, key


def call(url, key, path, method="GET", body=None):
    req = urllib.request.Request(
        url + path, method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"apikey": key, "Authorization": "Bearer " + key,
                 "Content-Type": "application/json", "Prefer": "return=minimal"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except Exception as e:  # network down, DNS, TLS
        return None, str(e)


def main():
    url, key = config()
    print(f"project: {url}")
    print(f"key:     {key[:16]}… (publishable)")
    failures = []

    # 1. Reads must come back empty — the key is insert-only.
    status, body = call(url, key, "/rest/v1/agartha_leads?select=*&limit=2")
    if status is None:
        failures.append(f"cannot reach the project: {body}")
    elif status == 200 and body.strip() in ("[]", ""):
        print("reads:   blocked by RLS (empty result) — correct")
    elif status in (401, 403):
        print(f"reads:   refused with HTTP {status} — correct")
    else:
        failures.append(f"the publishable key could READ data: HTTP {status} {body[:200]}")

    # 2. A column that does not exist must be rejected by name (PGRST204).
    status, body = call(url, key, "/rest/v1/agartha_leads", "POST",
                        {"definitely_not_a_column": "probe"})
    if status == 400 and "PGRST204" in body:
        print("table:   agartha_leads reachable, schema cache live")
    elif status is None:
        failures.append(f"cannot reach the table: {body}")
    else:
        failures.append(f"unexpected reply to the bogus-column probe: "
                        f"HTTP {status} {body[:200]}")

    # 3. The real payload shape, forced to fail on date coercion. Reaching the
    #    date error proves every other column name resolved.
    probe = {c: "probe" for c in PAYLOAD_COLUMNS}
    probe["preferred_date"] = "not-a-date"
    probe["email"] = "probe@example.com"
    status, body = call(url, key, "/rest/v1/agartha_leads", "POST", probe)
    if status == 400 and '"22007"' in body:
        print(f"columns: all {len(PAYLOAD_COLUMNS)} lead columns exist "
              "(insert reached type-coercion and stopped)")
    elif status in (200, 201, 204):
        failures.append("the probe INSERTED A ROW — check and delete it")
    elif status == 400 and "PGRST204" in body:
        failures.append(f"a column the forms post is missing: {body[:200]}")
    else:
        failures.append(f"unexpected reply to the payload probe: "
                        f"HTTP {status} {body[:200]}")

    if failures:
        print("\nPROBLEM(S):")
        for f in failures:
            print("  " + f)
        return 1
    print("\nBackend healthy: forms can insert, nothing else.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
