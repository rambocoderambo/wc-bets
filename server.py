"""
Betting Dashboard Server
Serves the dashboard + handles bet logging and odds refresh via POST.

Usage:
  python server.py
  -> Open http://localhost:5000
"""
import sys
import os
import json
import subprocess
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
BETS_FILE = os.path.join(BASE_DIR, "Bets.txt")  # root file


def rebuild():
    """Run main.py to regenerate the dashboard."""
    main_py = os.path.join(BASE_DIR, "main.py")
    result = subprocess.run(
        [sys.executable, main_py],
        capture_output=True, text=True, cwd=os.path.dirname(main_py)
    )
    return result.stdout + result.stderr


def find_next_purchase_id():
    """Find next Purchase Ticket ID."""
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


@app.route("/")
def index():
    path = os.path.join(OUTPUT_DIR, "dashboard.html")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read(), 200, {"Content-Type": "text/html; charset=utf-8"}
    return "Dashboard not built yet. Run main.py first.", 404


@app.route("/chart")
def chart():
    path = os.path.join(OUTPUT_DIR, "cumulative_pnl.html")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read(), 200, {"Content-Type": "text/html; charset=utf-8"}
    return "Chart not found", 404


@app.route("/api/log-bet", methods=["POST"])
def log_bet():
    data = request.json
    required = ["team", "odds", "stake", "status"]
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    team = data["team"]
    odds = float(data["odds"])
    stake = float(data["stake"])
    status = data["status"]
    market = data.get("market", "FT Asian Handicap")
    event = data.get("event", team.split()[0] + " vs Opponent")
    result = data.get("result", "0:0")

    if status in ("Won", "Half-won"):
        ret = round(stake * odds, 2)
    elif status == "Cashed Out":
        ret = float(data.get("cashout_return", 0))
    else:
        ret = 0.0

    pid = find_next_purchase_id()
    tid = pid + 1
    now = datetime.now().strftime("%Y/%m/%d %H:%M")

    lines = [
        "",
        f"Purchase Ticket ID:{pid}",
        f"Bet Ticket ID:{tid}",
        f"Bet Date:{now}",
        f"Bet:{team}",
        "Odds:",
        f" {odds:.2f} EU",
        "Bet Type:",
        f" {market}",
        f"Event:{event}",
        "Event Date:" + now,
        "League:World Cup 2026",
        "Stake:",
        f" {stake:.2f} MYR",
        "Return:",
        f" {ret:.2f} MYR",
        f"Status:{status}",
        f"Result:{result}",
    ]

    with open(BETS_FILE, "a") as f:
        f.write("\n".join(lines) + "\n")

    rebuild()
    return jsonify({"ok": True, "pid": pid, "message": f"{team} logged"}), 200


@app.route("/api/refresh-odds", methods=["POST"])
def refresh_odds():
    rebuild()
    return jsonify({"ok": True, "message": "Dashboard refreshed"}), 200


@app.route("/live")
def live():
    """Generate and serve the live R32 report."""
    import sys
    sys.path.insert(0, os.path.join(BASE_DIR, "src"))
    from parser import parse_bets
    from metrics import calculate_metrics
    from analysis import generate_analysis, generate_advice
    from recommendations import generate_recommendations
    from r32_report import generate_live_report
    from visualize import generate_chart

    bets = parse_bets(os.path.join(BASE_DIR, "data", "Bets.txt"))
    metrics = calculate_metrics(bets)
    chart_path = os.path.join(OUTPUT_DIR, "cumulative_pnl.html")
    if not os.path.exists(chart_path):
        generate_chart(bets, chart_path)
    analysis = generate_analysis(bets, metrics)
    advice = generate_advice(bets, metrics, analysis)
    recommendations = generate_recommendations(bets, metrics)
    output = os.path.join(OUTPUT_DIR, "live_r32.html")
    generate_live_report(bets, metrics, analysis, advice, recommendations, chart_path, output)
    with open(output, "r", encoding="utf-8") as f:
        return f.read(), 200, {"Content-Type": "text/html; charset=utf-8"}


@app.route("/api/parse-bulk", methods=["POST"])
def parse_bulk():
    data = request.json
    raw = data.get("raw", "").strip()
    if not raw:
        return jsonify({"error": "No data provided"}), 400

    # Try to parse compressed Format 2 entries first
    cleaned, count = _parse_compressed_format2(raw)

    if count > 0:
        # Append them in Format 1
        for b in cleaned:
            pid = find_next_purchase_id()
            tid = pid + 1
            bdate = b.get("bet_date", datetime.now().strftime("%Y/%m/%d %H:%M"))
            bet_line = b.get('bet_line', (b.get('team', '') + ' ' + b.get('handicap', '')).strip())
            odd_val = float(b['odds']) if b.get('odds') else 0.0
            stake_val = float(b['stake']) if b.get('stake') else 0.0
            profit_val = float(b.get('profit', 0))
            ret_val = stake_val + profit_val
            lines = [
                "",
                f"Purchase Ticket ID:{pid}",
                f"Bet Ticket ID:{tid}",
                f"Bet Date:{bdate}",
                f"Bet:{bet_line}",
                "Odds:",
                f" {odd_val:.2f} EU",
                "Bet Type:",
                " FT Asian Handicap",
                f"Event:{b.get('event', 'Unknown vs Unknown')}",
                "Event Date:" + bdate,
                "League:World Cup 2026",
                "Stake:",
                f" {stake_val:.2f} MYR",
                "Return:",
                f" {ret_val:.2f} MYR",
                f"Status:{b.get('status_raw', 'Won')}",
            ]
            with open(BETS_FILE, "a", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")

        shutil.copy2(BETS_FILE, os.path.join(BASE_DIR, "data", "Bets.txt"))
        rebuild()
        return jsonify({"ok": True, "message": f"{count} bet(s) saved from Format 2 data. Dashboard rebuilt."}), 200

    # Fallback: try standard parser via temp file
    import tempfile, shutil
    tmp = os.path.join(BASE_DIR, "temp_bulk.txt")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(raw)

    import sys
    sys.path.insert(0, os.path.join(BASE_DIR, "src"))
    from parser import parse_bets as pb

    parsed = pb(tmp)
    os.remove(tmp)

    if parsed:
        for b in parsed:
            pid = find_next_purchase_id()
            tid = pid + 1
            bdate = b.get("bet_date", datetime.now().strftime("%Y/%m/%d %H:%M"))
            lines = [
                "",
                f"Purchase Ticket ID:{pid}",
                f"Bet Ticket ID:{tid}",
                f"Bet Date:{bdate}",
                f"Bet:{b.get('bet', 'Unknown')}",
                "Odds:",
                f" {b.get('odds', 1):.2f} EU",
                "Bet Type:",
                f" {b.get('bet_type_raw', 'FT Asian Handicap')}",
                f"Event:{b.get('event', 'Unknown vs Unknown')}",
                "Event Date:" + bdate,
                "League:World Cup 2026",
                "Stake:",
                f" {b.get('stake', 0):.2f} MYR",
                "Return:",
                f" {b.get('return', 0):.2f} MYR",
                f"Status:{b.get('status', 'Won')}",
            ]
            result_val = b.get("result")
            if result_val and result_val != "-":
                lines.append(f"Result:{result_val}")
            with open(BETS_FILE, "a", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")

        shutil.copy2(BETS_FILE, os.path.join(BASE_DIR, "data", "Bets.txt"))
        rebuild()
        msg = f"{len(parsed)} bet(s) parsed and saved. Dashboard rebuilt."
        return jsonify({"ok": True, "message": msg}), 200
    else:
        with open(BETS_FILE, "a", encoding="utf-8") as f:
            if not raw.endswith("\n"):
                raw += "\n"
            f.write("\n" + raw)
        shutil.copy2(BETS_FILE, os.path.join(BASE_DIR, "data", "Bets.txt"))
        rebuild()
        return jsonify({
            "ok": True,
            "message": "Raw text saved to Bets.txt. Dashboard rebuilt.",
            "warning": "Format not recognized — data was saved as raw. Check Bets.txt for formatting."
        }), 200



def _parse_compressed_format2(raw):
    """Parse compressed Format 2 where fields are concatenated on one line."""
    import re
    clean = re.sub(r"^.*?(?=\d*ID:\d{18})", "", raw)
    entries = re.split(r"(?=\d+ID:\d{18})", clean)
    entries = [e.strip() for e in entries if re.search(r"ID:\d{18}", e)]
    results = []
    for e in entries:
        try:
            mid = re.search(r"ID:(\d{18})", e)
            if not mid: continue
            dates = re.findall(r"\d{1,2}/\d{1,2}/\d{4}\s+\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM)?", e)
            bet_date = dates[0] if len(dates) > 0 else ""
            event_date = dates[1] if len(dates) > 1 else ""
            if not bet_date: continue

            sm = re.search(r"Soccer\s*/\s*Handicap", e)
            if not sm: continue
            after_sport = e[sm.end():]
            hm = re.search(r"([-+]\d+(?:\.\d+)?)", after_sport)
            if not hm: continue
            team_name = after_sport[:hm.start()].strip()
            hcp = hm.group(1)
            bet_line = f"{team_name} {hcp}".strip()

            rest = after_sport[hm.end():]
            starm = re.search(r"\*", rest)
            if not starm: continue
            after_star = rest[starm.end():]

            if event_date:
                league = after_star.split(event_date)[0].strip()
            else:
                league = after_star.strip()

            known = ["France","Norway","Spain","Uruguay","Sweden","England",
                     "Brazil","Argentina","Portugal","Netherlands","Mexico",
                     "Canada","USA","Colombia","Croatia","Germany","Belgium",
                     "Morocco","Japan","Senegal","DR Congo"]
            team2 = ""
            for t in known:
                if t in after_star and t != team_name:
                    team2 = t
                    break
            event = f"{team_name} vs {team2}" if team2 else ""

            om = re.search(r"(\d+\.\d+)\s*Dec", e)
            if not om: continue
            odds = float(om.group(1))
            after_dec = e[om.end():]
            # Strip status text from end
            for st_label in ["Half Won","Half Lost","Cashed Out","Won","Lost","Draw","Push"]:
                if after_dec.endswith(st_label):
                    status = st_label
                    after_dec = after_dec[:-len(st_label)]
                    break
            else:
                status = "Won"
            # after_dec is now just numbers like "10076.00"
            # Profit has decimal, stake is integer — split at last decimal
            # Try to split stake + profit: profit has 2 decimals, stake is integer
            # Check possible split points by verifying profit/stake ~= odds-1
            best_stake, best_profit = 0, 0.0
            best_diff = 999.0
            for split_pos in range(1, len(after_dec)):
                try:
                    candidate_stake = float(after_dec[:split_pos])
                    candidate_profit = float(after_dec[split_pos:])
                except:
                    continue
                if candidate_profit <= 0 or candidate_stake <= 0:
                    continue
                expected_profit = candidate_stake * (odds - 1)
                # For half-wins, profit might be half of expected
                diff = min(abs(candidate_profit - expected_profit),
                           abs(candidate_profit - expected_profit / 2))
                if diff < best_diff:
                    best_diff = diff
                    best_stake = candidate_stake
                    best_profit = candidate_profit
            if best_stake > 0 and best_diff < 5:
                stake = best_stake
                profit = best_profit
            else:
                stake, profit = 0, 0.0

            results.append({
                "id": mid.group(1), "bet_date": bet_date, "event_date": event_date,
                "bet_line": bet_line, "team": team_name, "handicap": hcp,
                "odds": odds, "stake": stake, "profit": profit,
                "status_raw": status, "event": event,
            })
        except Exception as exc:
            continue
    return results, len(results)

if __name__ == "__main__":
    print("Starting Betting Dashboard Server...")
    print("Open http://localhost:5000 in your browser")
    app.run(host="0.0.0.0", port=5000, debug=True)
