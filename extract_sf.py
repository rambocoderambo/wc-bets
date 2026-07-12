"""Extract SF match data properly."""
import re

with open("ab_sf.html", "r", encoding="utf-8") as f:
    html = f.read()

# Split HTML into sections: 1X2, AH, O/U
# The page has these sections in order: 1X2, AH, O/U

# Find all matches in the 1X2 section
# Pattern: match IDs are in timetd1x2_XXXX
match_ids = re.findall(r'timetd1x2_([A-F0-9]+)', html)
print(f"Match IDs found: {len(match_ids)}")
for mid in match_ids:
    # Find the match data
    idx = html.find(f"timetd1x2_{mid}")
    section = html[idx:idx+800].replace("\n", "|")
    
    # Extract date
    date_m = re.search(r'(\d{2}/\w{3}\s+\d{2}:\d{2})', section)
    date = date_m.group(1) if date_m else "?"
    
    # Extract team names
    teams_m = re.search(r'(\w+)\s*\|\s*vs\s*\|\s*(\w+)', section)
    t1 = teams_m.group(1) if teams_m else "?"
    t2 = teams_m.group(2) if teams_m else "?"
    
    # Extract 1X2 odds
    o1 = re.search(r'id="d1_'+mid+r'">([\d.]+)', html)
    ox = re.search(r'id="d2_'+mid+r'">([\d.]+)', html)
    o2 = re.search(r'id="d3_'+mid+r'">([\d.]+)', html)
    
    print(f"\n{t1} vs {t2} | {date}")
    print(f"  1X2: {t1} {o1.group(1) if o1 else '?'} / Draw {ox.group(1) if ox else '?'} / {t2} {o2.group(1) if o2 else '?'}")

# Now find AH and O/U data by looking at the AH/O/U tables
# The AH table has columns: Home | Handicap | Away | Over | Total | Under
# Match rows in AH are: <tr><td class="xone/xtwo">[home_odds]</td><td>[handicap]</td><td>[away_odds]</td><td colspan="2">[over_odds] [total] [under_odds]</td></tr>

# Find the AH section
ah_idx = html.find("Asian Handicap")
ou_idx = html.find("Over/Under")
if ah_idx > 0 and ou_idx > 0:
    ah_section = html[ah_idx:ou_idx]
    # Find all matches in AH section
    ah_matches = re.findall(r'class="(?:xone|xtwo)"[^>]*>([\d.]+)</td>\s*<td[^>]*>([\d\s:/]+)</td>\s*<td[^>]*>([\d.]+)</td>\s*<td[^>]*>([\d.]+)</td>\s*<td[^>]*>([\d\s/]+)</td>\s*<td[^>]*>([\d.]+)</td>', ah_section, re.DOTALL)
    print(f"\nAH matches found: {len(ah_matches)}")
    for m in ah_matches:
        home_odds, hdp, away_odds, over_odds, total, under_odds = m
        print(f"  Odds: {home_odds} | Line: {hdp.strip()} | {away_odds} | O/U: {over_odds} / {total.strip()} / {under_odds}")
        # Find team names for this match (search backward from this position in ah_section)
        match_start = ah_section.find(home_odds)
        search_area = ah_section[max(0,match_start-500):match_start]
        teams = re.findall(r'>(\w+)\s*</span>\s*</td>\s*<td[^>]*>\s*<span', search_area)
        if teams:
            print(f"  Teams: {teams}")
