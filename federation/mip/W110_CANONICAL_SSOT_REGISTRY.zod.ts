import { z } from "zod";

export const MipDisposition = z.enum(["ACCEPT", "REJECT", "DEFER"]);
export const MipLevelStatus = z.enum([
  "CANDIDATE_ACTIVE",
  "ACTIVE_EXACT_HEAD_PROOF_REPORTED",
  "ACTIVE_CI_REGISTRY_RECEIPT",
  "ACTIVE_P6_BRIDGE_PROOF",
  "ACTIVE_P5_LEAK_PROOF",
  "DORMANT_CANDIDATE"
]);

export const PreviousTailReceipt = z.object({
  status: z.literal("FIXED_AS_HISTORICAL_ACCEPT_NOT_CURRENT_HEAD"),
  lane: z.string().min(1),
  codex_pr: z.string().url(),
  codex_exact_head_sha: z.string().regex(/^[a-f0-9]{40}$/),
  codex_workflow_run: z.string().url(),
  codex_receipt_artifact_id: z.number().int().positive(),
  codex_receipt_artifact_digest: z.string().regex(/^sha256:[a-f0-9]{64}$/),
  codex_receipt_sha256: z.string().regex(/^[a-f0-9]{64}$/),
  probe_status: z.literal("ACCEPT"),
  dov_status: z.literal("PASS"),
  real_lldb_steps: z.number().int().positive(),
  abacus_pr: z.string().url(),
  abacus_final_head_sha: z.string().regex(/^[a-f0-9]{40}$/),
  cryoplant_pr: z.string().url(),
  cryoplant_final_head_sha: z.string().regex(/^[a-f0-9]{40}$/),
  note: z.string().min(1),
});

export const SatelliteRepo = z.object({
  repo: z.string().regex(/^GBOGEB\//),
  observed_head_sha: z.string().regex(/^[a-f0-9]{40}$/),
  observed_at_utc: z.string().datetime(),
  evidence_url: z.string().url(),
  current_role: z.string().min(1),
  mip_level_1_status: MipLevelStatus,
  ssot_visibility: z.string().min(1),
});

export const MipCanonicalSsotRegistry = z.object({
  schema_version: z.literal("mip-canonical-ssot-registry/1.0"),
  wave: z.literal("W110"),
  created_utc: z.string().datetime(),
  purpose: z.string().min(1),
  authority_boundary: z.object({
    child_engineering_truth: z.literal("GBOGEB/cryoplant-project"),
    dow_consumption_analysis: z.literal("GBOGEB/ABACUS"),
    keb_semantic_runtime_receipts: z.literal("GBOGEB/CODEX"),
    smaller_active_repos: z.string().min(1),
  }),
  current_triad: z.record(z.string(), z.object({
    repo: z.string().regex(/^GBOGEB\//),
    current_main_observed_sha: z.string().regex(/^[a-f0-9]{40}$/),
    role: z.string().min(1),
    current_open_prs: z.array(z.string().url()).optional(),
  })),
  previous_tail: PreviousTailReceipt,
  active_last_24h_satellites: z.array(SatelliteRepo).min(1),
  dormant_candidates: z.array(z.object({
    repo: z.string().regex(/^GBOGEB\//),
    observed_head_sha: z.string().regex(/^[a-f0-9]{40}$/),
    observed_at_utc: z.string().datetime(),
    reason: z.string().min(1),
  })),
  mip: z.object({
    modernize: z.array(z.string().min(1)).min(1),
    innovate: z.array(z.string().min(1)).min(1),
    perpetuate: z.array(z.string().min(1)).min(1),
  }),
  zod_contract: z.string().endsWith(".ts"),
  disposition: z.literal("DEFER_FOR_SMALL_REPOS_UNTIL_REPO_LOCAL_SSOT_POINTERS_EXIST"),
  child_disposition_rule: z.object({
    ACCEPT: z.string().min(1),
    REJECT: z.string().min(1),
    DEFER: z.string().min(1),
  }),
}).superRefine((registry, ctx) => {
  const repos = new Set(registry.active_last_24h_satellites.map((entry) => entry.repo));
  if (repos.size !== registry.active_last_24h_satellites.length) {
    ctx.addIssue({ code: z.ZodIssueCode.custom, message: "active satellite repos must be unique" });
  }
  if (registry.previous_tail.real_lldb_steps <= 0) {
    ctx.addIssue({ code: z.ZodIssueCode.custom, message: "historical LLDB-DAP ACCEPT tail requires >0 real LLDB steps" });
  }
});

export type MipCanonicalSsotRegistryPayload = z.infer<typeof MipCanonicalSsotRegistry>;
