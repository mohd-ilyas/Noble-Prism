import { motion } from "framer-motion";
import { useCommerceWebSocket } from "@/hooks/useCommerceWebSocket";

export function LiveStatusPill() {
  const messages = useCommerceWebSocket();
  const lastMessage = messages[messages.length - 1];
  const timestamp = lastMessage?.payload?.timestamp ? new Date(lastMessage.payload.timestamp).toLocaleTimeString() : undefined;

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      className="inline-flex items-center gap-2 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-3 py-1 text-[10px] font-semibold uppercase tracking-[0.2em] text-emerald-300"
    >
      <span className="size-2 rounded-full bg-emerald-400" />
      {timestamp ? `Live @ ${timestamp}` : lastMessage?.message ?? "Live negotiation stream"}
    </motion.div>
  );
}
