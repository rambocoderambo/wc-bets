import os
import sys
sys.path.insert(0, "src")

from parser import parse_bets
from metrics import calculate_metrics
from visualize import generate_chart
from analysis import generate_analysis, generate_advice
from recommendations import generate_recommendations, R32_FIXTURES
from report import generate_report
from r32_report import generate_live_report


def split_bets(bets):
    """Split bets into group stage vs knockout (R32+R16) based on event matching fixtures."""
    from recommendations import R32_FIXTURES, R16_FIXTURES, QF_FIXTURES
    ko_events = set()
    for f in R32_FIXTURES + R16_FIXTURES + QF_FIXTURES:
        ko_events.add(f"{f['team1']} vs {f['team2']}")
    gs, ko = [], []
    for b in bets:
        if b.get("event", "") in ko_events:
            ko.append(b)
        else:
            gs.append(b)
    return gs, ko


def main():
    print("Parsing bets...")
    bets = parse_bets("data/Bets.txt")
    print(f"  {len(bets)} bets parsed")

    gs_bets, r32_bets = split_bets(bets)
    print(f"  Group stage: {len(gs_bets)} | R32: {len(r32_bets)}")

    print("Calculating metrics...")
    metrics = calculate_metrics(bets)
    gs_metrics = calculate_metrics(gs_bets)
    r32_metrics = calculate_metrics(r32_bets)
    print(f"  Overall: {metrics['total_pnl']} | GS: {gs_metrics['total_pnl']} | R32: {r32_metrics['total_pnl']}")

    print("Generating chart...")
    chart_path = "output/cumulative_pnl.html"
    generate_chart(bets, chart_path)
    print(f"  Chart saved to {chart_path}")

    print("Running analysis...")
    analysis = generate_analysis(bets, metrics)
    advice = generate_advice(bets, metrics, analysis)
    gs_analysis = generate_analysis(gs_bets, gs_metrics)
    gs_advice = generate_advice(gs_bets, gs_metrics, gs_analysis)
    r32_analysis = generate_analysis(r32_bets, r32_metrics)
    r32_advice = generate_advice(r32_bets, r32_metrics, r32_analysis)
    print(f"  Overall: {len(analysis)} findings | GS: {len(gs_analysis)} | R32: {len(r32_analysis)}")

    print("Generating R32 recommendations...")
    recommendations = generate_recommendations(bets, metrics)
    print(f"  {len(recommendations)} match recommendations")

    print("Building dashboard...")
    output_path = "output/dashboard.html"
    generate_report(bets, metrics, analysis, advice, recommendations, chart_path, output_path,
                    gs_analysis=gs_analysis, gs_advice=gs_advice,
                    r32_analysis=r32_analysis, r32_advice=r32_advice)
    
    live_path = "output/live_r32.html"
    generate_live_report(bets, metrics, analysis, advice, recommendations, chart_path, live_path)
    import shutil
    shutil.copy2(live_path, "output/index.html")
    print(f"  Live R32 report: file://{os.path.abspath(live_path)}")
    
    print(f"\nDone! Dashboard saved to {output_path}")
    print(f"Open in browser: file://{os.path.abspath(output_path)}")


if __name__ == "__main__":
    main()
