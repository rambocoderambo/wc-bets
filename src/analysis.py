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

    # 7. Odds Range Performance
    odds_ranges = {"1.0-1.5 (Heavy Fav)": (1.0, 1.5), "1.5-2.0 (Moderate)": (1.5, 2.0), "2.0+ (Value)": (2.0, 999)}
    odds_stats = []
    resolved_w_profit = [b for b in resolved if b.get("odds") and b.get("profit") is not None]
    for label, (lo, hi) in odds_ranges.items():
        group = [b for b in resolved_w_profit if lo <= b["odds"] < hi]
        if group:
            gp = sum(b["profit"] for b in group)
            gc = len(group)
            gw = len([b for b in group if b["profit"] > 0])
            odds_stats.append(f"{label}: {gw}/{gc} won ({round(gw/gc*100,1)}%), P&L MYR {round(gp,1)}")
    if odds_stats:
        lines.append({
            "icon": "odds-range",
            "title": "Performance by odds range",
            "body": "Breaking down results by price bracket: " + " | ".join(odds_stats) + ". Heavy favorites show strong returns while value bets may need more volume."
        })

    # 8. Win/Loss Magnitude — are wins larger than losses?
    wins = [b for b in resolved if b.get("profit") and b["profit"] > 0]
    losses = [b for b in resolved if b.get("profit") and b["profit"] < 0]
    if wins and losses:
        avg_win = round(sum(b["profit"] for b in wins) / len(wins), 2)
        avg_loss = round(abs(sum(b["profit"] for b in losses) / len(losses)), 2)
        ratio = round(avg_win / avg_loss, 2) if avg_loss > 0 else 0
        lines.append({
            "icon": "win-loss-mag",
            "title": "Win vs Loss magnitude",
            "body": (
                f"Average winning bet: MYR {avg_win} vs average losing bet: MYR {avg_loss} "
                f"(ratio {ratio}:1). {'Wins outweigh losses — strong risk/reward.' if ratio > 1.2 else 'Losses almost match wins in size — consider tighter stop-losses.' if ratio < 0.8 else 'Wins and losses are similar in magnitude.'}"
            )
        })

    # 9. ROI by Market Type
    market_groups = {}
    for b in resolved_w_profit:
        m = b.get("market", "Other")
        if m not in market_groups:
            market_groups[m] = {"stake": 0, "pnl": 0, "count": 0}
        market_groups[m]["stake"] += b.get("stake", 0)
        market_groups[m]["pnl"] += b["profit"]
        market_groups[m]["count"] += 1
    market_rois = []
    for m, s in sorted(market_groups.items(), key=lambda x: x[1]["count"], reverse=True):
        if s["count"] >= 2:
            roi_val = round(s["pnl"] / s["stake"] * 100, 1) if s["stake"] > 0 else 0
            market_rois.append(f"{m}: {roi_val}% ({s['count']} bets)")
    if market_rois:
        lines.append({
            "icon": "market-roi",
            "title": "ROI by market type",
            "body": "Return on investment by market: " + " | ".join(market_rois) + ". " + (
                "Asian Handicap dominates volume — monitor its ROI closely." if any("Asian Handicap" in m for m in market_rois) else ""
            )
        })

    # 10. Consecutive result impact — performance after a win vs after a loss
    if len(resolved_sorted) >= 3:
        after_win = {"bets": 0, "wins": 0, "pnl": 0}
        after_loss = {"bets": 0, "wins": 0, "pnl": 0}
        for i in range(1, len(resolved_sorted)):
            prev = resolved_sorted[i - 1]
            curr = resolved_sorted[i]
            prev_won = prev["status"] in ("Won", "Half-won")
            if prev_won:
                after_win["bets"] += 1
                if curr.get("profit"): after_win["pnl"] += curr["profit"]
                if curr["status"] in ("Won", "Half-won"): after_win["wins"] += 1
            else:
                after_loss["bets"] += 1
                if curr.get("profit"): after_loss["pnl"] += curr["profit"]
                if curr["status"] in ("Won", "Half-won"): after_loss["wins"] += 1
        if after_win["bets"] >= 3 and after_loss["bets"] >= 3:
            aw_pct = round(after_win["wins"] / after_win["bets"] * 100, 1)
            al_pct = round(after_loss["wins"] / after_loss["bets"] * 100, 1)
            aw_pnl = round(after_win["pnl"], 1)
            al_pnl = round(after_loss["pnl"], 1)
            gap = aw_pct - al_pct
            lines.append({
                "icon": "momentum",
                "title": "Momentum after wins vs losses",
                "body": (
                    f"After a WIN: {aw_pct}% win rate, MYR {aw_pnl} P&L ({after_win['bets']} bets). "
                    f"After a LOSS: {al_pct}% win rate, MYR {al_pnl} P&L ({after_loss['bets']} bets). "
                    f"{'Strong momentum effect — winning builds confidence.' if gap > 10 else 'No significant momentum effect — disciplined regardless of result.' if abs(gap) < 5 else 'Better results follow losses — you adapt after mistakes.' if gap < -5 else 'Slight edge when riding a win streak.'}"
                )
            })

    return lines


def generate_advice(bets, metrics, analysis):
    advice = []

    # Advice 1: Stop live betting (only if there ARE live bets)
    live_bets = [b for b in bets if "live" in (b.get("market") or "").lower()]
    live_profits_list = [b["profit"] for b in live_bets if b.get("profit") is not None]
    live_pnl = round(sum(live_profits_list), 2) if live_profits_list else 0
    non_live_pnl = round(metrics["total_pnl"] - live_pnl, 2)

    if live_bets:
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

    # Advice 6: Focus on one handicap line per match
    multi_line_events = {}
    for b in bets:
        evt = b.get("event", "")
        if evt:
            if evt not in multi_line_events:
                multi_line_events[evt] = set()
            multi_line_events[evt].add(b.get("bet", ""))
    worst_multi = max(multi_line_events, key=lambda e: len(multi_line_events[e])) if multi_line_events else None
    worst_count = len(multi_line_events[worst_multi]) if worst_multi else 0
    if worst_count >= 3:
        advice.append({
            "type": "warning",
            "title": "Stick to one handicap line per match",
            "body": (
                f"You bet on {worst_count} different handicap lines for \"{worst_multi}\". "
                f"Each extra line is a separate bet on the same match outcome — it doesn't improve your edge, "
                f"it just increases variance. Analyze the best line pre-match and commit to it."
            )
        })

    # Advice 7: Track edge by market
    if metrics["total_bets"] >= 10:
        best_market = None
        best_market_roi = -999
        for m, s in (metrics.get("market_stats") or {}).items():
            if isinstance(s, dict) and s.get("bets", 0) >= 3 and s.get("stake", 0) > 0:
                roi = s["pnl"] / s["stake"] * 100
                if roi > best_market_roi:
                    best_market_roi = roi
                    best_market = m
        if best_market and best_market_roi > 5:
            advice.append({
                "type": "success",
                "title": f"Your edge is in {best_market.split()[0]} markets",
                "body": (
                    f"Your best-performing market is {best_market} with {round(best_market_roi,1)}% ROI. "
                    f"Consider allocating 60-70% of your bankroll to this market type "
                    f"while reducing exposure to weaker markets."
                )
            })

    # Advice 8: Small stakes compound
    small_bets = [b for b in bets if b.get("stake") and b["stake"] <= 20 and b.get("profit") is not None]
    if small_bets and len(small_bets) >= 5:
        small_pnl = round(sum(b["profit"] for b in small_bets), 1)
        small_roi = round(small_pnl / sum(b["stake"] for b in small_bets) * 100, 1) if sum(b["stake"] for b in small_bets) > 0 else 0
        if small_roi > 10:
            advice.append({
                "type": "success",
                "title": "Small stakes are outperforming",
                "body": (
                    f"Bets under MYR 20 returned {small_roi}% ROI (+MYR {small_pnl}) across {len(small_bets)} bets. "
                    f"Consider scaling these up gradually — your smaller bets show better selection discipline."
                )
            })
        elif small_roi < -10:
            advice.append({
                "type": "info",
                "title": "Small bets need review",
                "body": (
                    f"Bets under MYR 20 returned {small_roi}% ROI (-MYR {abs(small_pnl)}) across {len(small_bets)} bets. "
                    f"Smaller stakes don't mean lower standards — every bet should pass the same analysis filter."
                )
            })

    # Advice 9: Favorites vs underdogs balance
    favs = [b for b in bets if b.get("odds") and b["odds"] <= 1.8 and b.get("profit") is not None]
    dogs = [b for b in bets if b.get("odds") and b["odds"] >= 2.5 and b.get("profit") is not None]
    if favs and dogs and len(favs) >= 3 and len(dogs) >= 3:
        fav_roi = round(sum(b["profit"] for b in favs) / sum(b["stake"] for b in favs) * 100, 1) if sum(b["stake"] for b in favs) > 0 else 0
        dog_roi = round(sum(b["profit"] for b in dogs) / sum(b["stake"] for b in dogs) * 100, 1) if sum(b["stake"] for b in dogs) > 0 else 0
        diff = fav_roi - dog_roi
        if diff > 20:
            advice.append({
                "type": "info",
                "title": "Stick with favorites for now",
                "body": (
                    f"Favorites (odds ≤ 1.8) return {fav_roi}% ROI vs underdogs (odds ≥ 2.5) at {dog_roi}% ROI "
                    f"({round(diff,1)}% gap). Your analysis method works best for stronger teams — "
                    f"focus there and limit underdog bets until your value model improves."
                )
            })
        elif diff < -20:
            advice.append({
                "type": "info",
                "title": "You have an underdog edge",
                "body": (
                    f"Underdogs (odds ≥ 2.5) return {dog_roi}% ROI vs favorites (odds ≤ 1.8) at {fav_roi}% ROI. "
                    f"Your value-finding ability shines on longer prices — lean into this strength."
                )
            })

    # Advice 10: Stake to bankroll ratio
    total_stake = metrics.get("total_stake", 0)
    total_pnl = metrics.get("total_pnl", 0)
    if total_stake > 0:
        implied_bankroll = total_stake / (metrics.get("total_bets", 1) or 1) * 20
        if implied_bankroll > 0:
            max_stake = metrics.get("max_stake", 0)
            pct_of_bankroll = round(max_stake / implied_bankroll * 100, 1)
            if pct_of_bankroll > 5:
                advice.append({
                    "type": "warning",
                    "title": f"Single bets exceed {pct_of_bankroll}% of bankroll",
                    "body": (
                        f"Your largest bet (MYR {max_stake:.0f}) represents ~{pct_of_bankroll}% of estimated bankroll "
                        f"(MYR {implied_bankroll:.0f}). Professional staking limits single bets to 1-2%. "
                        f"Either increase your bankroll or cut max stake to MYR {round(implied_bankroll * 0.02):.0f}."
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
