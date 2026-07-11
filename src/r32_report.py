import os
import re as _re
from completed_render import _eval_ah, _eval_ou


def generate_live_report(bets, metrics, analysis, advice, recommendations, chart_path, output_path="output/live_r32.html"):
    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="30">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Live QF Predictions</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0d1114; color: #d4d4d4; padding: 20px; }
  .container { max-width: 1400px; margin: 0 auto; }
  h1 { font-size: 22px; font-weight: 700; margin-bottom: 4px; color: #e8e6e3; }
  .subtitle { color: #9ca3a0; font-size: 13px; margin-bottom: 20px; }
  .badge { display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: 12px; font-weight: 600; }
  .badge-green { background: rgba(92,184,122,.15); color: #5cb87a; }
  .badge-orange { background: rgba(200,129,74,.15); color: #c8814a; }
  .badge-amber { background: rgba(212,168,92,.15); color: #d4a85c; }
  .badge-gray { background: rgba(156,163,160,.15); color: #9ca3a0; }

  .rec-section { margin-bottom: 20px; }
  .rec-card { background: #161a20; border: 1px solid #262b33; border-radius: 10px; padding: 18px; }
  .rec-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 16px; }
  .rec-header h2 { font-size: 16px; font-weight: 700; color: #e8e6e3; }
  .roi-badge { background: rgba(92,184,122,.15); color: #5cb87a; padding: 4px 14px; border-radius: 999px; font-size: 12px; font-weight: 600; }
  .rec-match { background: #13181d; border: 1px solid #1f242c; border-radius: 8px; padding: 14px 16px; margin-bottom: 8px; }
  .rec-match-top { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 8px; }
  .rec-match-teams { font-size: 15px; font-weight: 600; color: #e8e6e3; }
  .rec-match-teams .vs { color: #6b7278; font-weight: 400; margin: 0 6px; }
  .rec-match-teams .score-pred { font-size: 12px; color: #d4a85c; font-weight: 400; margin-left: 10px; }
  .rec-match-stage { font-size: 11px; color: #9ca3a0; background: #1f242c; padding: 2px 8px; border-radius: 5px; }
  .rec-picks { display: flex; gap: 10px; flex-wrap: wrap; }
  .rec-pick { background: #1a1e27; border: 1px solid #262b33; border-radius: 7px; padding: 8px 14px; flex: 1; min-width: 140px; }
  .rec-pick .pick-label { font-size: 10px; color: #9ca3a0; text-transform: uppercase; letter-spacing: .3px; margin-bottom: 3px; }
  .rec-pick .pick-value { font-size: 13px; font-weight: 600; color: #d4d4d4; }
  .rec-pick .pick-odds { font-size: 12px; color: #5cb87a; margin-top: 1px; }
  .rec-pick .pick-conf { display: flex; align-items: center; gap: 5px; margin-top: 4px; font-size: 11px; }
  .conf-dot { width: 7px; height: 7px; border-radius: 50%; display: inline-block; }
  .conf-high { background: #5cb87a; }
  .conf-mid { background: #d4a85c; }
  .conf-low { background: #c8814a; }
  .rec-reason { font-size: 12px; color: #9ca3a0; margin-top: 6px; line-height: 1.4; padding-top: 6px; border-top: 1px solid #1f242c; }
  .form-info { font-size: 11px; color: #9ca3a0; margin-top: 2px; }
  .form-w { color: #5cb87a; font-weight: bold; }
  .form-d { color: #5b8def; font-weight: bold; }
  .form-l { color: #6b7278; font-weight: bold; }

  .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin-bottom: 16px; }
  .stat-box { background: #0d1114; border-radius: 8px; padding: 12px; text-align: center; }
  .stat-box .label { font-size: 10px; color: #9ca3a0; text-transform: uppercase; letter-spacing: .3px; margin-bottom: 4px; }
  .stat-box .num { font-size: 22px; font-weight: 700; color: #e8e6e3; }
  .stat-box .sub { font-size: 11px; color: #5cb87a; margin-top: 2px; }

  .completed-section { margin-top: 20px; }
  .completed-box { background: #1a2520; border: 1px solid #2a3a2a; border-radius: 10px; padding: 18px; }
  .completed-box h3 { font-size: 15px; font-weight: 600; color: #5cb87a; margin-bottom: 12px; }
  .completed-row { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; padding: 10px 14px; background: #0d1114; border-radius: 8px; margin-bottom: 6px; }
  .completed-row .comp-badge { background: #2a3a2a; color: #5cb87a; padding: 2px 8px; border-radius: 5px; font-size: 10px; font-weight: 600; }
  .footer-note { margin-top: 20px; padding-top: 12px; border-top: 1px solid #1f242c; font-size: 11px; color: #6b7278; text-align: center; }
</style>
</head>
<body>
<div class="container">
  <h1>Live QF — Quarterfinal Predictions</h1>
  <div class="subtitle">Auto-refreshes every 30s &bull; QF stage</div>
"""

    def _form_html(form):
        out = ""
        for c in form:
            if c == "W":
                out += '<span class="form-w">W</span> '
            elif c == "D":
                out += '<span class="form-d">D</span> '
            else:
                out += '<span class="form-l">L</span> '
        return out.strip()

    # ===== ACCURACY SUMMARY =====
    total_correct = 0
    total_matches = 0
    ah_correct, ah_wrong, ah_push = 0, 0, 0
    ou_correct, ou_wrong, ou_push = 0, 0, 0

    for rec in recommendations:
        if not rec.get("result"):
            continue
        total_matches += 1
        parts = rec["result"].split("-")
        a1, a2 = int(parts[0]), int(parts[1])
        p1, p2 = rec["predicted_score"].split("-")
        if (int(p1) > int(p2) and a1 > a2) or (int(p1) < int(p2) and a1 < a2) or (int(p1) == int(p2) and a1 == a2):
            total_correct += 1

        for pick in rec["picks"]:
            lbl = pick["label"]
            if pick["type"] == "AH":
                m = _re.match(r"^(.+?)\s+([-+]?[\d.]+|PK)$", lbl)
                if m:
                    pt = m.group(1).strip()
                    hv = m.group(2)
                    if hv == "PK": w = (pt == rec["team1"] and a1 > a2) or (pt == rec["team2"] and a2 > a1); psh = a1 == a2
                    else:
                        h = float(hv)
                        if h < 0:
                            nd = abs(h)
                            w = (pt == rec["team1"] and (a1 - a2) > nd) or (pt == rec["team2"] and (a2 - a1) > nd)
                            psh = (pt == rec["team1"] and (a1 - a2) == nd) or (pt == rec["team2"] and (a2 - a1) == nd)
                        else:
                            w = (pt == rec["team1"] and (a1 - a2) > -h) or (pt == rec["team2"] and (a2 - a1) > -h)
                            psh = (pt == rec["team1"] and (a1 - a2) == -h) or (pt == rec["team2"] and (a2 - a1) == -h)
                    if w: ah_correct += 1
                    elif psh: ah_push += 1
                    else: ah_wrong += 1
            else:
                tg = a1 + a2
                m = _re.match(r"(Over|Under)\s+([\d.]+)", lbl)
                if m:
                    dr = m.group(1); lv = float(m.group(2))
                    w = (dr == "Over" and tg > lv) or (dr == "Under" and tg < lv)
                    psh = tg == lv
                    if w: ou_correct += 1
                    elif psh: ou_push += 1
                    else: ou_wrong += 1

    if total_matches > 0:
        pct = round(total_correct / total_matches * 100, 1)
        ah_total = ah_correct + ah_wrong + ah_push
        ou_total = ou_correct + ou_wrong + ou_push
        ah_pct = round(ah_correct / ah_total * 100, 1) if ah_total > 0 else 0
        ou_pct = round(ou_correct / ou_total * 100, 1) if ou_total > 0 else 0
        html += f"""<div class="completed-box" style="margin-bottom:20px;">
  <h3> Match Completed — Accuracy Summary</h3>
  <div class="stats-grid">
    <div class="stat-box"><div class="label">Matches</div><div class="num">{total_matches}</div><div class="sub">{total_correct}/{total_matches} correct ({pct}%)</div></div>
    <div class="stat-box"><div class="label">Asian Handicap</div><div class="num" style="color:#5cb87a;">{ah_pct}%</div><div class="sub" style="color:#d4d4d4;">{ah_correct}W - {ah_push}P - {ah_wrong}L</div></div>
    <div class="stat-box"><div class="label">Over / Under</div><div class="num" style="color:#5cb87a;">{ou_pct}%</div><div class="sub" style="color:#d4d4d4;">{ou_correct}W - {ou_push}P - {ou_wrong}L</div></div>
  </div>
</div>"""

    # ===== R32 PREDICTIONS =====
    html += """<div class="rec-section"><div class="rec-card">
  <div class="rec-header">
    <h2> QF — Quarterfinal Predictions</h2>
    <div class="roi-badge">Target: 80% Win Rate</div>
  </div>
"""

    for rec in recommendations:
        if rec.get("result"):
            continue
        picks_html = ""
        for p in rec["picks"]:
            conf_color = {"high": "#5cb87a", "mid": "#d4a85c", "low": "#c8814a"}[p["confidence"]]
            picks_html += f"""<div class="rec-pick"><div class="pick-label">{p['type']} Pick</div><div class="pick-value">{p['label']}</div><div class="pick-odds">@ {p['odds']}</div><div class="pick-conf"><span class="conf-dot conf-{p['confidence']}"></span><span style="color:{conf_color}">{p['confidence'].title()}</span></div>{f'<div style="font-size:10px;color:#5aa9a9;margin-top:3px;">Kelly: {p.get("kelly_pct",0)}%</div>' if p.get("kelly_pct",0) > 0 else ''}</div>"""

        form1 = _form_html(rec.get("team1_form", ""))
        form2 = _form_html(rec.get("team2_form", ""))

        html += f"""<div class="rec-match">
  <div class="rec-match-top">
    <div><span class="rec-match-teams">{rec['team1']} <span class="vs">vs</span> {rec['team2']}<span class="score-pred">Pred: {rec['predicted_score']}</span></span><div class="form-info">{rec['team1']}: {form1} &nbsp;|&nbsp; {rec['team2']}: {form2}</div></div>
    <span class="rec-match-stage">{rec['stage']}</span>
  </div>
  <div class="rec-picks">{picks_html}</div>
</div>"""

    html += """</div></div>"""

    # ===== MATCH COMPLETED =====
    completed_list = [r for r in recommendations if r.get("result")]
    if completed_list:
        html += """<div class="completed-section"><div class="completed-box">
  <h3> Match Completed — Prediction vs Result</h3>
"""
        for rec in completed_list:
            actual = rec["result"]
            pred = rec["predicted_score"]
            a1, a2 = int(actual.split("-")[0]), int(actual.split("-")[1])
            p1, p2 = pred.split("-")
            correct = (int(p1) > int(p2) and a1 > a2) or (int(p1) < int(p2) and a1 < a2) or (int(p1) == int(p2) and a1 == a2)

            pick_results = ""
            for p in rec["picks"]:
                lbl, ods, tp = p["label"], p["odds"], p["type"]
                res_rs, res_rc = (_eval_ah(lbl, rec["team1"], rec["team2"], a1, a2) if tp == "AH" else _eval_ou(lbl, a1 + a2))
                pick_results += f"""<div class="rec-pick"><div class="pick-label">{tp} Pick</div><div class="pick-value">{lbl}</div><div class="pick-odds">@ {ods}</div><div style="margin-top:4px;font-size:11px;font-weight:600;color:{res_rc};">{res_rs}</div></div>"""

            html += f"""<div class="completed-row">
  <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
    <span class="comp-badge">COMPLETED</span>
    <span style="font-weight:600;color:#e8e6e3;">{rec['team1']}</span><span style="color:#9ca3a0;">vs</span><span style="font-weight:600;color:#e8e6e3;">{rec['team2']}</span>
  </div>
  <div style="font-size:13px;"><span style="color:#9ca3a0;">Pred:</span> <span style="font-weight:600;">{pred}</span> <span style="margin:0 6px;color:#262b33;">|</span> <span style="color:#9ca3a0;">Actual:</span> <span style="font-weight:600;color:#5cb87a;">{actual.replace('-', ' - ')}</span> <span style="margin-left:6px;color:{'#5cb87a' if correct else '#c8814a'};font-weight:600;">{'CORRECT' if correct else 'MISSED'}</span></div>
</div>
<div style="display:flex;gap:10px;flex-wrap:wrap;padding:8px 14px;margin-bottom:6px;">{pick_results}</div>"""

        html += """</div></div>"""

    html += f"""<div class="footer-note">Live QF Dashboard — Auto-refreshes every 30s &bull; Generated at {__import__('datetime').datetime.now().strftime('%H:%M:%S')} &bull; <a href="/" style="color:#5b8def;text-decoration:none;">Full Dashboard</a></div>
</div>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    return output_path
