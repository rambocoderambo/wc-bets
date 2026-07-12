import sys; sys.path.insert(0, "src")
from parser import parse_bets
from metrics import calculate_metrics
from recommendations import generate_recommendations

bets = parse_bets("data/Bets.txt")
m = calculate_metrics(bets)
recs = generate_recommendations(bets, m)

for r in recs:
    if "SF:" in r.get("stage", ""):
        sr = r.get("score_reason", "")
        print(f"=== {r['team1']} vs {r['team2']} ===\n")
        print(sr)
        print()
