import sys; sys.path.insert(0, 'src')
from parser import parse_bets

bets = parse_bets('data/Bets.txt')
print(f"Total parsed: {len(bets)}")

# Find the Norway -0.25 bet
for b in bets:
    bet = b.get("bet", "")
    if "Norway" in bet and "0.25" in bet:
        print(f"Found: {b['bet_date']}: {bet} | stake={b['stake']} | return={b.get('return')} | profit={b['profit']} | status={b['status']}")

# Find the Haaland bet
for b in bets:
    if "Haaland" in b.get("bet", ""):
        print(f"Haaland: {b['bet']} | stake={b['stake']} | return={b.get('return')} | profit={b['profit']} | status={b['status']} | market={b.get('market')}")

# Check file encoding
with open('data/Bets.txt', 'rb') as f:
    raw = f.read()
print(f"\nFile size: {len(raw)} bytes")
# Check last few hundred bytes for the new entries
tail = raw[-500:].decode('utf-8', errors='replace')
if 'Haaland' in tail:
    print("Haaland bet found in file tail")
if '859742603343208448' in tail:
    print("New Purchase ID found in file tail")
