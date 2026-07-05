import { motion } from "framer-motion";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { useInsights } from "@/hooks/useApi";
import { volumeSeries as mockVolumeSeries } from "@/lib/mock-data";

export function VolumeChart() {
  const { data } = useInsights();
  const series = data?.volume_series ?? mockVolumeSeries;

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
      className="glass-card relative overflow-hidden rounded-3xl p-6"
    >
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="font-display text-lg font-bold text-white">
            Authorized vs Blocked Volume
          </h3>
          <p className="text-xs text-zinc-500">Last 24 hours · live from protocol gateway</p>
        </div>
        <div className="flex gap-1.5">
          <div className="inline-flex items-center gap-1.5 rounded-md border border-white/10 bg-white/[0.03] px-2 py-1 text-[10px] font-medium text-zinc-300">
            <span className="size-2 rounded-full bg-accent-primary" /> Authorized
          </div>
          <div className="inline-flex items-center gap-1.5 rounded-md border border-white/10 bg-white/[0.03] px-2 py-1 text-[10px] font-medium text-zinc-300">
            <span className="size-2 rounded-full bg-rose-500" /> Blocked
          </div>
        </div>
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={series} margin={{ top: 8, right: 8, left: -18, bottom: 0 }}>
            <defs>
              <linearGradient id="auth" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.55} />
                <stop offset="100%" stopColor="#3b82f6" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="blk" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#ef4444" stopOpacity={0.45} />
                <stop offset="100%" stopColor="#ef4444" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="rgba(255,255,255,0.05)" strokeDasharray="3 6" vertical={false} />
            <XAxis
              dataKey="hour"
              tick={{ fill: "#71717a", fontSize: 10 }}
              axisLine={false}
              tickLine={false}
              interval={3}
            />
            <YAxis tick={{ fill: "#71717a", fontSize: 10 }} axisLine={false} tickLine={false} />
            <Tooltip
              contentStyle={{
                background: "rgba(15,15,20,0.92)",
                border: "1px solid rgba(255,255,255,0.1)",
                borderRadius: 10,
                fontSize: 12,
                backdropFilter: "blur(8px)",
              }}
              labelStyle={{ color: "#a1a1aa" }}
            />
            <Area
              type="monotone"
              dataKey="authorized"
              stroke="#3b82f6"
              strokeWidth={2}
              fill="url(#auth)"
              isAnimationActive
              animationDuration={1400}
            />
            <Area
              type="monotone"
              dataKey="blocked"
              stroke="#ef4444"
              strokeWidth={2}
              fill="url(#blk)"
              isAnimationActive
              animationDuration={1400}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
}
