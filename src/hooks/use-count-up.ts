import { useEffect, useState } from "react";
import { animate } from "framer-motion";

export function useCountUp(target: number, duration = 1.4) {
  const [value, setValue] = useState(0);
  useEffect(() => {
    const controls = animate(0, target, {
      duration,
      ease: [0.16, 1, 0.3, 1],
      onUpdate: (v) => setValue(v),
    });
    return () => controls.stop();
  }, [target, duration]);
  return value;
}

export function formatCompact(n: number, prefix = "") {
  if (n >= 1_000_000) return `${prefix}${(n / 1_000_000).toFixed(2)}M`;
  if (n >= 1_000) return `${prefix}${(n / 1_000).toFixed(1)}K`;
  return `${prefix}${Math.round(n).toLocaleString()}`;
}
