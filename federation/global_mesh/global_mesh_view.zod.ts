import { z } from "zod";

export const MeshStatus = z.enum(["PASS", "HOLD", "DEFER", "REJECT", "ACCEPT", "UNKNOWN"]);
export const EvidenceClass = z.enum(["CONTROLLED", "SOURCE_SUPPORTED", "DERIVED", "POSTULATED", "UNKNOWN"]);
export const MeshLens = z.enum(["NARRATIVE", "REQUIREMENTS", "EVIDENCE", "COST", "RELIABILITY", "ARCHITECTURE", "DMAIC", "PROVENANCE", "RUNTIME"]);
export const MeshBoundary = z.enum(["GLOBAL_HIVE", "DOMAIN", "PROJECT", "REPO", "ARTEFACT", "SECTION", "ATOM"]);
export const MeshMode = z.enum(["BOOK", "FLOW", "GRAPH"]);

export const MeshNode = z.object({
  id: z.string().min(1),
  title: z.string().min(1),
  depth: z.number().int().min(0).max(5),
  boundary: MeshBoundary,
  lens: MeshLens,
  content: z.string(),
  parent_id: z.string().optional(),
  source_path: z.string().optional(),
  source_sha: z.string().optional(),
  status: MeshStatus.optional(),
  freshness_timestamp: z.string().optional(),
  confidence: z.number().min(0).max(1).optional(),
  evidence_class: EvidenceClass.optional(),
  next_action: z.string().optional(),
  blocking_atom: z.string().optional(),
  tags: z.array(z.string()).optional()
});

export const MeshViewManifest = z.object({
  schema_version: z.literal("global-mesh-view-manifest/1.0.0"),
  mode: MeshMode,
  boundary: MeshBoundary,
  lens: MeshLens,
  depth: z.number().int().min(0).max(5),
  filters: z.object({
    status: z.array(MeshStatus).default(MeshStatus.options),
    evidence_class: z.array(EvidenceClass).default(EvidenceClass.options)
  }).default({ status: MeshStatus.options, evidence_class: EvidenceClass.options }),
  render: z.object({
    page_size: z.enum(["A4", "LETTER"]).default("A4"),
    toc_depth: z.number().int().min(1).max(6).default(3),
    provenance_footer: z.boolean().default(true),
    interactive: z.boolean().default(true)
  }).default({ page_size: "A4", toc_depth: 3, provenance_footer: true, interactive: true })
});

export type MeshNodeType = z.infer<typeof MeshNode>;
export type MeshViewManifestType = z.infer<typeof MeshViewManifest>;
