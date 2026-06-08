# ALaT Clarification Bridge v0.1

YAML-driven single source of truth bridge for RTM traceability, Contract Follow-up, and OFFER_list management across the preserved Q3/Q4/Q5 route.

## Source of truth

- Questions: `ssot/alat_questions_ssot_v0_1.yaml`
- RTM links: `RTM_LINKS.yaml`
- OFFER actions: `OFFER_REGISTER.yaml`

## Controls

- Internal sub-question numbers are for SCK traceability only.
- Bidder-facing answers use short bullet roll-ups.
- Pressure, temperature, and flow values remain controlled by applicable input/interface tables.
- Slides are internal preparation material and must not appear in bidder-facing outputs.

## Local checks

```bash
python rtm_integration/contract_followup/alat_clarification_bridge/tools/validate_ssot.py
python rtm_integration/contract_followup/alat_clarification_bridge/tools/generate_bridge.py
```
