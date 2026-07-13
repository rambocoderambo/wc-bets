# Phase 1: Foundation — Bet Tracker Design Spec

**Date:** 2026-07-13
**Project:** bet-tracker (greenfield)
**Location:** `E:\AI LLMs\bet-tracker`
**Status:** Drafted, awaiting user review

---

## 1. Context

A 5-phase rollout of a full-stack betting tracker and analytics platform, replacing the existing static `WC Bets` Python dashboard. Phase 1 establishes the foundation: data model, main dashboard, bet entry (manual + paste parser), and seeding from the existing 127 bets.

Phases 2–5 are: Analytics page, Bankroll Management, Calculators, and Polish (real-time, export, production deploy). Each phase gets its own brainstorm → spec → plan → build cycle.

This phase does not modify the existing `WC Bets` project. The new project imports data from it via a one-shot script.

## 2. Tech Stack (Locked)

- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Database:** Postgres 16 (Docker Compose, local)
- **ORM:** Prisma
- **Charts:** Recharts
- **Styling:** Tailwind CSS
- **Validation:** Zod
- **Deployment:** Local only in Phase 1; production deploy in Phase 5

## 3. Project Structure

```
bet-tracker/
├── prisma/
│   └── schema.prisma
├── scripts/
│   └── import-bets.ts
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx                # Main Dashboard
│   │   ├── analytics/page.tsx      # Placeholder (Phase 2)
│   │   ├── bankroll/page.tsx       # Placeholder (Phase 3)
│   │   └── tools/page.tsx          # Placeholder (Phase 4)
│   ├── components/
│   │   ├── ui/                    # Card, StatCard, Badge, Table primitives
│   │   ├── charts/                # PnLChart, WonLostPie
│   │   └── forms/                 # AddBetForm, PasteParser, BetsPreviewTable
│   ├── lib/
│   │   ├── db.ts                  # Prisma client singleton
│   │   ├── metrics.ts             # Metric functions
│   │   ├── format.ts              # MYR / date / pct formatters
│   │   └── parse-bets.ts          # Format A/B/C parser
│   └── app/
│       └── api/
│           ├── bets/route.ts
│           ├── bets/[id]/route.ts
│           ├── parse-bets/route.ts
│           └── import-bets/route.ts
├── docker-compose.yml
├── .env.local
└── package.json
```

## 4. Data Model

### 4.1 Prisma schema

```prisma
model Bet {
  id           String    @id @default(cuid())
  betDate      DateTime
  eventDate    DateTime?
  sport        String
  league       String
  event        String
  betType      String
  betLabel     String
  odds         Float
  stake        Float
  returnAmount Float
  profit       Float     // computed at write-time, persisted for query speed
  status       BetStatus
  result       String?
  ticketId     String?   @unique
  bonus        Float?
  createdAt    DateTime  @default(now())
}

model Transaction {
  id        String          @id @default(cuid())
  type      TransactionType
  amount    Float
  balance   Float           // running bankroll snapshot after this txn
  betId     String?
  note      String?
  createdAt DateTime        @default(now())
}

enum BetStatus {
  WON
  LOST
  PUSH
  HALF_WON
  HALF_LOST
  DRAW
  CASHED_OUT
  VOID
  PENDING
}

enum TransactionType {
  DEPOSIT
  WITHDRAW
  BET_SETTLE
  ADJUSTMENT
}
```

### 4.2 Invariants

- Starting bankroll: MYR 1,000 seeded as a `DEPOSIT` Transaction at `min(betDate) − 1 second`.
- Each settled Bet spawns a linked `BET_SETTLE` Transaction with `amount = bet.profit`.
- `Transaction.balance` is the running bankroll snapshot — single SQL pass recomputes when new rows inserted.
- `profit` is computed at write-time (not on read) to keep queries cheap:
  `profit = returnAmount − max(stake − (bonus||0), 0)`

### 4.3 Status outcome buckets

The Prisma enum keeps all 9 statuses distinct (for accuracy in the DB and to support granular analysis in Phase 2). For Phase 1 dashboard win-rate and pie chart, they collapse into 4 buckets:

- Won = `WON`, `HALF_WON`, `CASHED_OUT`
- Lost = `LOST`, `HALF_LOST`
- Push = `PUSH`, `DRAW`, `VOID`
- Active = `PENDING` (unsettled — excluded from win-rate and settled P/L, surfaced only in Active Bets section)

## 5. Main Dashboard Page

**Route:** `/`  (App Router server component, initial data fetched server-side)

### 5.1 Layout (top-to-bottom)

1. **Top nav:** Dashboard · Analytics · Bankroll · Tools
2. **Page header:** `Dashboard` + current net worth pill (green/orange tint vs MYR 1000 start)
3. **Add Bet / Paste Bet buttons:** Collapsible inline form or paste parser card at top
4. **Summary cards row (4):** Total Bets · Net P/L · ROI · Win Rate
5. **Period breakdown row (2):** Weekly Performance · Monthly Performance (side-by-side cards with this/last comparisons)
6. **Charts row (2):** P/L over last 30 days (left) · Won/Push/Lost donut (right)
7. **Turnover & ROI stats row:** Total Turnover · Avg Stake · Largest Win · Largest Loss
8. **Latest bets table:** 10 most recent settled bets, color-coded status column
9. **Active bets section:** placeholder card (Phase 1 = static empty; live bet tracking comes later)

### 5.2 Color system (matches existing WC Bets aesthetic)

| Token | Value | Use |
|---|---|---|
| `bg-base` | `#0d1114` | Page background |
| `bg-card` | `#161a20` | Card background |
| `border` | `#262b33` | Borders, dividers |
| `text-primary` | `#e8e6e3` | Primary text |
| `text-muted` | `#9ca3a0` | Secondary text, labels |
| `positive` | `#5cb87a` | Won, positive P/L |
| `negative` | `#c8814a` | Lost, negative P/L (never red) |
| `push` | `#d4a85c` | Push, Draw, amber badges |
| `half` | `#5aa9a9` | Half-won / Half-lost |
| `accent` | `#5b8def` | Blue accents, links |

## 6. Bet Entry

### 6.1 Inline form (single manual entry)

Collapsible card at the top of dashboard, toggled by an "Add Bet" button. Fields:

- **Bet Label** (text) — e.g. "France -0.75", "Over 2.5", "Max Holloway"
- **Odds** (number, decimal, must be > 1.0)
- **Bet Type** (select with common types: FT Asian Handicap, FT O/U, 1st Half AH, To Qualify, FT Moneyline, Goalscorer, Player Over X, Goalkeeper Over Saves, Both Teams To Score, Total Cards O/U, 1st Set Handicap, Games O/U, 1X2, Live Betting AH, Live Betting O/U, Other)
- **Event** (text) — e.g. "France vs Spain"
- **League** (text with autocomplete from existing leagues)
- **Sport** (auto-derived from league, editable override)
- **Bet Date** (datetime-local, defaults to now)
- **Event Date** (datetime-local, optional)
- **Stake** (number MYR, must be > 0)
- **Return** (number MYR, 0 if unsettled)
- **Bonus** (number MYR, optional, default 0)
- **Ticket ID** (text, optional)
- **Status** (auto-derived from Return − Stake, user can override via enum dropdown)

### 6.2 Paste parser (bulk entries)

Textarea + "Parse & Import" button. Accepts 3 formats:

**Format A — Free-text paste:**
```
ID: 863998284061622272
France
1.64
To Qualify
France vs Spain
Stake: 120.00 MYR
Return: 196.80 MYR
```
Rules: line 1 `ID: <ticketId>`, line 2 = bet label, line 3 = odds (decimal), line 4 = bet type, line 5 = event, then `Stake:` and `Return:` lines anywhere after.

**Format B — Full key-value (existing Bets.txt format):**
```
Purchase Ticket ID:...
Bet Date:2026/07/13 09:58
Bet:Over 4.25
Odds:
 2.08 EU
Bet Type:
 [2:1]Live Betting O/U
Event:Austin FC II vs Minnesota United FC II
Stake:
 20.00 MYR
Return:
 41.60 MYR
Status:Won
Result:2 : 3
```

**Format C — CSV-ish one-line:** deferred beyond Phase 1, but parser is built extensible.

Format detection from first non-empty line:
- starts with `Purchase Ticket ID` → Format B
- starts with `ID:` → Format A
- comma-separated → Format C (future)

### 6.3 Two-step paste flow

1. **Parse button** → calls `/api/parse-bets` → returns JSON `{ bets: ParsedBet[], warnings: string[] }`, no DB writes
2. **Preview table** shows parsed bets with editable cells + per-bet warning badges
3. **Confirm & Import** → calls `/api/import-bets` → atomic `prisma.bet.createMany` + linked Transactions + recompute rolling balance

### 6.4 Server API routes

| Route | Method | Purpose |
|---|---|---|
| `/api/bets` | POST | Create single bet from inline form |
| `/api/parse-bets` | POST | Parse raw text → JSON (no DB write) |
| `/api/import-bets` | POST | Bulk add bets from paste preview + atomic transaction link |
| `/api/bets/[id]` | PATCH | Edit bet (status correction, etc) |
| `/api/refresh-metrics` | GET | Force re-aggregate (no-op in Phase 1) |

### 6.5 Bankroll invariants (DB transaction)

1. Insert Bet(s) — use `prisma.$transaction` to wrap all writes
2. Per settled bet, insert linked `Transaction { type: BET_SETTLE, amount: profit }`
3. Recompute rolling `balance` for the affected tail (single update with ordering by createdAt)
4. Commit or rollback whole batch — no partial imports

### 6.6 Status auto-derivation

- `return > stake` → `WON`
- `return == 0` → `LOST`
- `return == stake` → `PUSH`
- no `Return:` line / return field empty → `PENDING`
- User can override via dropdown before import

### 6.7 Validation

- Zod schemas for both paste formats and inline form
- Rejects bets with `stake <= 0` or `odds <= 1.0`
- Duplicate `ticketId` detection on import → skip + warn (don't overwrite)
- Date format parse failures → warning + skip that bet (don't fail whole batch)

## 7. Sport Inference

Static mapping in `src/lib/parse-bets.ts`:

| League substring | Sport |
|---|---|
| `World Cup 2026` | Soccer |
| `Wimbledon Men` / `Wimbledon Women` | Tennis |
| `UFC` | MMA |
| `USA - MLS Next Pro` | Soccer |
| `Friendly` | Soccer |
| (fallback) | Other |

User can override sport per-bet in the preview table.

## 8. Metrics (`src/lib/metrics.ts`)

All functions are pure, accept `Bet[]` and return typed objects. Consumed by both server components and API routes.

```ts
computeSummary(bets: Bet[]) => {
  totalBets, settledBets, netPL, roiPct, winRate,
  winningBets, losingBets, pushBets,
  bestBet, worstBet, avgStake, largestStake,
  totalTurnover, currentBankroll, startingBankroll, exposure
}

computePeriodStats(bets, period: 'week'|'month', offset = 0) => {
  label, bets, settled, netPL, roiPct, winRate
}

computeDailyPnL(bets, days = 30) => Array<{
  date, pnl, cumulative, betCount
}>

computeOutcomeBreakdown(bets) => {
  won, push, lost, wonPct, pushPct, lostPct
}

computeLatestBets(bets, limit = 10) => Bet[]   // sorted by betDate desc
computeActiveBets(bets) => Bet[]               // status === PENDING
```

## 9. Charts (`src/components/charts/`)

### 9.1 PnLChart

- Recharts `ComposedChart`
- Area layer: cumulative bankroll (`#5b8def` fill 20%, solid line on top)
- Bar layer: daily P/L (green `#5cb87a` positive / orange `#c8814a` negative)
- X-axis: dates formatted `dd MMM`
- Y-axis: MYR
- Tooltip: dark bg `#13181d`, black text (matches existing WC Bets Plotly tooltip)
- Zero baseline dashed line `#262b33`
- Data: `computeDailyPnL(bets, 30)`

### 9.2 WonLostPie

- Recharts `PieChart` in donut mode (inner radius 60%, outer 100%)
- 3 slices: Won `#5cb87a`, Push `#d4a85c`, Lost `#c8814a`
- Center label: total bets + "X% Win"
- Legend below with counts
- Data: `computeOutcomeBreakdown(bets)`

## 10. Summary Cards (4)

Left to right:

| # | Label | Value | Sub |
|---|---|---|---|
| 1 | Total Bets | count | "X active" |
| 2 | Net P/L | `+MYR X` | "vs MYR 1000 start" |
| 3 | ROI | `+X%` | "on MYR X turnover" |
| 4 | Win Rate | `X%` | "XW / YP / ZL" |

Tone (positive/negative/neutral/muted) drives value color. Component: `src/components/ui/StatCard.tsx`, props `{ label, value, sub, tone }`.

## 11. Period Breakdown Cards (2)

Two cards side-by-side: Weekly Performance and Monthly Performance.

Each shows current vs previous period:
- Weekly: this week bets / PnL / ROI ; last week same
- Monthly: this month bets / PnL / ROI ; last month same

Period cutoff: ISO weeks (Mon start), calendar months.

## 12. Turnover & ROI Stats Row

Inline stat strip below charts:
- Total Turnover (MYR)
- Average Stake (MYR)
- Largest Win (MYR green)
- Largest Loss (MYR orange)

## 13. Latest Bets Table

- 10 most recent settled bets, sorted by `betDate desc`
- Columns: Date · Event · Bet · Odds · Stake · Status · P/L
- Status column color-coded: green Won / orange Lost / amber Push / teal Half
- P/L column shows `+MYR` or `-MYR` prefixed
- Component: `src/components/ui/BetsTable.tsx` (reusable on other pages)

## 14. Active Bets Section

Card at bottom of dashboard:
- Phase 1: static placeholder ("No active bets")
- Reads from `computeActiveBets(bets)` — returns `[]` initially
- Layout reserved for future live bet tracking cards

## 15. Format Helpers (`src/lib/format.ts`)

```ts
fmtMYR(n: number): string    // "+MYR 205.56" | "-MYR 30.00" | "MYR 0.00"
fmtPct(n: number): string   // "+20.6%"
fmtDate(d: Date): string    // "13 Jul 2026"
fmtDateTime(d: Date): string // "13 Jul 09:58"
```

## 16. Caching Strategy

- No caching in Phase 1.
- All metrics computed server-side on every dashboard render.
- 127 bets → sub-50ms query time, no need for cache.
- Re-evaluate at Phase 5 — may add Redis/SWR.

## 17. Import Script (`scripts/import-bets.ts`)

One-shot, run via `npm run import -- ../WC\ Bets/Bets.txt`. Steps:

1. Connect Prisma client to local Docker Postgres
2. Confirm prompt: wipe existing Bets and Transactions (idempotent re-run) → `y/N`
3. Parse Bets.txt using ported logic from `src/parser.py` (Format 1 key-value + Format 2 compressed)
4. Dedup by `ticketId` (skip dups within this run)
5. Infer `sport` from `league` (see §7)
6. Compute `profit` per bet (see §4.2)
7. Seed bankroll: insert one `DEPOSIT` Transaction of `1000` at `min(betDate) − 1 second`
8. Insert Bet rows (`prisma.bet.createMany` batched 50 at a time, wrapped in a `prisma.$transaction`)
9. Insert linked `BET_SETTLE` Transaction per settled bet (same transaction block)
10. Recompute rolling `balance` for all transactions in chronological order — single SQL pass
11. Print summary: `✓ 127 bets imported, MYR 1000 deposited, current bankroll: MYR 1205.56`

Idempotent: re-running wipes & reinserts cleanly.

## 18. Dev Workflow

```bash
# First-time setup
cd E:\AI LLMs\bet-tracker
docker compose up -d
npm install
npx prisma migrate dev --name init
npm run import -- "../WC Bets/Bets.txt"
npm run dev

# Day-to-day
docker compose up -d
npm run dev
```

### 18.1 docker-compose.yml

```yaml
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: bettracker
      POSTGRES_USER: bettracker
      POSTGRES_PASSWORD: bettracker
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
volumes:
  pgdata:
```

### 18.2 .env.local

```
DATABASE_URL="postgresql://bettracker:bettracker@localhost:5432/bettracker?schema=public"
```

## 19. Dependencies

| Package | Purpose | Phase 1? |
|---|---|---|
| `next` (~14.2) | App Router framework | ✓ |
| `react` / `react-dom` (~18.3) | UI runtime | ✓ |
| `@prisma/client` | DB client | ✓ |
| `prisma` (dev) | Migrations + client gen | ✓ |
| `recharts` | Charts | ✓ |
| `tailwindcss` + `postcss` + `autoprefixer` (dev) | Styling | ✓ |
| `zod` | Validation | ✓ |
| `clsx` | Conditional classnames | ✓ |
| `tsx` (dev) | Run import script directly | ✓ |
| `eslint` + `eslint-config-next` (dev) | Lint | ✓ |
| `typescript` (dev) | Types | ✓ |

## 20. Edge Cases & Behavioral Rules

- **Bonus handling:** UI shows original stake. Profit uses `max(stake − bonus, 0)` as real out-of-pocket.
- **CASHED_OUT:** treated as Won for win-rate. Profit = return − stake (smaller than full-win).
- **Collapsed outcome buckets (win-rate):**
  - Won = `WON`, `HALF_WON`, `CASHED_OUT`
  - Lost = `LOST`, `HALF_LOST`
  - Push = `PUSH`, `DRAW`, `VOID`
  - Time-of-day granularity deferred to Phase 2 Analytics
- **Timezone:** all dates stored as UTC, displayed in local timezone (Asia/Kuala_Lumpur inferred from MYR currency). No timezone picker in Phase 1.
- **Negative bankroll:** UI does not enforce bet ≤ bankroll. Bankroll pill turns orange when current net worth < starting 1000.
- **Empty states:** dashboard renders zero-state cards (`—`, `MYR 0.00`) instead of failing when DB is empty (before import).
- **Duplicate import:** script wipes existing data, safe re-run.
- **Format ambiguity:** if a paste entry has no `Bet Date:`, it falls back to now; if `Event:` missing it falls back to "<No Event>"; both surface as warnings in the preview.

## 21. Phase 1 Acceptance Criteria

- [ ] `docker compose up && npm run import` populates 127 bets in < 5s
- [ ] Dashboard renders 4 summary cards with correct values (matches WC Bets: 127 bets, +MYR 205.56 net P/L)
- [ ] 30-day P/L chart renders green/orange bars + cumulative blue area
- [ ] Won/Push/Lost pie renders 3 segments with center label
- [ ] Weekly/Monthly comparison cards show correct period cutoffs
- [ ] Latest bets table shows 10 most recent with color-coded status
- [ ] Inline Add Bet form inserts a single bet + updates bankroll in < 200ms
- [ ] Paste parser accepts both the example Format A and Format B (Bets.txt) and produces DB rows
- [ ] All metrics remain accurate after manually editing a bet's status via `/api/bets/[id]` PATCH
- [ ] Dark theme colors match the WC Bets palette exactly (see §5.2)
- [ ] Empty state renders gracefully before any import

## 22. Out of Scope for Phase 1

Deferred to later phases:

- Phase 2 (Analytics): consistency map, losing runs, daily results, units won/lost by sport, bet type, time of day
- Phase 3 (Bankroll): full bankroll page (net worth, cash on hand, exposure, transaction history, growth chart)
- Phase 4 (Calculators): Kelly, EV, no-vig, Poisson, odds converter, parlay builder
- Phase 5 (Polish): real-time updates for active bets, CSV/PDF export, Vercel/Neon production deploy, framework migration complete, RSC streaming for slow queries

Also out of scope for Phase 1:
- Live bet tracking (status changes from PENDING → WON/LOST) — manual edit only

## 23. Open Questions Resolved

| Question | Answer |
|---|---|
| Architecture | Greenfield full React stack; never touch existing WC Bets project |
| Project location | `E:\AI LLMs\bet-tracker` |
| Postgres hosting | Docker Compose local |
| Seed data | Import all 127 bets from Bets.txt |
| Starting bankroll | MYR 1,000 |
| Deployment | Local only until Phase 5 |
| ORM | Prisma |
| Charts | Recharts |
| Styling | Tailwind CSS (dark theme matching existing palette) |