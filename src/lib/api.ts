/**
 * Noble Prism API client
 *
 * All backend calls are centralised here.  The base URL is read from
 * VITE_API_URL (defaults to http://localhost:8000 for local development).
 *
 * The frontend still works with its mock data even when the backend is
 * unavailable — this file simply provides the live integration layer.
 */

const BASE_URL = (import.meta.env.VITE_API_URL as string | undefined) ?? "http://localhost:8000";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const url = `${BASE_URL}${path}`;
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json", ...(options.headers ?? {}) },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "Unknown error");
    throw new Error(`API ${options.method ?? "GET"} ${path} → ${res.status}: ${text}`);
  }
  return res.json() as Promise<T>;
}

// ── Agents ──────────────────────────────────────────────────────────────────

export const AgentsApi = {
  list: () => request<AgentResponse[]>("/agents"),
  get: (id: string) => request<AgentResponse>(`/agents/${id}`),
  register: (body: AgentRegisterRequest) =>
    request<AgentResponse>("/agents/register", { method: "POST", body: JSON.stringify(body) }),
};

// ── Policies ────────────────────────────────────────────────────────────────

export const PoliciesApi = {
  list: () => request<PolicyResponse[]>("/policies"),
  create: (body: PolicyCreateRequest) =>
    request<PolicyResponse>("/policies", { method: "POST", body: JSON.stringify(body) }),
  update: (id: string, body: Partial<PolicyCreateRequest>) =>
    request<PolicyResponse>(`/policies/${id}`, { method: "PUT", body: JSON.stringify(body) }),
};

// ── Transactions ─────────────────────────────────────────────────────────────

export const TransactionsApi = {
  evaluate: (body: TransactionRequest) =>
    request<EvaluationResult>("/transactions/evaluate", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  initiate: (body: TransactionRequest) =>
    request<TransactionResult>("/transactions/initiate", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  approve: (transactionId: string, operatorNote = "") =>
    request<TransactionResult>("/transactions/approve", {
      method: "POST",
      body: JSON.stringify({ transaction_id: transactionId, operator_note: operatorNote }),
    }),
  reject: (transactionId: string, reason = "") =>
    request<TransactionResult>("/transactions/reject", {
      method: "POST",
      body: JSON.stringify({ transaction_id: transactionId, reason }),
    }),
};

// ── Ledger ───────────────────────────────────────────────────────────────────

export const LedgerApi = {
  list: (limit = 50) => request<LedgerEntry[]>(`/ledger?limit=${limit}`),
};

// ── Insights ─────────────────────────────────────────────────────────────────

export const InsightsApi = {
  get: () => request<InsightsResponse>("/insights"),
};

// ── Kill Switch ───────────────────────────────────────────────────────────────

export const KillSwitchApi = {
  activate: (agentId: string, reason: string, riskScore = 0.99) =>
    request("/killswitch/activate", {
      method: "POST",
      body: JSON.stringify({ agent_id: agentId, reason, risk_score: riskScore }),
    }),
  release: (agentId: string, note = "") =>
    request("/killswitch/release", {
      method: "POST",
      body: JSON.stringify({ agent_id: agentId, note }),
    }),
  events: () => request<KillSwitchEventItem[]>("/killswitch/events"),
};

// ── Commerce ────────────────────────────────────────────────────────────────

export const CommerceApi = {
  providers: () => request<ProviderProfileResponse[]>("/commerce/providers"),
  negotiate: (body: WorkflowCreateRequest) =>
    request<NegotiationResponse>("/commerce/negotiations", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  createWorkflow: (body: WorkflowCreateRequest) =>
    request<WorkflowResponse>("/commerce/workflows", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  listWorkflows: () => request<WorkflowResponse[]>("/commerce/workflows"),
  approveWorkflow: (workflowId: string) =>
    request<WorkflowResponse>(`/commerce/workflows/${workflowId}/approve`, { method: "POST" }),
  retryWorkflow: (workflowId: string) =>
    request<WorkflowResponse>(`/commerce/workflows/${workflowId}/retry`, { method: "POST" }),
};

// ── Type definitions ──────────────────────────────────────────────────────────

export interface AgentResponse {
  id: string;
  name: string;
  org: string;
  reputation: number;
  status: "online" | "idle" | "offline";
  spendToday: number;
  is_frozen: boolean;
}

export interface AgentRegisterRequest {
  name: string;
  org?: string;
  public_key: string;
  wallet_address: string;
}

export interface PolicyResponse {
  id: string;
  agent_id: string;
  name: string;
  scope: string;
  daily_limit: number;
  allowed_categories: string;
  max_transaction_amount: number;
  approval_threshold: number;
  velocity_limit_per_minute: number;
  status: string;
  triggers: number;
  blocks: number;
  detail: string;
}

export interface PolicyCreateRequest {
  agent_id: string;
  name?: string;
  daily_limit?: number;
  allowed_categories?: string;
  max_transaction_amount?: number;
  approval_threshold?: number;
}

export interface TransactionRequest {
  from: string;
  to: string;
  amount: number;
  currency?: string;
  category?: string;
  purpose?: string;
  merchant?: string;
}

export interface PolicyTraceStep {
  step: string;
  detail: string;
  passed: boolean;
}

export interface EvaluationResult {
  decision: "approved" | "blocked" | "human_approval_required" | "escalated";
  intent_score: number;
  risk_score: number;
  reason: string;
  latency_ms: number;
  policy_trace: PolicyTraceStep[];
}

export interface TransactionResult {
  id: string;
  from: string;
  to: string;
  amount: number;
  currency: string;
  purpose: string;
  status: "approved" | "blocked" | "escalated";
  riskScore: number;
  timestamp: string;
  latencyMs: number;
  policyTrace: PolicyTraceStep[];
}

export interface LedgerEntry {
  id: string;
  transaction_id: string;
  hash: string;
  previous_hash: string;
  display_id: string;
  from: string;
  to: string;
  amount: number;
  currency: string;
  purpose: string;
  status: string;
  riskScore: number;
  risk_score: number;
  latencyMs: number;
  latency_ms: number;
  timestamp: string;
  policyTrace: Array<{ step: string; detail: string; passed: boolean }>;
  signer?: string;
  block_number?: string;
}

export interface InsightsResponse {
  kpis: {
    authorized_volume: number;
    blocked_requests: number;
    avg_latency_ms: number;
    active_agents: number;
  };
  volume_series: Array<{ hour: string; authorized: number; blocked: number }>;
  insights: Array<{ tone: string; title: string; body: string; action: string }>;
  events: Array<{ kind: string; title: string; detail: string; dot: string }>;
}

export interface KillSwitchEventItem {
  id: string;
  agent_id: string;
  action: string;
  reason: string;
  risk_score: number;
  operator: string;
  note: string;
  timestamp: string;
}

export interface ProviderProfileResponse {
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
}

export interface WorkflowCreateRequest {
  goal: string;
  amount?: number;
  currency?: string;
}

export interface WorkflowStepResponse {
  id: string;
  step_name: string;
  status: string;
  detail: string;
  created_at: string;
}

export interface QuoteResponse {
  id: string;
  provider_name: string;
  price: number;
  sla_days: number;
  latency_ms: number;
  reputation_score: number;
  sustainability_score: number;
  decision_score: number;
  counter_offer: string;
  selected: boolean;
  status: string;
}

export interface WorkflowResponse {
  id: string;
  goal: string;
  amount: number;
  currency: string;
  status: string;
  selected_provider: string | null;
  workflow_summary: string;
  approval_required: boolean;
  created_at: string;
  updated_at: string;
  quotes: QuoteResponse[];
  steps: WorkflowStepResponse[];
}

export interface NegotiationResponse {
  goal: string;
  amount: number;
  currency: string;
  quotes: QuoteResponse[];
  ai_summary?: string;
  ai_summary_used?: boolean;
}
