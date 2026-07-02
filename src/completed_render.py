"""Render completed match with clickable dropdown and pick results."""
import re
import math


def _eval_ou(lbl, tg):
    """Evaluate O/U pick. Returns (result_str, color). Handles .25/.75 splits."""
    m = re.match(r"(Over|Under)\s+([\d.]+)", lbl)
    if not m:
        return "?", "#9ca3a0"
    dr = m.group(1)
    lv = float(m.group(2))

    # Check if it's a split line (.25 or .75)
    frac = lv - math.floor(lv)
    if abs(frac - 0.75) < 0.01:
        # Split into .5 and .0 (e.g., 2.75 -> Over 2.5 and Over 3.0)
        low = math.floor(lv) + 0.5
        high = math.floor(lv) + 1.0
        low_w = (dr == "Over" and tg > low) or (dr == "Under" and tg < low)
        high_w = (dr == "Over" and tg > high) or (dr == "Under" and tg < high)
        low_p = tg == low
        high_p = tg == high
        low_r = "W" if low_w else "P" if low_p else "L"
        high_r = "W" if high_w else "P" if high_p else "L"
        combos = {"WW": ("WON", "#5cb87a"), "WP": ("HALF WON", "#5aa9a9"),
                  "WL": ("HALF WON", "#5aa9a9"), "PW": ("HALF WON", "#5aa9a9"),
                  "PP": ("PUSH", "#d4a85c"), "PL": ("HALF LOST", "#c8814a"),
                  "LW": ("HALF LOST", "#c8814a"), "LP": ("HALF LOST", "#c8814a"),
                  "LL": ("LOST", "#c8814a")}
        return combos.get(low_r + high_r, ("?", "#9ca3a0"))
    elif abs(frac - 0.25) < 0.01:
        # Split into .0 and .5 (e.g., 2.25 -> Over 2.0 and Over 2.5)
        low = math.floor(lv)
        high = math.floor(lv) + 0.5
        low_w = (dr == "Over" and tg > low) or (dr == "Under" and tg < low)
        high_w = (dr == "Over" and tg > high) or (dr == "Under" and tg < high)
        low_p = tg == low
        high_p = tg == high
        low_r = "W" if low_w else "P" if low_p else "L"
        high_r = "W" if high_w else "P" if high_p else "L"
        combos = {"WW": ("WON", "#5cb87a"), "WP": ("HALF WON", "#5aa9a9"),
                  "WL": ("HALF WON", "#5aa9a9"), "PW": ("HALF WON", "#5aa9a9"),
                  "PP": ("PUSH", "#d4a85c"), "PL": ("HALF LOST", "#c8814a"),
                  "LW": ("HALF LOST", "#c8814a"), "LP": ("HALF LOST", "#c8814a"),
                  "LL": ("LOST", "#c8814a")}
        return combos.get(low_r + high_r, ("?", "#9ca3a0"))
    else:
        # Standard line (integer or .0)
        w = (dr == "Over" and tg > lv) or (dr == "Under" and tg < lv)
        psh = tg == lv
        if w: return ("WON", "#5cb87a")
        elif psh: return ("PUSH", "#d4a85c")
        else: return ("LOST", "#c8814a")


def _eval_ah(lbl, t1, t2, a1, a2):
    """Evaluate AH pick. Returns (result_str, color). Handles .25/.75 splits."""
    m = re.match(r"^(.+?)\s+([-+]?[\d.]+|PK)$", lbl)
    if not m:
        return "?", "#9ca3a0"
    pt = m.group(1).strip()
    hv = m.group(2)
    if hv == "PK":
        w = (pt == t1 and a1 > a2) or (pt == t2 and a2 > a1)
        psh = a1 == a2
        return ("WON", "#5cb87a") if w else ("PUSH", "#d4a85c") if psh else ("LOST", "#c8814a")

    h = float(hv)
    frac = abs(h) - math.floor(abs(h))
    # Margin for the team: positive = team wins by that much, negative = team loses
    if pt == t1:
        margin = a1 - a2
    else:
        margin = a2 - a1

    if h < 0:
        nd = abs(h)
        if abs(frac - 0.75) < 0.01:
            # -0.75 = half -0.5, half -1.0
            low = nd - 0.25  # -0.5
            high = nd  # -1.0
            low_w = margin > low
            high_w = margin > high
            low_p = margin == low
            high_p = margin == high
        elif abs(frac - 0.25) < 0.01:
            # -0.25 = half 0, half -0.5
            low = nd - 0.25  # 0
            high = nd  # -0.5
            low_w = margin > low
            high_w = margin > high
            low_p = margin == low
            high_p = margin == high
        else:
            # Standard line
            w = margin > nd
            psh = margin == nd
            return ("WON", "#5cb87a") if w else ("PUSH", "#d4a85c") if psh else ("LOST", "#c8814a")

        low_r = "W" if low_w else "P" if low_p else "L"
        high_r = "W" if high_w else "P" if high_p else "L"
        combos = {"WW": ("WON", "#5cb87a"), "WP": ("HALF WON", "#5aa9a9"),
                  "WL": ("HALF WON", "#5aa9a9"), "PW": ("HALF WON", "#5aa9a9"),
                  "PP": ("PUSH", "#d4a85c"), "PL": ("HALF LOST", "#c8814a"),
                  "LW": ("HALF LOST", "#c8814a"), "LP": ("HALF LOST", "#c8814a"),
                  "LL": ("LOST", "#c8814a")}
        return combos.get(low_r + high_r, ("?", "#9ca3a0"))
    else:
        # Positive handicap: team is getting goals
        give = abs(h)
        if abs(frac - 0.75) < 0.01:
            low = give - 0.25
            high = give
        elif abs(frac - 0.25) < 0.01:
            low = give - 0.25
            high = give
        else:
            w = margin > -give
            psh = margin == -give
            return ("WON", "#5cb87a") if w else ("PUSH", "#d4a85c") if psh else ("LOST", "#c8814a")

        low_w = margin > -low
        high_w = margin > -high
        low_p = margin == -low
        high_p = margin == -high
        low_r = "W" if low_w else "P" if low_p else "L"
        high_r = "W" if high_w else "P" if high_p else "L"
        combos = {"WW": ("WON", "#5cb87a"), "WP": ("HALF WON", "#5aa9a9"),
                  "WL": ("HALF WON", "#5aa9a9"), "PW": ("HALF WON", "#5aa9a9"),
                  "PP": ("PUSH", "#d4a85c"), "PL": ("HALF LOST", "#c8814a"),
                  "LW": ("HALF LOST", "#c8814a"), "LP": ("HALF LOST", "#c8814a"),
                  "LL": ("LOST", "#c8814a")}
        return combos.get(low_r + high_r, ("?", "#9ca3a0"))


def render_completed(match, a1, a2):
    """Generate HTML for a completed match with clickable details showing pick results."""
    pred = match["predicted_score"]
    result_display = match["result"].replace("-", " - ")
    p1, p2 = pred.split("-")
    correct = (int(p1) > int(p2) and a1 > a2) or (int(p1) < int(p2) and a1 < a2) or (int(p1) == int(p2) and a1 == a2)

    pick_cards = ""
    for p in match["picks"]:
        lbl = p["label"]
        ods = p["odds"]
        tp = p["type"]
        conf = p.get("confidence", "mid")
        conf_color = {"high": "#5cb87a", "mid": "#d4a85c", "low": "#c8814a"}.get(conf, "#9ca3a0")
        if tp == "AH":
            rs, rc = _eval_ah(lbl, match["team1"], match["team2"], a1, a2)
        else:
            tg = a1 + a2
            rs, rc = _eval_ou(lbl, tg)
        pick_cards += (
            '<div class="rec-pick">'
            '<div class="pick-label">{0} Pick</div>'
            '<div class="pick-value">{1}</div>'
            '<div class="pick-odds">@ {2}</div>'
            '<div style="margin-top:4px;font-size:11px;color:{5};">{6} Confidence</div>'
            '<div style="margin-top:4px;font-size:12px;font-weight:600;color:{3};">{4}</div>'
            '</div>'
        ).format(tp, lbl, ods, rc, rs, conf_color, conf.title())

    correct_label = "CORRECT" if correct else "MISSED"
    correct_color = "#5cb87a" if correct else "#c8814a"

    html = (
        '<div style="cursor:pointer;" onclick="var d=this.nextElementSibling;if(d)d.style.display=d.style.display===&#39;block&#39;?&#39;none&#39;:&#39;block&#39;;">'
        '<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;padding:12px 16px;background:#0d1114;border-radius:8px;margin-bottom:4px;">'
        '<div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;">'
        '<span style="background:#2a3a2a;color:#5cb87a;padding:3px 10px;border-radius:6px;font-size:11px;font-weight:600;">COMPLETED</span>'
        '<span style="font-weight:600;color:#e8e6e3;">{0}</span>'
        '<span style="color:#9ca3a0;">vs</span>'
        '<span style="font-weight:600;color:#e8e6e3;">{1}</span>'
        '</div>'
        '<div style="font-size:14px;color:#d4d4d4;">'
        '<span style="color:#9ca3a0;">Pred:</span> <span style="font-weight:600;">{2}</span>'
        '<span style="margin:0 8px;color:#262b33;">|</span>'
        '<span style="color:#9ca3a0;">Actual:</span> <span style="font-weight:600;color:#5cb87a;">{3}</span>'
        '<span style="margin-left:8px;color:{4};font-weight:600;">{5}</span>'
        '<span style="margin-left:8px;color:#9ca3a0;font-size:12px;">&#9660;</span>'
        '</div></div></div>'
        '<div style="display:none;padding:12px 16px;background:#0d1114;border-radius:0 0 8px 8px;margin-bottom:8px;">'
        '<div style="display:flex;gap:12px;flex-wrap:wrap;">{6}</div>'
        '<div style="margin-top:10px;font-size:12px;color:#9ca3a0;padding-top:10px;border-top:1px solid #1f242c;">{7}</div>'
        '</div>'
    ).format(match["team1"], match["team2"], pred, result_display, correct_color, correct_label, pick_cards, match.get("reason", ""))

    return html
