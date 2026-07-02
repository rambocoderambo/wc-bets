from collections import Counter, defaultdict


def calculate_metrics(bets):
    resolved = [b for b in bets if b.get("profit") is not None and b["profit"] is not None]
    total = len(resolved)
    stakes = [b["stake"] for b in resolved if b.get("stake")]
    profits = [b["profit"] for b in resolved]

    status_counts = Counter(b.get("status") for b in resolved)

    won = [b for b in resolved if b["status"] == "Won"]
    lost = [b for b in resolved if b["status"] == "Lost"]
    half_won = [b for b in resolved if b["status"] == "Half-won"]
    half_lost = [b for b in resolved if b["status"] == "Half-lost"]
    draws = [b for b in resolved if b["status"] == "Draw"]
    cashed = [b for b in resolved if b["status"] == "Cashed Out"]

    resolved_wl = [b for b in resolved if b["status"] in ("Won", "Lost", "Half-won", "Half-lost")]
    total_wl = len(resolved_wl)
    win_count = len([b for b in resolved_wl if b["status"] in ("Won", "Half-won")])
    loss_count = len([b for b in resolved_wl if b["status"] in ("Lost", "Half-lost")])

    win_pct = round(win_count / total_wl * 100, 1) if total_wl else 0
    loss_pct = round(loss_count / total_wl * 100, 1) if total_wl else 0
    push_pct = round(len(draws) / total * 100, 1) if total else 0
    cash_pct = round(len(cashed) / total * 100, 1) if total else 0

    best_bet = max(resolved, key=lambda b: b["profit"]) if resolved else None
    worst_loss = min(resolved, key=lambda b: b["profit"]) if resolved else None

    best_roi = max(
        [b for b in resolved if b["stake"] and b["stake"] > 0],
        key=lambda b: (b["profit"] / b["stake"])
    ) if resolved else None
    best_roi_pct = round(best_roi["profit"] / best_roi["stake"] * 100, 1) if best_roi else 0

    total_stake = round(sum(stakes), 2) if stakes else 0
    avg_stake = round(total_stake / len(stakes), 2) if stakes else 0
    total_pnl = round(sum(profits), 2) if profits else 0
    total_return = round(total_stake + total_pnl, 2) if total_stake is not None and total_pnl is not None else 0

    max_stake = max(stakes) if stakes else 0

    # Market breakdown
    market_stats = defaultdict(lambda: {"bets": 0, "pnl": 0, "wins": 0, "total": 0})
    for b in resolved:
        m = b.get("market", "Other")
        market_stats[m]["bets"] += 1
        market_stats[m]["pnl"] += b["profit"]
        if b["status"] == "Won":
            market_stats[m]["wins"] += 1
        market_stats[m]["total"] += 1

    # Team performance
    team_stats = defaultdict(lambda: {"bets": 0, "pnl": 0, "wins": 0, "losses": 0, "draws": 0})
    for b in resolved:
        team = _extract_team(b.get("bet", ""))
        if not team:
            continue
        team_stats[team]["bets"] += 1
        team_stats[team]["pnl"] += b["profit"]
        if b["status"] == "Won":
            team_stats[team]["wins"] += 1
        elif b["status"] == "Lost":
            team_stats[team]["losses"] += 1
        elif b["status"] == "Draw":
            team_stats[team]["draws"] += 1

    # Streak analysis
    streaks = _find_streaks(resolved)

    # Max drawdown
    cum = 0
    max_cum = 0
    min_cum = 0
    max_drawdown = 0
    for p in profits:
        cum += p
        max_cum = max(max_cum, cum)
        drawdown = max_cum - cum
        max_drawdown = max(max_drawdown, drawdown)
        min_cum = min(min_cum, cum)

    # Date range
    dated_bets = [b for b in bets if b.get("bet_date_parsed")]
    first_date = min(b["bet_date_parsed"] for b in dated_bets) if dated_bets else None
    last_date = max(b["bet_date_parsed"] for b in dated_bets) if dated_bets else None
    days_active = (last_date - first_date).days if first_date and last_date else 0

    # Daily turnover breakdown
    from collections import defaultdict as ddict
    daily = ddict(lambda: {"stake": 0, "bets": 0})
    for b in bets:
        if b.get("bet_date_parsed") and b.get("stake"):
            day = b["bet_date_parsed"].strftime("%a %d %b")
            daily[day]["stake"] += b["stake"]
            daily[day]["bets"] += 1

    return {
        "total_bets": total,
        "win_count": win_count,
        "loss_count": loss_count,
        "draw_count": len(draws),
        "cash_count": len(cashed),
        "win_pct": win_pct,
        "loss_pct": loss_pct,
        "push_pct": push_pct,
        "cash_pct": cash_pct,
        "best_bet": best_bet,
        "worst_loss": worst_loss,
        "best_roi": best_roi,
        "best_roi_pct": best_roi_pct,
        "total_stake": total_stake,
        "avg_stake": avg_stake,
        "max_stake": max_stake,
        "total_pnl": total_pnl,
        "total_return": total_return,
        "first_date": first_date.strftime("%d %b %Y") if first_date else "N/A",
        "last_date": last_date.strftime("%d %b %Y") if last_date else "N/A",
        "days_active": days_active,
        "daily_turnover": dict(daily),
        "market_stats": dict(market_stats),
        "team_stats": dict(team_stats),
        "streaks": streaks,
        "max_drawdown": round(max_drawdown, 2),
        "peak_cum": round(max_cum, 2),
        "low_cum": round(min_cum, 2),
    }


def _extract_team(bet_str):
    if not bet_str:
        return None
    parts = bet_str.split()
    if not parts:
        return None
    team_parts = []
    for p in parts:
        if p.startswith(("-", "+")) or p.replace(".", "").replace("/", "").isdigit():
            break
        team_parts.append(p)
    return " ".join(team_parts) if team_parts else parts[0]


def _find_streaks(bets):
    resolved = [b for b in bets if b.get("status") in ("Won", "Lost", "Half-won", "Half-lost")]
    current_streak = {"type": None, "count": 0, "pnl": 0}
    streaks = []
    for b in resolved:
        is_win = b["status"] in ("Won", "Half-won")
        is_loss = b["status"] in ("Lost", "Half-lost")

        if is_win:
            if current_streak["type"] == "win":
                current_streak["count"] += 1
                current_streak["pnl"] += b["profit"]
            else:
                if current_streak["count"] > 0:
                    streaks.append(dict(current_streak))
                current_streak = {"type": "win", "count": 1, "pnl": b["profit"]}
        elif is_loss:
            if current_streak["type"] == "loss":
                current_streak["count"] += 1
                current_streak["pnl"] += b["profit"]
            else:
                if current_streak["count"] > 0:
                    streaks.append(dict(current_streak))
                current_streak = {"type": "loss", "count": 1, "pnl": b["profit"]}

    if current_streak["count"] > 0:
        streaks.append(dict(current_streak))

    longest_win = max([s for s in streaks if s["type"] == "win"], key=lambda x: x["count"]) if any(s["type"] == "win" for s in streaks) else None
    longest_loss = max([s for s in streaks if s["type"] == "loss"], key=lambda x: x["count"]) if any(s["type"] == "loss" for s in streaks) else None

    return {
        "longest_win_streak": longest_win["count"] if longest_win else 0,
        "longest_win_pnl": round(longest_win["pnl"], 2) if longest_win else 0,
        "longest_loss_streak": longest_loss["count"] if longest_loss else 0,
        "longest_loss_pnl": round(longest_loss["pnl"], 2) if longest_loss else 0,
        "all_streaks": streaks,
    }
