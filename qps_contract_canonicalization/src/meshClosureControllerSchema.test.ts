import test from "node:test";
import assert from "node:assert/strict";
import { MeshClosureReceiptSchema } from "./meshClosureControllerSchema.js";

const sha = "0123456789abcdef0123456789abcdef01234567";

test("PASS requires executed validation and exact-SHA KR", () => {
  assert.throws(() => MeshClosureReceiptSchema.parse({
    controller_version: "gbogeb-mesh-closure-controller/1.0",
    repo: "GBOGEB/CODEX",
    source_sha: sha,
    classification: "DONE",
    CG: "ADMIT_MERGE",
    BG: null,
    EX: { executed_steps: 0 },
    QH: "PASS",
    KR: { exact_sha: sha, receipt_ref: "receipt://test" },
    stop: true,
    next_narrow_victory_condition: "none"
  }));
});

test("PASS requires KR", () => {
  assert.throws(() => MeshClosureReceiptSchema.parse({
    controller_version: "gbogeb-mesh-closure-controller/1.0",
    repo: "GBOGEB/CODEX",
    source_sha: sha,
    classification: "DONE",
    CG: "ADMIT_MERGE",
    BG: null,
    EX: { executed_steps: 1 },
    QH: "PASS",
    KR: null,
    stop: true,
    next_narrow_victory_condition: "none"
  }));
});

test("valid PASS binds KR to exact source SHA", () => {
  const result = MeshClosureReceiptSchema.parse({
    controller_version: "gbogeb-mesh-closure-controller/1.0",
    repo: "GBOGEB/CODEX",
    source_sha: sha,
    classification: "DONE",
    CG: "ADMIT_MERGE",
    BG: null,
    EX: { executed_steps: 2 },
    QH: "PASS",
    KR: { exact_sha: sha, receipt_ref: "receipt://test" },
    stop: true,
    next_narrow_victory_condition: "none"
  });
  assert.equal(result.stop, true);
});
