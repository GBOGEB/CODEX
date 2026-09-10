# Immutable QPS input ingress

This directory is a byte-preserving staging boundary for four pre-existing governed XLSX authorities. Do not regenerate, resave, normalize, convert, or substitute these workbooks.

Required files and SHA256:

- `QPS_OFFER_Cluster_v3_4_BT_RTM_Standards_Evidence.xlsx` — `00a5f0ed3ded00620a33edd045706ba5fb9a67b5fb7fe63c495305f911c43ccb`
- `QPS_ALAT_SSOT_CURRENT_2026-09-07.xlsx` — `5c4c845f7e9d88c1bfe002817c98e5584135cc8bc85bf9ea6596c183318a1907`
- `QPS_LKT_NEG_RFI_REVIEW_MASTER_W21_2.xlsx` — `6d763cce948a1ee14c30c42b0367226f97dc4712beb6ab4b6e641ad0e8b00f3f`
- `QPS_LKT_ALAT_RTM_COMPLIANCE_W22L_RETURN_PACKAGES.xlsx` — `b745ef62417d921495bffdc3154e8fc0340216d4ba7ad85e847a0b468a5327e4`

Admission rule: W101 must recompute `PASS_4_OF_4_IMMUTABLE_INPUTS` before any B1 diagnostic/materialisation execution is permitted. Any missing file or hash mismatch stops the chain at immutable provenance recovery.

Credit rule: staging or validation alone grants zero engineering, negotiation, compliance, or release credit. Native cryoplant exact-SHA execution remains mandatory for release credit.
