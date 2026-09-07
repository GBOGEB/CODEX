import { z } from 'zod';

export const PressureAxisSchema = z.enum([
  'scope',
  'frequency',
  'coverage',
  'workers',
  'evidence',
  'schema',
  'runtime',
  'qa',
  'binary_freshness',
  'receipts',
  'child_reentry',
  'zero_delta',
  'historical_cleanup',
]);

export const PressureLevelSchema = z.enum(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']);
export const RecommendationActionSchema = z.enum([
  'HOLD',
  'NARROW',
  'EXPAND_SCOPE',
  'INCREASE_FREQUENCY',
  'DECREASE_FREQUENCY',
  'ADD_COVERAGE',
  'ADD_WORKERS',
  'REDUCE_WORKERS',
  'ESCALATE_EVIDENCE_RECOVERY',
  'REGENERATE_BINARIES',
  'REQUIRE_HUMAN_REVIEW',
  'REQUEST_REAL_RECEIPT',
  'REQUEST_CHILD_REENTRY',
  'REPEAT_ZERO_DELTA_ROUNDTRIP',
  'DEFER_HISTORICAL_CLEANUP',
]);

export const DoVKindSchema = z.enum(['SESSION_CHAT', 'GLOBAL']);
export const DoVHorizonSchema = z.enum(['H0_SESSION_CHAT', 'H1_NEXT_PULSE', 'H5_FIVE_WAVE', 'H50_PORTFOLIO', 'H100_SUSTAINED']);
export const PulseControlStatusSchema = z.enum([
  'CONTROL_DEFINED',
  'CONTROL_DEFINED_PENDING_REAL_RUN',
  'PENDING_REAL_RECEIPTS',
  'PENDING_CHILD_REENTRY',
  'BLOCKED_UNTIL_CHILD_ACCEPT',
  'BLOCKED_UNTIL_P4',
  'BLOCKED_UNTIL_P5',
  'DEFERRED_UNTIL_ZERO_DELTA_BASELINE',
  'ACCEPTED',
  'REJECTED',
  'DEFERRED',
]);

export const ChildReentryDecisionSchema = z.enum(['ACCEPT', 'REJECT', 'DEFER']);

export const ReversePressureSignalSchema = z.object({
  axis: PressureAxisSchema,
  level: PressureLevelSchema,
  score: z.number().min(0).max(1),
  residual: z.number().min(0).max(1),
  sourceMetrics: z.array(z.string()).min(1),
  rationale: z.string().min(1),
});

export const GranularPcaDimensionSchema = z.object({
  id: z.string().min(1),
  score: z.number().min(0).max(1),
  residualWeight: z.number().min(0).max(1),
  reverseLoadPriority: z.number().min(0).max(1),
  isLowScoring: z.boolean(),
  linkedPulses: z.array(z.enum(['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7'])).min(1),
  emphasis: z.string().min(1),
});

export const DoVHorizonStateSchema = z.object({
  horizon: DoVHorizonSchema,
  kind: DoVKindSchema,
  expectedDov: z.number().min(0).max(1),
  currentDov: z.number().min(0).max(1),
  evidenceRequired: z.array(z.string()).min(1),
  closed: z.boolean(),
});

export const PulseControlSchema = z.object({
  pulse: z.enum(['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7']),
  name: z.string().min(1),
  status: PulseControlStatusSchema,
  gate: z.string().min(1),
  requiredReceiptSha256: z.string().regex(/^[a-f0-9]{64}$/).optional(),
  childDecision: ChildReentryDecisionSchema.optional(),
  blocksGlobalDovPromotion: z.boolean(),
});

export const ThreeP3RecommendationSchema = z.object({
  action: RecommendationActionSchema,
  targetAxis: PressureAxisSchema,
  proposedDelta: z.number().min(-1).max(1),
  boundedBy: z.array(z.string()).min(1),
  requiresChildAcceptance: z.boolean(),
  autoExecutable: z.boolean(),
  expectedBenefit: z.number().min(0).max(1),
  confidence: z.number().min(0).max(1),
});

export const ThreeP3SelfEvaluationSchema = z.object({
  moniker: z.literal('3PR'),
  scheme: z.literal('3P3'),
  pulse: z.enum(['P1_QPS', 'P2_KEB', 'P3_DOW', 'ROLLUP']),
  payloadSha256: z.string().regex(/^[a-f0-9]{64}$/),
  priorPulseReceiptSha256: z.string().regex(/^[a-f0-9]{64}$/).optional(),
  reversePressure: z.array(ReversePressureSignalSchema).min(1),
  recommendations: z.array(ThreeP3RecommendationSchema),
  dovScore: z.number().min(0).max(1),
  dovKind: DoVKindSchema.default('SESSION_CHAT'),
  horizons: z.array(DoVHorizonStateSchema).length(5).optional(),
  pulseControls: z.array(PulseControlSchema).length(7).optional(),
  pcaResidualScore: z.number().min(0).max(1),
  granularPca: z.array(GranularPcaDimensionSchema).optional(),
  btPriorityScore: z.number().min(0).max(1),
  stopConditions: z.array(z.string()),
  noFalseCompliancePromotion: z.boolean().default(true),
  nextPulseAllowed: z.boolean(),
  generatedAt: z.string().datetime(),
});

export type ThreeP3SelfEvaluation = z.infer<typeof ThreeP3SelfEvaluationSchema>;
export type DoVHorizonState = z.infer<typeof DoVHorizonStateSchema>;
export type PulseControl = z.infer<typeof PulseControlSchema>;
export type GranularPcaDimension = z.infer<typeof GranularPcaDimensionSchema>;
