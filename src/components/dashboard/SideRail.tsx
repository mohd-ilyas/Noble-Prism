import { LayoutDashboard, Cpu, ScrollText, ShieldCheck, Sparkles, Settings, Bot } from "lucide-react";
import { Link, useRouterState } from "@tanstack/react-router";

const items = [
  { icon: LayoutDashboard, label: "Overview", to: "/" as const },
  { icon: Bot, label: "Commerce", to: "/" as const },
  { icon: Cpu, label: "Agents", to: "/agents" as const },
  { icon: ScrollText, label: "Ledger", to: "/ledger" as const },
  { icon: ShieldCheck, label: "Policies", to: "/policies" as const },
  { icon: Sparkles, label: "Insights", to: "/insights" as const },
];

export function SideRail() {
  const pathname = useRouterState({ select: (s) => s.location.pathname });

  return (
    <nav className="fixed left-0 top-0 z-50 hidden h-full w-20 flex-col items-center border-r border-white/5 bg-black/30 py-8 backdrop-blur-xl md:flex">
      <Link
        to="/"
        className="mb-12 flex size-11 items-center justify-center rounded-xl bg-gradient-to-tr from-accent-primary to-accent-secondary font-display text-lg font-extrabold text-white shadow-[0_0_24px_rgba(59,130,246,0.5)]"
      >
        AE
      </Link>
      <div className="flex flex-col gap-3">
        {items.map(({ icon: Icon, label, to }) => {
          const active = to === "/" ? pathname === "/" : pathname.startsWith(to);
          return (
            <Link
              key={label}
              to={to}
              title={label}
              className={`group relative grid size-11 place-items-center rounded-xl border transition-all ${
                active
                  ? "border-accent-primary/30 bg-accent-primary/10 text-accent-primary"
                  : "border-transparent bg-white/[0.03] text-zinc-500 hover:border-white/10 hover:bg-white/[0.06] hover:text-white"
              }`}
            >
              <Icon className="size-5" />
              {active && (
                <span className="absolute -left-[9px] top-1/2 h-6 w-[2px] -translate-y-1/2 rounded-full bg-accent-primary shadow-[0_0_10px_rgba(59,130,246,0.8)]" />
              )}
            </Link>
          );
        })}
      </div>
      <div className="mt-auto flex flex-col items-center gap-3">
        <Link
          to="/settings"
          title="Settings"
          className={`grid size-11 place-items-center rounded-xl transition ${
            pathname.startsWith("/settings")
              ? "bg-accent-primary/10 text-accent-primary"
              : "bg-white/[0.03] text-zinc-500 hover:bg-white/[0.06] hover:text-white"
          }`}
        >
          <Settings className="size-5" />
        </Link>
        <div
          title="Noble Prism profile"
          className="grid size-10 place-items-center rounded-full border border-indigo-300/20 bg-gradient-to-br from-blue-500 via-indigo-500 to-violet-500 font-display text-[11px] font-bold text-white shadow-[0_0_22px_rgba(99,102,241,0.25)]"
        >
          NP
        </div>
      </div>
    </nav>
  );
}
