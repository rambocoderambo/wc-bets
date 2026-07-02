from collections import defaultdict


def get_h2h(bets, team1, team2):
    """Return head-to-head stats between two teams from bet data."""
    matches = []
    for b in bets:
        evt = b.get("event", "")
        result = b.get("result", "")
        if not result or " vs " not in evt:
            continue
        parts = evt.split(" vs ")
        if len(parts) != 2:
            continue
        t1, t2 = parts[0].strip(), parts[1].strip()
        if {t1, t2} == {team1, team2}:
            score_parts = result.split(":")
            if len(score_parts) == 2:
                try:
                    g1 = int(score_parts[0].strip())
                    g2 = int(score_parts[1].strip())
                except ValueError:
                    continue
                t1_win = g1 > g2
                t2_win = g2 > g1
                drawn = g1 == g2
                if t1 == team1:
                    winner = team1 if t1_win else team2 if t2_win else "Draw"
                    t1_goals = g1
                    t2_goals = g2
                else:
                    winner = team2 if t1_win else team1 if t2_win else "Draw"
                    t1_goals = g2
                    t2_goals = g1
                matches.append({
                    "team1_score": t1_goals,
                    "team2_score": t2_goals,
                    "winner": winner,
                    "date": b.get("bet_date", "")[:10],
                })

    # Deduplicate by date (multiple bets on same match)
    seen = set()
    unique = []
    for m in matches:
        key = (m["date"], m["team1_score"], m["team2_score"])
        if key not in seen:
            seen.add(key)
            unique.append(m)

    team1_wins = sum(1 for m in unique if m["winner"] == team1)
    team2_wins = sum(1 for m in unique if m["winner"] == team2)
    draws = sum(1 for m in unique if m["winner"] == "Draw")

    return {
        "team1": team1,
        "team2": team2,
        "team1_wins": team1_wins,
        "team2_wins": team2_wins,
        "draws": draws,
        "matches": unique,
    }
