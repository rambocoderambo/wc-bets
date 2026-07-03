import os
import sys
sys.path.insert(0, "src")

from parser import parse_bets
from metrics import calculate_metrics
from visualize import generate_chart
from analysis import generate_analysis, generate_advice
from recommendations import generate_recommendations
from report import generate_report
from r32_report import generate_live_report


def main():
    print("Parsing bets...")
    bets = parse_bets("data/Bets.txt")
    print(f"  {len(bets)} bets parsed")

    print("Calculating metrics...")
    metrics = calculate_metrics(bets)
    print(f"  Win: {metrics['win_pct']}% | Loss: {metrics['loss_pct']}% | P&L: {metrics['total_pnl']}")
    print(f"  Avg stake: MYR {metrics['avg_stake']} | Best: {metrics['best_bet']['bet']} (+{metrics['best_bet']['profit']})")

    print("Generating chart...")
    chart_path = "output/cumulative_pnl.html"
    generate_chart(bets, chart_path)
    print(f"  Chart saved to {chart_path}")

    print("Running analysis...")
    analysis = generate_analysis(bets, metrics)
    advice = generate_advice(bets, metrics, analysis)
    print(f"  {len(analysis)} findings, {len(advice)} recommendations")

    print("Generating R32 recommendations...")
    recommendations = generate_recommendations(bets, metrics)
    print(f"  {len(recommendations)} match recommendations")

    print("Building dashboard...")
    output_path = "output/dashboard.html"
    generate_report(bets, metrics, analysis, advice, recommendations, chart_path, output_path)
    
    live_path = "output/live_r32.html"
    generate_live_report(bets, metrics, analysis, advice, recommendations, chart_path, live_path)
    # Also copy as index.html for Vercel root
    import shutil
    shutil.copy2(live_path, "output/index.html")
    print(f"  Live R32 report: file://{os.path.abspath(live_path)}")
    
    print(f"\nDone! Dashboard saved to {output_path}")
    print(f"Open in browser: file://{os.path.abspath(output_path)}")


if __name__ == "__main__":
    main()
