#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fetch the full Kanun list from https://www.mevzuat.gov.tr/Anasayfa/MevzuatDatatable
and dump it to mevzuat_kanun.json

Requirements:
    pip install requests
"""

from pathlib import Path
import json
import time
import requests

URL = "https://www.mevzuat.gov.tr/Anasayfa/MevzuatDatatable"

# ---------------------------------------------------------------------
# 1)  COPY‑PASTE **exactly** what you see in a working browser request
#     (these will eventually expire – see notes below).
# ---------------------------------------------------------------------
HEADERS = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Content-Type": "application/json; charset=UTF-8",
    "Origin": "https://www.mevzuat.gov.tr",
    "Referer": "https://www.mevzuat.gov.tr/",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
    ),
    "X-Requested-With": "XMLHttpRequest",
}

COOKIES = {
    ".AspNetCore.Antiforgery.Pk46jo02iDM": (
        "CfDJ8PCQ8f3V401KkEuh7WCYGAGaRsxhQrc40y4dzrtFRjp5uAraMpR-87iyW8QxXHwgfnGf6iAUSZj7"
        "w4hzRFR6rhn4mmEnauiitgCwmHfQChhYDJAgezsmVkYC67l8ZggRqgpiWTmQLP_eXHjkrKzsgHo"
    ),
    "_ga": "GA1.1.1072477466.1753783579",
    "_ga_K30R4B6KS2": "GS2.1.s1753851984$o5$g1$t1753853382$j59$l0$h0",
    ".AspNetCore.Mvc.CookieTempDataProvider": (
        "CfDJ8PCQ8f3V401KkEuh7WCYGAECcEGSI3h7mpd7bXJI0nlgBwvXe2Zb472k9qWVpDhQEChEtbGgEOWk"
        "6ZsEvT_Lx6p5Zzn-blhx-N0UA8rqsnpBjs3hjCoFDsMXPWioyobSX7UO4ZIp01KzBrZ7MO_GkPM"
    ),
}

# ---------------------------------------------------------------------
# 2)  The part of the body *other than* start/length/draw.
#     You usually only change these when the UI inputs change.
# ---------------------------------------------------------------------
COMMON_BODY = {
    "columns": [
        {"data": None, "name": "", "searchable": True, "orderable": False, "search": {"value": "", "regex": False}},
        {"data": None, "name": "", "searchable": True, "orderable": False, "search": {"value": "", "regex": False}},
        {"data": None, "name": "", "searchable": True, "orderable": False, "search": {"value": "", "regex": False}},
    ],
    "order": [],
    "search": {"value": "", "regex": False},
    "parameters": {
        "MevzuatTur": "Teblig",
        "YonetmelikMevzuatTur": "OsmanliKanunu",
        "AranacakIfade": "",
        "AranacakYer": "2",
        "MevzuatNo": "",
        "BaslangicTarihi": "",
        "BitisTarihi": "",
        # 👇 Antiforgery token must match the cookie value above
        "antiforgerytoken": "CfDJ8PCQ8f3V401KkEuh7WCYGAEdjjSD7oyW-rS_t5rkpMOECFUYk4XOLWw1pWhSx_6LQsKBQ0nqc-__ROaMpAY19IfsAUTn-ZNRO0jDRXg0pwGxFeyO3IkeDHj0sU5oMdRojXINzuiDR03NS4k03EMtsiA",
    },
}

# Choose a larger page size to cut down on round‑trips; the server currently
# tolerates 200 just fine.  Use 10 if you prefer to mimic the UI exactly.
PAGE_SIZE = 200
OUTFILE = Path("mevzuat_Teblig.json")

def fetch_page(session: requests.Session, start: int, draw: int) -> dict:
    body = {
        **COMMON_BODY,
        "draw": draw,
        "start": start,
        "length": PAGE_SIZE,
    }
    resp = session.post(URL, headers=HEADERS, cookies=COOKIES, json=body, timeout=30)
    resp.raise_for_status()
    return resp.json()

def main() -> None:
    session = requests.Session()
    all_rows = []
    draw = 1
    start = 0

    while True:
        data = fetch_page(session, start=start, draw=draw)
        rows = data.get("data", [])
        if not rows:              # no more results – stop
            break

        all_rows.extend(rows)
        print(f"Fetched {len(rows):>3} rows (total {len(all_rows):>4}) [start={start}]")

        # Last page will be shorter than PAGE_SIZE
        if len(rows) < PAGE_SIZE:
            break

        start += PAGE_SIZE
        draw += 1
        time.sleep(0.6)           # be polite; the site is public

    # Persist to disk
    OUTFILE.write_text(json.dumps(all_rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSaved {len(all_rows)} records ➜ {OUTFILE.resolve()}")

if __name__ == "__main__":
    main()

