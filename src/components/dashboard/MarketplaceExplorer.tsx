import { motion } from "framer-motion";
import { Search } from "lucide-react";
import { useNegotiationProviders } from "@/hooks/useApi";

export function MarketplaceExplorer() {
  const { data: providers = [] } = useNegotiationProviders();

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.7, delay: 0.25 }}
      className="glass-card rounded-3xl p-6"
    >
      <div className="flex items-center justify-between gap-3">
        <div>
          <h3 className="font-display text-lg font-bold text-white">Marketplace Explorer</h3>
          <p className="text-xs text-zinc-500">Discover providers and compare your negotiation options.</p>
        </div>
        <div className="flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.03] px-3 py-2 text-[11px] text-zinc-400">
          <Search className="size-3.5" /> Find providers
        </div>
      </div>
      <div className="mt-6 space-y-3">
        {providers.map((provider) => (
          <div key={provider.id} className="rounded-2xl border border-white/10 bg-black/20 p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold text-white">{provider.provider_name}</p>
                <p className="text-[11px] text-zinc-500">{provider.description}</p>
              </div>
              <div className="text-right">
                <p className="font-mono text-sm font-semibold text-white">${provider.price_per_unit.toFixed(2)}</p>
                <p className="text-[10px] uppercase tracking-wider text-zinc-500">{provider.category}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  );
}
