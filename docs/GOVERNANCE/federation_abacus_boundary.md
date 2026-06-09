# Federation Hub / ABACUS Boundary

## Federation Hub

Location: `docs/GOVERNANCE/`

Owns:

- governance navigation
- canonical source routing
- federation index
- onboarding
- reference links

Does not own:

- ingestion runtime
- parser logic
- SSOT generation
- engine execution

## ABACUS

Location: `abacus_runtime/`

Owns:

- ingestion engine
- manifest processing
- SSOT generation
- source indexing
- RTM extraction
- document processing
- dashboard generation

Does not own:

- governance authority
- ADR canon
- RTM canon
- DMAIC lifecycle canon

## Rule

Governance declares authority.  
ABACUS executes ingestion.  
CODEX/MCP reconciles and validates without redefining either.
