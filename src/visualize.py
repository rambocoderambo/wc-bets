import plotly.graph_objects as go
import plotly.express as px


def generate_chart(bets, output_path="output/cumulative_pnl.html"):
    resolved = sorted(
        [b for b in bets if b.get("profit") is not None and b.get("bet_date_parsed")],
        key=lambda b: b["bet_date_parsed"]
    )

    dates = [b["bet_date_parsed"] for b in resolved]
    date_labels = [d.strftime("%b %d") for d in dates]
    profits = [b["profit"] for b in resolved]
    stakes = [b["stake"] for b in resolved]

    cum = 0
    cumulative = []
    for p in profits:
        cum += p
        cumulative.append(round(cum, 2))

    colors = []
    for b in resolved:
        s = b["status"]
        if s == "Won":
            colors.append("#5cb87a")
        elif s == "Lost":
            colors.append("#c8814a")
        elif s in ("Half-won", "Half-lost"):
            colors.append("#d4a85c")
        elif s == "Draw":
            colors.append("#9ca3a0")
        else:
            colors.append("#6b7278")

    sizes = [max(6, s / 8) for s in stakes]

    hover_texts = []
    for b in resolved:
        pl_str = f"+{b['profit']:.2f}" if b['profit'] > 0 else f"{b['profit']:.2f}"
        hover_texts.append(
            f"<b>{b['bet']}</b><br>"
            f"Date: {b['bet_date']}<br>"
            f"Market: {b['market']}<br>"
            f"Odds: {b['odds']}<br>"
            f"Stake: MYR {b['stake']}<br>"
            f"P&L: MYR {pl_str}<br>"
            f"Status: {b['status']}"
        )

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=dates,
        y=cumulative,
        mode="lines",
        name="Cumulative P&L",
        line=dict(color="#5b8def", width=2),
        fill="tozeroy",
        fillcolor="rgba(91,141,239,0.08)",
        hovertemplate="Cumulative: MYR %{y:.2f}<extra></extra>"
    ))

    for status_label, status_filter, color_val in [
        ("Won", "Won", "#5cb87a"),
        ("Lost", "Lost", "#c8814a"),
        ("Half/Draw", lambda s: s in ("Half-won", "Half-lost", "Draw"), "#d4a85c"),
    ]:
        indices = []
        for idx, b in enumerate(resolved):
            if isinstance(status_filter, str):
                match = b["status"] == status_filter
            else:
                match = status_filter(b["status"])
            if match:
                indices.append(idx)
        if not indices:
            continue
        fig.add_trace(go.Scatter(
            x=[dates[i] for i in indices],
            y=[profits[i] for i in indices],
            mode="markers",
            name=status_label,
            marker=dict(
                color=color_val,
                size=[sizes[i] for i in indices],
                line=dict(color=color_val, width=1),
            ),
            hovertemplate="%{customdata}<extra></extra>",
            customdata=[hover_texts[i] for i in indices],
            yaxis="y2"
        ))

    fig.update_layout(
        title=dict(
            text="Cumulative Profit & Loss Over Time",
            font=dict(color="#e8e6e3", size=16),
            x=0.02,
        ),
        paper_bgcolor="#0d1114",
        plot_bgcolor="#0d1114",
        xaxis=dict(
            title=dict(text="Bet Date", font=dict(color="#9ca3a0")),
            tickfont=dict(color="#9ca3a0"),
            gridcolor="rgba(38,43,51,0.5)",
            showgrid=True,
        ),
        yaxis=dict(
            title=dict(text="Cumulative P&L (MYR)", font=dict(color="#9ca3a0")),
            tickfont=dict(color="#9ca3a0"),
            gridcolor="rgba(38,43,51,0.5)",
            side="left",
        ),
        yaxis2=dict(
            title=dict(text="Bet P&L (MYR)", font=dict(color="#9ca3a0")),
            tickfont=dict(color="#9ca3a0"),
            gridcolor="rgba(38,43,51,0.0)",
            overlaying="y",
            side="right",
            showgrid=False,
        ),
        legend=dict(
            font=dict(color="#9ca3a0"),
            bgcolor="rgba(0,0,0,0)",
            orientation="h",
            y=1.1,
        ),
        hovermode="closest",
        hoverlabel=dict(
            bgcolor="#1c2129",
            bordercolor="#262b33",
            font=dict(color="#e8e6e3", size=13),
        ),
        margin=dict(l=60, r=60, t=50, b=40),
        height=400,
    )

    fig.write_html(output_path, include_plotlyjs="cdn", full_html=False)
    return output_path
