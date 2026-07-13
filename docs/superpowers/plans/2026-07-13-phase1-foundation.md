# Phase 1: Foundation — Bet Tracker Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Next.js 14 + Prisma + Postgres bet tracking dashboard at `E:\AI LLMs\bet-tracker`, seed it with 127 historical bets imported from `E:\AI Llms\WC Bets\Bets.txt`, and ship a working Main Dashboard page with summary cards, 30-day P/L chart, won/push/lost donut, latest bets table, and a bet entry form (inline + paste parser).

**Architecture:** Next.js App Router with server components for initial data fetch; Prisma ORM over a local Docker Postgres; Recharts for client-side charts; Tailwind for dark theme styling. Metric functions are pure TypeScript consumed by both server components and API routes. Bet entry flows (inline form + paste parser) write through atomic Prisma transactions that maintain bankroll invariants (Bet row + linked BET_SETTLE Transaction + recomputed running balance).

**Tech Stack:** Next.js 14.2 · React 18.3 · TypeScript 5 · Prisma 5 · Postgres 16 (Docker) · Recharts 2 · Tailwind 3 · Zod 3 · clsx · tsx (dev)

## Global Constraints

- Working directory for all `npm`/shell commands: `E:\AI LLMs\bet-tracker` (new project). Do not run any commands against `E:\AI Llms\WC Bets`.
- Source Bets.txt path (for import only): `E:\AI Llms\WC Bets\Bets.txt`
- Color palette tokens (Tailwind config must define these):
  - `bg-base: #0d1114` `bg-card: #161a20` `border-base: #262b33`
  - `text-primary: #e8e6e3` `text-muted: #9ca3a0`
  - `positive: #5cb87a` `negative: #c8814a` `push: #d4a85c` `half: #5aa9a9` `accent: #5b8def`
- Currency: MYR, starting bankroll MYR 1000
- Dates stored UTC, displayed Asia/Kuala_Lumpur
- Status outcome buckets (for win-rate and pie only): Won = {WON, HALF_WON, CASHED_OUT}, Lost = {LOST, HALF_LOST}, Push = {PUSH, DRAW, VOID}, Active = {PENDING}
- profit formula: `profit = returnAmount − max(stake − (bonus||0), 0)`
- All 9 BetStatus enum values kept distinct in DB; collapse only at display time
- Duplicate `ticketId` on import: skip + warn, do not overwrite
- Every task ends with a commit

---

## File Structure

| File | Responsibility |
|---|---|
| `docker-compose.yml` | Postgres 16 container on port 5432 with named volume `pgdata` |
| `.env.local` | `DATABASE_URL` for Prisma |
| `.env` | Same DB URL (for scripts/tsx) |
| `package.json` | Next.js, React, Prisma, Recharts, Tailwind, Zod, clsx, tsx, eslint, typescript |
| `tsconfig.json` | Strict TypeScript with `@/*` path alias → `src/*` |
| `tailwind.config.ts` | Dark theme tokens + content paths |
| `postcss.config.js` | Tailwind + autoprefixer |
| `prisma/schema.prisma` | Bet, Transaction, BetStatus, TransactionType |
| `src/lib/db.ts` | Prisma client singleton (avoid instantiation storms in dev HMR) |
| `src/lib/format.ts` | `fmtMYR`, `fmtPct`, `fmtDate`, `fmtDateTime` (Asia/Kuala_Lumpur) |
| `src/lib/metrics.ts` | `computeSummary`, `computePeriodStats`, `computeDailyPnL`, `computeOutcomeBreakdown`, `computeLatestBets`, `computeActiveBets` |
| `src/lib/sport-map.ts` | `inferSport(league)` mapping table |
| `src/lib/parse-bets.ts` | `parsePasteInput(text)` detecting Format A/B/C → `ParsedBet[]` with warnings |
| `src/lib/bet-zod.ts` | Zod schemas for inline form + paste + PATCH |
| `src/lib/profit.ts` | `computeProfit(returnAmount, stake, bonus)` used at write-time |
| `src/app/layout.tsx` | Root layout: `<html>` dark bg, top nav with 4 links |
| `src/app/page.tsx` | Main Dashboard (server component) — orchestrates fetch + UI composition |
| `src/app/globals.css` | Tailwind directives + small base rules |
| `src/app/api/bets/route.ts` | POST single bet — atomic tx |
| `src/app/api/bets/[id]/route.ts` | PATCH bet status — atomic tx |
| `src/app/api/parse-bets/route.ts` | POST raw text → parsed JSON (no DB) |
| `src/app/api/import-bets/route.ts` | POST `{bets: ParsedBet[]}` → bulk insert + bet_settle txns |
| `src/app/api/refresh-metrics/route.ts` | GET — `{ok:true}` no-op for Phase 1 |
| `src/app/analytics/page.tsx` | Placeholder card |
| `src/app/bankroll/page.tsx` | Placeholder card |
| `src/app/tools/page.tsx` | Placeholder card |
| `src/components/ui/StatCard.tsx` | `{label, value, sub, tone}` |
| `src/components/ui/Card.tsx` | Dark card wrapper with optional title |
| `src/components/ui/Badge.tsx` | Status badge with tone variants |
| `src/components/ui/BetsTable.tsx` | Reusable bets table |
| `src/components/charts/PnLChart.tsx` | Recharts ComposedChart (Area + Bar, 30-day) |
| `src/components/charts/WonLostPie.tsx` | Recharts donut with center label |
| `src/components/forms/AddBetForm.tsx` | Inline form (client component with zod validation) |
| `src/components/forms/PasteParser.tsx` | Textarea + parse + preview + import (client) |
| `src/components/nav/TopNav.tsx` | Header nav for dashboard |
| `scripts/import-bets.ts` | One-shot CLI: parse Bets.txt + Prisma bulk insert |
| `scripts/format-detector.test.ts` | Unit tests for parse-bets format detection |
| `scripts/profit.test.ts` | Unit tests for profit formula |
| `scripts/metrics.test.ts` | Unit tests for each metric function with seed data |
| `.gitignore` | node_modules, .next, .env*, dist |

---

## Task Sequence

1. **Scaffold + Docker** — next.js init, docker-compose, npm deps, .env, tsconfig, tailwind, git init
2. **Prisma schema + migration + client** — Bet, Transaction, enums, `src/lib/db.ts`
3. **Formatters (`format.ts`)** — fmtMYR, fmtPct, fmtDate, fmtDateTime
4. **Profit formula (`profit.ts`)** — computeProfit with bonus handling (TDD)
5. **Sport map (`sport-map.ts`)** — inferSport(league) (TDD)
6. **Parse-bets format detection + Format A parser** — TDD with example paste
7. **Parse-bets Format B parser** — TDD with Bets.txt excerpt
8. **Import script (`import-bets.ts`)** — one-shot CLI for seeding
9. **Metrics: computeSummary + computeOutcomeBreakdown** — TDD with synthetic bets
10. **Metrics: computePeriodStats + computeDailyPnL + computeLatestBets + computeActiveBets** — TDD
11. **UI primitives: Card, StatCard, Badge, BetsTable** — Tailwind components
12. **Charts: PnLChart, WonLostPie** — Recharts wrappers (client components)
13. **Nav + layout + placeholder pages** — app shell
14. **Main Dashboard page composition** — wire metrics to UI
15. **Add Bet form (inline) + POST /api/bets** — atomic transaction
16. **Paste parser UI + /api/parse-bets + /api/import-bets** — bulk flow
17. **PATCH /api/bets/[id]** — status correction
18. **End-to-end smoke test: wipe → import → verify metrics match WC Bets**

---

### Task 1: Project scaffold + Docker Compose + dependencies

**Files:**
- Create: `package.json`, `tsconfig.json`, `next.config.mjs`, `tailwind.config.ts`, `postcss.config.js`, `docker-compose.yml`, `.env.local`, `.env`, `.gitignore`, `src/app/globals.css`
- Create: `src/app/layout.tsx` (minimal placeholder), `src/app/page.tsx` (minimal "ok" page)

**Interfaces:**
- Consumes: nothing (ground zero)
- Produces: a running `npm run dev` server returning a placeholder page at `http://localhost:3000`, a running Postgres at `localhost:5432`, and a ready-to-edit Prisma project.

- [ ] **Step 1: Create project directory + init package.json**

```bash
New-Item -ItemType Directory -Path "E:\AI LLMs\bet-tracker" -Force
cd "E:\AI LLMs\bet-tracker"
npm init -y
```

- [ ] **Step 2: Install runtime dependencies**

```bash
npm install next@14.2.5 react@18.3.1 react-dom@18.3.1 @prisma/client@5.18.0 recharts@2.12.7 zod@3.23.8 clsx@2.1.1
```

- [ ] **Step 3: Install dev dependencies**

```bash
npm install -D prisma@5.18.0 tailwindcss@3.4.7 postcss@8.4.41 autoprefixer@10.4.20 eslint@8.57.0 eslint-config-next@14.2.5 tsx@4.19.0 @types/node@20 typescript@5.5.4 @types/react@18.3.3 @types/react-dom@18.3.0
```

- [ ] **Step 4: Initialize Next.js + TypeScript + Tailwind + Prisma**

```bash
npx tailwindcss init -p
npx prisma init --datasource-provider postgresql
```

- [ ] **Step 5: Write `tsconfig.json` with @/* alias**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": { "@/*": ["./src/*"] }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

- [ ] **Step 6: Write `next.config.mjs`**

```js
/** @type {import('next').NextConfig} */
export default {
  reactStrictMode: true,
};
```

- [ ] **Step 7: Write `tailwind.config.ts` with dark theme tokens**

```ts
import type { Config } from 'tailwindcss'

export default {
  content: ['./src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        base: '#0d1114',
        card: '#161a20',
        'card-border': '#262b33',
        primary: '#e8e6e3',
        muted: '#9ca3a0',
        positive: '#5cb87a',
        negative: '#c8814a',
        push: '#d4a85c',
        half: '#5aa9a9',
        accent: '#5b8def',
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
    },
  },
  plugins: [],
} satisfies Config
```

- [ ] **Step 8: Write `src/app/globals.css`**

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  color-scheme: dark;
}
body {
  background-color: #0d1114;
  color: #e8e6e3;
}
```

- [ ] **Step 9: Write `src/app/layout.tsx`**

```tsx
import './globals.css'

export const metadata = { title: 'Bet Tracker' }

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-base text-primary font-sans">
        {children}
      </body>
    </html>
  )
}
```

- [ ] **Step 10: Write `src/app/page.tsx` (temp placeholder)**

```tsx
export default function Home() {
  return <main className="p-8">ok</main>
}
```

- [ ] **Step 11: Write `docker-compose.yml`**

```yaml
services:
  postgres:
    image: postgres:16-alpine
    container_name: bettracker-postgres
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

- [ ] **Step 12: Write `.env.local` and `.env`**

```
DATABASE_URL="postgresql://bettracker:bettracker@localhost:5432/bettracker?schema=public"
```
(Same content for both files.)

- [ ] **Step 13: Write `.gitignore`**

```
node_modules
.next
.env
.env.local
.env.*.local
dist
*.tsbuildinfo
next-env.d.ts
```

- [ ] **Step 14: Add npm scripts to `package.json`**

```json
{
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "import": "tsx scripts/import-bets.ts",
    "typecheck": "tsc --noEmit",
    "test": "tsx --test scripts/*.test.ts"
  }
}
```

- [ ] **Step 15: Start Docker + verify Postgres reachable**

```bash
docker compose up -d
docker exec bettracker-postgres pg_isready -U bettracker
```
Expected: "no server response" first time → wait 3s → retry → "accepting connections"

- [ ] **Step 16: Run dev server smoke test**

```bash
npm run dev
```
In another terminal:
```bash
curl http://localhost:3000
```
Expected output contains `<body class="min-h-screen bg-base text-primary font-sans">` and "ok". Stop the dev server with Ctrl-C.

- [ ] **Step 17: Init git + first commit**

```bash
cd "E:\AI LLMs\bet-tracker"
git init
git add -A
git commit -m "chore: scaffold Next.js + Prisma + Tailwind + Docker"
```

---

### Task 2: Prisma schema, migration, client singleton

**Files:**
- Replace: `prisma/schema.prisma`
- Create: `src/lib/db.ts`
- Create: `scripts/migrate.test.ts` (smoke check)

**Interfaces:**
- Consumes: docker-compose postgres + DATABASE_URL
- Produces: `Bet`, `Transaction` Prisma models; `db` exported from `@/lib/db`

- [ ] **Step 1: Write `prisma/schema.prisma`**

```prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

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
  profit       Float
  status       BetStatus
  result       String?
  ticketId     String?   @unique
  bonus        Float?
  createdAt    DateTime  @default(now())

  @@index([betDate])
  @@index([status])
}

model Transaction {
  id        String          @id @default(cuid())
  type      TransactionType
  amount    Float
  balance   Float
  betId     String?
  note      String?
  createdAt DateTime        @default(now())

  @@index([createdAt])
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

- [ ] **Step 2: Run migration**

```bash
npx prisma migrate dev --name init
```
Expected: `Applied migration "init"` and Prisma Client regenerated.

- [ ] **Step 3: Write `src/lib/db.ts`**

```ts
import { PrismaClient } from '@prisma/client'

const globalForPrisma = global as unknown as { prisma?: PrismaClient }

export const db = globalForPrisma.prisma ?? new PrismaClient()

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = db
```

- [ ] **Step 4: Write smoke test `scripts/migrate.test.ts`**

```ts
import { db } from '../src/lib/db'

console.log('Testing DB connection...')
const count = await db.bet.count()
console.assert(count === 0, `expected 0 bets, got ${count}`)
console.log('OK')
process.exit(0)
```

- [ ] **Step 5: Run smoke test**

```bash
npx tsx scripts/migrate.test.ts
```
Expected: `OK` and exit code 0.

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "feat(db): add Prisma schema for Bet & Transaction, migration, client singleton"
```

---

### Task 3: Formatters (`format.ts`)

**Files:**
- Create: `src/lib/format.ts`
- Create: `scripts/format.test.ts`

**Interfaces:**
- Produces: `fmtMYR(n)`, `fmtPct(n)`, `fmtDate(d)`, `fmtDateTime(d)` — all return string

- [ ] **Step 1: Write `scripts/format.test.ts`**

```ts
import assert from 'node:assert/strict'
import { test } from 'node:test'
import { fmtMYR, fmtPct, fmtDate, fmtDateTime } from '../src/lib/format'

test('fmtMYR positive with + prefix', () => {
  assert.equal(fmtMYR(205.56), '+MYR 205.56')
})
test('fmtMYR negative with – prefix', () => {
  assert.equal(fmtMYR(-30), '-MYR 30.00')
})
test('fmtMYR zero', () => {
  assert.equal(fmtMYR(0), 'MYR 0.00')
})
test('fmtPct positive', () => {
  assert.equal(fmtPct(20.6), '+20.6%')
})
test('fmtPct negative', () => {
  assert.equal(fmtPct(-5.25), '-5.25%')
})
test('fmtPctZero', () => {
  assert.equal(fmtPct(0), '0.0%')
})
test('fmtDate formats', () => {
  assert.equal(fmtDate(new Date('2026-07-13T01:00:00Z')), '13 Jul 2026')
})
test('fmtDateTime formats', () => {
  const s = fmtDateTime(new Date('2026-07-13T01:58:00Z'))
  assert.match(s, /^13 Jul \d{2}:\d{2}$/)
})
```

- [ ] **Step 2: Run test (expect fail)**

```bash
npm test -- scripts/format.test.ts
```
Expected: FAIL — module not found.

- [ ] **Step 3: Write `src/lib/format.ts`**

```ts
const MYR = new Intl.NumberFormat('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
const PCT = new Intl.NumberFormat('en-US', { minimumFractionDigits: 1, maximumFractionDigits: 1 })
const TZ = 'Asia/Kuala_Lumpur'

export function fmtMYR(n: number): string {
  const abs = MYR.format(Math.abs(n))
  if (n > 0) return `+MYR ${abs}`
  if (n < 0) return `-MYR ${abs}`
  return `MYR ${abs}`
}

export function fmtPct(n: number): string {
  const s = PCT.format(Math.abs(n))
  if (n > 0) return `+${s}%`
  if (n < 0) return `-${s}%`
  return `${s}%`
}

export function fmtDate(d: Date): string {
  return new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', year: 'numeric', timeZone: TZ }).format(d)
}

export function fmtDateTime(d: Date): string {
  const date = new Intl.DateTimeFormat('en-GB', { day: '2-digit', month: 'short', timeZone: TZ }).format(d)
  const time = new Intl.DateTimeFormat('en-GB', { hour: '2-digit', minute: '2-digit', hour12: false, timeZone: TZ }).format(d)
  return `${date} ${time}`
}
```

- [ ] **Step 4: Run tests (expect pass)**

```bash
npm test -- scripts/format.test.ts
```
Expected: 8 tests pass.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat(format): MYR/percent/date formatters with Asia/Kuala_Lumpur TZ"
```

---

### Task 4: Profit formula (`profit.ts`)

**Files:**
- Create: `src/lib/profit.ts`
- Create: `scripts/profit.test.ts`

**Interfaces:**
- Produces: `computeProfit({ returnAmount, stake, bonus? }) => number`

- [ ] **Step 1: Write `scripts/profit.test.ts`**

```ts
import assert from 'node:assert/strict'
import { test } from 'node:test'
import { computeProfit } from '../src/lib/profit'

test('plain win', () => {
  assert.equal(computeProfit({ returnAmount: 88, stake: 50, bonus: 0 }), 38)
})
test('plain loss', () => {
  assert.equal(computeProfit({ returnAmount: 0, stake: 50, bonus: 0 }), -50)
})
test('plain half won (return = stake/4 extra)', () => {
  assert.equal(computeProfit({ returnAmount: 75, stake: 100, bonus: 0 }), -25)
})
test('bonus bet full credit + positive: profit = full return', () => {
  assert.equal(computeProfit({ returnAmount: 85, stake: 50, bonus: 50 }), 85)
})
test('bonus bet lost, no out-of-pocket: profit = 0 (not -50)', () => {
  assert.equal(computeProfit({ returnAmount: 0, stake: 50, bonus: 50 }), 0)
})
test('partial bonus lost: loss reduced by bonus', () => {
  assert.equal(computeProfit({ returnAmount: 0, stake: 50, bonus: 24 }), -26)
})
test('return exactly equals stake without bonus = push→zero', () => {
  assert.equal(computeProfit({ returnAmount: 50, stake: 50, bonus: 0 }), 0)
})
```

- [ ] **Step 2: Run test (expect fail)**

```bash
npm test -- scripts/profit.test.ts
```
Expected: FAIL — module not found.

- [ ] **Step 3: Write `src/lib/profit.ts`**

```ts
export function computeProfit(args: {
  returnAmount: number
  stake: number
  bonus?: number | null
}): number {
  const outOfPocket = Math.max(args.stake - (args.bonus ?? 0), 0)
  return args.returnAmount - args.stake + (args.stake - outOfPocket)
  // Equivalent to: returnAmount - outOfPocket - (stake - outOfPocket)
  //              = returnAmount - stake + (stake - outOfPocket)
  //              = returnAmount - max(stake - bonus, 0)
  // But formula deliberately decomposes so the "bonus credits reduce out-of-pocket" intent is visible.
}

// Simpler equivalent (used in code):
// return args.returnAmount - Math.max(args.stake - (args.bonus ?? 0), 0)
```

- [ ] **Step 4: Run tests**

```bash
npm test -- scripts/profit.test.ts
```
Expected: 7 tests pass. If any fail, fix the computation in `profit.ts`.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat(profit): bonus-aware profit formula"
```

---

### Task 5: Sport map (`sport-map.ts`)

**Files:**
- Create: `src/lib/sport-map.ts`
- Create: `scripts/sport-map.test.ts`

**Interfaces:**
- Produces: `inferSport(league: string): string` (one of Soccer, Tennis, MMA, Other)

- [ ] **Step 1: Write `scripts/sport-map.test.ts`**

```ts
import assert from 'node:assert/strict'
import { test } from 'node:test'
import { inferSport } from '../src/lib/sport-map'

test('World Cup 2026 → Soccer', () => assert.equal(inferSport('World Cup 2026'), 'Soccer'))
test('Wimbledon Men → Tennis', () => assert.equal(inferSport('Wimbledon Men'), 'Tennis'))
test('Wimbledon Women → Tennis', () => assert.equal(inferSport('Wimbledon Women'), 'Tennis'))
test('UFC 329 → MMA', () => assert.equal(inferSport('UFC 329'), 'MMA'))
test('USA - MLS Next Pro → Soccer', () => assert.equal(inferSport('USA - MLS Next Pro'), 'Soccer'))
test('Friendly → Soccer', () => assert.equal(inferSport('Friendly'), 'Soccer'))
test('Unknown → Other', () => assert.equal(inferSport('RandoLeague'), 'Other'))
```

- [ ] **Step 2: Run test (expect fail)**

```bash
npm test -- scripts/sport-map.test.ts
```

- [ ] **Step 3: Write `src/lib/sport-map.ts`**

```ts
export function inferSport(league: string): string {
  const l = league.toLowerCase()
  if (l.includes('world cup') || l.includes('mls') || l.includes('friendly')) return 'Soccer'
  if (l.includes('wimbledon')) return 'Tennis'
  if (l.includes('ufc')) return 'MMA'
  return 'Other'
}
```

- [ ] **Step 4: Run tests**

```bash
npm test -- scripts/sport-map.test.ts
```
Expected: 7 tests pass.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat(sport): league-to-sport inference map"
```

---

### Task 6: Parse-bets — format detection + Format A parser

**Files:**
- Create: `src/lib/parse-bets.ts`
- Create: `src/lib/bet-zod.ts`
- Create: `scripts/parse-format-A.test.ts`

**Interfaces:**
- Produces: `parsePasteInput(text: string) => { bets: ParsedBet[]; warnings: string[] }`
- Produces: `ParsedBet` type from `bet-zod.ts` (reused by Form A, B, import route, UI preview)

- [ ] **Step 1: Write `src/lib/bet-zod.ts`**

```ts
import { z } from 'zod'

export const ParsedBetSchema = z.object({
  ticketId: z.string().nullable(),
  betLabel: z.string().min(1),
  odds: z.number().gt(1.0),
  betType: z.string().min(1),
  event: z.string().min(1),
  league: z.string().default('Other'),
  sport: z.string().default('Other'),
  betDate: z.string().nullable(),
  eventDate: z.string().nullable(),
  stake: z.number().positive(),
  returnAmount: z.number().min(0).default(0),
  bonus: z.number().min(0).optional().nullable(),
  status: z.enum(['WON', 'LOST', 'PUSH', 'HALF_WON', 'HALF_LOST', 'DRAW', 'CASHED_OUT', 'VOID', 'PENDING']),
  result: z.string().optional().nullable(),
})

export type ParsedBet = z.infer<typeof ParsedBetSchema>

export const PasteInputSchema = z.object({ text: z.string().min(1) })
```

- [ ] **Step 2: Write `scripts/parse-format-A.test.ts`**

```ts
import assert from 'node:assert/strict'
import { test } from 'node:test'
import { parsePasteInput } from '../src/lib/parse-bets'

test('Parse Format A example', () => {
  const text = `ID: 863998284061622272
France
1.64
To Qualify
France vs Spain
Stake: 120.00 MYR
Return: 196.80 MYR`
  const { bets, warnings } = parsePasteInput(text)
  assert.equal(bets.length, 1)
  assert.equal(warnings.length, 0)
  const b = bets[0]
  assert.equal(b.ticketId, '863998284061622272')
  assert.equal(b.betLabel, 'France')
  assert.equal(b.odds, 1.64)
  assert.equal(b.betType, 'To Qualify')
  assert.equal(b.event, 'France vs Spain')
  assert.equal(b.stake, 120)
  assert.equal(b.returnAmount, 196.80)
  assert.equal(b.status, 'WON')
  assert.equal(b.league, 'Other')
  assert.equal(b.sport, 'Other')
  assert.equal(b.bonus, null)
})

test('Format A without Return → PENDING', () => {
  const text = `ID: 863998284061622272
France
1.64
To Qualify
France vs Spain
Stake: 120.00 MYR`
  const { bets, warnings } = parsePasteInput(text)
  assert.equal(bets.length, 1)
  assert.equal(bets.length, 1)
  assert.equal(bets[0].status, 'PENDING')
  assert.equal(bets[0].returnAmount, 0)
})
```

- [ ] **Step 3: Run tests (expect fail)**

```bash
npm test -- scripts/parse-format-A.test.ts
```

- [ ] **Step 4: Write `src/lib/parse-bets.ts` (Format A only for now)**

```ts
import { ParsedBetSchema, type ParsedBet } from './bet-zod'
import { inferSport } from './sport-map'

export type ParseResult = { bets: ParsedBet[]; warnings: string[] }

export function parsePasteInput(text: string): ParseResult {
  const bets: ParsedBet[] = []
  const warnings: string[] = []

  // Split blocks: Format blocks alternate by content shape.
  // First line of block decides format.
  const blocks = text.split(/\n\s*\n/).filter(b => b.trim().length > 0)

  for (const block of blocks) {
    const firstLine = block.split('\n').find(l => l.trim().length > 0) ?? ''
    if (firstLine.startsWith('Purchase Ticket ID')) {
      // Format B (next task)
      const parsed = parseFormatB(block, warnings)
      if (parsed) bets.push(parsed)
    } else if (firstLine.startsWith('ID:')) {
      const parsed = parseFormatA(block, warnings)
      if (parsed) bets.push(parsed)
    } else {
      warnings.push(`Unrecognized block (first line: "${firstLine.slice(0, 40)}..."). Skipped.`)
    }
  }

  return { bets, warnings }
}

function parseFormatA(block: string, warnings: string[]): ParsedBet | null {
  const lines = block.split('\n').map(l => l.trim()).filter(Boolean)
  const ticketId = lines[0].replace(/^ID:\s*/, '').trim() || null
  const betLabel = lines[1] ?? ''
  const odds = Number(lines[2] ?? '0')
  const betType = lines[3] ?? ''
  const event = lines[4] ?? ''

  const findKV = (key: string) => lines.find(l => l.toLowerCase().startsWith(key.toLowerCase() + ':'))
  const stakeLine = findKV('Stake')
  const returnLine = findKV('Return')

  if (!betLabel || !odds || !betType || !event || !stakeLine) {
    warnings.push(`Format A block missing required field: ${betLabel ? betLabel : '(no label)'}`)
    return null
  }

  const stake = Number(stakeLine.replace(/^Stake:\s*/i, '').replace(/MYR/i, '').trim())
  const returnAmount = returnLine ? Number(returnLine.replace(/^Return:\s*/i, '').replace(/MYR/i, '').trim()) : 0
  if (!stake || stake <= 0 || odds <= 1.0) {
    warnings.push(`Invalid stake/odds for bet "${betLabel}". Skipped.`)
    return null
  }

  const status: ParsedBet['status'] = returnLine
    ? (returnAmount > stake ? 'WON' : returnAmount === stake ? 'PUSH' : returnAmount === 0 ? 'LOST' : 'PENDING')
    : 'PENDING'

  const raw = ParsedBetSchema.safeParse({
    ticketId, betLabel, odds, betType, event,
    league: 'Other',
    sport: 'Other',
    betDate: null, eventDate: null,
    stake, returnAmount,
    bonus: null,
    status,
    result: null,
  })
  if (!raw.success) {
    warnings.push(`Schema validation failed for bet "${betLabel}": ${raw.error.message}`)
    return null
  }
  return raw.data
}

// Format B placeholder — implemented in next task
function parseFormatB(block: string, warnings: string[]): ParsedBet | null {
  warnings.push('Format B not yet implemented')
  return null
}
```

- [ ] **Step 5: Run tests**

```bash
npm test -- scripts/parse-format-A.test.ts
```
Expected: 2 tests pass.

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "feat(parse): Format A (free-text paste) parser with detection"
```

---

### Task 7: Parse-bets — Format B (Bets.txt) parser

**Files:**
- Modify: `src/lib/parse-bets.ts` (replace `parseFormatB` stub)
- Create: `scripts/parse-format-B.test.ts`

**Interfaces:**
- Consumes: same ParsedBet schema
- Produces: full Format B coverage (coexists with Format A)

- [ ] **Step 1: Write `scripts/parse-format-B.test.ts`**

```ts
import assert from 'node:assert/strict'
import { test } from 'node:test'
import { parsePasteInput } from '../src/lib/parse-bets'

test('Parse Format B single settle block', () => {
  const text = `Purchase Ticket ID:864324808816156672
Bet Ticket ID:864324808816156673
Bet Date:2026/07/13 09:58
Bet:Over 4.25
Odds:
 2.08 EU
Bet Type:
 [2:1]Live Betting O/U
Event:Austin FC II vs Minnesota United FC II
Event Date:2026/07/13 08:30
League:USA - MLS Next Pro
Stake:
 20.00 MYR
Return:
 41.60 MYR
Status:Won
Result:2 : 3`
  const { bets, warnings } = parsePasteInput(text)
  assert.equal(warnings.length, 0)
  assert.equal(bets.length, 1)
  const b = bets[0]
  assert.equal(b.ticketId, '864324808816156673')
  assert.equal(b.betLabel, 'Over 4.25')
  assert.equal(b.odds, 2.08)
  assert.equal(b.betType, '[2:1]Live Betting O/U')
  assert.equal(b.event, 'Austin FC II vs Minnesota United FC II')
  assert.equal(b.league, 'USA - MLS Next Pro')
  assert.equal(b.sport, 'Soccer')
  assert.equal(b.stake, 20)
  assert.equal(b.returnAmount, 41.60)
  assert.equal(b.status, 'WON')
  assert.equal(b.result, '2 : 3')
})

test('Parse Format B with bonus', () => {
  const text = `Purchase Ticket ID:856724099262189568
Bet Ticket ID:856724099262189569
Bet Date:2026/06/22 10:35
Bet:Under 3.5
Odds:
 2.02 EU
Bet Type:
 [1:2]Live Betting O/U
Event:New Zealand vs Egypt
Event Date:2026/06/22 09:00
League:World Cup 2026
Bonus:50.00 MYR
Stake:
 50.00 MYR
Return:
 0.00 MYR
Status:Lost
Result:1 : 3`
  const { bets, warnings } = parsePasteInput(text)
  assert.equal(warnings.length, 0)
  assert.equal(bets.length, 1)
  const b = bets[0]
  assert.equal(b.betLabel, 'Under 3.5')
  assert.equal(b.bonus, 50)
  assert.equal(b.stake, 50)
  assert.equal(b.returnAmount, 0)
  assert.equal(b.status, 'LOST')
})

test('Parse multi-block Bets.txt (separated by blank lines)', () => {
  const text = `Purchase Ticket ID:864324808816156672
Bet Ticket ID:864324808816156673
Bet Date:2026/07/13 09:58
Bet:Over 4.25
Odds:
 2.08 EU
Bet Type:
 [2:1]Live Betting O/U
Event:Austin FC II vs Minnesota United FC II
Event Date:2026/07/13 08:30
League:USA - MLS Next Pro
Stake:
 20.00 MYR
Return:
 41.60 MYR
Status:Won
Result:2 : 3

Purchase Ticket ID:864142176488669184
Bet Ticket ID:864142176488669185
Bet Date:2026/07/12 21:52
Bet:Jannik Sinner -1.5
Odds:
 1.76 EU
Bet Type:
 1st Set Handicap
Event:Jannik Sinner vs Alexander Zverev
Event Date:2026/07/12 23:05
League:Wimbledon Men
Stake:
 50.00 MYR
Return:
 0.00 MYR
Status:Lost
Result:6 : 7`
  const { bets, warnings } = parsePasteInput(text)
  assert.equal(warnings.length, 0)
  assert.equal(bets.length, 2)
  assert.equal(bets[0].betLabel, 'Over 4.25')
  assert.equal(bets[1].betLabel, 'Jannik Sinner -1.5')
  assert.equal(bets[1].sport, 'Tennis')
})
```

- [ ] **Step 2: Run tests (expect fail — Format B returns null + "not yet implemented" warning)**

```bash
npm test -- scripts/parse-format-B.test.ts
```

- [ ] **Step 3: Replace `parseFormatB` stub with real implementation in `src/lib/parse-bets.ts`**

Add helper and replace the stub:

```ts
const STATUS_MAP: Record<string, ParsedBet['status']> = {
  won: 'WON', win: 'WON',
  lost: 'LOST', lose: 'LOST', loss: 'LOST',
  push: 'PUSH', draw: 'DRAW', 'cashed out': 'CASHED_OUT',
  'cash out': 'CASHED_OUT', cashedout: 'CASHED_OUT',
  'half-won': 'HALF_WON', 'half won': 'HALF_WON',
  'half-lost': 'HALF_LOST', 'half lost': 'HALF_LOST',
  void: 'VOID',
  pending: 'PENDING',
  '': 'PENDING',
}

function parseFormatB(block: string, warnings: string[]): ParsedBet | null {
  const lines = block.split('\n')
  const kv: Record<string, string> = {}
  let lastKey = ''
  for (const line of lines) {
    const trimmed = line.trim()
    if (!trimmed) continue
    const match = trimmed.match(/^([A-Za-z][\w\s]{0,30}):(.*)$/)
    if (match) {
      const key = match[1].trim()
      const value = match[2].trim()
      if (value) {
        kv[key] = value
      } else {
        lastKey = key
      }
    } else if (lastKey) {
      kv[lastKey] = (kv[lastKey] ?? '') + trimmed
      lastKey = ''
    }
  }

  const ticketId = kv['Bet Ticket ID'] ?? kv['Purchase Ticket ID'] ?? null
  const betLabel = kv['Bet'] ?? ''
  const odds = Number((kv['Odds'] ?? '').replace(/[A-Za-z]/g, '').trim()) || 0
  const betType = (kv['Bet Type'] ?? '').trim()
  const event = kv['Event'] ?? ''
  const eventDateRaw = kv['Event Date'] ?? ''
  const betDateRaw = kv['Bet Date'] ?? ''
  const league = kv['League'] ?? 'Other'
  const stake = Number((kv['Stake'] ?? '').replace(/MYR/i, '').trim()) || 0
  const returnAmount = Number((kv['Return'] ?? '').replace(/MYR/i, '').trim()) || 0
  const bonus = kv['Bonus'] ? Number(kv['Bonus'].replace(/MYR/i, '').trim()) : null
  const statusRaw = (kv['Status'] ?? '').toLowerCase()
  const result = kv['Result'] ?? null

  if (!betLabel || !odds || !stake || odds <= 1.0) {
    warnings.push(`Format B invalid block (label="${betLabel || '?'}"). Skipped.`)
    return null
  }

  const status: ParsedBet['status'] =
    STATUS_MAP[statusRaw] ??
    (returnAmount > stake ? 'WON' : returnAmount === stake ? 'PUSH' : returnAmount === 0 ? 'LOST' : 'PENDING')

  const raw = ParsedBetSchema.safeParse({
    ticketId, betLabel, odds, betType, event,
    league, sport: inferSport(league),
    betDate: betDateRaw || null,
    eventDate: eventDateRaw || null,
    stake, returnAmount,
    bonus: bonus ?? null,
    status,
    result,
  })
  if (!raw.success) {
    warnings.push(`Schema validation failed for bet "${betLabel}": ${raw.error.message}`)
    return null
  }
  return raw.data
}
```

- [ ] **Step 4: Run tests**

```bash
npm test -- scripts/parse-format-B.test.ts
```
Expected: 3 tests pass.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat(parse): Format B (Bets.txt key-value) parser with status mapping"
```

---

### Task 8: Import script (`scripts/import-bets.ts`)

**Files:**
- Create: `scripts/import-bets.ts`
- No tests (smoke tested via end-to-end in Task 18)

**Interfaces:**
- Consumes: Prisma `db`, `parsePasteInput` from Task 6/7, `computeProfit` from Task 4, `inferSport` from Task 5
- Produces: working `npm run import -- <path-to-Bets.txt>` CLI that populates DB idempotently

- [ ] **Step 1: Write `scripts/import-bets.ts`**

```ts
import { readFile } from 'node:fs/promises'
import { db } from '../src/lib/db'
import { parsePasteInput } from '../src/lib/parse-bets'
import { computeProfit } from '../src/lib/profit'
import type { BetStatus } from '@prisma/client'

const ACTIVE_STATUSES: BetStatus[] = ['PENDING']

async function main() {
  const filePath = process.argv[2]
  if (!filePath) {
    console.error('Usage: npm run import -- <path-to-Bets.txt>')
    process.exit(1)
  }

  const text = await readFile(filePath, 'utf-8')
  const { bets, warnings } = parsePasteInput(text)
  for (const w of warnings) console.warn(`⚠️  ${w}`)
  console.log(`Parsed ${bets.length} bets (${warnings.length} warnings)`)

  if (bets.length === 0) {
    console.error('No bets to import.')
    process.exit(1)
  }

  console.log('Wiping existing data...')
  await db.$transaction([db.bet.deleteMany({}), db.transaction.deleteMany({})])

  const minBetDate = bets
    .map(b => b.betDate ? new Date(b.betDate) : new Date())
    .reduce((min, d) => d < min ? d : min, new Date())

  const seedTs = new Date(minBetDate.getTime() - 1000)
  await db.transaction.create({
    data: {
      type: 'DEPOSIT',
      amount: 1000,
      balance: 1000,
      note: 'Starting bankroll',
      createdAt: seedTs,
    },
  })
  console.log('Seeded starting bankroll: MYR 1000')

  const seenTicketIds = new Set<string>()
  const betRows: any[] = []
  const txnRows: any[] = []
  let runningBalance = 1000

  // Sort bets by betDate (nulls last) for chronological txn insertion
  const sortedBets = [...bets].sort((a, b) => {
    const ad = a.betDate ? new Date(a.betDate).getTime() : Date.now()
    const bd = b.betDate ? new Date(b.betDate).getTime() : Date.now()
    return ad - bd
  })

  for (const b of sortedBets) {
    if (b.ticketId) {
      if (seenTicketIds.has(b.ticketId)) {
        console.warn(`⚠️  Skipping duplicate ticketId: ${b.ticketId}`)
        continue
      }
      seenTicketIds.add(b.ticketId)
    }

    const profit = computeProfit({ returnAmount: b.returnAmount, stake: b.stake, bonus: b.bonus ?? 0 })
    const isActive = ACTIVE_STATUSES.includes(b.status)
    const betDate = b.betDate ? new Date(b.betDate) : new Date()
    const eventDate = b.eventDate ? new Date(b.eventDate) : null

    betRows.push({
      betDate,
      eventDate,
      sport: b.sport,
      league: b.league,
      event: b.event,
      betType: b.betType,
      betLabel: b.betLabel,
      odds: b.odds,
      stake: b.stake,
      returnAmount: b.returnAmount,
      profit,
      status: b.status,
      result: b.result,
      ticketId: b.ticketId,
      bonus: b.bonus ?? null,
    })

    if (!isActive) {
      runningBalance += profit
      txnRows.push({
        type: 'BET_SETTLE',
        amount: profit,
        balance: runningBalance,
        betId: `pending-link`, // linked after createMany returns IDs
        createdAt: new Date(betDate.getTime() + 1000),
        note: `${b.betLabel} @ ${b.odds} (${b.event})`,
      })
    }
  }

  console.log(`Inserting ${betRows.length} bets...`)
  await db.bet.createMany({ data: betRows })
  // Note: createMany doesn't return IDs in sqlite/postgres without extra work.
  // For the linked txns, we run them as a second pass below.

  // Second pass — link transactions to inserted bets by ticketId + betDate
  const insertedBets = await db.bet.findMany({
    orderBy: { betDate: 'asc' },
  })
  // Re-walk sortedBets to create proper txn links
  await db.transaction.createMany({
    data: insertedBets
      .filter(b => b.status !== 'PENDING')
      .map((b, i) => ({
        type: 'BET_SETTLE',
        amount: b.profit,
        balance: 1000 + insertedBets.slice(0, i).reduce((sum, ob) => sum + (ob.status === 'PENDING' ? 0 : ob.profit), 0),
        betId: b.id,
        createdAt: new Date(b.betDate.getTime() + 1000),
        note: `${b.betLabel} @ ${b.odds} (${b.event})`,
      })),
  })

  console.log(`Inserted ${insertedBets.length} bets + linked transactions`)
  const finalBalance = await db.transaction.orderByFirst?.() ?? await db.transaction.findFirst({ orderBy: { createdAt: 'desc' }})
  console.log(`✓ Import done. Current bankroll: MYR ${finalBalance?.balance.toFixed(2)}`)
  await db.$disconnect()
}

main().catch(e => {
  console.error(e)
  process.exit(1)
})
```

- [ ] **Step 2: Run import smoke test**

```bash
npm run import -- "E:\AI Llms\WC Bets\Bets.txt"
```
Expected: `Parsed 127 bets (0 warnings)` → `Seeded starting bankroll: MYR 1000` → `✓ Import done. Current bankroll: MYR 1205.56`.

(Note: exact end balance may vary slightly if parser finds edge cases in Bets.txt not covered by tests — if warnings appear and are obvious to fix, fix in parse-bets.ts and re-run.)

- [ ] **Step 3: Verify DB**

```bash
npx tsx -e "import { db } from './src/lib/db'; (async () => { const c = await db.bet.count(); console.log('bets:', c); const t = await db.transaction.count(); console.log('txns:', t); await db.\$disconnect(); })()"
```
Expected: `bets: 127` and `txns: 128` (127 settles + 1 deposit).

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat(import): one-shot Bets.txt → Postgres import with bankroll seeding"
```

---

### Task 9: Metrics — `computeSummary` + `computeOutcomeBreakdown`

**Files:**
- Create: `src/lib/metrics.ts`
- Create: `scripts/metrics-summary.test.ts`

**Interfaces:**
- Produces: `computeSummary(bets, txns)` and `computeOutcomeBreakdown(bets)` pure functions

- [ ] **Step 1: Write `scripts/metrics-summary.test.ts`**

```ts
import assert from 'node:assert/strict'
import { test } from 'node:test'
import { computeSummary, computeOutcomeBreakdown } from '../src/lib/metrics'
import type { Bet, Transaction } from '@prisma/client'

const mkBet = (p: Partial<Bet>): Bet => ({
  id: '1', betDate: new Date('2026-07-13'), eventDate: null,
  sport: 'Soccer', league: 'World Cup 2026', event: 'A vs B',
  betType: 'FT Asian Handicap', betLabel: 'A',
  odds: 1.8, stake: 50, returnAmount: 90, profit: 40, status: 'WON',
  result: '1-0', ticketId: null, bonus: null, createdAt: new Date(),
  ...p,
})
const mkTxn = (p: Partial<Transaction>): Transaction => ({
  id: '1', type: 'DEPOSIT', amount: 1000, balance: 1000,
  betId: null, note: null, createdAt: new Date('2026-07-12'),
  ...p,
})

test('Summary counts basic', () => {
  const bets = [
    mkBet({ id: 'a', status: 'WON', profit: 40, stake: 50, returnAmount: 90 }),
    mkBet({ id: 'b', status: 'LOST', profit: -50, stake: 50, returnAmount: 0 }),
    mkBet({ id: 'c', status: 'PUSH', profit: 0, stake: 50, returnAmount: 50 }),
    mkBet({ id: 'd', status: 'PENDING', profit: 0, stake: 50, returnAmount: 0 }),
  ]
  const txns = [
    mkTxn({ balance: 1000 }),
    mkTxn({ id: 't1', balance: 1040, type: 'BET_SETTLE', amount: 40, }),
    mkTxn({ id: 't2', balance: 990, type: 'BET_SETTLE', amount: -50 }),
    mkTxn({ id: 't3', balance: 990, type: 'BET_SETTLE', amount: 0 }),
  ]
  const s = computeSummary(bets, txns)
  assert.equal(s.totalBets, 4)
  assert.equal(s.settledBets, 3)
  assert.equal(s.netPL, -10)
  assert.equal(s.roiPct, -10 / (50+50+50) * 100)
  assert.equal(s.winningBets, 1)
  assert.equal(s.losingBets, 1)
  assert.equal(s.pushBets, 1)
  assert.equal(s.currentBankroll, 990)
  assert.equal(s.startingBankroll, 1000)
  assert.equal(s.exposure, 50) // PENDING bet stake
  assert.equal(s.bestBet?.id, 'a')
  assert.equal(s.worstBet?.id, 'b')
  assert.equal(s.totalTurnover, 200) // 4 * 50
  assert.equal(s.avgStake, 50)
})

test('Outcome breakdown from mixed statuses', () => {
  const bets = [
    mkBet({ status: 'WON' }),
    mkBet({ status: 'HALF_WON' }),
    mkBet({ status: 'CASHED_OUT' }),
    mkBet({ status: 'LOST' }),
    mkBet({ status: 'HALF_LOST' }),
    mkBet({ status: 'PUSH' }),
    mkBet({ status: 'DRAW' }),
    mkBet({ status: 'VOID' }),
    mkBet({ status: 'PENDING' }),
  ]
  const o = computeOutcomeBreakdown(bets)
  assert.equal(o.won, 3)
  assert.equal(o.lost, 2)
  assert.equal(o.push, 3)
  assert.equal(o.wonPct, 3/8 * 100)  // exclude pending
  assert.equal(o.pushPct, 3/8 * 100)
  assert.equal(o.lostPct, 2/8 * 100)
})
```

- [ ] **Step 2: Run test (expect fail)**

```bash
npm test -- scripts/metrics-summary.test.ts
```

- [ ] **Step 3: Write `src/lib/metrics.ts`**

```ts
import type { Bet, Transaction, BetStatus } from '@prisma/client'

const WON_BUCKET: BetStatus[] = ['WON', 'HALF_WON', 'CASHED_OUT']
const LOST_BUCKET: BetStatus[] = ['LOST', 'HALF_LOST']
const PUSH_BUCKET: BetStatus[] = ['PUSH', 'DRAW', 'VOID']
const ACTIVE_BUCKET: BetStatus[] = ['PENDING']

export interface Summary {
  totalBets: number
  settledBets: number
  netPL: number
  roiPct: number
  winRate: number
  winningBets: number
  losingBets: number
  pushBets: number
  bestBet: Bet | null
  worstBet: Bet | null
  avgStake: number
  largestStake: number
  totalTurnover: number
  currentBankroll: number
  startingBankroll: number
  exposure: number
}

export interface OutcomeBreakdown {
  won: number
  lost: number
  push: number
  wonPct: number
  lostPct: number
  pushPct: number
}

const isSettled = (s: BetStatus) => !ACTIVE_BUCKET.includes(s)

export function computeSummary(bets: Bet[], txns: Transaction[]): Summary {
  const settled = bets.filter(b => isSettled(b.status))
  const won = bets.filter(b => WON_BUCKET.includes(b.status))
  const lost = bets.filter(b => LOST_BUCKET.includes(b.status))
  const push = bets.filter(b => PUSH_BUCKET.includes(b.status))
  const active = bets.filter(b => ACTIVE_BUCKET.includes(b.status))

  const netPL = settled.reduce((s, b) => s + b.profit, 0)
  const turnoverAll = bets.reduce((s, b) => s + b.stake, 0)
  const turnoverSettled = settled.reduce((s, b) => s + b.stake, 0)
  const roi = turnoverSettled > 0 ? (netPL / turnoverSettled) * 100 : 0
  const totalSettled = won.length + lost.length + push.length
  const winRate = totalSettled > 0 ? (won.length / totalSettled) * 100 : 0

  const latestTxn = txns
    .slice()
    .sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime())[0]
  const startTxn = txns.find(t => t.type === 'DEPOSIT')
  const largestStake = bets.reduce((m, b) => Math.max(m, b.stake), 0)

  return {
    totalBets: bets.length,
    settledBets: settled.length,
    netPL,
    roiPct: roi,
    winRate,
    winningBets: won.length,
    losingBets: lost.length,
    pushBets: push.length,
    bestBet: settled.reduce<Bet | null>((best, b) => (!best || b.profit > best.profit) ? b : best, null),
    worstBet: settled.reduce<Bet | null>((worst, b) => (!worst || b.profit < worst.profit) ? b : worst, null),
    avgStake: bets.length > 0 ? turnoverAll / bets.length : 0,
    largestStake,
    totalTurnover: turnoverAll,
    currentBankroll: latestTxn?.balance ?? 1000,
    startingBankroll: startTxn?.amount ?? 1000,
    exposure: active.reduce((s, b) => s + b.stake, 0),
  }
}

export function computeOutcomeBreakdown(bets: Bet[]): OutcomeBreakdown {
  const won = bets.filter(b => WON_BUCKET.includes(b.status))
  const lost = bets.filter(b => LOST_BUCKET.includes(b.status))
  const push = bets.filter(b => PUSH_BUCKET.includes(b.status))
  const denom = won.length + lost.length + push.length
  return {
    won: won.length,
    lost: lost.length,
    push: push.length,
    wonPct: denom > 0 ? (won.length / denom) * 100 : 0,
    lostPct: denom > 0 ? (lost.length / denom) * 100 : 0,
    pushPct: denom > 0 ? (push.length / denom) * 100 : 0,
  }
}
```

- [ ] **Step 4: Run tests**

```bash
npm test -- scripts/metrics-summary.test.ts
```
Expected: 2 tests pass.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat(metrics): computeSummary + computeOutcomeBreakdown"
```

---

### Task 10: Metrics — `computePeriodStats`, `computeDailyPnL`, `computeLatestBets`, `computeActiveBets`

**Files:**
- Modify: `src/lib/metrics.ts` (add functions)
- Create: `scripts/metrics-rest.test.ts`

**Interfaces:**
- Produces: 4 additional pure functions

- [ ] **Step 1: Write `scripts/metrics-rest.test.ts`**

```ts
import assert from 'node:assert/strict'
import { test } from 'node:test'
import { computePeriodStats, computeDailyPnL, computeLatestBets, computeActiveBets } from '../src/lib/metrics'
import type { Bet } from '@prisma/client'

const mkBet = (p: Partial<Bet>): Bet => ({
  id: '1', betDate: new Date('2026-07-13T02:00:00Z'), eventDate: null,
  sport: 'Soccer', league: 'X', event: 'A vs B',
  betType: 'AH', betLabel: 'A', odds: 1.8, stake: 50, returnAmount: 90,
  profit: 40, status: 'WON', result: null, ticketId: null, bonus: null,
  createdAt: new Date(),
  ...p,
})

test('computePeriodStats week offset 0', () => {
  const bets = [
    mkBet({ betDate: new Date('2026-07-13T02:00:00Z'), status: 'WON', profit: 40, stake: 50 }),
    mkBet({ betDate: new Date('2026-07-07T02:00:00Z'), status: 'LOST', profit: -50, stake: 50 }),
  ]
  const s = computePeriodStats(bets, 'week', 0, new Date('2026-07-13T03:00:00Z'))
  // Week containing Jul 13 = Mon Jul 13 (assume Mon start) to Sun Jul 19
  assert.equal(s.label, 'This Week')
  assert.equal(s.bets, 1)
  assert.equal(s.netPL, 40)
})

test('computePeriodStats month offset 0', () => {
  const bets = [
    mkBet({ betDate: new Date('2026-07-13T02:00:00Z'), status: 'WON', profit: 40, stake: 50 }),
    mkBet({ betDate: new Date('2026-06-15T02:00:00Z'), status: 'LOST', profit: -50, stake: 50 }),
  ]
  const s = computePeriodStats(bets, 'month', 0, new Date('2026-07-13T03:00:00Z'))
  assert.equal(s.label, 'This Month')
  assert.equal(s.bets, 1)
  assert.equal(s.netPL, 40)
})

test('computeDailyPnL 30 days', () => {
  const bets = [
    mkBet({ betDate: new Date('2026-07-13T02:00:00Z'), status: 'WON', profit: 40, stake: 50 }),
    mkBet({ betDate: new Date('2026-07-13T05:00:00Z'), status: 'LOST', profit: -10, stake: 30 }),
  ]
  const series = computeDailyPnL(bets, 30, new Date('2026-07-13T23:00:00Z'))
  assert.equal(series.length, 30)
  const today = series[series.length - 1]
  assert.equal(today.pnl, 30)
  assert.equal(today.betCount, 2)
  // cumulative starts at 1000
  assert.equal(series[0].cumulative, 1000)
  assert.equal(today.cumulative, 1030)
})

test('computeLatestBets returns most recent 10', () => {
  const bets = Array.from({ length: 15 }, (_, i) =>
    mkBet({ id: String(i), betDate: new Date(`2026-07-${10 + i}T02:00:00Z`), })
  )
  const latest = computeLatestBets(bets, 10)
  assert.equal(latest.length, 10)
  assert.equal(latest[0].id, '14')  // most recent first
})

test('computeActiveBets filters PENDING', () => {
  const bets = [
    mkBet({ id: '1', status: 'PENDING' }),
    mkBet({ id: '2', status: 'WON' }),
    mkBet({ id: '3', status: 'PENDING' }),
  ]
  const active = computeActiveBets(bets)
  assert.equal(active.length, 2)
  assert.equal(active[0].id, '1')
})
```

- [ ] **Step 2: Run tests (expect fail)**

```bash
npm test -- scripts/metrics-rest.test.ts
```

- [ ] **Step 3: Add functions to `src/lib/metrics.ts`**

Append:

```ts
export interface PeriodStats {
  label: string
  bets: number
  settled: number
  netPL: number
  roiPct: number
  winRate: number
}

function startOfWeek(d: Date): Date {
  const r = new Date(d)
  r.setHours(0, 0, 0, 0)
  const day = r.getDay()  // 0=Sun,1=Mon
  r.setDate(r.getDate() - (day === 0 ? 6 : day - 1))
  return r
}

function startOfMonth(d: Date): Date {
  return new Date(d.getFullYear(), d.getMonth(), 1)
}

export function computePeriodStats(
  bets: Bet[],
  period: 'week' | 'month',
  offset: number = 0,
  now: Date = new Date()
): PeriodStats {
  const span = period === 'week' ? 7 : 31  // month approx
  const stepMs = span * 24 * 60 * 60 * 1000
  let thisStart: Date
  let prevStart: Date
  let prevEnd: Date
  if (period === 'week') {
    thisStart = startOfWeek(now)
    thisStart = new Date(thisStart.getTime() - offset * stepMs)
    prevStart = new Date(thisStart.getTime() - stepMs)
    prevEnd = thisStart
  } else {
    // Months are variable; do calendar months
    const ref = new Date(now.getFullYear(), now.getMonth() - offset, 1)
    thisStart = ref
    prevStart = new Date(now.getFullYear(), now.getMonth() - offset - 1, 1)
    prevEnd = thisStart
  }
  const thisEnd = new Date(thisStart.getTime() + stepMs)

  const periodBets = bets.filter(b => {
    const bd = b.betDate
    return bd >= thisStart && bd < thisEnd
  })
  const settled = periodBets.filter(b => isSettled(b.status))
  const won = periodBets.filter(b => WON_BUCKET.includes(b.status))
  const lost = periodBets.filter(b => LOST_BUCKET.includes(b.status))
  const push = periodBets.filter(b => PUSH_BUCKET.includes(b.status))
  const total = won.length + lost.length + push.length
  const turnover = settled.reduce((s, b) => s + b.stake, 0)
  const netPL = settled.reduce((s, b) => s + b.profit, 0)
  return {
    label: offset === 0 ? (period === 'week' ? 'This Week' : 'This Month') : (period === 'week' ? 'Last Week' : 'Last Month'),
    bets: periodBets.length,
    settled: settled.length,
    netPL,
    roiPct: turnover > 0 ? (netPL / turnover) * 100 : 0,
    winRate: total > 0 ? (won.length / total) * 100 : 0,
  }
}

export interface DailyPnLPoint {
  date: string  // YYYY-MM-DD (UTC)
  pnl: number
  cumulative: number
  betCount: number
}

export function computeDailyPnL(bets: Bet[], days: number = 30, now: Date = new Date()): DailyPnLPoint[] {
  const points: DailyPnLPoint[] = []
  const dayMs = 24 * 60 * 60 * 1000
  // Start with starting bankroll txn = look up via env constant; pass 1000 as default.
  // For Phase 1 we hard-code starting bankroll; passed-in now acts as upper bound.
  let cumulative = 1000

  // If bets exist before window, accumulate their P/L into starting cumulative
  const windowStart = new Date(now.getTime() - (days - 1) * dayMs)
  const beforeWindow = bets.filter(b => isSettled(b.status) && b.betDate.getTime() < windowStart.getTime())
  cumulative += beforeWindow.reduce((s, b) => s + b.profit, 0)

  for (let i = 0; i < days; i++) {
    const dayStart = new Date(windowStart.getTime() + i * dayMs)
    const dayEnd = new Date(dayStart.getTime() + dayMs)
    const dayKey = dayStart.toISOString().slice(0, 10)
    const dayBets = bets.filter(b =>
      isSettled(b.status) &&
      b.betDate.getTime() >= dayStart.getTime() &&
      b.betDate.getTime() < dayEnd.getTime()
    )
    const pnl = dayBets.reduce((s, b) => s + b.profit, 0)
    cumulative += pnl
    points.push({ date: dayKey, pnl, cumulative, betCount: dayBets.length })
  }
  return points
}

export function computeLatestBets(bets: Bet[], limit: number = 10): Bet[] {
  return bets
    .slice()
    .sort((a, b) => b.betDate.getTime() - a.betDate.getTime())
    .slice(0, limit)
}

export function computeActiveBets(bets: Bet[]): Bet[] {
  return bets.filter(b => ACTIVE_BUCKET.includes(b.status))
}
```

- [ ] **Step 4: Run tests**

```bash
npm test -- scripts/metrics-rest.test.ts
```
Expected: 4 tests pass.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat(metrics): periodStats, dailyPnL, latestBets, activeBets"
```

---

### Task 11: UI primitives (Card, StatCard, Badge, BetsTable)

**Files:**
- Create: `src/components/ui/Card.tsx`
- Create: `src/components/ui/StatCard.tsx`
- Create: `src/components/ui/Badge.tsx`
- Create: `src/components/ui/BetsTable.tsx`

**Interfaces:**
- Produces 4 reusable UI components for dashboard composition

- [ ] **Step 1: Write `src/components/ui/Card.tsx`**

```tsx
import clsx from 'clsx'

export function Card({
  title, children, className, action,
}: {
  title?: string
  children: React.ReactNode
  className?: string
  action?: React.ReactNode
}) {
  return (
    <section className={clsx('bg-card border border-card-border rounded-lg p-4', className)}>
      {title && (
        <header className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold text-muted uppercase tracking-wide">{title}</h2>
          {action}
        </header>
      )}
      {children}
    </section>
  )
}
```

- [ ] **Step 2: Write `src/components/ui/StatCard.tsx`**

```tsx
import clsx from 'clsx'
import { Card } from './Card'

const TONE_CLASS = {
  positive: 'text-positive',
  negative: 'text-negative',
  push: 'text-push',
  muted: 'text-muted',
  neutral: 'text-primary',
}

export function StatCard({
  label, value, sub, tone = 'neutral',
}: {
  label: string
  value: string | number
  sub?: string
  tone?: keyof typeof TONE_CLASS
}) {
  return (
    <Card>
      <div className="text-xs uppercase tracking-wide text-muted">{label}</div>
      <div className={clsx('mt-1 text-2xl font-bold', TONE_CLASS[tone])}>{value}</div>
      {sub && <div className="text-xs mt-1 text-muted">{sub}</div>}
    </Card>
  )
}
```

- [ ] **Step 3: Write `src/components/ui/Badge.tsx`**

```tsx
import clsx from 'clsx'
import type { BetStatus } from '@prisma/client'

const TONE: Record<BetStatus, string> = {
  WON: 'bg-positive/15 text-positive',
  HALF_WON: 'bg-half/15 text-half',
  CASHED_OUT: 'bg-positive/15 text-positive',
  LOST: 'bg-negative/15 text-negative',
  HALF_LOST: 'bg-half/15 text-half',
  PUSH: 'bg-push/15 text-push',
  DRAW: 'bg-push/15 text-push',
  VOID: 'bg-muted/15 text-muted',
  PENDING: 'bg-accent/15 text-accent',
}
export function Badge({ status }: { status: BetStatus }) {
  const label = status.replace(/_/g, ' ').toLowerCase()
  return (
    <span className={clsx('px-2 py-0.5 rounded-full text-xs font-semibold capitalize whitespace-nowrap', TONE[status])}>
      {label}
    </span>
  )
}
```

- [ ] **Step 4: Write `src/components/ui/BetsTable.tsx`**

```tsx
import { Badge } from './Badge'
import { fmtMYR, fmtDate } from '@/lib/format'
import type { Bet } from '@prisma/client'

export function BetsTable({ bets }: { bets: Bet[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-muted border-b border-card-border">
            <th className="py-2 pr-2">Date</th>
            <th className="py-2 pr-2">Event</th>
            <th className="py-2 pr-2">Bet</th>
            <th className="py-2 pr-2 text-right">Odds</th>
            <th className="py-2 pr-2 text-right">Stake</th>
            <th className="py-2 pr-2">Status</th>
            <th className="py-2 pr-2 text-right">P/L</th>
          </tr>
        </thead>
        <tbody>
          {bets.map(b => (
            <tr key={b.id} className="border-b border-card-border/50 last:border-0">
              <td className="py-2 pr-2 whitespace-nowrap">{fmtDate(b.betDate)}</td>
              <td className="py-2 pr-2 max-w-[220px] truncate" title={b.event}>{b.event}</td>
              <td className="py-2 pr-2" title={b.betType}>{b.betLabel}</td>
              <td className="py-2 pr-2 text-right">{b.odds.toFixed(2)}</td>
              <td className="py-2 pr-2 text-right">MYR {b.stake.toFixed(2)}</td>
              <td className="py-2 pr-2"><Badge status={b.status} /></td>
              <td className={`py-2 pr-2 text-right font-semibold ${b.profit > 0 ? 'text-positive' : b.profit < 0 ? 'text-negative' : 'text-push'}`}>
                {fmtMYR(b.profit)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
```

- [ ] **Step 5: Typecheck**

```bash
npm run typecheck
```
Expected: no errors.

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "feat(ui): Card, StatCard, Badge, BetsTable primitives"
```

---

### Task 12: Charts (PnLChart, WonLostPie)

**Files:**
- Create: `src/components/charts/PnLChart.tsx`
- Create: `src/components/charts/WonLostPie.tsx`

**Interfaces:**
- Consumes: `DailyPnLPoint[]` and `OutcomeBreakdown` from `@/lib/metrics`
- Produces: two client-side Recharts components

- [ ] **Step 1: Write `src/components/charts/PnLChart.tsx`**

```tsx
'use client'
import { ComposedChart, Area, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'
import type { DailyPnLPoint } from '@/lib/metrics'

export function PnLChart({ data }: { data: DailyPnLPoint[] }) {
  return (
    <ResponsiveContainer width="100%" height={260}>
      <ComposedChart data={data} margin={{ left: 0, right: 12, top: 8, bottom: 0 }}>
        <defs>
          <linearGradient id="cumGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#5b8def" stopOpacity={0.35} />
            <stop offset="100%" stopColor="#5b8def" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid stroke="#262b33" strokeDasharray="3 3" />
        <XAxis
          dataKey="date"
          tickFormatter={d => new Date(d).toLocaleDateString('en-GB', { day: '2-digit', month: 'short', timeZone: 'UTC' })}
          stroke="#9ca3a0" fontSize={11} tickLine={false}
        />
        <YAxis stroke="#9ca3a0" fontSize={11} tickLine={false} width={48} />
        <Tooltip
          contentStyle={{ background: '#13181d', border: '1px solid #262b33', borderRadius: 6, color: '#000' }}
          labelStyle={{ color: '#000' }}
          itemStyle={{ color: '#000' }}
        />
        <Area
          type="monotone"
          dataKey="cumulative"
          stroke="#5b8def" strokeWidth={2} fill="url(#cumGrad)" name="Bankroll"
        />
        <Bar dataKey="pnl" name="Daily P/L" radius={[2, 2, 0, 0]}>
          {data.map((d, i) => (
            <rect key={i} fill={d.pnl >= 0 ? '#5cb87a' : '#c8814a'} />
          ))}
        </Bar>
      </ComposedChart>
    </ResponsiveContainer>
  )
}
```

- [ ] **Step 2: Write `src/components/charts/WonLostPie.tsx`**

```tsx
'use client'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Label } from 'recharts'
import type { OutcomeBreakdown } from '@/lib/metrics'

const COLORS = { won: '#5cb87a', push: '#d4a85c', lost: '#c8814a' }

export function WonLostPie({ data }: { data: OutcomeBreakdown }) {
  const total = data.won + data.lost + data.push
  const rows = [
    { name: 'Won', value: data.won, color: COLORS.won },
    { name: 'Push', value: data.push, color: COLORS.push },
    { name: 'Lost', value: data.lost, color: COLORS.lost },
  ]
  return (
    <div className="flex items-center gap-4">
      <div className="relative w-[180px] h-[180px]">
        <ResponsiveContainer>
          <PieChart>
            <Pie data={rows} dataKey="value" nameKey="name" innerRadius={60} outerRadius={90} paddingAngle={2}>
              {rows.map((r, i) => <Cell key={i} fill={r.color} />)}
            </Pie>
            <Tooltip contentStyle={{ background: '#13181d', border: '1px solid #262b33' }} />
            <Label
              position="center"
              content={({ viewBox }) => {
                const { cx, cy } = viewBox as any
                return (
                  <text x={cx} y={cy - 8} textAnchor="middle" fill="#e8e6e3" fontSize={20} fontWeight={700}>
                    {total}
                  </text>
                )}}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
      <div className="space-y-1 text-sm">
        {rows.map(r => (
          <div key={r.name} className="flex items-center gap-2">
            <span className="inline-block w-3 h-3 rounded-sm" style={{ background: r.color }} />
            <span className="text-muted">{r.name}</span>
            <span className="text-primary font-semibold ml-1">{r.value}</span>
            <span className="text-muted text-xs">
              {total > 0 ? (r.value / total * 100).toFixed(1) : '0.0'}%
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
```

- [ ] **Step 3: Typecheck**

```bash
npm run typecheck
```

- [ ] **Step 4: Build**

```bash
npm run build
```
Expected: build succeeds (warnings ok if Tailwind/React exhaustive deps).

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat(charts): PnLChart (Composed) and WonLostPie (Donut)"
```

---

### Task 13: TopNav + layout + placeholder pages

**Files:**
- Modify: `src/app/layout.tsx`
- Create: `src/components/nav/TopNav.tsx`
- Create: `src/app/analytics/page.tsx`
- Create: `src/app/bankroll/page.tsx`
- Create: `src/app/tools/page.tsx`

**Interfaces:**
- Produces: shared nav across pages, dark theme shell, 3 placeholders

- [ ] **Step 1: Write `src/components/nav/TopNav.tsx`**

```tsx
import Link from 'next/link'

const linkClass = 'px-3 py-1.5 rounded-md text-sm font-medium text-muted hover:bg-card hover:text-primary transition-colors'
const activeClass = 'bg-card text-primary'

export function TopNav({ current }: { current: 'dashboard' | 'analytics' | 'bankroll' | 'tools' }) {
  return (
    <header className="border-b border-card-border bg-base sticky top-0 z-10">
      <div className="max-w-7xl mx-auto flex items-center justify-between py-3 px-4">
        <Link href="/" className="text-lg font-bold tracking-tight">Bet Tracker</Link>
        <nav className="flex gap-1">
          <Link href="/" className={`${linkClass} ${current === 'dashboard' ? activeClass : ''}`}>Dashboard</Link>
          <Link href="/analytics" className={`${linkClass} ${current === 'analytics' ? activeClass : ''}`}>Analytics</Link>
          <Link href="/bankroll" className={`${linkClass} ${current === 'bankroll' ? activeClass : ''}`}>Bankroll</Link>
          <Link href="/tools" className={`${linkClass} ${current === 'tools' ? activeClass : ''}`}>Tools</Link>
        </nav>
      </div>
    </header>
  )
}
```

- [ ] **Step 2: Replace `src/app/layout.tsx`**

```tsx
import './globals.css'
import { TopNav } from '@/components/nav/TopNav'

export const metadata = { title: 'Bet Tracker' }

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-base text-primary font-sans">
        <TopNav current="dashboard" />
        <main className="max-w-7xl mx-auto p-4 md:p-6">{children}</main>
      </body>
    </html>
  )
}
```

- [ ] **Step 3: Write placeholder pages**

`src/app/analytics/page.tsx`:
```tsx
import { Card } from '@/components/ui/Card'
import { TopNav } from '@/components/nav/TopNav'

export default function Page() {
  return (
    <>
      <TopNav current="analytics" />
      <div className="max-w-7xl mx-auto p-6">
        <Card title="Analytics">
          <p className="text-muted">Coming in Phase 2 — consistency map, losing runs, daily breakdown.</p>
        </Card>
      </div>
    </>
  )
}
```

`src/app/bankroll/page.tsx` (same structure, current='bankroll, message about Phase 3)
`src/app/tools/page.tsx` (same structure, current='tools, message about Phase 4)

(Note: for the placeholder pages, the TopNav must be inside each page since layout passes current='dashboard'. An alternative is to make TopNav a context-aware component — for Phase 1 we duplicate it in placeholders and override active state per-page.)

- [ ] **Step 4: Typecheck + build**

```bash
npm run typecheck
npm run build
```
Expected: clean.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat(nav): TopNav, layout shell, placeholder pages for Phases 2-4"
```

---

### Task 14: Main Dashboard page (`src/app/page.tsx`)

**Files:**
- Replace: `src/app/page.tsx`

**Interfaces:**
- Consumes: Prisma `db`, metrics functions, UI primitives, charts
- Produces: full dashboard layout per spec §5

- [ ] **Step 1: Write `src/app/page.tsx`**

```tsx
import { db } from '@/lib/db'
import { Card } from '@/components/ui/Card'
import { StatCard } from '@/components/ui/StatCard'
import { BetsTable } from '@/components/ui/BetsTable'
import { PnLChart } from '@/components/charts/PnLChart'
import { WonLostPie } from '@/components/charts/WonLostPie'
import { computeSummary, computeOutcomeBreakdown, computePeriodStats, computeDailyPnL, computeLatestBets, computeActiveBets } from '@/lib/metrics'
import { fmtMYR, fmtPct } from '@/lib/format'

export const dynamic = 'force-dynamic'

export default async function DashboardPage() {
  const [bets, txns] = await Promise.all([
    db.bet.findMany({ orderBy: { betDate: 'desc' } }),
    db.transaction.findMany({ orderBy: { createdAt: 'asc' } }),
  ])

  const summary = computeSummary(bets, txns)
  const breakdown = computeOutcomeBreakdown(bets)
  const weeklyThis = computePeriodStats(bets, 'week', 0)
  const weeklyLast = computePeriodStats(bets, 'week', 1)
  const monthlyThis = computePeriodStats(bets, 'month', 0)
  const monthlyLast = computePeriodStats(bets, 'month', 1)
  const daily = computeDailyPnL(bets, 30)
  const latest = computeLatestBets(bets, 10)
  const active = computeActiveBets(bets)

  const tonePL = summary.netPL > 0 ? 'positive' : summary.netPL < 0 ? 'negative' : 'push'
  const toneROI = summary.roiPct > 0 ? 'positive' : summary.roiPct < 0 ? 'negative' : 'push'
  const toneWR = summary.winRate >= 50 ? 'positive' : summary.winRate >= 40 ? 'push' : 'negative'

  return (
    <>
      <header className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <div className={`px-3 py-1.5 rounded-full text-sm font-semibold ${summary.currentBankroll >= 1000 ? 'bg-positive/15 text-positive' : 'bg-negative/15 text-negative'}`}>
          Net worth: {fmtMYR(summary.currentBankroll)}
          {summary.exposure > 0 && (
            <span className="text-muted ml-2 font-normal">({summary.exposure.toFixed(0)} exposed)</span>
          )}
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 mb-4">
        <StatCard label="Total Bets" value={summary.totalBets} sub={`${summary.exposure.toFixed(0)} MYR exposure`} />
        <StatCard label="Net P/L" value={fmtMYR(summary.netPL)} sub={`vs MYR ${summary.startingBankroll.toFixed(0)} start`} tone={tonePL} />
        <StatCard label="ROI" value={fmtPct(summary.roiPct)} sub={`on MYR ${summary.totalTurnover.toFixed(0)} turnover`} tone={toneROI} />
        <StatCard label="Win Rate" value={`${summary.winRate.toFixed(1)}%`} sub={`${summary.winningBets}W / ${summary.pushBets}P / ${summary.losingBets}L`} tone={toneWR} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-3 mb-4">
        <Card title={weeklyThis.label}>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div><div className="text-muted">Bets</div><div className="font-semibold">{weeklyThis.bets}</div></div>
            <div><div className="text-muted">Net P/L</div><div className={`font-semibold ${weeklyThis.netPL >= 0 ? 'text-positive' : 'text-negative'}`}>{fmtMYR(weeklyThis.netPL)}</div></div>
            <div><div className="text-muted">ROI</div><div className="font-semibold">{fmtPct(weeklyThis.roiPct)}</div></div>
            <div><div className="text-muted">Win Rate</div><div className="font-semibold">{weeklyThis.winRate.toFixed(1)}%</div></div>
          </div>
          <div className="mt-3 pt-2 border-t border-card-border text-xs text-muted">
            Last week: {weeklyLast.bets} bets · {fmtMYR(weeklyLast.netPL)} · {fmtPct(weeklyLast.roiPct)}
          </div>
        </Card>
        <Card title={monthlyThis.label}>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div><div className="text-muted">Bets</div><div className="font-semibold">{monthlyThis.bets}</div></div>
            <div><div className="text-muted">Net P/L</div><div className={`font-semibold ${monthlyThis.netPL >= 0 ? 'text-positive' : 'text-negative'}`}>{fmtMYR(monthlyThis.netPL)}</div></div>
            <div><div className="text-muted">ROI</div><div className="font-semibold">{fmtPct(monthlyThis.roiPct)}</div></div>
            <div><div className="text-muted">Win Rate</div><div className="font-semibold">{monthlyThis.winRate.toFixed(1)}%</div></div>
          </div>
          <div className="mt-3 pt-2 border-t border-card-border text-xs text-muted">
            Last month: {monthlyLast.bets} bets · {fmtMYR(monthlyLast.netPL)} · {fmtPct(monthlyLast.roiPct)}
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-3 mb-4">
        <Card title="Profit / Loss — Last 30 Days">
          <PnLChart data={daily} />
        </Card>
        <Card title="Won / Push / Lost">
          <WonLostPie data={breakdown} />
        </Card>
      </div>

      <Card title="Turnover & ROI" className="mb-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div><div className="text-muted">Total Turnover</div><div className="font-semibold">MYR {summary.totalTurnover.toFixed(2)}</div></div>
          <div><div className="text-muted">Average Stake</div><div className="font-semibold">MYR {summary.avgStake.toFixed(2)}</div></div>
          <div><div className="text-muted">Largest Win</div><div className="font-semibold text-positive">{summary.bestBet ? fmtMYR(summary.bestBet.profit) : '—'}</div></div>
          <div><div className="text-muted">Largest Loss</div><div className="font-semibold text-negative">{summary.worstBet ? fmtMYR(summary.worstBet.profit) : '—'}</div></div>
        </div>
      </Card>

      <Card title="Latest Bets" className="mb-4">
        {latest.length === 0 ? (
          <p className="text-muted text-sm">No bets yet. Add one using the form above.</p>
        ) : (
          <BetsTable bets={latest} />
        )}
      </Card>

      <Card title="Active Bets">
        {active.length === 0 ? (
          <p className="text-muted text-sm">No active bets.</p>
        ) : (
          <BetsTable bets={active} />
        )}
      </Card>
    </>
  )
}
```

- [ ] **Step 2: Verify dev server**

```bash
npm run dev
```
Open `http://localhost:3000` — should show:
- 127 Total Bets, +MYR 205.56 Net P/L, +20.X% ROI, ~58% Win Rate
- 30-day chart with green/blue bars + area
- Donut showing won/push/lost counts
- 10 latest bets in table
- "No active bets" card

Stop dev server.

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "feat(dashboard): main page with summary, charts, table, period cards"
```

---

### Task 15: Add Bet form + POST /api/bets

**Files:**
- Create: `src/components/forms/AddBetForm.tsx` (client)
- Create: `src/app/api/bets/route.ts`

**Interfaces:**
- Consumes: `bet-zod.ts`, sport-map, profit, db
- Produces: inline form posting to API; atomic bet + BET_SETTLE Transaction

- [ ] **Step 1: Write `src/app/api/bets/route.ts`**

```ts
import { NextRequest, NextResponse } from 'next/server'
import { db } from '@/lib/db'
import { computeProfit } from '@/lib/profit'
import { inferSport } from '@/lib/sport-map'
import { ParsedBetSchema } from '@/lib/bet-zod'
import type { BetStatus, TransactionType } from '@prisma/client'

export async function POST(req: NextRequest) {
  const body = await req.json()
  const parsed = ParsedBetSchema.safeParse({
    ticketId: body.ticketId ?? null,
    betLabel: body.betLabel,
    odds: Number(body.odds),
    betType: body.betType,
    event: body.event,
    league: body.league ?? 'Other',
    sport: body.sport ?? inferSport(body.league ?? 'Other'),
    betDate: body.betDate ?? new Date().toISOString(),
    eventDate: body.eventDate ?? null,
    stake: Number(body.stake),
    returnAmount: Number(body.returnAmount ?? 0),
    bonus: body.bonus ? Number(body.bonus) : null,
    status: body.status ?? (Number(body.returnAmount ?? 0) > Number(body.stake) ? 'WON' : Number(body.returnAmount ?? 0) === 0 ? 'LOST' : 'PENDING'),
    result: body.result ?? null,
  })
  if (!parsed.success) return NextResponse.json({ error: parsed.error.flatten() }, { status: 400 })

  const b = parsed.data
  const profit = computeProfit({ returnAmount: b.returnAmount, stake: b.stake, bonus: b.bonus ?? 0 })
  const isActive = b.status === 'PENDING'

  const created = await db.$transaction(async (tx) => {
    const bet = await tx.bet.create({
      data: {
        betDate: new Date(b.betDate || Date.now()),
        eventDate: b.eventDate ? new Date(b.eventDate) : null,
        sport: b.sport, league: b.league, event: b.event, betType: b.betType,
        betLabel: b.betLabel, odds: b.odds, stake: b.stake, returnAmount: b.returnAmount,
        profit, status: b.status, result: b.result, ticketId: b.ticketId, bonus: b.bonus ?? null,
      },
    })
    if (!isActive) {
      const latest = await tx.transaction.findFirst({ orderBy: { createdAt: 'desc' } })
      const newBalance = (latest?.balance ?? 1000) + profit
      await tx.transaction.create({
        data: {
          type: 'BET_SETTLE' as TransactionType,
          amount: profit, balance: newBalance,
          betId: bet.id, createdAt: new Date(bet.betDate.getTime() + 1000),
          note: `${b.betLabel} @ ${b.odds} (${b.event})`,
        },
      })
    }
    return bet
  })

  return NextResponse.json({ id: created.id })
}
```

- [ ] **Step 2: Write `src/components/forms/AddBetForm.tsx`**

```tsx
'use client'
import { useState } from 'react'
import { Card } from '@/components/ui/Card'

const BET_TYPES = [
  'FT Asian Handicap', 'FT O/U', '1st Half AH', 'To Qualify', 'FT Moneyline',
  'Goalscorer', 'Player Over X', 'Goalkeeper Over Saves', 'Both Teams To Score',
  'Total Cards O/U', '1st Set Handicap', 'Games O/U', '1X2',
  'Live Betting AH', 'Live Betting O/U', 'Other',
]

export function AddBetForm({ onInserted }: { onInserted: () => void }) {
  const [open, setOpen] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function submit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    setBusy(true); setError(null)
    const form = new FormData(e.currentTarget)
    const payload = Object.fromEntries(form.entries())
    const res = await fetch('/api/bets', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    if (!res.ok) {
      const err = await res.json()
      setError(JSON.stringify(err.error?.fieldErrors ?? err.error ?? err))
    } else {
      e.currentTarget.reset()
      onInserted()
    }
    setBusy(false)
  }

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="mb-4 px-3 py-1.5 rounded-md text-sm font-semibold bg-accent/15 text-accent"
      >
        + Add Bet
      </button>
    )
  }

  return (
    <Card title="Add Bet" className="mb-4">
      <form onSubmit={submit} className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
        <label className="md:col-span-1">
          <span className="text-muted">Bet Label</span>
          <input name="betLabel" required placeholder="France -0.75" className="mt-1 w-full bg-base border border-card-border rounded p-2" />
        </label>
        <label>
          <span className="text-muted">Odds</span>
          <input name="odds" type="number" step="0.01" required placeholder="1.65" className="mt-1 w-full bg-base border border-card-border rounded p-2" />
        </label>
        <label>
          <span className="text-muted">Stake (MYR)</span>
          <input name="stake" type="number" step="0.01" required placeholder="50.00" className="mt-1 w-full bg-base border border-card-border rounded p-2" />
        </label>
        <label className="md:col-span-1">
          <span className="text-muted">Bet Type</span>
          <select name="betType" className="mt-1 w-full bg-base border border-card-border rounded p-2">
            {BET_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
          </select>
        </label>
        <label className="md:col-span-2">
          <span className="text-muted">Event</span>
          <input name="event" required placeholder="A vs B" className="mt-1 w-full bg-base border border-card-border rounded p-2" />
        </label>
        <label className="md:col-span-1">
          <span className="text-muted">League</span>
          <input name="league" placeholder="World Cup 2026" className="mt-1 w-full bg-base border border-card-border rounded p-2" />
        </label>
        <label className="md:col-span-1">
          <span className="text-muted">Bet Date</span>
          <input name="betDate" type="datetime-local" className="mt-1 w-full bg-base border border-card-border rounded p-2" />
        </label>
        <label className="md:col-span-1">
          <span className="text-muted">Return (MYR, 0 if unsettled)</span>
          <input name="returnAmount" type="number" step="0.01" defaultValue="0" className="mt-1 w-full bg-base border border-card-border rounded p-2" />
        </label>
        <label className="md:col-span-1">
          <span className="text-muted">Bonus (MYR)</span>
          <input name="bonus" type="number" step="0.01" placeholder="0.00" className="mt-1 w-full bg-base border border-card-border rounded p-2" />
        </label>
        <label className="md:col-span-1">
          <span className="text-muted">Ticket ID</span>
          <input name="ticketId" placeholder="optional" className="mt-1 w-full bg-base border border-card-border rounded p-2" />
        </label>
        <div className="md:col-span-3 flex gap-2 mt-2">
          <button type="submit" disabled={busy} className="px-4 py-2 rounded-md text-sm font-semibold positive bg-positive text-base">
            {busy ? 'Saving...' : 'Save Bet'}
          </button>
          <button type="button" onClick={() => setOpen(false)} className="px-4 py-2 rounded-md text-sm text-muted">Cancel</button>
          {error && <span className="text-sm text-negative">{error}</span>}
        </div>
      </form>
    </Card>
  )
}
```

- [ ] **Step 3: Wire AddBetForm into dashboard page**

Edit `src/app/page.tsx` to render the form above the summary cards row. Wrap the dashboard server component so that AddBetForm sits in a client wrapper that triggers `router.refresh()` on insert.

```tsx
// Add at top of page component return, above the header:
import { AddBetForm } from '@/components/forms/AddBetForm'
import { RefreshCwButton } from '@/components/forms/RefreshCwButton'  // optional nav

// Place <AddBetForm onInserted={...} /> above the summary grid
```

For Phase 1, since dashboard is a server component, we add a thin client wrapper that handles refresh:

`src/components/forms/DashboardRefresh.tsx`:
```tsx
'use client'
import { useRouter } from 'next/navigation'
import { AddBetForm } from './AddBetForm'

export function DashboardRefresh() {
  const router = useRouter()
  return <AddBetForm onInserted={() => router.refresh()} />
}
```

Update `src/app/page.tsx`'s JSX to insert <div className="mb-4"><DashboardRefresh /></div> right after the header and before the summary cards grid.

- [ ] **Step 4: Smoke test**

Start dev server, open dashboard, click "+ Add Bet", enter a stub bet (`A`, 1.65, 50, FT Asian Handicap, "A vs B", World Cup 2026, return 82.50). Click Save.

Expected: form collapses, dashboard refreshes, bet count increments to 128, Net P/L updates by +MYR 32.50.

Stop dev server.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat(bets): AddBetForm + POST /api/bets with atomic transaction"
```

---

### Task 16: Paste parser UI + /api/parse-bets + /api/import-bets

**Files:**
- Create: `src/app/api/parse-bets/route.ts`
- Create: `src/app/api/import-bets/route.ts`
- Create: `src/components/forms/PasteParser.tsx`
- Create: `src/components/forms/DashboardRefresh.tsx` (modify to include paste parser too)

**Interfaces:**
- Produces: paste textarea → parse → preview → confirm → bulk insert

- [ ] **Step 1: Write `src/app/api/parse-bets/route.ts`**

```ts
import { NextRequest, NextResponse } from 'next/server'
import { parsePasteInput } from '@/lib/parse-bets'

export async function POST(req: NextRequest) {
  const { text } = await req.json()
  if (!text) return NextResponse.json({ error: 'missing text' }, { status: 400 })
  const result = parsePasteInput(text)
  return NextResponse.json(result)
}
```

- [ ] **Step 2: Write `src/app/api/import-bets/route.ts`**

```ts
import { NextRequest, NextResponse } from 'next/server'
import { db } from '@/lib/db'
import { computeProfit } from '@/lib/profit'
import { inferSport } from '@/lib/sport-map'
import type { ParsedBet } from '@/lib/bet-zod'
import type { BetStatus } from '@prisma/client'

export async function POST(req: NextRequest) {
  const { bets } = (await req.json()) as { bets: ParsedBet[] }
  if (!Array.isArray(bets) || bets.length === 0) {
    return NextResponse.json({ error: 'no bets' }, { status: 400 })
  }

  const inserted: string[] = []
  let runningBalance = 1000
  const latest = await db.transaction.findFirst({ orderBy: { createdAt: 'desc' } })
  runningBalance = latest?.balance ?? 1000

  await db.$transaction(async (tx) => {
    for (const b of bets) {
      // Skip duplicate ticketIds
      if (b.ticketId) {
        const dup = await tx.bet.findUnique({ where: { ticketId: b.ticketId } })
        if (dup) continue
      }
      const profit = computeProfit({ returnAmount: b.returnAmount, stake: b.stake, bonus: b.bonus ?? 0 })
      const isActive = b.status === 'PENDING'
      const betDate = b.betDate ? new Date(b.betDate) : new Date()
      const bet = await tx.bet.create({
        data: {
          betDate,
          eventDate: b.eventDate ? new Date(b.eventDate) : null,
          sport: b.sport ?? inferSport(b.league ?? 'Other'),
          league: b.league ?? 'Other', event: b.event, betType: b.betType,
          betLabel: b.betLabel, odds: b.odds, stake: b.stake, returnAmount: b.returnAmount,
          profit, status: b.status as BetStatus, result: b.result, ticketId: b.ticketId, bonus: b.bonus ?? null,
        },
      })
      if (!isActive) {
        runningBalance += profit
        await tx.transaction.create({
          data: {
            type: 'BET_SETTLE',
            amount: profit, balance: runningBalance,
            betId: bet.id, createdAt: new Date(bet.betDate.getTime() + 1000),
            note: `${b.betLabel} @ ${b.odds} (${b.event})`,
          },
        })
      }
      inserted.push(bet.id)
    }
  })

  return NextResponse.json({ inserted: inserted.length })
}
```

- [ ] **Step 3: Write `src/components/forms/PasteParser.tsx`**

```tsx
'use client'
import { useState } from 'react'
import { Card } from '@/components/ui/Card'
import type { ParsedBet } from '@/lib/bet-zod'
import type { BetStatus } from '@prisma/client'

const STATUS_TONE: Record<string, string> = {
  WON: 'text-positive', LOST: 'text-negative', PUSH: 'text-push', PENDING: 'text-accent'
}

export function PasteParser({ onImported }: { onImported: () => void }) {
  const [open, setOpen] = useState(false)
  const [text, setText] = useState('')
  const [parsed, setParsed] = useState<{ bets: ParsedBet[]; warnings: string[] } | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function parse() {
    setBusy(true); setError(null)
    const res = await fetch('/api/parse-bets', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    })
    const data = await res.json()
    if (!res.ok) setError(data.error ?? 'parse failed')
    else setParsed(data)
    setBusy(false)
  }

  async function confirmImport() {
    if (!parsed) return
    setBusy(true); setError(null)
    const res = await fetch('/api/import-bets', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ bets: parsed.bets }),
    })
    if (res.ok) {
      setParsed(null); setText(''); setOpen(false)
      onImported()
    } else setError('import failed')
    setBusy(false)
  }

  if (!open) {
    return (
      <button onClick={() => setOpen(true)} className="mb-4 ml-2 px-3 py-1.5 rounded-md text-sm font-semibold bg-accent/15 text-accent">
        Paste Bets
      </button>
    )
  }

  return (
    <Card title="Paste Bets" className="mb-4">
      <textarea
        value={text} onChange={e => setText(e.target.value)}
        placeholder="Paste bet slips here..."
        className="w-full min-h-[140px] bg-base border border-card-border rounded p-2 text-sm font-mono"
      />
      <div className="flex gap-2 mt-2">
        <button onClick={parse} disabled={busy || !text} className="px-4 py-2 rounded-md text-sm font-semibold bg-accent text-base">
          {busy ? 'Parsing...' : 'Parse'}
        </button>
        {parsed && parsed.bets.length > 0 && (
          <button onClick={confirmImport} disabled={busy} className="px-4 py-2 rounded-md text-sm font-semibold bg-positive text-base">
            Confirm ({parsed.bets.length})
          </button>
        )}
        <button onClick={() => setOpen(false)} className="px-4 py-2 rounded-md text-sm text-muted">Cancel</button>
        {error && <span className="text-sm text-negative">{error}</span>}
      </div>
      {parsed && parsed.warnings.length > 0 && (
        <div className="mt-2 text-xs text-push">
          {parsed.warnings.map((w, i) => <div key={i}>⚠️ {w}</div>)}
        </div>
      )}
      {parsed && parsed.bets.length > 0 && (
        <div className="mt-2 overflow-x-auto">
          <table className="w-full text-xs">
            <thead><tr className="text-muted text-left"><th className="py-1 pr-2">Label</th><th className="pr-2">Odds</th><th className="pr-2">Event</th><th className="pr-2">Stake</th><th className="pr-2">Return</th><th className="pr-2">Status</th></tr></thead>
            <tbody>
              {parsed.bets.map((b, i) => (
                <tr key={i} className="border-t border-card-border/50">
                  <td className="py-1 pr-2">{b.betLabel}</td>
                  <td className="pr-2">{b.odds}</td>
                  <td className="pr-2 max-w-[200px] truncate">{b.event}</td>
                  <td className="pr-2">{b.stake}</td>
                  <td className="pr-2">{b.returnAmount}</td>
                  <td className={`pr-2 ${STATUS_TONE[b.status] ?? ''}`}>{b.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  )
}
```

- [ ] **Step 4: Add PasteParser to DashboardRefresh client wrapper**

```tsx
'use client'
import { useRouter } from 'next/navigation'
import { AddBetForm } from './AddBetForm'
import { PasteParser } from './PasteParser'

export function DashboardRefresh() {
  const router = useRouter()
  const refresh = () => router.refresh()
  return (
    <div className="mb-4 flex gap-2 items-center">
      <AddBetForm onInserted={refresh} />
      <PasteParser onImported={refresh} />
    </div>
  )
}
```

- [ ] **Step 5: Smoke test paste parser**

```bash
npm run dev
```
Open dashboard, click "Paste Bets", paste this example:

```
ID: 863998284061622272
France
1.64
To Qualify
France vs Spain
Stake: 120.00 MYR
Return: 196.80 MYR
```

Click Parse → table shows 1 bet (France, 1.64, WON). Click Confirm (1) → form collapses, dashboard refreshes with 129 total bets and net P/L updated by +MYR 76.80.

Stop dev server.

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "feat(parse): PasteParser UI + /api/parse-bets + /api/import-bets"
```

---

### Task 17: PATCH /api/bets/[id] (status correction)

**Files:**
- Create: `src/app/api/bets/[id]/route.ts`
- Create: `src/app/api/refresh-metrics/route.ts` (Phase 1 no-op)

**Interfaces:**
- Produces: PATCH bet route that updates status/result/profit + recomputes linked txn

- [ ] **Step 1: Write `src/app/api/bets/[id]/route.ts`**

```ts
import { NextRequest, NextResponse } from 'next/server'
import { db } from '@/lib/db'
import { computeProfit } from '@/lib/profit'
import type { BetStatus } from '@prisma/client'

export async function PATCH(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  const body = await req.json()
  const id = params.id
  const existing = await db.bet.findUnique({ where: { id } })
  if (!existing) return NextResponse.json({ error: 'not found' }, { status: 404 })

  const newStatus = body.status as BetStatus | undefined
  const newReturn = body.returnAmount !== undefined ? Number(body.returnAmount) : existing.returnAmount
  const newResult = body.result !== undefined ? body.result : existing.result

  // Recompute profit if return changed
  const profit = newReturn !== existing.returnAmount
    ? computeProfit({ returnAmount: newReturn, stake: existing.stake, bonus: existing.bonus ?? 0 })
    : existing.profit

  await db.$transaction(async (tx) => {
    const updated = await tx.bet.update({
      where: { id },
      data: { status: newStatus ?? existing.status, returnAmount: newReturn, result: newResult, profit },
    })
    // Update linked BET_SETTLE txn if exists
    const existingTxn = await tx.transaction.findFirst({ where: { betId: id, type: 'BET_SETTLE' } })
    if (updated.status === 'PENDING' && existingTxn) {
      // remove txn (unsettled)
      await tx.transaction.delete({ where: { id: existingTxn.id } })
    } else if (updated.status !== 'PENDING' && !existingTxn) {
      // newly settled — insert BET_SETTLE
      const latestBefore = await tx.transaction.findFirst({
        where: { createdAt: { lt: updated.betDate } },
        orderBy: { createdAt: 'desc' },
      })
      const startBal = latestBefore?.balance ?? 1000
      await tx.transaction.create({
        data: {
          type: 'BET_SETTLE',
          amount: profit, balance: 0, betId: id,
          createdAt: new Date(updated.betDate.getTime() + 1000),
          note: `${updated.betLabel} @ ${updated.odds} (${updated.event})`,
        },
      })
    } else if (existingTxn) {
      // update amount
      await tx.transaction.update({
        where: { id: existingTxn.id },
        data: { amount: profit },
      })
    }
    // Recompute rolling balance for all txns after the affected one
    const allTxns = await tx.transaction.findMany({ orderBy: { createdAt: 'asc' } })
    let bal = 1000
    for (const t of allTxns) {
      if (t.type === 'DEPOSIT' || t.type === 'WITHDRAW') bal = t.amount
      else if (t.type === 'BET_SETTLE') bal += t.amount
      else if (t.type === 'ADJUSTMENT') bal += t.amount
      await tx.transaction.update({ where: { id: t.id }, data: { balance: bal } })
    }
  })

  return NextResponse.json({ ok: true })
}
```

- [ ] **Step 2: Write `src/app/api/refresh-metrics/route.ts`**

```ts
import { NextResponse } from 'next/server'

export async function GET() {
  return NextResponse.json({ ok: true, cached: false, note: 'Phase 1: no caching, all metrics computed on render' })
}
```

- [ ] **Step 3: Smoke test PATCH**

```bash
# Pick a bet ID from the DB and toggle it to PENDING
npx tsx -e "import { db } from './src/lib/db'; (async () => { const b = await db.bet.findFirst(); console.log(b?.id); await db.\$disconnect(); })()"
```

Use that ID:
```bash
curl -X PATCH http://localhost:3000/api/bets/<ID> -H "Content-Type: application/json" -d "{\"status\":\"PENDING\"}"
```
Expected: `{"ok":true}`. Re-fetch the bet — it should be PENDING with no linked BET_SETTLE txn.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat(bets): PATCH /api/bets/[id] with txn reconciliation + refresh-metrics no-op"
```

---

### Task 18: End-to-end smoke test — wipe → import → verify metrics match WC Bets

**Files:**
- No new files; verifies acceptance criteria §21

- [ ] **Step 1: Wipe DB**

```bash
npx tsx -e "import { db } from './src/lib/db'; (async () => { await db.bet.deleteMany({}); await db.transaction.deleteMany({}); console.log('wiped'); await db.\$disconnect(); })()"
```

- [ ] **Step 2: Run import**

```bash
npm run import -- "E:\AI Llms\WC Bets\Bets.txt"
```
Expected output:
```
Parsed 127 bets (0 warnings)
Seeded starting bankroll: MYR 1000
✓ Import done. Current bankroll: MYR 1205.56
```
(If warnings appear, note them; fix `parse-bets.ts` if obvious.)

- [ ] **Step 3: Verify row counts**

```bash
npx tsx -e "import { db } from './src/lib/db'; (async () => { const b = await db.bet.count(); const t = await db.transaction.count(); console.log('bets:', b, 'txns:', t); await db.\$disconnect(); })()"
```
Expected: `bets: 127 txns: 128`

- [ ] **Step 4: Start dev server and check dashboard**

```bash
npm run dev
```
Open `http://localhost:3000`. Verify against acceptance criteria:
- [ ] Summary cards: 127 total bets, +MYR 205.56 net P/L, ~+20.6% ROI, ~58% win rate
- [ ] 30-day P/L chart renders green+orange bars
- [ ] Won/Push/Lost pie has 3 segments + center label
- [ ] Weekly/Monthly cards show real data
- [ ] Latest bets table shows 10 rows with color-coded status
- [ ] Active bets card renders "No active bets."

If any metric is off by >1 MYR, debug: it's almost certainly a profit formula edge case not covered by tests. Fix in `parse-bets.ts` or `profit.ts` and re-import.

- [ ] **Step 5: Stop dev server + final commit (if any fixes were needed)**

```bash
git add -A
git commit -m "test:e2e import verified — 127 bets, MYR 205.56 P/L" --allow-empty
```

---

## Self-Review

### Spec coverage

- §1 Context → addressed by whole plan (greenfield, doesn't touch WC Bets)
- §3 Folder structure → Task 1 + every file path laid out in tasks
- §4 Data model → Task 2 (Prisma schema, invariants in schema + import script)
- §5 Main Dashboard → Tasks 11 (UI primitives) + 14 (page composition)
- §5.2 Color system → Task 1 step 7 (tailwind config tokens)
- §6 Bet entry (inline + paste) → Tasks 15 + 16
- §6.4 Server API routes → Tasks 15, 16, 17
- §6.5 Bankroll invariants → Tasks 8, 15, 16, 17 (all use `db.$transaction`)
- §6.6 Status auto-derivation → Task 6/7 parsers, plus API route fallback in Task 15
- §6.7 Validation → Zod in Task 6
- §7 Sport inference → Task 5
- §8 Metrics → Tasks 9, 10
- §9 Charts → Task 12
- §10 Summary cards → Task 11 (StatCard) + 14 (page)
- §11 Period breakdown → Task 14
- §12 Turnover & ROI stats → Task 14
- §13 Latest bets table → Task 14 (uses BetsTable from Task 11)
- §14 Active bets section → Task 14 (placeholder)
- §15 Formatters → Task 3
- §16 Caching (no-cache) → implicit in all server components (no caching utilities used)
- §17 Import script → Task 8
- §18 Dev workflow → Task 1
- §19 Dependencies → Task 1
- §20 Edge cases → bonus in profit (T4), duplicate ticketId skip in/import (T8 + T16), collapsed status buckets in metrics (T9), empty states (T14)
- §21 Acceptance criteria → covered by Tasks 1, 8, 14, 15, 18; verified explicitly in Task 18
- §22 Out of scope → placeholders in Task 13

### Placeholder scan

All code blocks are real implementations. No "TBD" or "implement later" markers. Test blocks include real assertions. The one "deferred beyond Phase 1" note (Format C) is intentional, declared in spec §22, and the function exists with a clear stub (Format B function before Task 7).

### Type consistency

- `ParsedBetSchema` defined in Task 6, consumed in Tasks 7, 8, 15, 16 with matching field names (`ticketId`, `betLabel`, `odds`, `betType`, `event`, `league`, `sport`, `betDate`, `eventDate`, `stake`, `returnAmount`, `bonus`, `status`, `result`)
- `ComputeSummary`, `computeOutcomeBreakdown`, `computePeriodStats`, `computeDailyPnL`, `computeLatestBets`, `computeActiveBets` — all defined in Tasks 9/10, all imported in Task 14 with matching signatures
- `computeProfit` signature consistent across Tasks 4, 15, 16, 17
- `DailyPnLPoint`, `OutcomeBreakdown`, `Summary`, `PeriodStats` interfaces consistent
- One mild ambiguity: `computeDailyPnL` uses `1000` as the starting bankroll hard-coded value. For the dashboard this is fine since starting bankroll = 1000 per spec invariant. (Documented in the inline comment.)