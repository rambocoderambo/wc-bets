def generate_analysis(bets, metrics):
    lines = []

    # 1. Over-staking analysis
    high_stakes = [b for b in bets if b.get("stake") and b["stake"] >= 100]
    high_stake_pct = round(len(high_stakes) / metrics["total_bets"] * 100, 1) if metrics["total_bets"] else 0
    high_stake_pnl = round(sum(b["profit"] for b in high_stakes if b.get("profit") is not None), 2)
    bankroll_equiv = round(100 / metrics["avg_stake"] * 100, 1) if metrics["avg_stake"] else 0

    lines.append({
        "icon": "over-staking",
        "title": "Over-staking on single bets",
        "body": (
            f"You placed {len(high_stakes)} bets of MYR 100+, representing {high_stake_pct}% "
            f"of all bets. These large bets combined for MYR {high_stake_pnl} P&L. "
            f"A single MYR 100 loss represents {bankroll_equiv}% of your average bet size — "
            f"too much concentration risk."
        )
    })

    # 2. Chasing losses detection
    resolved = [b for b in bets if b.get("status") in ("Won", "Lost", "Half-won", "Half-lost")]
    resolved_sorted = sorted(
        [b for b in resolved if b.get("bet_date_parsed")],
        key=lambda b: b["bet_date_parsed"]
    )

    chase_events = []
    i = 0
    while i < len(resolved_sorted):
        if resolved_sorted[i]["status"] in ("Lost", "Half-lost"):
            streak_start = i
            while i < len(resolved_sorted) and resolved_sorted[i]["status"] in ("Lost", "Half-lost"):
                i += 1
            streak_end = i - 1
            streak_len = streak_end - streak_start + 1

            if streak_len >= 2 and streak_end + 1 < len(resolved_sorted):
                next_bet = resolved_sorted[streak_end + 1]
                team_lost = _extract_team_name(resolved_sorted[streak_start].get("bet", ""))
                team_next = _extract_team_name(next_bet.get("bet", ""))
                if team_lost and team_next and team_lost.lower() == team_next.lower():
                    chase_events.append({
                        "streak_len": streak_len,
                        "team": team_lost,
                        "streak_pnl": round(sum(b["profit"] for b in resolved_sorted[streak_start:streak_end + 1]), 2),
                        "next_stake": next_bet.get("stake"),
                        "next_pnl": next_bet.get("profit"),
                    })
        else:
            i += 1

    if chase_events:
        worst_chase = max(chase_events, key=lambda x: abs(x["streak_pnl"]))
        lines.append({
            "icon": "chasing",
            "title": "Chasing losses detected",
            "body": (
                f"After a {worst_chase['streak_len']}-bet losing streak on "
                f"{worst_chase['team']} (-MYR {abs(worst_chase['streak_pnl'])})"
                f"{', you immediately bet again on the same team' if worst_chase.get('next_stake') else ''}. "
                f"This is classic revenge betting — emotionally driven, not data-driven."
            )
        })
    else:
        lines.append({
            "icon": "chasing",
            "title": "No clear chasing pattern",
            "body": "You generally avoid doubling down on the same team after losses, which is good discipline."
        })

    # 3. Live betting performance
    live_bets = [b for b in bets if "live" in (b.get("market") or "").lower()]
    live_profits = [b["profit"] for b in live_bets if b.get("profit") is not None]
    live_pnl = round(sum(live_profits), 2) if live_profits else 0
    live_wins = len([b for b in live_bets if b["status"] == "Won"])
    live_total = len([b for b in live_bets if b["status"] in ("Won", "Lost", "Half-won", "Half-lost")])

    if live_total > 0:
        lines.append({
            "icon": "live-betting",
            "title": "Live betting is a leak",
            "body": (
                f"You are {live_wins}/{live_total} in live betting ({round(live_wins/live_total*100,1)}% win rate), "
                f"losing MYR {abs(live_pnl)}. "
                f"Asian Handicap live bets have a significantly lower win rate than pre-match AH bets. "
                f"Live betting introduces emotional decision-making under time pressure."
            )
        })

    # 4. Market concentration
    market_counts = metrics["market_stats"]
    total_bets = metrics["total_bets"]
    ah_bets = market_counts.get("FT Asian Handicap", {}).get("bets", 0) if isinstance(market_counts.get("FT Asian Handicap"), dict) else 0
    ah_pct = round(ah_bets / total_bets * 100, 1) if total_bets else 0
    x2_bets = sum(v["bets"] for k, v in market_counts.items() if isinstance(v, dict) and "1X2" in k)

    if ah_pct > 60:
        lines.append({
            "icon": "concentration",
            "title": "Market concentration risk",
            "body": (
                f"{ah_pct}% of all bets are Asian Handicap. "
                f"{'No 1X2 bets found — that market is not bleeding you, but lack of diversification amplifies variance.' if x2_bets == 0 else ''} "
                f"Consider adding O/U and 1X2 markets to spread risk."
            )
        })

    # 5. Stake size volatility
    stakes = [b["stake"] for b in bets if b.get("stake")]
    if stakes:
        max_s = max(stakes)
        min_s = min(stakes)
        ratio = round(max_s / min_s, 1) if min_s > 0 else 0
        if ratio > 5:
            lines.append({
                "icon": "volatility",
                "title": "Inconsistent stake sizing",
                "body": (
                    f"Your bet sizes range from MYR {min_s:.0f} to MYR {max_s:.0f} "
                    f"({ratio}x difference). Consistent stake sizing is a cornerstone "
                    f"of proper bankroll management. The Kelly Criterion suggests staking "
                    f"1-2% of bankroll per bet regardless of confidence."
                )
            })

    # 6. Overall bankroll assessment
    roi = round(metrics["total_pnl"] / metrics["total_stake"] * 100, 2) if metrics["total_stake"] else 0
    if metrics["total_pnl"] < 0:
        lines.append({
            "icon": "bankroll",
            "title": "Negative ROI",
            "body": (
                f"Overall ROI: {roi}% (MYR {metrics['total_pnl']} on MYR {metrics['total_stake']} staked). "
                f"At this rate, your bankroll is eroding. The priority must shift from "
                f"betting volume to bet quality."
            )
        })

    return lines


def generate_advice(bets, metrics, analysis):
    advice = []

    # Advice 1: Stop live betting
    live_bets = [b for b in bets if "live" in (b.get("market") or "").lower()]
    live_profits_list = [b["profit"] for b in live_bets if b.get("profit") is not None]
    live_pnl = round(sum(live_profits_list), 2) if live_profits_list else 0
    non_live_pnl = round(metrics["total_pnl"] - live_pnl, 2)

    advice.append({
        "type": "danger",
        "title": "Stop live betting immediately",
        "body": (
            f"Your live betting record is bleeding MYR {abs(live_pnl)}. "
            f"Without those bets, your P&L improves from MYR {metrics['total_pnl']} "
            f"to MYR {non_live_pnl}. Live betting removes the analytical advantage "
            f"you have pre-match."
        )
    })

    # Advice 2: Cap stake
    advice.append({
        "type": "warning",
        "title": "Cap stake at 2% of bankroll",
        "body": (
            f"Your MYR 100 bets represent a significant portion of your active funds. "
            f"If your bankroll is MYR 2,200 (your total staked), each MYR 100 bet is ~4.5%. "
            f"Drop to MYR 20-44 (1-2% of bankroll) per bet until you have a 100-bet sample "
            f"at positive ROI."
        )
    })

    # Advice 3: One entry per event
    event_counts = {}
    for b in bets:
        evt = b.get("event", "")
        if evt:
            event_counts[evt] = event_counts.get(evt, 0) + 1
    worst_event = max(event_counts, key=event_counts.get) if event_counts else None
    worst_count = event_counts.get(worst_event, 0) if worst_event else 0

    if worst_count >= 4:
        advice.append({
            "type": "info",
            "title": "One entry per event",
            "body": (
                f"You placed {worst_count} bets on \"{worst_event}\" across different lines. "
                f"Multiple stabs at the same game increase variance without improving edge. "
                f"Pick your best line and stick to one bet per event."
            )
        })

    # Advice 4: O/U markets
    ou_bets = [b for b in bets if b.get("market") in ("FT O/U", "O/U (Live)")]
    ou_profits = [b["profit"] for b in ou_bets if b.get("profit") is not None]
    ou_pnl = round(sum(ou_profits), 2) if ou_profits else 0
    ou_wins = len([b for b in ou_bets if b["status"] == "Won"])
    ou_total = len([b for b in ou_bets if b["status"] in ("Won", "Lost")])

    if ou_total > 1 and ou_pnl > 0:
        advice.append({
            "type": "success",
            "title": "O/U markets show promise",
            "body": (
                f"Your O/U bets returned +MYR {ou_pnl} ({ou_wins}/{ou_total} wins). "
                f"Pre-match O/U has been profitable. Consider shifting 20-30% of your "
                f"action to O/U markets for diversification."
            )
        })
    elif ou_total > 1:
        advice.append({
            "type": "info",
            "title": "Review O/U selection process",
            "body": (
                f"Your O/U bets are at {ou_wins}/{ou_total} (-MYR {abs(ou_pnl)}). "
                f"The sample is small but the results suggest your O/U analysis needs refinement. "
                f"Focus on team scoring patterns (avg goals for/against) before picking O/U."
            )
        })

    # Advice 5: Streak management
    longest_loss = metrics["streaks"]["longest_loss_streak"]
    if longest_loss >= 4:
        advice.append({
            "type": "warning",
            "title": f"Break the {longest_loss}-bet losing streaks",
            "body": (
                f"You had a {longest_loss}-bet losing streak costing MYR "
                f"{abs(metrics['streaks']['longest_loss_pnl'])}. "
                f"Implement a stop-loss rule: after 3 consecutive losses, "
                f"take a 24-hour break and review your last 5 bets before betting again."
            )
        })

    return advice


def _extract_team_name(bet_str):
    if not bet_str:
        return ""
    parts = bet_str.split()
    team_parts = []
    for p in parts:
        if p.startswith(("-", "+")) or p.replace(".", "").replace("/", "").isdigit():
            break
        team_parts.append(p)
    return " ".join(team_parts) if team_parts else parts[0]
