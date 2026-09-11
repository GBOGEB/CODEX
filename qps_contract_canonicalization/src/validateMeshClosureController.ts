import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { MeshClosureControllerSchema } from "./meshClosureControllerSchema.js";

const here = path.dirname(fileURLToPath(import.meta.url));
const contractPath = path.resolve(here, "../../federation/mesh/MESH_CLOSURE_CONTROLLER_v1.json");
const parsed = JSON.parse(fs.readFileSync(contractPath, "utf8"));
const contract = MeshClosureControllerSchema.parse(parsed);

console.log(JSON.stringify({
  validated: true,
  document_id: contract.document_id,
  controller: contract.human_invocation.canonical_moniker,
  classifications: contract.classifications.length,
  atomic_actions: contract.atomic_action_monikers.length,
  stop_rule: contract.stop_rule.when_dov_satisfied,
  zero_step_pass_forbidden: true,
  qps_child_reentry_required: contract.invariants.includes("QPS_ENGINEERING_PROMOTION_REQUIRES_QPS_CHILD_REENTRY")
}, null, 2));
