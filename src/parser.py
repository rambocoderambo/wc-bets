import re
from datetime import datetime


def parse_bets(filepath="data/Bets.txt"):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    lines = text.split("\n")
    bets = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if not line:
            i += 1
            continue

        if line.startswith("Purchase Ticket ID:"):
            block = []
            while i < len(lines):
                stripped = lines[i].strip()
                if stripped.startswith("Purchase Ticket ID:") and len(block) > 0:
                    break
                block.append(lines[i])
                if stripped.startswith("Result:") or stripped == "":
                    i += 1
                    break
                i += 1
            bet = _parse_format1(block)
            if bet:
                bets.append(bet)
        elif re.match(r"^\d+$", line) and i + 1 < len(lines) and lines[i + 1].strip().startswith("ID:"):
            block = []
            while i < len(lines) and len(block) < 16:
                block.append(lines[i].strip())
                i += 1
            bet = _parse_format2(block)
            if bet:
                bets.append(bet)
        else:
            i += 1

    return bets


def _parse_format1(block):
    text = "\n".join(block)
    bet = {}

    bet["purchase_id"] = _extract_field(text, r"Purchase Ticket ID:\s*(\S+)")
    bet["ticket_id"] = _extract_field(text, r"Bet Ticket ID:\s*(\S+)")
    bet["bet_date"] = _extract_field(text, r"Bet Date:\s*(.+)")
    bet["bet"] = _extract_field(text, r"Bet:\s*(.+)")
    bet["bet_type_raw"] = _extract_field(text, r"Bet Type:\s*(.+)")
    bet["event"] = _extract_field(text, r"Event:\s*(.+)")
    bet["event_date"] = _extract_field(text, r"Event Date:\s*(.+)")
    bet["league"] = _extract_field(text, r"League:\s*(.+)")
    bet["status"] = _extract_field(text, r"Status:\s*(.+)")
    bet["result"] = _extract_field(text, r"Result:\s*(.+)")

    odds_match = re.search(r"Odds:\s*\n\s*([\d.]+)", text)
    bet["odds"] = float(odds_match.group(1)) if odds_match else None

    stake_match = re.search(r"Stake:\s*\n\s*([\d.]+)", text)
    bet["stake"] = float(stake_match.group(1)) if stake_match else None

    ret_match = re.search(r"Return:\s*\n\s*([\d.]+)", text)
    bet["return"] = float(ret_match.group(1)) if ret_match else None

    bonus_match = re.search(r"Bonus:\s*\n\s*([\d.]+)", text)
    bet["bonus"] = float(bonus_match.group(1)) if bonus_match else None

    bet["profit"] = round(bet["return"] - bet["stake"], 2) if bet["return"] is not None and bet["stake"] is not None else None
    # If bonus >= stake, the stake was free credits — user risked 0, so profit = return
    if bet.get("bonus") and bet["bonus"] > 0 and bet.get("stake"):
        if bet["bonus"] >= bet["stake"]:
            bet["profit"] = round(bet["return"], 2) if bet["return"] is not None else None
        else:
            # Partial bonus: effective stake = stake - bonus
            effective_stake = bet["stake"] - bet["bonus"]
            bet["profit"] = round(bet["return"] - effective_stake, 2) if bet["return"] is not None else None

    bet["market"] = _classify_market(bet.get("bet_type_raw", ""), bet.get("bet", ""))
    bet["source_format"] = 1

    _parse_dates(bet)

    return bet


def _parse_format2(block):
    if len(block) < 16:
        return None

    bet = {}
    bet["seq"] = block[0]
    bet["purchase_id"] = block[1].replace("ID:", "").strip()
    bet["bet_date"] = block[2]
    bet["code"] = block[3]
    bet["sport_market"] = block[4]
    bet["bet"] = f"{block[5]} {block[6]}"
    bet["bet_type_raw"] = block[4]
    bet["event"] = f"{block[8]} vs {block[9]}" if block[8] and block[9] else block[7]
    bet["league"] = block[7]
    bet["event_date"] = block[10]
    bet["result"] = None

    bet["odds"] = float(block[11]) if block[11] else None
    bet["stake"] = float(block[13]) if block[13] else None
    profit_val = float(block[14]) if block[14] else None

    status_map = {
        "Won": "Won", "Half Won": "Half-won", "Half Won ": "Half-won",
        "Lost": "Lost", "Half Lost": "Half-lost", "Half Lost ": "Half-lost",
        "Draw": "Draw", "Push": "Draw", "Cashed Out": "Cashed Out",
        "Cash Out": "Cashed Out"
    }
    bet["status"] = status_map.get(block[15].strip(), block[15].strip())

    bet["return"] = round(bet["stake"] + profit_val, 2) if bet["stake"] is not None and profit_val is not None else None
    bet["profit"] = profit_val
    bet["bonus"] = None
    bet["market"] = _classify_market(bet.get("bet_type_raw", ""), bet.get("bet", ""))
    bet["source_format"] = 2

    _parse_dates(bet)

    return bet


def _extract_field(text, pattern):
    match = re.search(pattern, text)
    return match.group(1).strip() if match else None


def _classify_market(bet_type_raw, bet_name):
    bt = bet_type_raw.lower() if bet_type_raw else ""
    bn = bet_name.lower() if bet_name else ""

    if "asian handicap" in bt or "ah" in bt.lower():
        if "live" in bt:
            return "Asian Handicap (Live)"
        return "FT Asian Handicap"
    if "o/u" in bt or "over" in bn or "under" in bn:
        if "live" in bt:
            return "O/U (Live)"
        return "FT O/U"
    if "1x2" in bt or "to qualify" in bt:
        return "1X2"
    if "live" in bt:
        if "handicap" in bt:
            return "Asian Handicap (Live)"
        return "Live"
    return "Other"


def _parse_dates(bet):
    for date_field in ["bet_date", "event_date"]:
        raw = bet.get(date_field)
        if not raw:
            continue
        raw = raw.strip()
        for fmt in ["%Y/%m/%d %H:%M", "%m/%d/%Y %I:%M:%S %p", "%Y/%m/%d %H:%M:%S", "%m/%d/%Y"]:
            try:
                bet[date_field + "_parsed"] = datetime.strptime(raw, fmt)
                break
            except ValueError:
                continue
        if date_field + "_parsed" not in bet:
            bet[date_field + "_parsed"] = None
