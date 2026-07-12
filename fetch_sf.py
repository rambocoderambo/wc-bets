import cloudscraper, re
s = cloudscraper.create_scraper()
headers = {"User-Agent": "Mozilla/5.0"}
r = s.get("https://asianbookie.com/index.cfm/World-Cup/?league=4&tz=8", headers=headers, timeout=30)
html = r.text
print(f"Status: {r.status_code}, Size: {len(html)}")

# Find the SF matches in the 1X2 section
for team1, team2 in [("France","Spain"),("England","Argentina")]:
    pattern = team1 + r"\s*\n\s*vs\s*\n\s*" + team2
    m = re.search(pattern, html)
    if m:
        print(f"\n{team1} vs {team2}: FOUND")
        around = html[m.start()-200:m.end()+800]
        dates = re.findall(r"(\d{2}/\w{3}\s+\d{2}:\d{2})", around)
        print(f"  Date: {dates[0] if dates else '?'}")
        print(f"  Date raw: {dates}")
        odds = re.findall(r'id="[d]+\_[A-F0-9]+">([\d.]+)', around)
        print(f"  1X2 odds: {odds}")

# Search for AH data - look for the table after the AH header
ah_start = html.find('">Asian Handicap</th>') 
if ah_start < 0:
    ah_start = html.find("Asian Handicap")
if ah_start > 0:
    print(f"\nAH section found at {ah_start}")
    section = html[ah_start:ah_start+8000]
    # Save for inspection
    with open("ah_data.html","w",encoding="utf-8") as f:
        f.write(section)
    # Find all numbers that look like odds (x.xxx format)
    odds_nums = re.findall(r'([\d]+\.[\d]{3})', section)
    print(f"  Odds values: {odds_nums[:20]}")
    
    # Try a broader match for lines
    lines = re.findall(r'(\d+\s*:\s*\d+/\d+|\d+\s*:\s*\d+|\d+/\d+\s*:\s*\d+)', section)
    print(f"  Handicap lines: {lines[:10]}")
else:
    print("No AH section found")
