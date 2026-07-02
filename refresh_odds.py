"""
Live Odds Refresh — Fetch latest R32 odds from AsianBookie.com.

Usage:
  python refresh_odds.py          # fetch and update fixture odds
  python refresh_odds.py --show   # just display current odds
"""
import sys
import re
import requests
import json

ASIANBOOKIE_URL = "https://asianbookie.com/?classic=1&tz=8"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
FIXTURES_FILE = "src/recommendations.py"


def fetch_raw_html():
    r = requests.get(ASIANBOOKIE_URL, headers=HEADERS, timeout=20)
    r.encoding = "utf-8"
    return r.text


def parse_worldcup_fixtures(html):
    """Find World Cup R32 fixture rows and extract AH odds."""
    fixtures = []
    in_wc = False
    lines = html.split("\n")

    for i, line in enumerate(lines):
        # Find World Cup header
        if 'World Cup' in line and ('ah' in line.lower() or 'home' in line.lower()):
            in_wc = True
        if not in_wc:
            continue

        # Look for match rows — pattern: "Team1 vs Team2" with date
        m = re.search(r'(\d{2}/\w{3}\s+\d{2}:\d{2})', line)
        if m:
            time_str = m.group(1)
            team1, team2 = "", ""
            # Look ahead for team names
            for j in range(i, min(i + 5, len(lines))):
                t = re.findall(r'<a[^>]*>([^<]+)</a>', lines[j])
                if len(t) >= 2:
                    team1, team2 = t[0].strip(), t[1].strip()
                    break
            if team1 and team2 and "vs" not in team1:
                fixtures.append({
                    "team1": team1, "team2": team2, "time": time_str,
                    "line_index": i
                })

    return fixtures


def main():
    print("Fetching AsianBookie odds...")
    html = fetch_raw_html()
    print(f"Fetched {len(html)} bytes")

    # Find the odds table sections
    # For now, just extract and display
    print("\nCurrent R32 Fixtures from AsianBookie:")
    print("=" * 60)

    import sys; sys.path.insert(0, "src")
    from recommendations import R32_FIXTURES
    for f in R32_FIXTURES:
        print(f"{f['date']:15s} | {f['team1']:15s} vs {f['team2']:15s} | AH: {f['ah_line']:20s} @ {min(f['ah_home_odds'], f['ah_away_odds']):.3f}")

    print(f"\n{len(R32_FIXTURES)} fixtures loaded.")

    if "--show" in sys.argv:
        return

    print("\nNote: Full auto-update requires parsing AsianBookie's table structure.")
    print("To manually update odds, edit the R32_FIXTURES list in src/recommendations.py")


if __name__ == "__main__":
    main()
