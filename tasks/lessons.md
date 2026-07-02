# Lessons Learned

1. **Parser edge cases matter**: Bets with `Status:Cashed Out` and no blank line before the next bet caused block merging. Fix: check for `Purchase Ticket ID:` in the inner loop as a break condition with `len(block) > 0`.

2. **Two data formats**: The file has a verbose key-value format (79 bets) and a compact numbered format (2 bets). The compact format uses **profit** instead of total return — critical difference.

3. **Python inline if-else limitation**: `x if cond1 else y if cond2 else z` can't be nested with `if` comprehensions. Use explicit for-loops or helper functions instead.

4. **Plotly 6.x API**: No changes needed for basic usage, but `write_html` with `full_html=False` generates clean embeddable charts.

5. **No red colors**: User specified no red (hurts eyes) and no white fonts. Used warm orange (`#c8814a`) for losses, soft green (`#5cb87a`) for wins, amber (`#d4a85c`) for pushes. Background colors stay dark.
