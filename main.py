import os
import sys
sys.path.insert(0, "src")

from parser import parse_bets
from metrics import calculate_metrics
from visualize import generate_chart
from analysis import generate_analysis, generate_advice
from recommendations import generate_recommendations
from report import generate_report


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
    print(f"\nDone! Dashboard saved to {output_path}")
    print(f"Open in browser: file://{os.path.abspath(output_path)}")


if __name__ == "__main__":
    main()
