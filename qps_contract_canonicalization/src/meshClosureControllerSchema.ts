import { z } from "zod";

const Sha40 = z.string().regex(/^[0-9a-f]{40}$/i);

export const ClosureClassification = z.enum([
  "DONE",
  "REPAIR_REENTRY",
  "HARDENING",
  "NEW_CAPABILITY",
  "PROPAGATION_PROOF",
  "REPEAT"
]);

export const ClosureMethod = z.enum([
  "3PR",
  "MIP_IF_NEEDED",
  "3PC_IF_TRANSACTIONAL",
  "3P3_IF_GENERALISATION_MISSING"
]);

export const ControllerState = z.enum([
  "DIAGNOSE",
  "RECURSE_FIRST_BG",
  "PROVE",
  "COMMIT_OR_REENTER",
  "PROPAGATE_ONCE",
  "STOP"
]);

export const MeshClosureControllerSchema = z.object({
  schema_version: z.literal("gbogeb-mesh-closure-controller/1.0"),
  document_id: z.literal("GLOBAL_MESH_CLOSURE_CONTROLLER"),
  status: z.string().min(1),
  owner_repo: z.literal("GBOGEB/CODEX"),
  purpose: z.string().min(1),
  authority: z.object({
    global_controller_semantics_owner: z.literal("GBOGEB/CODEX"),
    runtime_orchestration_plane: z.literal("GBOGEB/ABACUS"),
    qps_engineering_authority: z.literal("GBOGEB/cryoplant-project"),
    rule: z.string().min(1)
  }),
  human_invocation: z.object({
    canonical_moniker: z.literal("mesh closure control"),
    aliases: z.array(z.string().min(1)).min(1)
  }),
  classifications: z.array(ClosureClassification).length(6).refine(v => new Set(v).size === v.length, "classifications must be unique"),
  method_catalog: z.object({
    "3PR": z.string().min(1),
    MIP: z.string().min(1),
    "3PC": z.string().min(1),
    "3P3": z.string().min(1)
  }),
  selection_policy: z.object({
    default_sequence: z.array(ClosureMethod).length(4),
    minimum_work_rule: z.string().min(1),
    first_blocker_rule: z.string().min(1),
    repeat_rule: z.string().min(1)
  }),
  scheduler_bindings: z.object({
    CG: z.string().min(1),
    BG: z.string().min(1),
    EX: z.string().min(1),
    QH: z.string().min(1),
    KR: z.string().min(1),
    DR: z.string().min(1),
    SR: z.string().min(1),
    WD: z.string().min(1),
    PB: z.string().min(1)
  }),
  execution_proof_rule: z.object({
    pass_requires: z.tuple([
      z.literal("EX_GT_0"),
      z.literal("QH_PASS"),
      z.literal("KR_BOUND_TO_EXACT_OBSERVED_SHA")
    ]),
    zero_step_rule: z.string().min(1),
    floating_ref_rule: z.string().min(1)
  }),
  controller_states: z.array(ControllerState).length(6),
  stop_rule: z.object({
    when_dov_satisfied: z.literal("STOP"),
    rerun_mip: z.literal("ONLY_IF_NEW_STRUCTURAL_GAP_OBSERVED"),
    run_3p3: z.literal("ONLY_IF_GENERALISATION_PROOF_IS_MISSING"),
    repeat_3pr: z.literal("ONLY_IF_REPO_PR_CHECK_OR_EVIDENCE_STATE_CHANGED_MATERIALLY"),
    no_ceremonial_repetition: z.literal(true)
  }),
  required_output: z.array(z.enum([
    "classification",
    "goal",
    "todo",
    "dov",
    "dod",
    "CG",
    "BG",
    "EX",
    "QH",
    "KR",
    "exact_sha_boundary",
    "stop_condition",
    "next_narrow_victory_condition"
  ])).length(13),
  atomic_action_monikers: z.array(z.enum([
    "CLOSE","RED","RUNTIME","SEM","SSOT","RECEIPT","ENABLE","HARDEN","CLEAN","MAINT","READ","EXP","WATCH"
  ])).length(13),
  invariants: z.array(z.string().min(1)).min(1),
  first_use_case: z.object({
    prompt: z.literal("mesh closure control this"),
    expected_decision: z.string().min(1)
  })
}).superRefine((v, ctx) => {
  if (v.atomic_action_monikers.some(m => ["CG","BG","EX","QH","KR","DR","SR","WD","PB"].includes(m))) {
    ctx.addIssue({ code: z.ZodIssueCode.custom, message: "action monikers may not collide with status keys" });
  }
  if (!v.invariants.includes("QPS_ENGINEERING_PROMOTION_REQUIRES_QPS_CHILD_REENTRY")) {
    ctx.addIssue({ code: z.ZodIssueCode.custom, message: "QPS child re-entry invariant is required" });
  }
});

export const MeshClosureReceiptSchema = z.object({
  controller_version: z.literal("gbogeb-mesh-closure-controller/1.0"),
  repo: z.string().min(1),
  source_sha: Sha40,
  classification: ClosureClassification,
  CG: z.string().min(1),
  BG: z.string().nullable(),
  EX: z.object({ executed_steps: z.number().int().nonnegative() }),
  QH: z.enum(["PASS","FAIL","BLOCKED","DEFER","UNKNOWN"]),
  KR: z.object({ exact_sha: Sha40, receipt_ref: z.string().min(1) }).nullable(),
  stop: z.boolean(),
  next_narrow_victory_condition: z.string().min(1)
}).superRefine((v, ctx) => {
  if (v.QH === "PASS" && v.EX.executed_steps <= 0) {
    ctx.addIssue({ code: z.ZodIssueCode.custom, message: "PASS requires EX.executed_steps > 0" });
  }
  if (v.QH === "PASS" && !v.KR) {
    ctx.addIssue({ code: z.ZodIssueCode.custom, message: "PASS requires exact-SHA KR" });
  }
  if (v.KR && v.KR.exact_sha !== v.source_sha) {
    ctx.addIssue({ code: z.ZodIssueCode.custom, message: "KR exact_sha must bind the observed source_sha" });
  }
});
