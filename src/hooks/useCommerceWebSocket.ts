import { useEffect, useState, useRef } from "react";

export interface CommerceSnapshot {
  type: "connected" | "heartbeat" | "commerce_snapshot";
  message: string;
  payload?: {
    providers?: Array<{
      id: string;
      provider_name: string;
      category: string;
      region: string;
      price_per_unit: number;
      sla_days: number;
      latency_ms: number;
      reputation_score: number;
      sustainability_score: number;
      availability: string;
      description: string;
      status: string;
    }>;
    workflows?: Array<unknown>;
    timestamp?: string;
  };
}

export function useCommerceWebSocket() {
  const [messages, setMessages] = useState<CommerceSnapshot[]>([]);
  const retryCountRef = useRef(0);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const baseUrl = (import.meta.env.VITE_API_URL as string | undefined) ?? "http://localhost:8000";
    const url = `${baseUrl.replace(/^http/, "ws")}/commerce/ws`;

    const connect = () => {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        retryCountRef.current = 0;
        setMessages((prev) => [...prev.slice(-9), { type: "connected", message: "Commerce stream connected" }]);
      };

      ws.onmessage = (event) => {
        const payload = JSON.parse(event.data) as CommerceSnapshot;
        setMessages((prev) => [...prev.slice(-9), payload]);
      };

      ws.onclose = () => {
        const retry = Math.min(6, retryCountRef.current + 1);
        retryCountRef.current = retry;
        const delay = Math.min(5000, 1000 * retry);
        setTimeout(connect, delay);
      };

      ws.onerror = () => {
        ws.close();
      };
    };

    connect();

    return () => {
      wsRef.current?.close();
    };
  }, []);

  return messages;
}
