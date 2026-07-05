import type { ReactNode } from "react";
import { SideRail } from "./SideRail";
import { TopHeader } from "./TopHeader";

export function AppShell({ breadcrumb, children }: { breadcrumb?: string; children: ReactNode }) {
  return (
    <div className="mesh-bg min-h-screen font-sans text-zinc-100 selection:bg-accent-primary/30">
      <SideRail />
      <div className="md:pl-20">
        <TopHeader breadcrumb={breadcrumb} />
        <main className="mx-auto max-w-[1440px] space-y-8 p-6 md:p-10">
          {children}
          <footer className="pt-6 pb-2 text-center text-[11px] text-zinc-600">
            Aether Protocol · agent-to-agent payments · v0.9 preview · policy engine online
          </footer>
        </main>
      </div>
    </div>
  );
}
