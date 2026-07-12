"""Scrape AsianBookie World Cup odds using cloudscraper."""
import cloudscraper, re, json

scraper = cloudscraper.create_scraper()

# Try the classic ColdFusion view with proper headers
url = "https://asianbookie.com/index.cfm/World-Cup/?league=4&tz=8"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Cookie": "classic=1; tz=8"
}

r = scraper.get(url, headers=headers, timeout=30)
html = r.text
print(f"Status: {r.status_code}, Length: {len(html)}")

# Save for inspection
with open("ab_sf.html", "w", encoding="utf-8") as f:
    f.write(html)

# Find all date patterns
dates = re.findall(r'(\d{2}/\w{3}\s+\d{2}:\d{2})', html)
print(f"\nDates found: {len(dates)}")
for d in dates[:20]:
    print(f"  {d}")

# Find any team names near dates
for d in dates[:20]:
    idx = html.find(d)
    # Look for team names after the date
    chunk = html[idx:idx+500]
    # Find links with team names
    teams = re.findall(r'<a[^>]*>([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)</a>', chunk)
    if teams:
        print(f"  {d}: teams={teams[:4]}")

# Also try main page with classic
url2 = "https://asianbookie.com/?classic=1&tz=8"
r2 = scraper.get(url2, headers=headers, timeout=30)
html2 = r2.text
# Find World Cup section
wc_idx = html2.find("World Cup")
if wc_idx > 0:
    section = html2[wc_idx:wc_idx+30000]
    dates2 = re.findall(r'(\d{2}/\w{3}\s+\d{2}:\d{2})', section)
    print(f"\nMain page World Cup dates: {len(dates2)}")
    for d in dates2[:10]:
        print(f"  {d}")
        idx2 = section.find(d)
        chunk2 = section[idx2:idx2+400]
        teams2 = re.findall(r'<a[^>]*>([\w\s]+)</a>', chunk2)
        print(f"    teams: {[t.strip() for t in teams2 if t.strip()][:4]}")
else:
    print("\nNo World Cup section on main page")
