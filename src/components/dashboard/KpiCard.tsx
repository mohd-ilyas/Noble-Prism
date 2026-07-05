import { motion } from "framer-motion";
import { ArrowUpRight, ArrowDownRight, type LucideIcon } from "lucide-react";
import { useCountUp } from "@/hooks/use-count-up";

interface Props {
  label: string;
  value: number;
  format: (n: number) => string;
  delta: string;
  deltaTone: "up" | "down" | "flat";
  icon: LucideIcon;
  spark: number[];
  accent?: "primary" | "secondary" | "success" | "danger";
  delay?: number;
}

const accentToStroke: Record<NonNullable<Props["accent"]>, string> = {
  primary: "#3b82f6",
  secondary: "#a855f7",
  success: "#10b981",
  danger: "#ef4444",
};

export function KpiCard({
  label,
  value,
  format,
  delta,
  deltaTone,
  icon: Icon,
  spark,
  accent = "primary",
  delay = 0,
}: Props) {
  const animated = useCountUp(value, 1.6);
  const stroke = accentToStroke[accent];

  const max = Math.max(...spark);
  const min = Math.min(...spark);
  const range = Math.max(1, max - min);
  const points = spark
    .map((v, i) => {
      const x = (i / (spark.length - 1)) * 100;
      const y = 30 - ((v - min) / range) * 26 - 2;
      return `${x},${y}`;
    })
    .join(" ");
  const area = `0,30 ${points} 100,30`;

  const gradId = `spark-${label.replace(/\s+/g, "-")}`;

  return (
    <motion.div
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1], delay }}
      className="glass-card glow-hover group relative overflow-hidden rounded-2xl p-5"
    >
      <div className="mb-4 flex items-start justify-between">
        <div className="flex items-center gap-2">
          <div
            className="grid size-8 place-items-center rounded-lg border"
            style={{ background: `${stroke}15`, borderColor: `${stroke}33`, color: stroke }}
          >
            <Icon className="size-4" />
          </div>
          <span className="text-[11px] font-medium uppercase tracking-wider text-zinc-400">
            {label}
          </span>
        </div>
        <span
          className={`inline-flex items-center gap-0.5 text-[11px] font-semibold ${
            deltaTone === "up"
              ? "text-emerald-400"
              : deltaTone === "down"
                ? "text-rose-400"
                : "text-zinc-500"
          }`}
        >
          {deltaTone === "up" && <ArrowUpRight className="size-3" />}
          {deltaTone === "down" && <ArrowDownRight className="size-3" />}
          {delta}
        </span>
      </div>

      <div className="font-display text-3xl font-bold tracking-tight text-white">
        {format(animated)}
      </div>

      <svg viewBox="0 0 100 32" preserveAspectRatio="none" className="mt-4 h-10 w-full">
        <defs>
          <linearGradient id={gradId} x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor={stroke} stopOpacity="0.4" />
            <stop offset="100%" stopColor={stroke} stopOpacity="0" />
          </linearGradient>
        </defs>
        <polygon points={area} fill={`url(#${gradId})`} />
        <polyline
          points={points}
          fill="none"
          stroke={stroke}
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    </motion.div>
  );
}
