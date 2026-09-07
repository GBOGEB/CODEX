# KEB Architecture W57

## High-level architecture

```text
ENGINEERING PAYLOAD
        |
        v
CONTRACT / ZOD
        |
        v
SEMANTIC NORMALIZER
        |
   +----+-----+
   |    |     |
   v    v     v
PROV  POLICY  ADR
   \    |    /
    \   |   /
     v  v  v
 GOVERNANCE GRAPH
        |
   +----+-----+
   v          v
BRIDGES    ADAPTORS
   \          /
    \        /
       v
   FEDERATION
       |
       v
   KEB RECEIPT
```

## cADR
See `KEB_cADR_W57.yaml`.

## xOCD
See `KEB_xOCD_W57.yaml`.

## User-facing outward family
- KEB_ARCHITECTURE.xlsx
- KEB_ARCHITECTURE.html
- KEB_ARCHITECTURE.pptx
- KEB_ARCHITECTURE.pdf
- KEB_SCHEMA_REGISTER.xlsx
- KEB_BRIDGE_REGISTER.xlsx
- KEB_ADAPTOR_REGISTER.xlsx
- KEB_PROVENANCE_GRAPH.html
- KEB_FEDERATION_MAP.html

## Interaction role
B1 receives engineering semantic/provenance payload from cryoplant-project. B2 emits governed execution payload to ABACUS/DOW. KEB reconciles the DOW receipt and returns a hash-bound governance receipt to the child.

## Boundary
CODEX governs meaning, provenance, policy and federation contracts. It does not own QPS engineering truth or DOW runtime execution.
