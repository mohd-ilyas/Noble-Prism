import { motion } from "framer-motion";
import { Sparkles } from "lucide-react";
import { useInsights } from "@/hooks/useApi";

export function HeroSection() {
  const { data } = useInsights();
  const kpis = data?.kpis;

  const volume = kpis?.authorized_volume
    ? `$${(kpis.authorized_volume / 1_000_000).toFixed(2)}M`
    : "$1.28M";
  const latency = kpis?.avg_latency_ms ? `${Math.round(kpis.avg_latency_ms)}ms` : "14ms";
  const agents = kpis?.active_agents ?? 312;

  return (
    <section className="relative">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
        className="mb-3 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.03] px-3 py-1 text-xs font-medium text-zinc-400"
      >
        <Sparkles className="size-3 text-accent-primary" />
        Agent Payment Protocol · v0.9 preview
      </motion.div>

      <motion.h1
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, delay: 0.05, ease: [0.16, 1, 0.3, 1] }}
        className="font-display text-4xl font-extrabold leading-[1.05] tracking-tight text-white md:text-5xl"
      >
        Agent commerce,
        <br />
        <span className="bg-gradient-to-r from-accent-primary via-sky-300 to-accent-secondary bg-clip-text text-transparent">
          under machine-speed control.
        </span>
      </motion.h1>

      <motion.p
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.15 }}
        className="mt-4 max-w-2xl text-base leading-relaxed text-zinc-400"
      >
        <span className="font-semibold text-white">{agents}</span> autonomous agents transacted{" "}
        <span className="font-semibold text-white">{volume}</span> in the last 24h. Every request
        passed identity, velocity, and anomaly checks in{" "}
        <span className="font-semibold text-accent-primary">{latency}</span> — with a tamper-evident
        audit trail.
      </motion.p>
    </section>
  );
}
