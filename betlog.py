"""
Bet Logger — Add a new bet to Bets.txt and regenerate the dashboard.

Usage:
  python betlog.py                          # interactive mode
  python betlog.py --quick "France -1.5" 1.85 50 Lost  # quick mode
"""
import sys
import os
from datetime import datetime

BETS_FILE = "data/Bets.txt"


def find_last_purchase_id():
    """Find the highest Purchase Ticket ID in the file."""
    import re
    max_id = 1000000000000000000
    try:
        with open(BETS_FILE, "r") as f:
            for line in f:
                m = re.search(r"Purchase Ticket ID:(\d+)", line)
                if m:
                    tid = int(m.group(1))
                    if tid > max_id:
                        max_id = tid
    except FileNotFoundError:
        pass
    return max_id + 1


def append_bet(bet):
    """Append a bet dict to Bets.txt in Format 1."""
    pid = find_last_purchase_id()
    tid = pid + 1
    now = datetime.now().strftime("%Y/%m/%d %H:%M")

    lines = [
        "",
        f"Purchase Ticket ID:{pid}",
        f"Bet Ticket ID:{tid}",
        f"Bet Date:{now}",
        f"Bet:{bet['team']}",
        "Odds:",
        f" {bet['odds']:.2f} EU",
        "Bet Type:",
        f" {bet['market']}",
        f"Event:{bet['event']}",
        "Event Date:" + now,
        "League:World Cup 2026",
        "Stake:",
        f" {bet['stake']:.2f} MYR",
        "Return:",
        f" {bet['return']:.2f} MYR",
        f"Status:{bet['status']}",
        f"Result:{bet['result']}",
    ]

    with open(BETS_FILE, "a") as f:
        f.write("\n".join(lines) + "\n")

    print(f"Bet logged: {bet['team']} @ {bet['odds']} | Stake MYR {bet['stake']} | {bet['status']}")
    return pid, tid


def interactive():
    print("=== New Bet Logger ===\n")
    team = input("Team (e.g. France -1.5): ").strip()
    odds = float(input("Odds (decimal): ").strip())
    stake = float(input("Stake (MYR): ").strip())
    status = input("Status (Won/Lost/Half-won/Half-lost/Draw/Cashed Out): ").strip().title()
    market = input("Market (e.g. FT Asian Handicap, FT O/U): ").strip() or "FT Asian Handicap"
    event = input("Event (e.g. France vs Sweden): ").strip() or team.split()[0] + " vs Opponent"
    result = input("Result (e.g. 2:0): ").strip() or "0:0"

    if status in ("Won", "Half-won"):
        ret = round(stake * odds, 2)
    elif status == "Cashed Out":
        ret = round(float(input("Cash out return (MYR): ").strip()), 2)
    else:
        ret = 0.0

    bet = {
        "team": team, "odds": odds, "stake": stake,
        "return": ret, "status": status,
        "market": market, "event": event, "result": result,
    }
    append_bet(bet)
    print("\nRegenerating dashboard...")
    import main
    main.main()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        # Quick mode: betlog.py --quick "France -1.5" 1.85 50 Lost
        team = sys.argv[2]
        odds = float(sys.argv[3])
        stake = float(sys.argv[4])
        status = sys.argv[5].title()
        market = sys.argv[6] if len(sys.argv) > 6 else "FT Asian Handicap"
        event = sys.argv[7] if len(sys.argv) > 7 else team.split()[0] + " vs Opponent"
        result = sys.argv[8] if len(sys.argv) > 8 else "0:0"
        ret = round(stake * odds, 2) if status in ("Won", "Half-won") else 0.0
        bet = {"team": team, "odds": odds, "stake": stake, "return": ret,
               "status": status, "market": market, "event": event, "result": result}
        append_bet(bet)
        import main; main.main()
    else:
        interactive()
