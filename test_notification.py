import os
import requests

topic = os.environ.get("NTFY_TOPIC")

if not topic:
    print("[!] NTFY_TOPIC env var is missing - check your GitHub secret.")
    raise SystemExit(1)

resp = requests.post(
    f"https://ntfy.sh/{topic}",
    data="This is a test - if you got this, notifications are working!".encode("utf-8"),
    headers={
        "Title": "Test notification",
        "Priority": "urgent",
        "Tags": "white_check_mark",
    },
    timeout=15,
)

if resp.status_code >= 300:
    print(f"[!] ntfy error {resp.status_code}: {resp.text}")
    raise SystemExit(1)
else:
    print("[+] Test notification sent successfully")
