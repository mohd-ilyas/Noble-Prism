export type TxStatus = "approved" | "blocked" | "escalated";

export interface Agent {
  id: string;
  name: string;
  org: string;
  reputation: number;
  status: "online" | "idle" | "offline";
  spendToday: number;
}

export interface Transaction {
  id: string;
  from: string;
  to: string;
  amount: number;
  currency: "USD" | "USDC" | "EUR";
  purpose: string;
  status: TxStatus;
  riskScore: number;
  timestamp: string;
  latencyMs: number;
  policyTrace: {
    step: string;
    detail: string;
    passed: boolean;
  }[];
}

export const agents: Agent[] = [
  {
    id: "a1",
    name: "openai-buyer-07",
    org: "OpenAI",
    reputation: 99.4,
    status: "online",
    spendToday: 42_180,
  },
  {
    id: "a2",
    name: "anthropic-broker",
    org: "Anthropic",
    reputation: 98.1,
    status: "online",
    spendToday: 31_402,
  },
  {
    id: "a3",
    name: "mistral-relayer",
    org: "Mistral",
    reputation: 96.7,
    status: "online",
    spendToday: 18_209,
  },
  {
    id: "a4",
    name: "llama-compute-4",
    org: "Meta AI",
    reputation: 94.2,
    status: "idle",
    spendToday: 9_120,
  },
  {
    id: "a5",
    name: "aws-c-broker",
    org: "AWS",
    reputation: 99.8,
    status: "online",
    spendToday: 67_902,
  },
  {
    id: "a6",
    name: "stripe-relay-01",
    org: "Stripe",
    reputation: 99.9,
    status: "online",
    spendToday: 12_500,
  },
];

export const transactions: Transaction[] = [
  {
    id: "0x4f9a2921",
    from: "openai-buyer-07",
    to: "aws-c-broker",
    amount: 1402.0,
    currency: "USDC",
    purpose: "H100 GPU lease · 4h",
    status: "approved",
    riskScore: 0.04,
    timestamp: "14:28:42",
    latencyMs: 11,
    policyTrace: [
      {
        step: "Identity Verification",
        detail: "mTLS + VC signature verified against W3C registry",
        passed: true,
      },
      { step: "Velocity Check", detail: "Window spend 14% of policy ceiling", passed: true },
      { step: "Anomaly Model v2.4", detail: "Entropy score within expected band", passed: true },
      { step: "Settlement", detail: "Ledger commit 0x4f9a... appended", passed: true },
    ],
  },
  {
    id: "0x9d3ef42a",
    from: "anthropic-broker",
    to: "vertex-inference-eu",
    amount: 890.0,
    currency: "USD",
    purpose: "Batch inference · 2.1M tokens",
    status: "approved",
    riskScore: 0.11,
    timestamp: "14:28:39",
    latencyMs: 14,
    policyTrace: [
      { step: "Identity Verification", detail: "OAuth2 delegated token valid", passed: true },
      { step: "Velocity Check", detail: "Within hourly cap", passed: true },
      { step: "Anomaly Model v2.4", detail: "Nominal", passed: true },
      { step: "Settlement", detail: "Ledger commit appended", passed: true },
    ],
  },
  {
    id: "0x1a7c1109",
    from: "unknown-ext-01",
    to: "compute-cluster-A",
    amount: 50_000.0,
    currency: "USD",
    purpose: "Unclassified transfer",
    status: "blocked",
    riskScore: 0.94,
    timestamp: "14:28:35",
    latencyMs: 9,
    policyTrace: [
      { step: "Identity Verification", detail: "Agent not present in registry", passed: false },
      { step: "Velocity Check", detail: "Skipped — identity failure", passed: false },
      { step: "Anomaly Model v2.4", detail: "Amount 42σ above baseline", passed: false },
      { step: "Settlement", detail: "Blocked at gateway", passed: false },
    ],
  },
  {
    id: "0x77bc21e0",
    from: "mistral-relayer",
    to: "stripe-relay-01",
    amount: 0.042,
    currency: "USDC",
    purpose: "Micro-inference · 1.2k tokens",
    status: "approved",
    riskScore: 0.02,
    timestamp: "14:28:32",
    latencyMs: 8,
    policyTrace: [
      { step: "Identity Verification", detail: "Verified", passed: true },
      { step: "Velocity Check", detail: "Nominal", passed: true },
      { step: "Anomaly Model v2.4", detail: "Nominal", passed: true },
      { step: "Settlement", detail: "Ledger commit appended", passed: true },
    ],
  },
  {
    id: "0x21a0b8f4",
    from: "custom-agent-99",
    to: "tax-oracle-eu",
    amount: 458.12,
    currency: "EUR",
    purpose: "Tax calculation service",
    status: "escalated",
    riskScore: 0.62,
    timestamp: "14:28:29",
    latencyMs: 22,
    policyTrace: [
      { step: "Identity Verification", detail: "Verified — new agent (48h old)", passed: true },
      { step: "Velocity Check", detail: "First cross-border request", passed: true },
      { step: "Anomaly Model v2.4", detail: "Ambiguous — escalating", passed: false },
      { step: "Human Approval", detail: "Routed to on-call operator", passed: false },
    ],
  },
  {
    id: "0x55e2a913",
    from: "llama-compute-4",
    to: "hf-model-registry",
    amount: 12.5,
    currency: "USDC",
    purpose: "Weights checkpoint pull",
    status: "approved",
    riskScore: 0.06,
    timestamp: "14:28:24",
    latencyMs: 12,
    policyTrace: [
      { step: "Identity Verification", detail: "Verified", passed: true },
      { step: "Velocity Check", detail: "Nominal", passed: true },
      { step: "Anomaly Model v2.4", detail: "Nominal", passed: true },
      { step: "Settlement", detail: "Ledger commit appended", passed: true },
    ],
  },
  {
    id: "0x88df01ca",
    from: "openai-buyer-07",
    to: "pinecone-vector",
    amount: 24.9,
    currency: "USD",
    purpose: "Vector index query",
    status: "approved",
    riskScore: 0.03,
    timestamp: "14:28:19",
    latencyMs: 10,
    policyTrace: [
      { step: "Identity Verification", detail: "Verified", passed: true },
      { step: "Velocity Check", detail: "Nominal", passed: true },
      { step: "Anomaly Model v2.4", detail: "Nominal", passed: true },
      { step: "Settlement", detail: "Ledger commit appended", passed: true },
    ],
  },
];

// 24 hour volume series
export const volumeSeries = Array.from({ length: 24 }, (_, i) => {
  const base = 40 + Math.sin(i / 2.5) * 22 + Math.cos(i / 4) * 10;
  return {
    hour: `${String(i).padStart(2, "0")}:00`,
    authorized: Math.max(8, Math.round(base * 1.6 + (i % 3) * 4)),
    blocked: Math.max(1, Math.round(6 + Math.sin(i / 3) * 3 + (i === 14 ? 12 : 0))),
  };
});

export const eventsFeed = [
  {
    kind: "settle",
    title: "Settlement batch #4291 finalized",
    detail: "312 transactions · $184,209 net",
    dot: "success" as const,
  },
  {
    kind: "policy",
    title: "Policy 'eu-cross-border' triggered",
    detail: "3 escalations routed to on-call",
    dot: "warning" as const,
  },
  {
    kind: "agent",
    title: "New agent onboarded",
    detail: "cohere-embedder-02 · reputation seed 80.0",
    dot: "primary" as const,
  },
  {
    kind: "anomaly",
    title: "Anomaly cluster detected",
    detail: "unknown-ext-01 · $50k blocked",
    dot: "danger" as const,
  },
  {
    kind: "ledger",
    title: "Ledger checkpoint anchored",
    detail: "L2 root 0x9c…4a2 · block 18,209,442",
    dot: "secondary" as const,
  },
];
