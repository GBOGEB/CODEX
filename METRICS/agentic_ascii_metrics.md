# Agentic MCP GitHub Orchestration Metrics

## Flow

Source Push             [####################] READY
PR Context Read         [####################] READY
Comment Intake          [####################] READY
Discrepancy Detection   [################----] READY
Patch Proposal          [############--------] USER-GATED
Commit                  [--------------------] WAITING CONFIRMATION
Bulk Commit             [--------------------] WAITING CONFIRMATION

## Agentic Loop

local git push
  -> PR opened/updated
  -> comments/checks scanned
  -> discrepancies classified
  -> patch prepared
  -> user reads comment + fix
  -> confirm one / confirm bulk / answer only
  -> commit
  -> push
  -> PR follow-up comment
