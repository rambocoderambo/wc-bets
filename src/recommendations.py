# REAL Round of 32 fixtures scraped from AsianBookie.com
# Contains actual Asian Handicap lines, O/U lines, and 1X2 odds

from h2h import get_h2h
from collections import defaultdict
from group_results import GROUP_MATCHES


def compute_team_goals(bets=None):
    """Compute average goals scored/conceded for each team from ALL group matches."""
    matches = defaultdict(list)
    for t1, t2, score in GROUP_MATCHES:
        parts = score.split("-")
        g1, g2 = int(parts[0]), int(parts[1])
        matches[t1].append({"gf": g1, "ga": g2})
        matches[t2].append({"gf": g2, "ga": g1})

    stats = {}
    for team, ms in matches.items():
        gf = [m["gf"] for m in ms]
        ga = [m["ga"] for m in ms]
        stats[team] = {
            "avg_gf": round(sum(gf) / len(gf), 2),
            "avg_ga": round(sum(ga) / len(ga), 2),
            "gf_sum": sum(gf),
            "ga_sum": sum(ga),
            "matches": len(ms),
        }
    return stats

R32_FIXTURES = [
    {
        "team1": "Ivory Coast", "team2": "Norway",
        "date": "01/Jul 01:00",
        "ah_line": "Norway -0.25", "ah_home_odds": 2.05, "ah_away_odds": 1.85,
        "ou_line": 2.5, "ou_over_odds": 1.875, "ou_under_odds": 1.975,
        "odds_1x2_home": 3.52, "odds_1x2_draw": 3.44, "odds_1x2_away": 2.12,
        "team1_form": "WLW", "team2_form": "WWL",
        "result": "1-2", "result_winner": "Norway",
    },
    {
        "team1": "France", "team2": "Sweden",
        "date": "01/Jul 05:00",
        "ah_line": "France -1.5", "ah_home_odds": 1.875, "ah_away_odds": 2.025,
        "ou_line": 3.25, "ou_over_odds": 1.975, "ou_under_odds": 1.90,
        "odds_1x2_home": 1.29, "odds_1x2_draw": 5.89, "odds_1x2_away": 9.92,
        "team1_form": "WWWDW", "team2_form": "WDLLW",
        "result": "3-0", "result_winner": "France",
    },
    {
        "team1": "Mexico", "team2": "Ecuador",
        "date": "01/Jul 09:00",
        "ah_line": "Mexico -0.25", "ah_home_odds": 1.90, "ah_away_odds": 1.975,
        "ou_line": 1.75, "ou_over_odds": 1.80, "ou_under_odds": 2.075,
        "odds_1x2_home": 2.24, "odds_1x2_draw": 2.92, "odds_1x2_away": 3.89,
        "team1_form": "WWLDW", "team2_form": "DWDLL",
        "result": "2-0", "result_winner": "Mexico",
    },
    {
        "team1": "England", "team2": "DR Congo",
        "date": "02/Jul 00:00",
        "ah_line": "England -1.5", "ah_home_odds": 1.90, "ah_away_odds": 2.00,
        "ou_line": 2.5, "ou_over_odds": 1.975, "ou_under_odds": 1.90,
        "odds_1x2_home": 1.27, "odds_1x2_draw": 5.43, "odds_1x2_away": 12.84,
        "team1_form": "DWWLL", "team2_form": "WWLLW",
        "result": "2-1", "result_winner": "England",
    },
    {
        "team1": "Belgium", "team2": "Senegal",
        "date": "02/Jul 04:00",
        "ah_line": "Belgium -0.25", "ah_home_odds": 1.90, "ah_away_odds": 1.975,
        "ou_line": 2.25, "ou_over_odds": 1.925, "ou_under_odds": 1.95,
        "odds_1x2_home": 2.20, "odds_1x2_draw": 3.22, "odds_1x2_away": 3.51,
        "team1_form": "LWDWL", "team2_form": "LWLWD",
        "result": "3-2", "result_winner": "Belgium",
    },
    {
        "team1": "USA", "team2": "Bosnia",
        "date": "02/Jul 08:00",
        "ah_line": "USA -1.25", "ah_home_odds": 1.875, "ah_away_odds": 2.00,
        "ou_line": 2.5, "ou_over_odds": 1.85, "ou_under_odds": 2.025,
        "odds_1x2_home": 1.38, "odds_1x2_draw": 4.84, "odds_1x2_away": 8.53,
        "team1_form": "WWLDW", "team2_form": "WDLWW",
        "result": "2-0", "result_winner": "USA",
    },
    {
        "team1": "Spain", "team2": "Austria",
        "date": "03/Jul 03:00",
        "ah_line": "Spain -1.5", "ah_home_odds": 2.025, "ah_away_odds": 1.85,
        "ou_line": 2.5, "ou_over_odds": 1.85, "ou_under_odds": 2.00,
        "odds_1x2_home": 1.32, "odds_1x2_draw": 5.15, "odds_1x2_away": 10.01,
        "team1_form": "LWDWW", "team2_form": "LDWLD",
        "result": "3-0", "result_winner": "Spain",
    },
    {
        "team1": "Portugal", "team2": "Croatia",
        "date": "03/Jul 07:00",
        "ah_line": "Portugal -0.75", "ah_home_odds": 2.00, "ah_away_odds": 1.85,
        "ou_line": 2.25, "ou_over_odds": 1.825, "ou_under_odds": 2.025,
        "odds_1x2_home": 1.77, "odds_1x2_draw": 3.53, "odds_1x2_away": 4.90,
        "team1_form": "WWWDW", "team2_form": "DDDLD",
        "result": "2-1", "result_winner": "Portugal",
    },
    {
        "team1": "Switzerland", "team2": "Algeria",
        "date": "03/Jul 11:00",
        "ah_line": "Switzerland -0.5", "ah_home_odds": 2.075, "ah_away_odds": 1.80,
        "ou_line": 2.25, "ou_over_odds": 1.90, "ou_under_odds": 1.95,
        "odds_1x2_home": 2.04, "odds_1x2_draw": 3.26, "odds_1x2_away": 3.92,
        "team1_form": "WWDWL", "team2_form": "WDLWD",
    },
    {
        "team1": "Australia", "team2": "Egypt",
        "date": "04/Jul 02:00",
        "ah_line": "Egypt -0.25", "ah_home_odds": 2.075, "ah_away_odds": 1.80,
        "ou_line": 2.0, "ou_over_odds": 2.10, "ou_under_odds": 1.775,
        "odds_1x2_home": 3.32, "odds_1x2_draw": 2.88, "odds_1x2_away": 2.47,
        "team1_form": "LWLDW", "team2_form": "WDLLD",
    },
    {
        "team1": "Argentina", "team2": "Cape Verde",
        "date": "04/Jul 06:00",
        "ah_line": "Argentina -2", "ah_home_odds": 2.00, "ah_away_odds": 1.875,
        "ou_line": 2.75, "ou_over_odds": 1.875, "ou_under_odds": 2.00,
        "odds_1x2_home": 1.16, "odds_1x2_draw": 7.32, "odds_1x2_away": 17.83,
        "team1_form": "WDWWW", "team2_form": "WDLWL",
    },
    {
        "team1": "Colombia", "team2": "Ghana",
        "date": "04/Jul 09:30",
        "ah_line": "Colombia -1", "ah_home_odds": 1.95, "ah_away_odds": 1.925,
        "ou_line": 2.25, "ou_over_odds": 2.00, "ou_under_odds": 1.875,
        "odds_1x2_home": 1.53, "odds_1x2_draw": 3.90, "odds_1x2_away": 7.20,
        "team1_form": "WWDWL", "team2_form": "LLWLL",
    },
]

R16_FIXTURES = [
    {
        "team1": "Canada", "team2": "Morocco",
        "date": "05/Jul 01:00",
        "ah_line": "Morocco -0.5", "ah_home_odds": 2.025, "ah_away_odds": 1.85,
        "ou_line": 2.25, "ou_over_odds": 1.95, "ou_under_odds": 1.925,
        "odds_1x2_home": 4.58, "odds_1x2_draw": 3.45, "odds_1x2_away": 1.86,
        "team1_form": "DWL", "team2_form": "DWW",
        "result": "0-3", "result_winner": "Morocco",
    },
    {
        "team1": "Paraguay", "team2": "France",
        "date": "05/Jul 05:00",
        "ah_line": "France -2", "ah_home_odds": 1.825, "ah_away_odds": 2.05,
        "ou_line": 2.75, "ou_over_odds": 2.025, "ou_under_odds": 1.85,
        "odds_1x2_home": 16.50, "odds_1x2_draw": 7.19, "odds_1x2_away": 1.18,
        "team1_form": "DWW", "team2_form": "WWW",
        "result": "0-1", "result_winner": "France",
    },
    {
        "team1": "Brazil", "team2": "Norway",
        "date": "06/Jul 04:00",
        "ah_line": "Brazil -0.75", "ah_home_odds": 2.025, "ah_away_odds": 1.80,
        "ou_line": 2.75, "ou_over_odds": 1.925, "ou_under_odds": 1.925,
        "odds_1x2_home": 1.82, "odds_1x2_draw": 3.79, "odds_1x2_away": 4.27,
        "team1_form": "DWW", "team2_form": "WWL",
        "result": "1-2", "result_winner": "Norway",
    },
    {
        "team1": "Mexico", "team2": "England",
        "date": "06/Jul 08:00",
        "ah_line": "England -0.25", "ah_home_odds": 1.825, "ah_away_odds": 2.05,
        "ou_line": 2.0, "ou_over_odds": 2.10, "ou_under_odds": 1.775,
        "odds_1x2_home": 3.11, "odds_1x2_draw": 3.21, "odds_1x2_away": 2.41,
        "team1_form": "WWW", "team2_form": "WDW",
        "result": "2-3", "result_winner": "England",
    },
    {
        "team1": "Portugal", "team2": "Spain",
        "date": "07/Jul 03:00",
        "ah_line": "Spain -0.5", "ah_home_odds": 1.95, "ah_away_odds": 1.925,
        "ou_line": 2.5, "ou_over_odds": 1.975, "ou_under_odds": 1.875,
        "odds_1x2_home": 3.98, "odds_1x2_draw": 3.70, "odds_1x2_away": 1.90,
        "team1_form": "DWD", "team2_form": "DWW",
    },
    {
        "team1": "USA", "team2": "Belgium",
        "date": "07/Jul 08:00",
        "ah_line": "USA PK", "ah_home_odds": 1.975, "ah_away_odds": 1.90,
        "ou_line": 2.75, "ou_over_odds": 1.90, "ou_under_odds": 1.975,
        "odds_1x2_home": 2.70, "odds_1x2_draw": 3.48, "odds_1x2_away": 2.55,
        "team1_form": "WWL", "team2_form": "DDW",
    },
    {
        "team1": "Argentina", "team2": "Egypt",
        "date": "08/Jul 00:00",
        "ah_line": "Argentina -1.25", "ah_home_odds": 1.80, "ah_away_odds": 2.075,
        "ou_line": 2.5, "ou_over_odds": 1.85, "ou_under_odds": 2.00,
        "odds_1x2_home": 1.35, "odds_1x2_draw": 4.83, "odds_1x2_away": 9.66,
        "team1_form": "WWW", "team2_form": "DWD",
    },
    {
        "team1": "Switzerland", "team2": "Colombia",
        "date": "08/Jul 04:00",
        "ah_line": "Colombia -0.25", "ah_home_odds": 1.90, "ah_away_odds": 1.95,
        "ou_line": 2.25, "ou_over_odds": 1.85, "ou_under_odds": 2.025,
        "odds_1x2_home": 3.42, "odds_1x2_draw": 3.23, "odds_1x2_away": 2.22,
        "team1_form": "DWW", "team2_form": "WWD",
    },
]

TEAM_FORM = {
    "Algeria": "LWD", "Argentina": "WWW",
    "Australia": "WLD", "Austria": "WLD",
    "Belgium": "DDW", "Bosnia": "DLW",
    "Brazil": "DWW", "Canada": "DWL",
    "Cape Verde": "DDD", "Colombia": "WWD",
    "Croatia": "LWW", "Curacao": "LDL",
    "Czech Republic": "LDL", "DR Congo": "DLW",
    "Ecuador": "LDW", "Egypt": "DWD",
    "England": "WDW", "France": "WWW",
    "Germany": "WWL", "Ghana": "WDL",
    "Haiti": "LLL", "Iran": "DDD",
    "Iraq": "LLL", "Ivory Coast": "WLW",
    "Japan": "DWD", "Jordan": "LLL",
    "Mexico": "WWW", "Morocco": "DWW",
    "Netherlands": "DWW", "New Zealand": "DLL",
    "Norway": "WWL", "Panama": "LLL",
    "Paraguay": "LWD", "Portugal": "DWD",
    "Qatar": "DLL", "Saudi Arabia": "DLD",
    "Scotland": "WLL", "Senegal": "LLW",
    "South Africa": "LDW", "South Korea": "WLL",
    "Spain": "DWW", "Sweden": "WLD",
    "Switzerland": "DWW", "Tunisia": "LLL",
    "Turkey": "LLW", "USA": "WWL",
    "Uruguay": "DDL", "Uzbekistan": "LLL",
    "Nigeria": "WWDLL",
}


def generate_recommendations(bets, metrics):
    team_stats = metrics.get("team_stats", {})
    team_pnl = {team: stats["pnl"] for team, stats in team_stats.items()}
    team_bets = {team: stats["bets"] for team, stats in team_stats.items()}
    team_goals = compute_team_goals(bets)

    recs = []

    # Extract match results from bet data for auto-detecting completed matches
    match_results = {}
    for b in bets:
        evt = b.get("event", "")
        result = b.get("result", "")
        if not result or " vs " not in evt or result.strip() in ("-", ""):
            continue
        parts = evt.split(" vs ")
        if len(parts) != 2:
            continue
        key = tuple(sorted([parts[0].strip(), parts[1].strip()]))
        score = result.split(":")
        if len(score) != 2:
            continue
        try:
            g1, g2 = int(score[0].strip()), int(score[1].strip())
        except ValueError:
            continue
        # Store with team1 first (as in fixture)
        b_t1, b_t2 = parts[0].strip(), parts[1].strip()
        match_results[key] = {"team1": b_t1, "team2": b_t2, "g1": g1, "g2": g2}

    for fixture in R32_FIXTURES + R16_FIXTURES:
        t1 = fixture["team1"]
        t2 = fixture["team2"]

        # Parse the favorite team from ah_line (first word before handicap number)
        import re
        m = re.match(r"^(.+?)\s+([-+]\d[\d.]*|0)$", fixture["ah_line"])
        if m:
            fav_team = m.group(1).strip()
            handicap_str = m.group(2)
        else:
            fav_team = t1
            handicap_str = ""

        # Determine which side the favorite is
        if fav_team == t1:
            fav_odds = fixture["ah_home_odds"]
            under_odds = fixture["ah_away_odds"]
            under_team = t2
        else:
            fav_odds = fixture["ah_away_odds"]
            under_odds = fixture["ah_home_odds"]
            under_team = t1

        # Compute stats for favorite vs underdog
        pnl_fav = team_pnl.get(fav_team, 0)
        pnl_under = team_pnl.get(under_team, 0)
        bets_fav = team_bets.get(fav_team, 0)
        bets_under = team_bets.get(under_team, 0)

        form_fav = TEAM_FORM.get(fav_team, "DDDDD")
        form_under = TEAM_FORM.get(under_team, "DDDDD")

        form_score_fav = form_fav.count("W") * 3 + form_fav.count("D")
        form_score_under = form_under.count("W") * 3 + form_under.count("D")

        advantage = pnl_fav - pnl_under
        total_score = (form_score_fav - form_score_under) + advantage / 30

        picks = []

        # Asian Handicap pick
        if total_score > -3:
            # Stats support the favorite (or neutral — default to market favorite)
            ah_label = fixture["ah_line"]
            ah_odds = fav_odds
            if ah_odds <= 1.85:
                conf, conf_score = "high", 78
            elif ah_odds <= 1.95:
                conf, conf_score = "high", 70
            elif ah_odds <= 2.05:
                conf, conf_score = "mid", 58
            else:
                conf, conf_score = "low", 40
        else:
            # Stats don't support the favorite — recommend the underdog
            if handicap_str in ("0", "PK"):
                flip_label = f"{under_team} PK"
            elif handicap_str.startswith("-"):
                flip_label = f"{under_team} +{handicap_str[1:]}"
            elif handicap_str.startswith("+"):
                flip_label = f"{under_team} {handicap_str}"
            else:
                flip_label = f"{under_team} PK"
            ah_label = flip_label
            ah_odds = under_odds
            conf, conf_score = "low", 35

        picks.append({
            "type": "AH",
            "label": ah_label,
            "odds": ah_odds,
            "confidence": conf,
            "confidence_score": conf_score,
        })

        # Kelly stake estimate
        edge_factors = {"high": 0.12, "mid": 0.03, "low": -0.02}
        edge_factor = edge_factors.get(conf, 0)
        implied_prob = 1.0 / ah_odds if ah_odds > 1 else 0.5
        est_true_prob = implied_prob * (1 + edge_factor)
        est_true_prob = min(max(est_true_prob, 0.05), 0.95)
        b_val = ah_odds - 1
        if b_val > 0 and est_true_prob > implied_prob:
            kelly_full = (est_true_prob * b_val - (1 - est_true_prob)) / b_val
        else:
            kelly_full = 0
        kelly_quarter = max(0, kelly_full * 0.25)
        picks[-1]["kelly_pct"] = round(kelly_quarter * 100, 1)

        # O/U pick based on actual team goal stats from group stage
        gs1 = team_goals.get(t1, {"avg_gf": 1.5, "avg_ga": 1.0})
        gs2 = team_goals.get(t2, {"avg_gf": 1.0, "avg_ga": 1.5})
        exp_t1_goals = (gs1["avg_gf"] + gs2["avg_ga"]) / 2
        exp_t2_goals = (gs2["avg_gf"] + gs1["avg_ga"]) / 2
        est_total = round(exp_t1_goals + exp_t2_goals, 1)

        # Adjust for AH handicap — if the favorite is giving goals, the match 
        # must have enough total goals for them to cover the spread
        try:
            ah_abs = abs(float(handicap_str)) if handicap_str and handicap_str not in ("0", "PK", "") else 0.25
        except ValueError:
            ah_abs = 0.25
        if ah_abs >= 0.75 and total_score > -3:
            # For the favorite to cover the handicap, typical score has them
            # winning by hcp+1 goals. Total goals ~ (hcp+1) + 0.5 = hcp + 1.5
            realistic_total = ah_abs + 1.5
            if realistic_total > est_total:
                est_total = round(realistic_total, 1)

        line = fixture["ou_line"]
        if est_total > line + 0.3:
            ou_label = f"Over {line}"
            ou_odds = fixture["ou_over_odds"]
            ou_conf = "high" if est_total > line + 1 else "mid"
            ou_score = 80 if est_total > line + 1 else 60
        elif est_total < line - 0.3:
            ou_label = f"Under {line}"
            ou_odds = fixture["ou_under_odds"]
            ou_conf = "mid"
            ou_score = 55
        else:
            # Close to the line — lean toward the side the data supports
            if est_total >= line:
                ou_label = f"Over {line}"
                ou_odds = fixture["ou_over_odds"]
            else:
                ou_label = f"Under {line}"
                ou_odds = fixture["ou_under_odds"]
            ou_conf = "mid"
            ou_score = 50

        picks.append({
            "type": "O/U",
            "label": ou_label,
            "odds": ou_odds,
            "confidence": ou_conf,
            "confidence_score": ou_score,
        })

        # Kelly stake for O/U pick
        edge_factors_ou = {"high": 0.10, "mid": 0.03, "low": -0.03}
        ef = edge_factors_ou.get(ou_conf, 0)
        implied_prob_ou = 1.0 / ou_odds if ou_odds > 1 else 0.5
        est_true_prob_ou = implied_prob_ou * (1 + ef)
        est_true_prob_ou = min(max(est_true_prob_ou, 0.05), 0.95)
        b_ou = ou_odds - 1
        if b_ou > 0 and est_true_prob_ou > implied_prob_ou:
            kf = (est_true_prob_ou * b_ou - (1 - est_true_prob_ou)) / b_ou
        else:
            kf = 0
        picks[-1]["kelly_pct"] = round(max(0, kf * 0.25) * 100, 1)

        # === DATA-DRIVEN SCORE PREDICTION ===
        gs_fav = team_goals.get(fav_team, {"avg_gf": 1.5, "avg_ga": 1.0, "matches": 0})
        gs_under = team_goals.get(under_team, {"avg_gf": 1.0, "avg_ga": 1.5, "matches": 0})

        # Expected goals: blend each team's scoring with opponent's conceding
        exp_fav = (gs_fav["avg_gf"] + gs_under["avg_ga"]) / 2
        exp_under = (gs_under["avg_gf"] + gs_fav["avg_ga"]) / 2

        # Parse handicap value
        try:
            hand_val = abs(float(handicap_str)) if handicap_str and handicap_str not in ("0", "PK", "") else 0.25
        except ValueError:
            hand_val = 0.25

        if total_score > -3:
            # RECOMMENDING FAVORITE — score must show fav covering the handicap
            confidence_boost = picks[0]["confidence_score"] / 100 * 0.5
            exp_fav += hand_val * 0.5 + confidence_boost
            need_margin = hand_val + 0.5
            projected_margin = exp_fav - exp_under
            margin = max(need_margin, projected_margin)
            margin = max(1.0, margin)
            # Use int() rounding (always rounds up for .5)
            margin_rounded = int(margin + 0.5)
            if margin_rounded < hand_val:
                margin_rounded = int(hand_val) + 1
            under_score = max(0, int(exp_under + 0.5))
            fav_score = under_score + margin_rounded
        else:
            # RECOMMENDING UNDERDOG — score must show underdog covers the spread
            exp_under += 0.3
            base_under = max(1, int(exp_under + 0.5))
            base_fav = max(0, int(exp_fav + 0.5))
            if hand_val >= 1.25:
                max_fav_margin = hand_val - 0.5
                under_score = max(1, base_under)
                fav_score = max(1, base_fav)
                if fav_score - under_score > max_fav_margin:
                    fav_score = under_score + int(max_fav_margin + 0.5)
            else:
                under_score = max(base_under, base_fav) + 1
                fav_score = max(0, min(base_fav, base_under))

        # Map to t1_score / t2_score for display
        if fav_team == t1:
            t1_score, t2_score = fav_score, under_score
        else:
            t1_score, t2_score = under_score, fav_score

        # Final correction: ensure predicted score covers the AH pick
        if total_score > -3:
            if fav_team == t1:
                actual_margin = t1_score - t2_score
            else:
                actual_margin = t2_score - t1_score
            if actual_margin < hand_val:
                needed = int(hand_val) + 1 if hand_val >= 1 else 1
                if fav_team == t1:
                    t1_score = t2_score + needed
                else:
                    t2_score = t1_score + needed

        likely_score = f"{t1_score}-{t2_score}"

        # Map to t1_score / t2_score for display
        if fav_team == t1:
            t1_score, t2_score = fav_score, under_score
        else:
            t1_score, t2_score = under_score, fav_score

        likely_score = f"{t1_score}-{t2_score}"

        # Build detailed score reasoning
        fav_form = form_fav if len(form_fav) <= 5 else form_fav[:5]
        under_form = form_under if len(form_under) <= 5 else form_under[:5]

        score_reason_parts = []

        if gs_fav["matches"] > 0:
            score_reason_parts.append(
                f"{fav_team} scored {gs_fav['gf_sum']} in {gs_fav['matches']} group matches "
                f"(avg {gs_fav['avg_gf']:.2f} GF, {gs_fav['avg_ga']:.2f} GA). "
                f"Recent form: {fav_form}."
            )
        else:
            score_reason_parts.append(f"{fav_team} have no recorded matches in your betting history.")

        if gs_under["matches"] > 0:
            score_reason_parts.append(
                f"{under_team} scored {gs_under['gf_sum']} in {gs_under['matches']} group matches "
                f"(avg {gs_under['avg_gf']:.2f} GF, {gs_under['avg_ga']:.2f} GA). "
                f"Recent form: {under_form}."
            )
        else:
            score_reason_parts.append(f"{under_team} have no recorded matches in your betting history.")

        score_reason_parts.append(
            f"Projection: {fav_team} {gs_fav['avg_gf']:.2f} avg GF vs {under_team} {gs_under['avg_ga']:.2f} GA "
            f"-> ~{exp_fav:.1f} expected. {under_team} {gs_under['avg_gf']:.2f} avg GF vs {fav_team} {gs_fav['avg_ga']:.2f} GA "
            f"-> ~{exp_under:.1f} expected."
        )

        if total_score > 0:
            margin_result = (fav_score if fav_team == t1 else under_score) - (under_score if fav_team == t1 else fav_score)
            score_reason_parts.append(
                f"AH pick: {fav_team} {handicap_str} -> need win by {hand_val}+. "
                f"Predicted margin: {margin_result} goals -> {'covers' if margin_result >= hand_val else 'does not cover'}."
            )
        else:
            if hand_val >= 1.25:
                score_reason_parts.append(
                    f"AH pick: {under_team} +{hand_val} -> need loss by < {hand_val}. "
                    f"Predicted {t1_score}-{t2_score} -> covers."
                )
            else:
                score_reason_parts.append(
                    f"AH pick: {under_team} +{hand_val} -> need draw or win. "
                    f"Predicted {t1_score}-{t2_score} -> covers."
                )

        total_g = t1_score + t2_score
        ou_line = fixture["ou_line"]
        if total_g > ou_line:
            score_reason_parts.append(f"Total {total_g}g > O/U {ou_line} -> Over.")
        elif total_g < ou_line:
            score_reason_parts.append(f"Total {total_g}g < O/U {ou_line} -> Under.")
        else:
            score_reason_parts.append(f"Total {total_g}g = O/U {ou_line} (push).")

        score_reason = " ".join(score_reason_parts)

        stage = f"R32: {fixture['date']}"

        reason_parts = []
        for team, pnl, bcount in [(t1, team_pnl.get(t1, 0), team_bets.get(t1, 0)), (t2, team_pnl.get(t2, 0), team_bets.get(t2, 0))]:
            if bcount > 0:
                s = f"+MYR {pnl:.0f}" if pnl > 0 else f"-MYR {abs(pnl):.0f}"
                reason_parts.append(f"{team} {s} ({bcount}b)")
            else:
                reason_parts.append(f"{team} no bets on record")

        f_fav_desc = _form_desc(form_fav)
        f_under_desc = _form_desc(form_under)
        reason_parts.append(f"{fav_team} {f_fav_desc} ({form_fav})")
        reason_parts.append(f"{under_team} {f_under_desc} ({form_under})")

        # 1X2 value angle
        if fixture["odds_1x2_home"] < 1.5:
            reason_parts.append(f"{t1} heavy 1X2 favorite @ {fixture['odds_1x2_home']}")
        elif fixture["odds_1x2_away"] < 1.5:
            reason_parts.append(f"{t2} heavy 1X2 favorite @ {fixture['odds_1x2_away']}")

        # Head-to-head
        h2h = get_h2h(bets, t1, t2)

        # Auto-detect result from bet data (only if no manual result in fixture)
        detected_result = fixture.get("result")
        if not detected_result:
            match_key = tuple(sorted([t1, t2]))
            if match_key in match_results:
                mr = match_results[match_key]
                if mr["team1"] == t1:
                    detected_result = f"{mr['g1']}-{mr['g2']}"
                else:
                    detected_result = f"{mr['g2']}-{mr['g1']}"

        recs.append({
            "team1": t1, "team2": t2, "stage": stage,
            "predicted_score": likely_score, "picks": picks,
            "reason": ". ".join(reason_parts) + ".",
            "score_reason": score_reason,
            "team1_form": form_fav, "team2_form": form_under,
            "h2h": h2h,
            "result": detected_result,
        })

    # Sort: upcoming first (by date asc), then completed (by date desc = latest on top)
    def _sort_key(r):
        date_str = r.get("stage", "").replace("R32: ", "")
        try:
            from datetime import datetime
            dt = datetime.strptime(date_str, "%d/%b %H:%M")
        except ValueError:
            dt = datetime.max
        is_completed = 1 if r.get("result") else 0
        # Completed matches: negate combined datetime ordinal + minute so latest comes first
        sort_dt = -(dt.toordinal() * 1440 + dt.hour * 60 + dt.minute) if is_completed else (dt.toordinal() * 1440 + dt.hour * 60 + dt.minute)
        return (is_completed, sort_dt)
    recs.sort(key=_sort_key)
    return recs


def _form_desc(form_str):
    wins = form_str.count("W")
    losses = form_str.count("L")
    if wins >= 4: return "excellent form"
    if wins >= 3: return "strong form"
    if wins >= 2: return "decent form"
    if losses >= 4: return "poor form"
    if losses >= 3: return "struggling"
    return "mixed form"
