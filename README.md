# Frisco Bowl Weekly Stats Report

Posts a weekly (Monday) stats summary to Discord for a curated list of
notable Frisco Bowl alumni, using free NFL data from [nflverse](https://nflverse.nflverse.com/)
via the `nfl_data_py` package. No paid API key needed.

## How it works

- `frisco_bowl_report.py` pulls the most recent week of NFL player stats
  and filters to the names in `NOTABLE_PLAYERS`.
- `.github/workflows/monday_report.yml` runs that script every Monday
  via GitHub Actions and posts the result to a Discord webhook.

## Setup (15 minutes)

### 1. Create a new Supabase project
Go to [supabase.com](https://supabase.com) → **New project**. Pick any name
(e.g. `frisco-bowl-bot`), region, and password — you won't need the password
for this.

Once it's created:
- Go to **SQL Editor → New query**, paste in the contents of `supabase_schema.sql`,
  and click **Run**. This creates the `notable_players` table.
- Go to **Project Settings → API**. Copy the **Project URL** and the
  **anon public key** — you'll need both in step 3.

### 2. Add players to the table
In Supabase: **Table Editor → notable_players → Insert row**. Add each
player's exact NFL display name (must match nflverse's `player_display_name`
field — e.g. "Patrick Mahomes"), plus optional school/year notes.

If a name doesn't match later, check exact formatting locally:
```python
import nfl_data_py as nfl
players = nfl.import_players()
players[players['display_name'].str.contains("Mahomes", case=False)]
```

You can keep adding players here any time — no code changes or redeploys needed.

### 3. Create a Discord webhook
In your Discord server: **Channel Settings → Integrations → Webhooks → New Webhook**.
Copy the webhook URL.

### 4. Create a GitHub repo
Push this folder to a new (can be private) GitHub repo.

```bash
cd frisco-bowl-bot
git init
git add .
git commit -m "Frisco Bowl weekly report bot"
git remote add origin https://github.com/<you>/frisco-bowl-bot.git
git push -u origin main
```

### 5. Add secrets
In the repo: **Settings → Secrets and variables → Actions → New repository secret**.
Add all three:
- `DISCORD_WEBHOOK_URL` — from step 3
- `SUPABASE_URL` — Project URL from step 1
- `SUPABASE_KEY` — anon public key from step 1

### 6. Test it manually
Go to the repo's **Actions** tab → "Frisco Bowl Weekly Report" →
**Run workflow** to trigger it immediately without waiting for Monday.

### 7. Done
It will now run automatically every Monday at 9am Central, pull the current
player list from Supabase, and post to your Discord channel.

## Notes / next steps

- **Access control**: the Supabase table currently allows open read/write via
  the anon key (kept simple, matching what you asked for). If you later want
  it locked down like your DFR content calendar (admin-only edits), swap the
  RLS policy for an authenticated one and gate the Table Editor / a small
  admin UI behind a password, same pattern as before.
- **Building the notable-player list**: this ships with an empty table.
  If you want, the list can be built out from Frisco Bowl box scores/rosters
  for past games — that's a research task, separate from the bot plumbing.
- **Off-season handling**: `nfl_data_py` will simply return no data outside
  the season; the script handles that gracefully and posts a note instead of erroring.
- **Multiple leagues**: nflverse is NFL/NCAA-focused. If you want college
  stats specifically (since some alumni may still be in college), `nfl_data_py`
  also exposes `import_seasonal_rosters` and college data is more limited —
  let me know if you want that layered in.
