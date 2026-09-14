#!/usr/bin/env python3
"""
Frisco Bowl Weekly Stats Report
--------------------------------
Pulls the latest NFL weekly stats (via nflverse / nfl_data_py) for a curated
list of "notable Frisco Bowl alumni" and posts a formatted summary to a
Discord channel via webhook.

Designed to run every Monday via GitHub Actions (see .github/workflows/monday_report.yml)
or any other scheduler (cron, Railway, etc.)

ENV VARS REQUIRED:
    DISCORD_WEBHOOK_URL   - webhook URL for the target Discord channel
    SUPABASE_URL          - your Supabase project URL
    SUPABASE_KEY          - Supabase anon/service key (read access to notable_players)

Optional:
    SEASON                - override season year (defaults to current year)
"""

import os
import sys
import datetime
import requests
import nfl_data_py as nfl

# ---------------------------------------------------------------------------
# 1. CONFIG
# ---------------------------------------------------------------------------
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
SEASON = int(os.environ.get("SEASON", datetime.datetime.now().year))


def get_notable_players():
    """Fetch the notable-player list from the Supabase `notable_players` table."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("SUPABASE_URL / SUPABASE_KEY not set — no players to report on.")
        return []

    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/notable_players",
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
        },
        params={"select": "player_name"},
    )
    resp.raise_for_status()
    return [row["player_name"] for row in resp.json()]

STAT_COLUMNS = [
    "passing_yards", "passing_tds", "interceptions",
    "rushing_yards", "rushing_tds",
    "receptions", "receiving_yards", "receiving_tds",
]


def get_latest_week_stats():
    """Load this season's weekly player stats and return only the most recent week."""
    df = nfl.import_weekly_data([SEASON])
    if df.empty:
        return df, None
    latest_week = df["week"].max()
    return df[df["week"] == latest_week], latest_week


def build_player_report(df, latest_week, notable_players):
    if not notable_players:
        return (
            "⚠️ No players configured yet. Add rows to the `notable_players` "
            "table in Supabase."
        )

    subset = df[df["player_display_name"].isin(notable_players)]

    if subset.empty:
        return (
            f"No stats found for tracked Frisco Bowl alumni in Week {latest_week}. "
            f"(They may have been on bye, inactive, or the name list needs updating.)"
        )

    lines = [f"**🏈 Frisco Bowl Alumni Report — Week {latest_week}, {SEASON}**\n"]

    for _, row in subset.iterrows():
        name = row["player_display_name"]
        team = row.get("recent_team", "FA")
        pos = row.get("position", "")

        stat_bits = []
        if row.get("passing_yards", 0):
            stat_bits.append(
                f"{int(row['passing_yards'])} pass yds, "
                f"{int(row.get('passing_tds', 0))} TD, "
                f"{int(row.get('interceptions', 0))} INT"
            )
        if row.get("rushing_yards", 0):
            stat_bits.append(
                f"{int(row['rushing_yards'])} rush yds, "
                f"{int(row.get('rushing_tds', 0))} TD"
            )
        if row.get("receiving_yards", 0) or row.get("receptions", 0):
            stat_bits.append(
                f"{int(row.get('receptions', 0))} rec, "
                f"{int(row.get('receiving_yards', 0))} yds, "
                f"{int(row.get('receiving_tds', 0))} TD"
            )

        stat_line = "; ".join(stat_bits) if stat_bits else "No stats recorded (DNP/inactive)"
        lines.append(f"• **{name}** ({pos}, {team}) — {stat_line}")

    return "\n".join(lines)


def post_to_discord(content):
    if not DISCORD_WEBHOOK_URL:
        print("DISCORD_WEBHOOK_URL not set — printing report instead:\n")
        print(content)
        return

    # Discord messages cap at 2000 chars; split if needed
    chunks = [content[i:i + 1900] for i in range(0, len(content), 1900)] or [content]
    for chunk in chunks:
        resp = requests.post(DISCORD_WEBHOOK_URL, json={"content": chunk})
        resp.raise_for_status()


def main():
    notable_players = get_notable_players()

    df, latest_week = get_latest_week_stats()
    if df.empty:
        post_to_discord(f"No NFL weekly data available yet for {SEASON}.")
        return

    report = build_player_report(df, latest_week, notable_players)
    post_to_discord(report)


if __name__ == "__main__":
    main()
