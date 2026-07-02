import plotly.graph_objects as go


def generate_chart(bets, output_path="output/cumulative_pnl.html"):
    resolved = sorted(
        [b for b in bets if b.get("profit") is not None and b.get("bet_date_parsed")],
        key=lambda b: b["bet_date_parsed"]
    )

    dates = [b["bet_date_parsed"] for b in resolved]
    profits = [b["profit"] for b in resolved]
    stakes = [b["stake"] for b in resolved]

    cum = 0
    cumulative = []
    for p in profits:
        cum += p
        cumulative.append(round(cum, 2))

    sizes = [max(6, s / 8) for s in stakes]

    hover_texts = []
    for b in resolved:
        pl_str = f"+{b['profit']:.2f}" if b['profit'] > 0 else f"{b['profit']:.2f}"
        bonus_str = f" (Bonus: MYR {b['bonus']:.0f})" if b.get("bonus") and b["bonus"] > 0 else ""
        hover_texts.append(
            f"<b>{b['bet']}</b><br>"
            f"Date: {b['bet_date']}<br>"
            f"Market: {b['market']}<br>"
            f"Odds: {b['odds']}<br>"
            f"Stake: MYR {b['stake']}{bonus_str}<br>"
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
        hovertemplate="Cumulative: MYR %{y:.2f}<extra></extra>",
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
        margin=dict(l=60, r=60, t=50, b=40),
        height=400,
    )

    fig.write_html(output_path, include_plotlyjs="cdn", full_html=False)

    # Inject hoverlabel bgcolor (Plotly 6.x drops it from layout) + JS to fix SVG attributes
    import re
    with open(output_path, "r", encoding="utf-8") as f:
        html = f.read()

    # Force bgcolor into the layout hoverlabel
    html = re.sub(
        r'"hoverlabel"\s*:\s*\{',
        '"hoverlabel":{"bgcolor":"#e8e6e3","bordercolor":"#363b44","font":{"color":"#000000","size":13},',
        html,
    )

    # Append JS that patches SVG attributes + CSS properties
    patch = """<script>
(function(){
  var D='#e8e6e3',L='#000000',B='#363b44';
  setInterval(function(){
    var tags=document.querySelectorAll('.hoverlayer *');
    for(var i=0;i<tags.length;i++){
      var t=tags[i];
      var tag=t.tagName;
      if(tag==='RECT'||tag==='rect'){
        t.setAttribute('fill',D);
        t.setAttribute('stroke',B);
      }
      if(tag==='TEXT'||tag==='text'||tag==='tspan'||tag==='DIV'||tag==='SPAN'){
        t.setAttribute('fill',L);
        t.style.setProperty('color',L,'important');
        t.setAttribute('font-size','13');
      }
      if(tag==='PATH'||tag==='path'){
        t.setAttribute('stroke',B);
      }
    }
  },20);
})();
</script>"""
    html = html.replace("</body>", patch + "</body>")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return output_path
