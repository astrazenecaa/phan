#!/usr/bin/env python3
"""
Ticket resale monitor - Dan and Phil: Hard Launch Tour, Melbourne (Palais
Theatre, Mon 23 Nov 2026).

Checks:
  - Tixel  (the event's actual resale marketplace)
  - Ticketmaster (verified resale, if you supply the event URL below)
  - Reddit (public search - people sometimes post "selling my ticket" there)

Sends a push notification via ntfy.sh the instant something new turns up.
Meant to run on a schedule (see .github/workflows/monitor.yml for a free
way to do that).

IMPORTANT LIMITATIONS - read this:
  - Tixel already has an official waitlist / auto-purchase feature on the
    event page. Set that up too (arguably more reliable than this script for
    Tixel specifically, since it's server-side and instant).
  - Twitter/X and Facebook are NOT covered here. Both actively block
    automated scraping and doing so risks your account / breaks their ToS.
    Facebook Marketplace has a native "save search + alert" feature - use
    that. For Twitter/X, a saved/bookmarked search you check manually a
    couple of times a day is the realistic option.
  - Don't drop the polling interval too low (below every few minutes) - it
    increases the chance a site starts blocking the requests entirely,
    which would defeat the point.
"""

import json
import os
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# CONFIG - edit these
# ---------------------------------------------------------------------------

TIXEL_URL = "https://tixel.com/au/comedy-tickets/2026/11/23/dan-and-phil-hard-launch-world-t"

# Ticketmaster event URLs are unstable/expire - paste the real one here
# yourself (search ticketmaster.com.au for "Dan and Phil Melbourne").
# Leave blank to skip this check.
TICKETMASTER_URL = ""  # e.g. "https://www.ticketmaster.com.au/event/1B0063A1B2C3D4E5"

REDDIT_QUERIES = [
    "Dan and Phil Melbourne ticket",
    "Dan and Phil VIP ticket",
    "Dan and Phil Hard Launch resale",
    "Dan and Phil meet and greet ticket",
]

# A Reddit post must contain at least one of EACH group below to count
REQUIRED_KEYWORDS = ["dan and phil", "hard launch"]
CONTEXT_KEYWORDS = ["melbourne", "vip", "gold", "meet"]

STATE_FILE = Path(__file__).parent / "seen.json"
USER_AGENT = "Mozilla/5.0 (ticket-monitor-script/1.0; personal use)"

# ---------------------------------------------------------------------------
# Notification (ntfy.sh - free, no account needed)
# ---------------------------------------------------------------------------

def send_notification(message: str) -> None:
    topic = os.environ.get("NTFY_TOPIC")

    if not topic:
        print("[!] NTFY_TOPIC env var missing - printing instead of notifying:")
        print(message)
        return

    resp = requests.post(
        f"https://ntfy.sh/{topic}",
        data=message.encode("utf-8"),
        headers={
            "Title": "Ticket lead found!",
            "Priority": "urgent",
            "Tags": "rotating_light",
        },
        timeout=15,
    )
    if resp.status_code >= 300:
        print(f"[!] ntfy error {resp.status_code}: {resp.text}")
    else:
        print("[+] Push notification sent")


# ---------------------------------------------------------------------------
# State - so you don't get texted about the same listing every 5 minutes
# ---------------------------------------------------------------------------

def load_seen() -> set:
    if STATE_FILE.exists():
        try:
            return set(json.loads(STATE_FILE.read_text()))
        except Exception:
            return set()
    return set()


def save_seen(seen: set) -> None:
    STATE_FILE.write_text(json.dumps(sorted(seen)))


# ---------------------------------------------------------------------------
# Checkers - each returns a list of (unique_id, alert_message) tuples
# ---------------------------------------------------------------------------

def check_tixel():
    hits = []
    try:
        r = requests.get(TIXEL_URL, headers={"User-Agent": USER_AGENT}, timeout=20)
        r.raise_for_status()
    except Exception as e:
        print(f"[!] Tixel fetch failed: {e}")
        return hits

    text = r.text
    # Tixel shows this exact prompt ONLY when there is nothing currently
    # listed for sale on the event page. If it's gone, a listing exists.
    if "see the tickets you want" in text:
        return hits

    soup = BeautifulSoup(text, "html.parser")
    snippet = soup.get_text(" ", strip=True)[:350]
    hits.append((
        "tixel-listing-live",
        f"TIXEL: a resale listing may be live right now!\n{snippet}\n{TIXEL_URL}",
    ))
    return hits


def check_ticketmaster():
    hits = []
    if not TICKETMASTER_URL:
        return hits
    try:
        r = requests.get(TICKETMASTER_URL, headers={"User-Agent": USER_AGENT}, timeout=20)
        r.raise_for_status()
    except Exception as e:
        print(f"[!] Ticketmaster fetch failed: {e}")
        return hits

    text = r.text.lower()
    if "resale" in text or "verified resale" in text:
        hits.append((
            "ticketmaster-resale",
            f"TICKETMASTER: resale tickets may be available!\n{TICKETMASTER_URL}",
        ))
    return hits


def check_reddit():
    hits = []
    for query in REDDIT_QUERIES:
        try:
            r = requests.get(
                "https://www.reddit.com/search.json",
                params={"q": query, "sort": "new", "limit": 15},
                headers={"User-Agent": USER_AGENT},
                timeout=20,
            )
            r.raise_for_status()
        except Exception as e:
            print(f"[!] Reddit search failed for '{query}': {e}")
            continue

        for post in r.json().get("data", {}).get("children", []):
            data = post.get("data", {})
            post_id = data.get("id")
            combined = f"{data.get('title', '')} {data.get('selftext', '')}".lower()

            if not any(k in combined for k in REQUIRED_KEYWORDS):
                continue
            if not any(k in combined for k in CONTEXT_KEYWORDS):
                continue

            url = "https://www.reddit.com" + data.get("permalink", "")
            hits.append((f"reddit-{post_id}", f"REDDIT: {data.get('title')}\n{url}"))
    return hits


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    seen = load_seen()

    all_hits = []
    all_hits += check_tixel()
    all_hits += check_ticketmaster()
    all_hits += check_reddit()

    new_hits = [(uid, msg) for uid, msg in all_hits if uid not in seen]

    for uid, msg in new_hits:
        print(f"[NEW] {msg}")
        send_notification(msg)
        seen.add(uid)

    if not new_hits:
        print("No new leads this run.")

    save_seen(seen)


if __name__ == "__main__":
    sys.exit(main())
