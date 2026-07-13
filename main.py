import os
import sys
sys.path.insert(0, "src")

from parser import parse_bets
from metrics import calculate_metrics
from visualize import generate_chart
from analysis import generate_analysis, generate_advice
from recommendations import generate_recommendations, R32_FIXTURES, R16_FIXTURES, QF_FIXTURES, SF_FIXTURES
from report import generate_report
from r32_report import generate_live_report


def split_bets(bets):
    """Split bets into separate periods by event matching fixture lists."""
    def _events(fixtures):
        return {f"{f['team1']} vs {f['team2']}" for f in fixtures}
    
    sf_evts = _events(SF_FIXTURES)
    qf_evts = _events(QF_FIXTURES)
    r16_evts = _events(R16_FIXTURES)
    r32_evts = _events(R32_FIXTURES)
    
    gs, r32, r16, qf, sf = [], [], [], [], []
    for b in bets:
        evt = b.get("event", "")
        if evt in sf_evts:
            sf.append(b)
        elif evt in qf_evts:
            qf.append(b)
        elif evt in r16_evts:
            r16.append(b)
        elif evt in r32_evts:
            r32.append(b)
        else:
            gs.append(b)
    return gs, r32, r16, qf, sf


def main():
    print("Parsing bets...")
    bets = parse_bets("data/Bets.txt")
    print(f"  {len(bets)} bets parsed")

    gs_bets, r32_bets, r16_bets, qf_bets, sf_bets = split_bets(bets)
    print(f"  GS: {len(gs_bets)} | R32: {len(r32_bets)} | R16: {len(r16_bets)} | QF: {len(qf_bets)} | SF: {len(sf_bets)}")

    print("Calculating metrics...")
    metrics = calculate_metrics(bets)
    gs_metrics = calculate_metrics(gs_bets) if gs_bets else None
    r32_metrics = calculate_metrics(r32_bets) if r32_bets else None
    r16_metrics = calculate_metrics(r16_bets) if r16_bets else None
    qf_metrics = calculate_metrics(qf_bets) if qf_bets else None
    sf_metrics = calculate_metrics(sf_bets) if sf_bets else None
    print(f"  P&L: Overall={metrics['total_pnl']} | GS={gs_metrics['total_pnl'] if gs_metrics else 0} | R32={r32_metrics['total_pnl'] if r32_metrics else 0} | R16={r16_metrics['total_pnl'] if r16_metrics else 0} | QF={qf_metrics['total_pnl'] if qf_metrics else 0} | SF={sf_metrics['total_pnl'] if sf_metrics else 0}")

    print("Generating chart...")
    chart_path = "output/cumulative_pnl.html"
    generate_chart(bets, chart_path)

    print("Running analysis by period...")
    analysis = generate_analysis(bets, metrics)
    advice = generate_advice(bets, metrics, analysis)
    gs_a = generate_analysis(gs_bets, gs_metrics) if gs_bets else []
    gs_ad = generate_advice(gs_bets, gs_metrics, gs_a) if gs_bets else []
    r32_a = generate_analysis(r32_bets, r32_metrics) if r32_bets else []
    r32_ad = generate_advice(r32_bets, r32_metrics, r32_a) if r32_bets else []
    r16_a = generate_analysis(r16_bets, r16_metrics) if r16_bets else []
    r16_ad = generate_advice(r16_bets, r16_metrics, r16_a) if r16_bets else []
    qf_a = generate_analysis(qf_bets, qf_metrics) if qf_bets else []
    qf_ad = generate_advice(qf_bets, qf_metrics, qf_a) if qf_bets else []
    print(f"  Overall: {len(analysis)} | GS: {len(gs_a)} | R32: {len(r32_a)} | R16: {len(r16_a)} | QF: {len(qf_a)}")

    print("Generating knockout recommendations...")
    recommendations = generate_recommendations(bets, metrics)
    print(f"  {len(recommendations)} match recommendations")

    print("Building dashboard...")
    output_path = "output/dashboard.html"
    generate_report(bets, metrics, analysis, advice, recommendations, chart_path, output_path,
                    gs_analysis=gs_a, gs_advice=gs_ad,
                    r32_analysis=r32_a, r32_advice=r32_ad,
                    r16_analysis=r16_a, r16_advice=r16_ad,
                    qf_analysis=qf_a, qf_advice=qf_ad)
    
    live_path = "output/live_qf.html"
    generate_live_report(bets, metrics, analysis, advice, recommendations, chart_path, live_path)
    import shutil
    shutil.copy2(output_path, "output/index.html")
    print(f"  Live QF report: file://{os.path.abspath(live_path)}")
    
    print(f"\nDone! Dashboard saved to {output_path}")
    print(f"Open in browser: file://{os.path.abspath(output_path)}")


if __name__ == "__main__":
    main()
