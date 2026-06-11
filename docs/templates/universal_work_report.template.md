# Universal Work Report — STANDARD Template

```yaml
schema_name: universal_work_report
schema_version: 1.0.0
work_id: <WORK-ID>
agent: <AGENT>
level: <PROGRAMME|WAVE|SUB-WAVE|PHASE|SPRINT|TASK|SUBTASK>
parent_id: <PARENT-ID|null>
track_type: <SEQ|PAR>
risk_class: <REVERSIBLE|IRREVERSIBLE|SECRET-SENSITIVE|EXTERNAL-EFFECT>
review_status: <REVIEW-FIRST|READY|BLOCKED|HOLD-POINT>
merge_allowed: false
victory:
  overall: <MET|NOT MET|PARTIAL>
  criteria:
    - id: <V1>
      status: <PASS|FAIL|PARTIAL|N/A>
      evidence: <EVIDENCE>
testing_ledger:
  - command: <COMMAND>
    status: <PASS|FAIL|ENVIRONMENT-LIMITATION>
    evidence: <EVIDENCE>
artifacts:
  runtime_only: []
  committed: []
  persistent_verified: []
audit:
  tree_sha: null
  container_head_sha: null
  base_ref_stable: false
  pin_container_sha: false
  pin_remote_sha: true
  merge_requires_human_go: true
```

## 0. Identity and mapping
- WORK_ID:
- LEVEL:
- PARENT_ID:
- DEPENDS_ON:
- BLOCKS:

## 1. Intent

## 2. Goal

## 3. Action taken / commit refs

## 4. Victory checklist delta

## 5. Track status [SEQ]/[PAR]

## 6. FF / FB loops

## 7. Milestone vs hold-point

## 8. Blockers and environment limitations

## 9. Testing ledger

## 10. Artifacts / files touched

## 11. Audit / data available
