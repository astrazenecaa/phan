# Dan and Phil Melbourne ticket monitor

Watches for resale/reselling leads for the Gold VIP Meet & Greet ticket
(Dan and Phil, Hard Launch Tour, Palais Theatre Melbourne, Mon 23 Nov 2026)
and pushes a notification to your phone the moment something new turns up.

## What it checks
- **Tixel** - the event's actual resale marketplace. Flags the moment ANY
  listing goes live on the page (it can't tell ticket types apart, so
  you'll need to check within seconds whether it's the Gold VIP one).
- **Ticketmaster** verified resale (optional - you need to paste in the
  exact event URL yourself, see below).
- **Reddit** - public search for people mentioning selling a ticket.

## What it does NOT cover (and why)
- **Twitter/X** - reliable automated search now needs a paid API tier.
  Recommendation: save a search on X for "dan and phil melbourne ticket"
  and check it manually a couple of times a day.
- **Facebook** - scraping Facebook risks your account and rarely works
  reliably. Recommendation: use Facebook Marketplace's own "Save search"
  feature (it has a built-in alert option) and join any Dan & Phil /
  Melbourne gig-swap Facebook groups and turn on notifications for them.
- Tixel's own official waitlist/auto-purchase - worth joining as a backup
  layer even though it can't filter by "Gold VIP" specifically.

## One-time setup (about 10 minutes)

### 1. Put this code on GitHub (free)
1. Create a free GitHub account if you don't have one: https://github.com/signup
2. Create a new **private** repository (e.g. `ticket-monitor`).
3. Upload all the files in this folder to it, keeping the folder structure
   (the `.github/workflows/monitor.yml` file must stay in that exact path).
4. Create one more file in the repo called `seen.json` containing just:
   `[]`

### 2. Get push notifications working (ntfy, free, no account needed)
1. Install the **ntfy** app on your phone (search "ntfy" on the App Store
   or Google Play) - or just use https://ntfy.sh in a browser tab you leave
   open.
2. Pick a "topic" name - this is just a shared channel name, and it works
   like a secret URL, so make it long and hard to guess (e.g.
   `danphil-melb-vip-x7q2f9`), NOT something short like "tickets".
3. In the app, tap "+" and subscribe to that exact topic name.
4. That's it - no sign-up, no API keys.

### 3. Add your secret to GitHub
In your repo: **Settings → Secrets and variables → Actions → New repository
secret**. Add:
- `NTFY_TOPIC` — the topic name you picked above (e.g. `danphil-melb-vip-x7q2f9`)

### 4. Turn it on
The workflow runs automatically every ~5 minutes once it's on the default
branch. You can also trigger a run manually any time from the repo's
**Actions** tab → "Ticket Monitor" → "Run workflow", which is a good way to
confirm everything's wired up correctly before you walk away from it.

## Optional: add the exact Ticketmaster URL
Open `monitor.py` and paste the event's real Ticketmaster URL into
`TICKETMASTER_URL` (search ticketmaster.com.au for "Dan and Phil Melbourne"
to find it - the listing may still be pending as of when this was written).

## A couple of honest caveats
- Automated checking of ticket resale sites can bump into rate limiting or
  anti-bot measures if the interval is too aggressive - 5 minutes is a
  reasonable balance of speed vs. not getting blocked.
- This increases your odds of being fast, but it isn't a guarantee -
  someone could still buy a listing in the seconds between it appearing
  and you completing checkout.
