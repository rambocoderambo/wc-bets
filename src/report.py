import os
from completed_render import render_completed


def generate_report(bets, metrics, analysis, advice, recommendations, chart_path, output_path="output/dashboard.html",
                    gs_analysis=None, gs_advice=None, r32_analysis=None, r32_advice=None,
                    r16_analysis=None, r16_advice=None, qf_analysis=None, qf_advice=None):
    chart_html = ""
    if os.path.exists(chart_path):
        with open(chart_path, "r", encoding="utf-8") as f:
            chart_html = f.read()

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Betting Analytics Dashboard</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0d1114; color: #d4d4d4; padding: 24px; }}
  .container {{ max-width: 1500px; margin: 0 auto; }}
  h1 {{ font-size: 28px; font-weight: 700; margin-bottom: 4px; color: #e8e6e3; }}
  .subtitle {{ color: #9ca3a0; font-size: 14px; margin-bottom: 28px; }}

  .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 14px; margin-bottom: 24px; }}
  .card {{ background: #161a20; border: 1px solid #262b33; border-radius: 12px; padding: 18px 20px; }}
  .card:hover {{ border-color: #5b8def; }}
  .card .label {{ font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: .6px; color: #9ca3a0; margin-bottom: 8px; }}
  .card .value {{ font-size: 30px; font-weight: 700; line-height: 1.1; }}
  .card .value.green {{ color: #5cb87a; }}
  .card .value.amber {{ color: #d4a85c; }}
  .card .value.orange {{ color: #c8814a; }}
  .card .value.teal {{ color: #5aa9a9; }}
  .card .sub {{ font-size: 13px; color: #9ca3a0; margin-top: 6px; }}

  .two-col {{ display: grid; grid-template-columns: 2fr 1fr; gap: 16px; margin-bottom: 24px; }}
  @media (max-width: 900px) {{ .two-col {{ grid-template-columns: 1fr; }} }}

  .chart-card {{ background: #161a20; border: 1px solid #262b33; border-radius: 12px; padding: 20px; }}
  .chart-card h2 {{ font-size: 16px; font-weight: 600; margin-bottom: 16px; color: #e8e6e3; }}

  .summary-table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
  .summary-table th {{ text-align: left; padding: 8px 0 12px; color: #9ca3a0; font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: .5px; border-bottom: 1px solid #262b33; }}
  .summary-table td {{ padding: 10px 0; border-bottom: 1px solid #1f242b; }}
  .summary-table tr:last-child td {{ border-bottom: none; }}
  .badge {{ display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: 12px; font-weight: 600; }}
  .badge-green {{ background: rgba(92,184,122,.15); color: #5cb87a; }}
  .badge-amber {{ background: rgba(212,168,92,.15); color: #d4a85c; }}
  .badge-orange {{ background: rgba(200,129,74,.15); color: #c8814a; }}
  .badge-gray {{ background: rgba(156,163,160,.15); color: #9ca3a0; }}

  .analysis-section {{ margin-top: 24px; }}
  .analysis-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
  @media (max-width: 900px) {{ .analysis-grid {{ grid-template-columns: 1fr; }} }}
  .analysis-card {{ background: #161a20; border: 1px solid #262b33; border-radius: 12px; padding: 20px; }}
  .analysis-card h3 {{ font-size: 15px; font-weight: 600; margin-bottom: 12px; padding-bottom: 10px; border-bottom: 1px solid #262b33; color: #e8e6e3; }}
  .analysis-card p, .analysis-card li {{ font-size: 14px; line-height: 1.7; color: #c8c6c0; margin-bottom: 8px; }}
  .analysis-card ul {{ list-style: none; }}
  .analysis-card ul li::before {{ content: "\\2022"; color: #5b8def; font-weight: bold; display: inline-block; width: 16px; }}

  .insight {{ border-left: 3px solid #5b8def; padding: 12px 16px; background: rgba(91,141,239,.06); border-radius: 0 8px 8px 0; margin-top: 12px; font-size: 14px; line-height: 1.6; color: #c8c6c0; }}
  .insight.warning {{ border-left-color: #d4a85c; background: rgba(212,168,92,.06); }}
  .insight.danger {{ border-left-color: #c8814a; background: rgba(200,129,74,.06); }}
  .insight.success {{ border-left-color: #5cb87a; background: rgba(92,184,122,.06); }}
  .insight.info {{ border-left-color: #5b8def; background: rgba(91,141,239,.06); }}

  .rec-section {{ margin-top: 24px; }}
  .rec-card {{ background: linear-gradient(135deg, #161a20 0%, #1a1f28 100%); border: 1px solid #262b33; border-radius: 12px; padding: 24px; }}
  .rec-header {{ display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-bottom: 20px; }}
  .rec-header h2 {{ font-size: 18px; font-weight: 700; color: #e8e6e3; }}
  .rec-header .roi-badge {{ background: rgba(92,184,122,.15); color: #5cb87a; padding: 6px 16px; border-radius: 999px; font-size: 13px; font-weight: 600; }}
  .rec-match {{ background: #13181d; border: 1px solid #1f242c; border-radius: 10px; padding: 16px 20px; margin-bottom: 12px; }}
  .rec-match-top {{ display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 10px; }}
  .rec-match-teams {{ font-size: 16px; font-weight: 600; color: #e8e6e3; }}
  .rec-match-teams .vs {{ color: #6b7278; font-weight: 400; margin: 0 8px; }}
  .rec-match-teams .score-pred {{ font-size: 13px; color: #d4a85c; font-weight: 400; margin-left: 12px; }}
  .rec-match-stage {{ font-size: 12px; color: #9ca3a0; background: #1f242c; padding: 3px 10px; border-radius: 6px; }}
  .rec-picks {{ display: flex; gap: 12px; flex-wrap: wrap; }}
  .rec-pick {{ background: #1a1e27; border: 1px solid #262b33; border-radius: 8px; padding: 10px 16px; flex: 1; min-width: 160px; }}
  .rec-pick .pick-label {{ font-size: 11px; color: #9ca3a0; text-transform: uppercase; letter-spacing: .4px; margin-bottom: 4px; }}
  .rec-pick .pick-value {{ font-size: 14px; font-weight: 600; color: #d4d4d4; }}
  .rec-pick .pick-odds {{ font-size: 13px; color: #5cb87a; margin-top: 2px; }}
  .rec-pick .pick-conf {{ display: flex; align-items: center; gap: 6px; margin-top: 6px; font-size: 12px; }}
  .conf-dot {{ width: 8px; height: 8px; border-radius: 50%; display: inline-block; }}
  .conf-high {{ background: #5cb87a; }}
  .conf-mid {{ background: #d4a85c; }}
  .conf-low {{ background: #c8814a; }}
  .rec-reason {{ font-size: 13px; color: #9ca3a0; margin-top: 8px; line-height: 1.5; padding-top: 8px; border-top: 1px solid #1f242c; }}
  .form-info {{ font-size: 12px; color: #9ca3a0; }}
  .form-w {{ color: #5cb87a; font-weight: bold; }}
  .form-d {{ color: #5b8def; font-weight: bold; }}
  .form-l {{ color: #6b7278; font-weight: bold; }}

  .history-section {{ margin-top: 24px; }}
  .history-card {{ background: #161a20; border: 1px solid #262b33; border-radius: 12px; padding: 20px; overflow: hidden; }}
  .history-card h2 {{ font-size: 16px; font-weight: 600; margin-bottom: 16px; color: #e8e6e3; }}
  .history-table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  .history-table th {{ text-align: left; padding: 10px 12px; color: #9ca3a0; font-weight: 600; font-size: 11px; text-transform: uppercase; letter-spacing: .5px; border-bottom: 1px solid #262b33; background: #13181d; position: sticky; top: 0; }}
  .history-table td {{ padding: 8px 12px; border-bottom: 1px solid #1f242b; color: #c8c6c0; }}
  .history-table tr {{ cursor: pointer; transition: background .15s; }}
  .history-table tbody tr:hover {{ background: #1c2129; }}
  .history-table .detail-row {{ display: none; }}
  .history-table .detail-row td {{ padding: 12px 16px 16px 40px; background: #101418; }}
  .detail-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 10px; }}
  .detail-grid .item {{ font-size: 13px; }}
  .detail-grid .item .lbl {{ color: #9ca3a0; font-size: 11px; text-transform: uppercase; letter-spacing: .3px; }}
  .detail-grid .item .val {{ color: #d4d4d4; margin-top: 2px; }}
  .arrow {{ display: inline-block; transition: transform .2s; margin-right: 6px; color: #9ca3a0; font-size: 11px; }}
  .arrow.open {{ transform: rotate(90deg); }}
  .search-box {{ background: #13181d; border: 1px solid #262b33; border-radius: 6px; padding: 8px 14px; color: #d4d4d4; font-size: 13px; width: 240px; outline: none; }}
  .search-box:focus {{ border-color: #5b8def; }}
  .search-box::placeholder {{ color: #6b7278; }}

  .team-bar {{ display: flex; align-items: center; gap: 8px; margin: 4px 0; font-size: 13px; }}
  .team-bar-fill {{ height: 6px; border-radius: 3px; transition: width .3s; }}
</style>
</head>
<body>
<div class="container">
  <h1> Betting Analytics Dashboard</h1>
  <div class="subtitle">World Cup 2026 &bull; {metrics['total_bets']} bets from {metrics['first_date']} to {metrics['last_date']} ({metrics['days_active']} days) &bull; Turnover: MYR {metrics['total_stake']:.2f}</div>

  <div class="metrics-grid">
    <div class="card">
      <div class="label">Win Rate</div>
      <div class="value green">{metrics['win_pct']}%</div>
      <div class="sub">{metrics['win_count']} Won / {metrics['win_count'] + metrics['loss_count']} resolved</div>
    </div>
    <div class="card">
      <div class="label">Loss Rate</div>
      <div class="value orange">{metrics['loss_pct']}%</div>
      <div class="sub">{metrics['loss_count']} Lost / {metrics['win_count'] + metrics['loss_count']} resolved</div>
    </div>
    <div class="card">
      <div class="label">Push / Half / Void</div>
      <div class="value amber">{metrics['push_pct']}%</div>
      <div class="sub">{metrics['draw_count']} Draws, Halfs &amp; Cashouts</div>
    </div>
    <div class="card">
      <div class="label">Best Bet</div>
      <div class="value green">+MYR {metrics['best_bet']['profit']:.0f}</div>
      <div class="sub">{metrics['best_bet']['bet']} &bull; {metrics['best_bet']['market']}</div>
    </div>
    <div class="card">
      <div class="label">Best ROI Bet</div>
      <div class="value green">+{metrics['best_roi_pct']}%</div>
      <div class="sub">{metrics['best_roi']['bet']} &bull; Odds {metrics['best_roi']['odds']}</div>
    </div>
    <div class="card">
      <div class="label">Worst Loss</div>
      <div class="value orange">-MYR {abs(metrics['worst_loss']['profit']):.0f}</div>
      <div class="sub">{metrics['worst_loss']['bet']}</div>
    </div>
    <div class="card">
      <div class="label">Avg Bet Size</div>
      <div class="value amber">MYR {metrics['avg_stake']:.2f}</div>
      <div class="sub">Total staked: MYR {metrics['total_stake']:.2f}</div>
    </div>
    <div class="card">
      <div class="label">Net P&amp;L</div>
      <div class="value {'green' if metrics['total_pnl'] >= 0 else 'orange'}">{'+' if metrics['total_pnl'] >= 0 else ''}MYR {metrics['total_pnl']:.2f}</div>
      <div class="sub">Return: MYR {metrics['total_return']:.2f} on {metrics['total_stake']:.0f} staked</div>
    </div>
  </div>

  <!-- R16 PREDICTIONS -->
  <div class="rec-section">
    <div class="rec-card">
      <div class="rec-header">
        <div>
          <h2> Quarterfinal Predictions</h2>
          <div style="font-size:13px;color:#9ca3a0;margin-top:4px;">Asian Handicap &amp; O/U picks for the remaining QF matches</div>
        </div>
        <div class="roi-badge">Target: 80% Win Rate</div>
      </div>
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

    # Upcoming matches
    for rec in recommendations:
        if rec.get("result"):
            continue
        picks_html = ""
        for p in rec["picks"]:
            conf_color = {"high": "#5cb87a", "mid": "#d4a85c", "low": "#c8814a"}[p["confidence"]]
            kelly = p.get("kelly_pct", 0)
            kelly_str = f'Stake: {kelly}%' if kelly > 0 else ''
            picks_html += f"""
            <div class="rec-pick">
              <div class="pick-label">{p['type']} Pick</div>
              <div class="pick-value">{p['label']}</div>
              <div class="pick-odds">@ {p['odds']}</div>
              <div class="pick-conf">
                <span class="conf-dot conf-{p['confidence']}"></span>
                <span style="color:{conf_color}">{p['confidence'].title()}</span>
              </div>
              {f'<div style="font-size:11px;color:#5aa9a9;margin-top:4px;">{kelly_str}</div>' if kelly_str else ''}
            </div>"""

        form1 = _form_html(rec.get("team1_form", ""))
        form2 = _form_html(rec.get("team2_form", ""))

        extra_html = f'<div class="rec-picks">{picks_html}</div><div class="rec-reason">{rec["reason"]}</div><div class="rec-reason" style="margin-top:6px;font-size:12px;cursor:pointer;color:#5b8def;" onclick="this.nextElementSibling.style.display=this.nextElementSibling.style.display===&quot;block&quot;?&quot;none&quot;:&quot;block&quot;;">[+] Score Analysis</div><div class="rec-reason" style="display:none;margin-top:6px;padding:10px;background:#13181d;border-radius:6px;font-size:12px;line-height:1.7;color:#c8c6c0;">' + (rec.get("score_reason", "No detailed analysis available.") or "") + '</div>'

        html += f"""
      <div class="rec-match">
        <div class="rec-match-top">
          <div>
            <span class="rec-match-teams">
              {rec['team1']} <span class="vs">vs</span> {rec['team2']}
              <span class="score-pred">Predicted: {rec['predicted_score']}</span>
            </span>
            <div class="form-info">{rec['team1']}: {form1} &nbsp;|&nbsp; {rec['team2']}: {form2}</div>
          </div>
          <span class="rec-match-stage">{rec['stage']}</span>
        </div>
        {extra_html}
      </div>"""

    # Computed completed match stats
    import re as _re
    total_correct = 0
    total_matches = 0
    ah_correct = 0
    ah_wrong = 0
    ah_push = 0
    ou_correct = 0
    ou_wrong = 0
    ou_push = 0

    for rec in recommendations:
        if not rec.get("result"):
            continue
        total_matches += 1
        parts = rec["result"].split("-")
        a1, a2 = int(parts[0]), int(parts[1])

        # Score direction check
        p1, p2 = rec["predicted_score"].split("-")
        score_correct = (int(p1) > int(p2) and a1 > a2) or (int(p1) < int(p2) and a1 < a2) or (int(p1) == int(p2) and a1 == a2)
        if score_correct:
            total_correct += 1

        # Evaluate each pick
        for pick in rec["picks"]:
            lbl = pick["label"]
            if pick["type"] == "AH":
                m = _re.match(r"^(.+?)\s+([-+]?[\d.]+|PK)$", lbl)
                if m:
                    pt = m.group(1).strip()
                    hv = m.group(2)
                    if hv == "PK":
                        w = (pt == rec["team1"] and a1 > a2) or (pt == rec["team2"] and a2 > a1)
                        psh = a1 == a2
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
                    dr = m.group(1)
                    lv = float(m.group(2))
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
        html += f"""<div style="margin-top:24px;padding:18px 20px;background:#1a2520;border:1px solid #2a3a2a;border-radius:10px;">
        <h3 style="font-size:15px;font-weight:600;color:#5cb87a;margin-bottom:14px;"> Match Completed — Accuracy Summary</h3>
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;">
          <div style="background:#0d1114;border-radius:8px;padding:14px;text-align:center;">
            <div style="font-size:11px;color:#9ca3a0;text-transform:uppercase;letter-spacing:0.4px;">Matches</div>
            <div style="font-size:26px;font-weight:700;color:#e8e6e3;">{total_matches}</div>
            <div style="font-size:12px;color:#5cb87a;">{total_correct}/{total_matches} correct ({pct}%)</div>
          </div>
          <div style="background:#0d1114;border-radius:8px;padding:14px;text-align:center;">
            <div style="font-size:11px;color:#9ca3a0;text-transform:uppercase;letter-spacing:0.4px;">Asian Handicap</div>
            <div style="font-size:26px;font-weight:700;color:#5cb87a;">{ah_pct}%</div>
            <div style="font-size:12px;color:#d4d4d4;">{ah_correct}W - {ah_push}P - {ah_wrong}L</div>
          </div>
          <div style="background:#0d1114;border-radius:8px;padding:14px;text-align:center;">
            <div style="font-size:11px;color:#9ca3a0;text-transform:uppercase;letter-spacing:0.4px;">Over / Under</div>
            <div style="font-size:26px;font-weight:700;color:#5cb87a;">{ou_pct}%</div>
            <div style="font-size:12px;color:#d4d4d4;">{ou_correct}W - {ou_push}P - {ou_wrong}L</div>
          </div>
        </div>
      </div>"""

    # Completed matches section
    completed_rendered = False
    for rec in recommendations:
        if not rec.get("result"):
            continue
        if not completed_rendered:
            html += """<div style="margin-top:24px;padding:18px 20px;background:#1a2520;border:1px solid #2a3a2a;border-radius:10px;">
        <h3 style="font-size:15px;font-weight:600;color:#5cb87a;margin-bottom:14px;"> Match Completed — Prediction vs Result</h3>
"""
            completed_rendered = True
        a_parts = rec["result"].split("-")
        a1, a2 = int(a_parts[0]), int(a_parts[1])
        html += render_completed(rec, a1, a2)
    if completed_rendered:
        html += """</div>"""

    html += """
    </div>
  </div>
  <!-- END R32 -->

  <!-- Chart + Market Sidebar -->
  <div class="two-col">
    <div class="chart-card">
"""

    if chart_html:
        html += f"<div style='height:400px;'>{chart_html}</div>"
    else:
        html += "<p style='color:#9ca3a0;'>Chart not available</p>"

    # Market breakdown
    market_rows = ""
    sorted_markets = sorted(
        metrics["market_stats"].items(),
        key=lambda x: x[1]["pnl"] if isinstance(x[1], dict) else 0
    )
    for mkt, stats in sorted_markets:
        if not isinstance(stats, dict):
            continue
        pnl = stats["pnl"]
        total_m = stats["total"]
        wins = stats["wins"]
        win_pct = round(wins / total_m * 100, 1) if total_m > 0 else 0
        pnl_color = "#5cb87a" if pnl >= 0 else "#c8814a"
        badge_class = "badge-green" if win_pct >= 50 else "badge-orange"
        market_rows += f"""
            <tr><td>{mkt}</td><td>{stats['bets']}</td><td style="color:{pnl_color};font-size:14px">{'+' if pnl >= 0 else ''}MYR {pnl:.2f}</td><td><span class="badge {badge_class}">{win_pct}%</span></td></tr>"""

    # Team performance
    team_rows = ""
    sorted_teams = sorted(
        metrics["team_stats"].items(),
        key=lambda x: x[1]["pnl"],
        reverse=True
    )[:8]
    max_abs_pnl = max(
        (abs(s["pnl"]) for _, s in sorted_teams),
        default=1
    )
    for team, stats in sorted_teams:
        pnl = stats["pnl"]
        pnl_color = "#5cb87a" if pnl >= 0 else "#c8814a"
        bar_width = max(3, abs(pnl) / max_abs_pnl * 100)
        bar_color = "#5cb87a" if pnl >= 0 else "#c8814a"
        wl = f"{stats['wins']}-{stats['losses']}-{stats['draws']}"
        team_rows += f"""
            <div class="team-bar">
              <span style="width:120px;color:#d4d4d4;">{team}</span>
              <div style="flex:1;background:#1f242c;border-radius:3px;height:6px;">
                <div class="team-bar-fill" style="width:{bar_width:.0f}%;background:{bar_color};"></div>
              </div>
              <span style="width:80px;text-align:right;color:{pnl_color};">{'+' if pnl >= 0 else ''}MYR {pnl:.0f}</span>
              <span style="width:60px;text-align:right;color:#9ca3a0;font-size:11px;">({wl})</span>
            </div>"""

    html += f"""
    </div>
    <div class="chart-card">
      <h2>Market Breakdown</h2>
      <table class="summary-table">
        <thead><tr><th>Market</th><th>Bets</th><th>P&amp;L</th><th>Win %</th></tr></thead>
        <tbody>{market_rows}</tbody>
      </table>
      <div style="margin-top:16px;padding-top:14px;border-top:1px solid #262b33;">
        <div style="font-size:13px;color:#9ca3a0;margin-bottom:8px;">Team Performance Index</div>
        {team_rows}
      </div>
      <div style="margin-top:16px;padding-top:14px;border-top:1px solid #262b33;">
        <div style="font-size:12px;color:#9ca3a0;">Max Drawdown: <span style="color:#c8814a;">MYR {metrics['max_drawdown']:.2f}</span></div>
        <div style="font-size:12px;color:#9ca3a0;">Peak: <span style="color:#5cb87a;">MYR {metrics['peak_cum']:.2f}</span> &bull; Low: <span style="color:#c8814a;">MYR {metrics['low_cum']:.2f}</span></div>
        <div style="font-size:12px;color:#9ca3a0;">Longest Win Streak: <span style="color:#5cb87a;">{metrics['streaks']['longest_win_streak']}</span> &bull; Longest Loss: <span style="color:#c8814a;">{metrics['streaks']['longest_loss_streak']}</span></div>
      </div>
    </div>
  </div>

  <!-- Analysis + Advice -->
  <div class="analysis-section">
    <div style="font-size:14px;color:#9ca3a0;margin-bottom:16px;font-weight:600;">BETTING PERFORMANCE BY STAGE</div>
"""

    def _render_block(label, an_data, ad_data):
        from datetime import datetime
        ts = datetime.now().strftime("%d %b %Y %H:%M")
        b = ""
        b += '<div style="margin-bottom:20px;background:#161a20;border:1px solid #262b33;border-radius:12px;padding:20px;">'
        b += '<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:12px;">'
        b += '<h3 style="font-size:15px;font-weight:600;color:#e8e6e3;margin:0;">' + label + '</h3>'
        b += '<span style="background:#5b8def;color:#fff;padding:2px 10px;border-radius:6px;font-size:11px;font-weight:600;">UPDATED</span></div>'
        b += '<div style="font-size:11px;color:#6b7278;margin-bottom:10px;">Last updated: ' + ts + '</div>'
        b += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">'
        b += '<div><h4 style="font-size:13px;font-weight:600;color:#d4a85c;margin-bottom:8px;">Strategy Analysis</h4><ul style="list-style:none;padding:0;margin:0;">'
        for it in an_data:
            b += '<li style="font-size:13px;line-height:1.6;color:#c8c6c0;margin-bottom:6px;"><strong>' + it["title"] + ':</strong> ' + it["body"] + '</li>'
        b += '</ul></div>'
        b += '<div><h4 style="font-size:13px;font-weight:600;color:#5aa9a9;margin-bottom:8px;">Actionable Advice</h4>'
        cm = {"danger": "#c8814a", "warning": "#d4a85c", "info": "#5b8def", "success": "#5cb87a"}
        for it in ad_data:
            c = cm.get(it["type"], "#5b8def")
            rv, gv, bv = int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)
            b += '<div style="border-left:3px solid ' + c + ';padding:8px 12px;background:rgba(' + str(rv) + ',' + str(gv) + ',' + str(bv) + ',.06);border-radius:0 6px 6px 0;margin-bottom:8px;font-size:13px;line-height:1.5;color:#c8c6c0;"><strong>' + it["title"] + '.</strong> ' + it["body"] + '</div>'
        b += '</div></div></div>'
        return b

    if gs_analysis and gs_advice:
        html += _render_block("Group Stage (Before R32)", gs_analysis, gs_advice)
    if r32_analysis and r32_advice:
        html += _render_block("Round of 32", r32_analysis, r32_advice)
    if r16_analysis and r16_advice:
        html += _render_block("Round of 16", r16_analysis, r16_advice)
    if qf_analysis and qf_advice:
        html += _render_block("Quarterfinals", qf_analysis, qf_advice)
    html += _render_block("Overall (All Bets)", analysis, advice)

    html += """
  </div>
  <!-- End Analysis + Advice -->

  <!-- Bet History -->
  <div class="history-section">
    <div class="history-card">
      <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;margin-bottom:16px;">
        <h2 style="margin-bottom:0;">Full Bet History</h2>
        <input type="text" class="search-box" id="betSearch" placeholder="Search teams, markets..." oninput="filterBets()">
      </div>
      <div style="overflow-x:auto;">
        <table class="history-table" id="betTable">
          <thead>
            <tr>
              <th style="width:28px"></th>
              <th>Date</th>
              <th>Bet</th>
              <th>Market</th>
              <th>Odds</th>
              <th>Stake</th>
              <th>Return</th>
              <th>P&amp;L</th>
              <th>Status</th>
              <th>Result</th>
            </tr>
          </thead>
          <tbody id="betBody"></tbody>
        </table>
      </div>
    </div>
  </div>
</div>

<script>
const betData = """ + _bets_to_json(bets) + """;

function renderTable(data) {
  const tbody = document.getElementById('betBody');
  tbody.innerHTML = '';
  data.forEach((b, i) => {
    const plClass = b.pl > 0 ? 'green' : b.pl < 0 ? 'orange' : 'amber';
    const statusBadge = b.status === 'Won' ? 'badge-green' :
      b.status === 'Lost' ? 'badge-orange' :
      b.status === 'Draw' ? 'badge-amber' : 'badge-gray';
    const plStr = (b.pl > 0 ? '+' : '') + b.pl.toFixed(2);
    const tr = document.createElement('tr');
    tr.setAttribute('onclick', 'toggleDetail(' + i + ')');
    tr.innerHTML = '<td><span class=\"arrow\" id=\"arrow-' + i + '\">\\u25b6</span></td>' +
      '<td style=\"color:#d4d4d4\">' + b.date + '</td>' +
      '<td style=\"color:#e8e6e3;font-weight:600\">' + b.team + '</td>' +
      '<td>' + b.market + '</td>' +
      '<td>' + b.odds + '</td>' +
      '<td>MYR ' + b.stake + '</td>' +
      '<td>MYR ' + b.ret + '</td>' +
      '<td class=\"value ' + plClass + '\" style=\"font-size:14px;font-weight:600\">MYR ' + plStr + '</td>' +
      '<td><span class=\"badge ' + statusBadge + '\">' + b.status + '</span></td>' +
      '<td>' + (b.result || '-') + '</td>';
    tbody.appendChild(tr);
    const dr = document.createElement('tr');
    dr.id = 'detail-' + i;
    dr.className = 'detail-row';
    dr.innerHTML = '<td colspan=\"10\"><div class=\"detail-grid\">' +
      '<div class=\"item\"><div class=\"lbl\">Ticket ID</div><div class=\"val\">' + (b.ticketId || '-') + '</div></div>' +
      '<div class=\"item\"><div class=\"lbl\">Event</div><div class=\"val\">' + (b.evt || '-') + '</div></div>' +
      '<div class=\"item\"><div class=\"lbl\">League</div><div class=\"val\">World Cup 2026</div></div>' +
      '<div class=\"item\"><div class=\"lbl\">Odds</div><div class=\"val\">' + b.odds + ' EU</div></div>' +
      '<div class=\"item\"><div class=\"lbl\">Stake</div><div class=\"val\">MYR ' + b.stake + '</div></div>' +
      '<div class=\"item\"><div class=\"lbl\">Return</div><div class=\"val\">MYR ' + b.ret + '</div></div>' +
      '<div class=\"item\"><div class=\"lbl\">Profit</div><div class=\"val\" style=\"color:' + (b.pl > 0 ? '#5cb87a' : b.pl < 0 ? '#c8814a' : '#d4a85c') + '\">MYR ' + plStr + '</div></div>' +
      '</div></td>';
    tbody.appendChild(dr);
  });
}

function toggleDetail(i) {
  const row = document.getElementById('detail-' + i);
  const arrow = document.getElementById('arrow-' + i);
  const isOpen = row.style.display === 'table-row';
  row.style.display = isOpen ? 'none' : 'table-row';
  arrow.className = isOpen ? 'arrow' : 'arrow open';
}

function filterBets() {
  const q = document.getElementById('betSearch').value.toLowerCase();
  const filtered = betData.filter(b =>
    b.team.toLowerCase().includes(q) ||
    b.market.toLowerCase().includes(q) ||
    (b.evt || '').toLowerCase().includes(q) ||
    b.status.toLowerCase().includes(q)
  );
  renderTable(filtered);
}

renderTable(betData.reverse());
</script>

<style>
.btn { padding:8px 20px; border:none; border-radius:6px; font-size:13px; font-weight:600; cursor:pointer; }
.btn-primary { background:#5b8def; color:#fff; }
.btn-secondary { background:#262b33; color:#9ca3a0; }
.btn-primary:hover { background:#4a7de0; }
.btn-secondary:hover { background:#2d3542; }
.toast { position:fixed; bottom:90px; right:24px; background:#1c2129; border:1px solid #262b33; border-radius:8px; padding:12px 18px; color:#d4d4d4; font-size:13px; display:none; z-index:1001; max-width:300px; }
.toast.show { display:block; animation:fadeIn 0.3s; }
@keyframes fadeIn { from{opacity:0;transform:translateY(10px)} to{opacity:1;transform:translateY(0)} }
.form-card { background:#1a1f28; border:1px solid #262b33; border-radius:12px; padding:20px 24px; margin-bottom:24px; }
.form-card h3 { font-size:16px; font-weight:600; color:#e8e6e3; margin-bottom:12px; cursor:pointer; user-select:none; }
.form-card h3:hover { color:#5b8def; }
.form-row { display:grid; grid-template-columns:repeat(auto-fit, minmax(180px,1fr)); gap:12px; margin-bottom:12px; }
.form-row label { display:block; font-size:11px; color:#9ca3a0; margin-bottom:4px; text-transform:uppercase; letter-spacing:.4px; }
.form-row input,.form-row select { width:100%; padding:8px 10px; background:#13181d; border:1px solid #262b33; border-radius:6px; color:#d4d4d4; font-size:13px; outline:none; }
.form-row input:focus,.form-row select:focus { border-color:#5b8def; }
.form-actions { display:flex; gap:10px; justify-content:flex-end; margin-top:4px; }
.form-card textarea:focus { border-color:#5b8def; }
</style>
<script>
// Force-fix Plotly tooltip styling the moment they appear in the DOM
(function() {
  function fix(el) {
    if (!el || el.dataset.hoverfixed) return;
    el.dataset.hoverfixed = '1';
    el.style.setProperty('background', '#1c2129', 'important');
    el.style.setProperty('border', '1px solid #363b44', 'important');
    el.style.setProperty('border-radius', '6px', 'important');
    el.style.setProperty('box-shadow', '0 4px 12px rgba(0,0,0,0.4)', 'important');
    el.style.setProperty('color', '#e8e6e3', 'important');
    el.style.setProperty('font-size', '13px', 'important');
    // Fix all children (text lines inside tooltip)
    el.querySelectorAll('*').forEach(function(c) {
      c.style.setProperty('color', '#e8e6e3', 'important');
      c.style.setProperty('fill', '#e8e6e3', 'important');
      c.style.setProperty('font-size', '13px', 'important');
      if (c.tagName === 'RECT' || c.tagName === 'rect') {
        c.style.setProperty('fill', '#1c2129', 'important');
        c.style.setProperty('stroke', '#363b44', 'important');
      }
    });
  }
  // Scan every 200ms for new Plotly hover elements
  setInterval(function() {
    document.querySelectorAll('.hoverlayer .hovertext, .hoverlayer g.hovertext, [class*="hovertext"]').forEach(fix);
    // Also fix any rect inside hover groups
    document.querySelectorAll('.hoverlayer rect, .hoverlayer g rect').forEach(function(r) {
      r.style.setProperty('fill', '#1c2129', 'important');
      r.style.setProperty('stroke', '#363b44', 'important');
    });
    // Fix any text inside hover groups
    document.querySelectorAll('.hoverlayer text, .hoverlayer g text').forEach(function(t) {
      t.style.setProperty('fill', '#e8e6e3', 'important');
      t.style.setProperty('font-size', '13px', 'important');
    });
  }, 200);
})();
</script>

<div class="toast" id="toast"></div>

<div class="form-card" id="betFormCard">
  <h3 onclick="var d=document.getElementById('betFormBody');d.style.display=d.style.display==='none'?'grid':'none';"> Log New Bet &#9660;</h3>
  <div class="form-row" id="betFormBody">
    <div><label>Team (e.g. France -1.5)</label><input id="fTeam" placeholder="France -1.5"></div>
    <div><label>Odds</label><input id="fOdds" type="number" step="0.01" placeholder="1.85"></div>
    <div><label>Stake (MYR)</label><input id="fStake" type="number" step="0.1" placeholder="50"></div>
    <div><label>Status</label>
      <select id="fStatus">
        <option value="">Select...</option>
        <option value="Won">Won</option>
        <option value="Lost">Lost</option>
        <option value="Half-won">Half-won</option>
        <option value="Half-lost">Half-lost</option>
        <option value="Draw">Draw</option>
        <option value="Cashed Out">Cashed Out</option>
      </select>
    </div>
    <div><label>Market</label><input id="fMarket" value="FT Asian Handicap"></div>
    <div><label>Event</label><input id="fEvent" placeholder="France vs Sweden"></div>
    <div><label>Result (e.g. 2:0)</label><input id="fResult" placeholder="0:0"></div>
  </div>
  <div class="form-actions">
    <button class="btn btn-secondary" onclick="document.getElementById('fTeam').value='';document.getElementById('fOdds').value='';document.getElementById('fStake').value='';document.getElementById('fStatus').value='';">Clear</button>
    <button class="btn btn-primary" onclick="submitBet()">Log Bet</button>
  </div>
</div>

<div class="form-card">
  <h3 onclick="var d=document.getElementById('bulkPasteBody');d.style.display=d.style.display==='none'?'block':'none';"> Paste Bulk Bets &#9660;</h3>
  <div id="bulkPasteBody" style="display:none;">
    <textarea id="bulkData" rows="6" style="width:100%;background:#13181d;border:1px solid #262b33;border-radius:6px;color:#d4d4d4;font-size:13px;padding:10px;outline:none;resize:vertical;font-family:monospace;" placeholder="Paste your bet history here...&#10;&#10;e.g.&#10;2026/06/30 18:30&#9;France -1.5&#9;1.85&#9;50&#9;Won&#10;2026/06/30 12:58&#9;Norway -0.25&#9;1.87&#9;100&#9;Won"></textarea>
    <div class="form-actions" style="margin-top:8px;">
      <button class="btn btn-primary" onclick="submitBulk()">Parse &amp; Save</button>
    </div>
  </div>
</div>

<button class="btn btn-secondary" style="position:fixed;bottom:24px;right:24px;z-index:999;padding:10px 16px;border-radius:8px;" onclick="refreshOdds()">&#x21bb; Refresh Odds</button>

<script>
function toast(msg, color) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.style.borderLeft = '3px solid ' + (color || '#5cb87a');
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 3000);
}

async function submitBet() {
  const team = document.getElementById('fTeam').value.trim();
  const odds = parseFloat(document.getElementById('fOdds').value);
  const stake = parseFloat(document.getElementById('fStake').value);
  const status = document.getElementById('fStatus').value;
  if (!team || !odds || !stake || !status) { toast('Fill all required fields', '#c8814a'); return; }
  const market = document.getElementById('fMarket').value.trim() || 'FT Asian Handicap';
  const event = document.getElementById('fEvent').value.trim() || team.split(' ')[0] + ' vs Opponent';
  const result = document.getElementById('fResult').value.trim() || '0:0';
  toast('Logging bet...', '#5b8def');
  try {
    const r = await fetch('/api/log-bet', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ team, odds, stake, status, market, event, result })
    });
    const data = await r.json();
    if (data.ok) { toast('Bet logged! Refreshing...', '#5cb87a'); setTimeout(() => location.reload(), 1000); }
    else { toast('Error: ' + (data.error || 'Unknown'), '#c8814a'); }
  } catch(e) { toast('Server error. Is the server running?', '#c8814a'); }
}

async function submitBulk() {
  const data = document.getElementById('bulkData').value.trim();
  if (!data) { toast('Paste some bet data first', '#c8814a'); return; }
  toast('Parsing bulk bets...', '#5b8def');
  try {
    const r = await fetch('/api/parse-bulk', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ raw: data })
    });
    const j = await r.json();
    if (j.ok) { toast(j.message || 'Saved! Refreshing...', '#5cb87a'); setTimeout(() => location.reload(), 1000); }
    else { toast('Error: ' + (j.error || 'Unknown'), '#c8814a'); }
  } catch(e) { toast('Server error', '#c8814a'); }
}

async function refreshOdds() {
  toast('Refreshing odds...', '#5b8def');
  try {
    const r = await fetch('/api/refresh-odds', { method: 'POST' });
    const data = await r.json();
    if (data.ok) { toast('Dashboard refreshed!', '#5cb87a'); setTimeout(() => location.reload(), 1000); }
    else { toast('Error refreshing', '#c8814a'); }
  } catch(e) { toast('Server error', '#c8814a'); }
}
</script>
<div style="margin-top:40px;padding:16px 24px;border-top:1px solid #1f242c;font-size:12px;color:#6b7278;display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;">
  <span>WC Bets Analytics v1.1.0</span>
  <span>Betting data from Bets.txt &bull; 90 bets imported &bull; <a href="CHANGELOG.md" style="color:#5b8def;text-decoration:none;">Changelog</a></span>
</div>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return output_path


def _bets_to_json(bets):
    import json
    data = []
    for b in bets:
        if b.get("profit") is None:
            continue
        pl = b["profit"]
        pl_str = f"+{pl:.2f}" if pl >= 0 else f"{pl:.2f}"
        data.append({
            "date": b.get("bet_date", ""),
            "team": b.get("bet", ""),
            "market": b.get("market", ""),
            "odds": b.get("odds", 0),
            "stake": b.get("stake", 0),
            "ret": b.get("return", 0),
            "pl": pl,
            "pl_str": pl_str,
            "status": b.get("status", ""),
            "result": b.get("result", ""),
            "ticketId": b.get("ticket_id", ""),
            "evt": b.get("event", ""),
        })
    return json.dumps(data)
