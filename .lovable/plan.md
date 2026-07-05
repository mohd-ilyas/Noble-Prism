# Agent-to-Agent Payment Protocol — Dashboard MVP

A premium dark-mode command center for an **Agent-to-Agent Payment Protocol** (Aether/Axiom), built in the Obsidian Glass direction: glassmorphism cards, blue→purple gradient mesh, Plus Jakarta Sans display + Inter body.

## Scope (this build)

Single-route dashboard experience. All data is realistic mock data — no backend, no auth. Frontend-only, optimized for judge wow-factor in the first 5 seconds.

## Screens & Sections

**1. Root shell (`src/routes/__root.tsx`)**
- Set app metadata (title: "Aether — Agent Payment Protocol", description, og tags)
- Load Inter + Plus Jakarta Sans via `<link>` in head
- Fixed left icon rail (nav: Overview, Agents, Ledger, Policies, Insights)
- Top header: workspace breadcrumb, "System Operational" pulse chip, "Deploy Agent" CTA

**2. Dashboard home (`src/routes/index.tsx`)** — replaces placeholder
- **Hero**: "Agent Commerce, Under Control" + animated subline with live throughput number
- **KPI strip (4 cards)**: Authorized Volume ($1.28M), Blocked Requests (1,402), Avg Auth Latency (14ms), Active Agents (312) — each with animated count-up, sparkline, delta badge
- **Live Transaction Stream** (main panel, 2/3 width): scrolling feed of agent→agent transactions with slide-in animation, status badges (Approved/Blocked/Escalated), agent names, amounts in USD/USDC, click-to-inspect
- **Real-time Volume Chart**: Recharts area chart with gradient fill showing last 24h authorized vs blocked
- **AI Insights card**: anomaly detection callout with "Apply Policy" action
- **Agent Roster**: top 5 agents with reputation scores + status dots
- **Policy Inspector drawer**: opens on transaction click, shows policy evaluation trace (identity verify → velocity check → risk score → decision) with tamper-evident receipt CTA
- **Recent Events timeline**: settlement confirmations, policy triggers

## Design System

- Install `@fontsource-variable/inter` and `@fontsource-variable/plus-jakarta-sans`
- Extend `src/styles.css` @theme with:
  - `--color-accent-primary: #3b82f6` (blue), `--color-accent-secondary: #a855f7` (purple)
  - `--color-success: #10b981`, `--color-warning: #f59e0b`, `--color-danger: #ef4444`
  - `--font-sans: 'Inter Variable'`, `--font-display: 'Plus Jakarta Sans Variable'`
- Custom utilities: `.glass-card` (translucent + backdrop-blur + border), `.mesh-bg` (radial gradients), `.glow-hover`
- Dark mode is default and only mode (skip light toggle for MVP focus)

## Animations

Install `framer-motion`. Use for:
- KPI count-up (custom hook with `useMotionValue` + `animate`)
- Transaction row slide-in from top
- Card hover lift + glow
- Chart draw-in on mount
- Drawer slide-in for policy inspector
- Staggered reveal of dashboard sections on mount

## Tech additions

- `bun add framer-motion recharts @fontsource-variable/inter @fontsource-variable/plus-jakarta-sans`
- Lucide icons (already available)
- Shadcn Button, Badge, Card (already available)
- Mock data lives in `src/lib/mock-data.ts` (agents, transactions, timeseries, policies)

## File plan

- `src/styles.css` — add theme tokens, glass/mesh utilities, font faces
- `src/routes/__root.tsx` — real metadata, font `<link>`s
- `src/routes/index.tsx` — full dashboard composition
- `src/components/dashboard/` — `AppShell.tsx`, `SideRail.tsx`, `TopHeader.tsx`, `HeroSection.tsx`, `KpiStrip.tsx`, `KpiCard.tsx`, `TransactionStream.tsx`, `VolumeChart.tsx`, `AgentRoster.tsx`, `AiInsights.tsx`, `PolicyInspector.tsx`, `EventsTimeline.tsx`
- `src/lib/mock-data.ts` — agents, transactions, timeseries
- `src/hooks/use-count-up.ts` — animated number hook

## Out of scope

- Auth, backend, Lovable Cloud (pure frontend MVP)
- Light mode toggle
- Additional routes (Agents/Ledger/Policies pages are nav placeholders for now)
- Mobile-optimized layout beyond basic responsive stacking (desktop-first for judging)
