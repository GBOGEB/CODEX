# W003 Arrow Direction Validation

## Actual source files found
| path | kind | size_bytes |
| --- | --- | --- |
| data/svg/QCELL_PARASITIC.drawio.svg | svg | 11360 |
| data/svg/pressure_diagnostic_v0_6_2.svg | svg | 1458 |
| data/svg/qps-graph-mvp.svg | svg | 1957 |
| data/svg/temperature_analysis_v0_6_2.svg | svg | 2007 |

## Source file counts
- SVG files found: 4
- PDF files found: 0
- PPT/PPTX files found: 0

## SVG load status
| path | status | error |
| --- | --- | --- |
| data/svg/QCELL_PARASITIC.drawio.svg | loaded |  |
| data/svg/pressure_diagnostic_v0_6_2.svg | loaded |  |
| data/svg/qps-graph-mvp.svg | loaded |  |
| data/svg/temperature_analysis_v0_6_2.svg | loaded |  |

## Colour bins detected
| colour_bin | process_line_count |
| --- | --- |
| blue_A | 7 |
| cyan_B_2K | 0 |
| green_W_coupler | 0 |
| grey_V_vent | 0 |
| olive_S_line | 4 |
| red_orange_D_E | 0 |
| unknown_black_or_other | 3 |

## Object counts
- Process lines: 14
- Tags: 50
- Valves: 4
- Instruments: 0
- Equipment: 4
- Arrows: 1
- Boundaries: 8

## Arrow counts per colour
| colour_bin | arrow_count |
| --- | --- |
| blue_A | 0 |
| cyan_B_2K | 0 |
| green_W_coupler | 0 |
| grey_V_vent | 0 |
| olive_S_line | 0 |
| red_orange_D_E | 0 |
| unknown_black_or_other | 1 |

## Subsystem counts
| subsystem | object_count |
| --- | --- |
| QM | 32 |
| Jumper | 2 |
| QVB | 0 |
| QINFRA | 23 |
| Unknown | 16 |

## Unresolved counts
- Unresolved arrows: 0
- Unresolved colours: 3
- Unresolved tags: 3
- Unresolved boundaries: 6
- Unresolved objects: 12

## Completion status
- complete_nonzero

## Known Limitations / Resolution Rates
- Arrow extraction: 1 arrow(s) resolved from 14 line(s). Direction is emitted only for explicit SVG marker or draw.io `endArrow`/`startArrow` evidence; connector lines without arrowhead evidence are not silently treated as flow direction.
- Arrow coverage: 13 line(s) lack explicit arrow evidence. The one resolved arrow comes from draw.io `endArrow` metadata in `QCELL_PARASITIC.drawio.svg`; the other local SVGs use plain SVG lines or non-arrow diagnostic graphics.
- Subsystem resolution: 57 resolved vs 16 Unknown. Unknown labels generally do not contain QM, Jumper, QVB, or QINFRA text evidence.
- Target for the next rule-improvement PR: reduce Unknown subsystem classification to ≤50% on this same local asset set without weakening evidence requirements.
- Colour-bin reconciliation: blue_A=7, cyan_B_2K=0, green_W_coupler=0, grey_V_vent=0, olive_S_line=4, red_orange_D_E=0, unknown_black_or_other=3. Empty per-bin JSON files are retained as stable viewer/model outputs for toggle compatibility.
- Unresolved boundaries: 6. These are reported separately; subsystem Unknown is driven by missing subsystem text evidence, not by boundary resolution alone.

## QM Precision Check
| object_type | object_id | source_file | source_svg_id | label_text_used | subsystem_pattern | evidence_type |
| --- | --- | --- | --- | --- | --- | --- |
| tag | tag_01_mx_1_00001 | data/svg/QCELL_PARASITIC.drawio.svg | sheet1:2 | QCELL BSLN_0 | QM label token: QCELL | direct label or explicit draw.io endpoint label |
| tag | tag_01_mx_1_00002 | data/svg/QCELL_PARASITIC.drawio.svg | sheet1:3 | Thermal Shell (2 K mass) | QM label token: THERMAL | direct label or explicit draw.io endpoint label |
| tag | tag_01_mx_2_00004 | data/svg/QCELL_PARASITIC.drawio.svg | sheet2:2 | QCELL - Copy of BSLN_0 | QM label token: QCELL | direct label or explicit draw.io endpoint label |
| tag | tag_01_mx_2_00005 | data/svg/QCELL_PARASITIC.drawio.svg | sheet2:3 | Thermal Shell (2 K mass) | QM label token: THERMAL | direct label or explicit draw.io endpoint label |
| tag | tag_01_mx_3_00008 | data/svg/QCELL_PARASITIC.drawio.svg | sheet3:2 | QCELL - Copy of Copy of BSLN_0 | QM label token: QCELL | direct label or explicit draw.io endpoint label |
| tag | tag_01_mx_3_00009 | data/svg/QCELL_PARASITIC.drawio.svg | sheet3:3 | Thermal Shell (2 K mass) | QM label token: THERMAL | direct label or explicit draw.io endpoint label |
| tag | tag_01_mx_4_00011 | data/svg/QCELL_PARASITIC.drawio.svg | sheet4:2 | QCELL v0.8.1 - Canonical Sheet | QM label token: QCELL | direct label or explicit draw.io endpoint label |
| tag | tag_01_mx_4_00012 | data/svg/QCELL_PARASITIC.drawio.svg | sheet4:10 | Thermal Layer | QM label token: THERMAL | direct label or explicit draw.io endpoint label |
| tag | tag_01_mx_4_00013 | data/svg/QCELL_PARASITIC.drawio.svg | sheet4:11 | 2 K Superfluid Mass | QM label token: 2 K | direct label or explicit draw.io endpoint label |
| tag | tag_01_mx_4_00014 | data/svg/QCELL_PARASITIC.drawio.svg | sheet4:12 | He II Heat Exchanger | QM label token: HE II | direct label or explicit draw.io endpoint label |
| tag | tag_01_mx_4_00015 | data/svg/QCELL_PARASITIC.drawio.svg | sheet4:13 | Thermal Flow | QM label token: THERMAL | direct label or explicit draw.io endpoint label |
| tag | tag_01_mx_4_00021 | data/svg/QCELL_PARASITIC.drawio.svg | sheet4:31 | Coolant In | QM label token: COOLANT | direct label or explicit draw.io endpoint label |
| tag | tag_01_mx_4_00022 | data/svg/QCELL_PARASITIC.drawio.svg | sheet4:32 | QCell Core | QM label token: QCELL | direct label or explicit draw.io endpoint label |
| tag | tag_01_mx_4_00023 | data/svg/QCELL_PARASITIC.drawio.svg | sheet4:33 | Heat Load | QM label token: HEAT LOAD | direct label or explicit draw.io endpoint label |
| tag | tag_01_mx_4_00025 | data/svg/QCELL_PARASITIC.drawio.svg | sheet4:35 | Coolant Out | QM label token: COOLANT | direct label or explicit draw.io endpoint label |
| tag | tag_04_00001 | data/svg/temperature_analysis_v0_6_2.svg | svg4_text_16 | QCell Thermal Analysis — Temperature Primary (v0.6.2) | QM label token: QCELL | direct label or explicit draw.io endpoint label |
| tag | tag_04_00002 | data/svg/temperature_analysis_v0_6_2.svg | svg4_text_18 | Cryogenic temperature scale (2–77 K): | QM label token: 77 K | direct label or explicit draw.io endpoint label |
| tag | tag_04_00003 | data/svg/temperature_analysis_v0_6_2.svg | svg4_text_20 | 2 K | QM label token: 2 K | direct label or explicit draw.io endpoint label |
| tag | tag_04_00004 | data/svg/temperature_analysis_v0_6_2.svg | svg4_text_21 | 4 K | QM label token: 4 K | direct label or explicit draw.io endpoint label |
| tag | tag_04_00005 | data/svg/temperature_analysis_v0_6_2.svg | svg4_text_22 | 30 K | QM label token: 30 K | direct label or explicit draw.io endpoint label |
| tag | tag_04_00006 | data/svg/temperature_analysis_v0_6_2.svg | svg4_text_23 | 50 K | QM label token: 50 K | direct label or explicit draw.io endpoint label |
| tag | tag_04_00007 | data/svg/temperature_analysis_v0_6_2.svg | svg4_text_24 | 60 K | QM label token: 60 K | direct label or explicit draw.io endpoint label |
| tag | tag_04_00008 | data/svg/temperature_analysis_v0_6_2.svg | svg4_text_25 | 77 K | QM label token: 77 K | direct label or explicit draw.io endpoint label |
| tag | tag_04_00009 | data/svg/temperature_analysis_v0_6_2.svg | svg4_text_27 | Warm extension (separate semantic band): 77–300 K | QM label token: WARM EXTENSION | direct label or explicit draw.io endpoint label |
| boundary | boundary_01_mx_4_00002 | data/svg/QCELL_PARASITIC.drawio.svg | sheet4:10 | Thermal Layer | QM label token: THERMAL | direct label or explicit draw.io endpoint label |
| line | line_01_mx_1_00001 | data/svg/QCELL_PARASITIC.drawio.svg | sheet1:5 | source=Thermal Shell (2 K mass); target=Pressure Diagnostic | QM label token: THERMAL | direct label or explicit draw.io endpoint label |
| line | line_01_mx_3_00002 | data/svg/QCELL_PARASITIC.drawio.svg | sheet3:5 | source=Thermal Shell (2 K mass); target=Pressure Diagnostic | QM label token: THERMAL | direct label or explicit draw.io endpoint label |
| line | line_01_mx_4_00003 | data/svg/QCELL_PARASITIC.drawio.svg | sheet4:14 | source=2 K Superfluid Mass; target=He II Heat Exchanger | QM label token: 2 K | direct label or explicit draw.io endpoint label |
| line | line_01_mx_4_00004 | data/svg/QCELL_PARASITIC.drawio.svg | sheet4:36 | source=Coolant In; target=QCell Core | QM label token: COOLANT | direct label or explicit draw.io endpoint label |
| line | line_01_mx_4_00005 | data/svg/QCELL_PARASITIC.drawio.svg | sheet4:37 | source=QCell Core; target=Heat Load | QM label token: QCELL | direct label or explicit draw.io endpoint label |
| line | line_01_mx_4_00006 | data/svg/QCELL_PARASITIC.drawio.svg | sheet4:38 | source=Heat Load; target=Buffer/JT Valve | QM label token: HEAT LOAD | direct label or explicit draw.io endpoint label |
| arrow | arrow_01_mx_3_00001 | data/svg/QCELL_PARASITIC.drawio.svg | sheet3:5 | source=Thermal Shell (2 K mass); target=Pressure Diagnostic | QM label token: THERMAL | direct label or explicit draw.io endpoint label |

## QM Pattern Review Flags (>10 matches)
| subsystem_pattern | match_count |
| --- | --- |
| none | 0 |

## Unknown Classification Breakdown
| primary_failure_cause | unknown_object_count |
| --- | --- |
| no_matching_pattern_in_tag_layer_register | 5 |
| outside_all_resolved_boundaries | 11 |
| no_tag_or_label | 0 |

## Unknown Object Details
| object_type | object_id | source_file | source_svg_id | label | primary_failure_cause | reason |
| --- | --- | --- | --- | --- | --- | --- |
| tag | tag_01_mx_2_00007 | data/svg/QCELL_PARASITIC.drawio.svg | sheet2:5 | Hierarchy group | no_matching_pattern_in_tag_layer_register | Draw.io label does not match tag/subsystem regex. |
| tag | tag_01_mx_4_00020 | data/svg/QCELL_PARASITIC.drawio.svg | sheet4:30 | Teaching Flow Layer | no_matching_pattern_in_tag_layer_register | Draw.io label does not match tag/subsystem regex. |
| tag | tag_01_mx_4_00026 | data/svg/QCELL_PARASITIC.drawio.svg | sheet4:40 | [Endpoint guide: layer-separated canonical form — Sheet 4 is v0.8.1 input] | no_matching_pattern_in_tag_layer_register | Draw.io label does not match tag/subsystem regex. |
| boundary | boundary_01_mx_2_00001 | data/svg/QCELL_PARASITIC.drawio.svg | sheet2:5 | Hierarchy group | no_matching_pattern_in_tag_layer_register | Boundary label is not one of QM/Jumper/QVB/QINFRA. |
| boundary | boundary_01_mx_4_00004 | data/svg/QCELL_PARASITIC.drawio.svg | sheet4:30 | Teaching Flow Layer | no_matching_pattern_in_tag_layer_register | Boundary label is not one of QM/Jumper/QVB/QINFRA. |
| boundary | boundary_02_00001 | data/svg/pressure_diagnostic_v0_6_2.svg | svg2_rect_9 |  | outside_all_resolved_boundaries | Boundary/scope label not directly associated. |
| boundary | boundary_02_00002 | data/svg/pressure_diagnostic_v0_6_2.svg | svg2_rect_11 |  | outside_all_resolved_boundaries | Boundary/scope label not directly associated. |
| boundary | boundary_04_00001 | data/svg/temperature_analysis_v0_6_2.svg | svg4_rect_15 |  | outside_all_resolved_boundaries | Boundary/scope label not directly associated. |
| boundary | boundary_04_00002 | data/svg/temperature_analysis_v0_6_2.svg | svg4_rect_17 |  | outside_all_resolved_boundaries | Boundary/scope label not directly associated. |
| line | line_03_00001 | data/svg/qps-graph-mvp.svg | svg3_line_2 |  | outside_all_resolved_boundaries | Line has no direct label; no resolved subsystem boundary contains it. |
| line | line_03_00002 | data/svg/qps-graph-mvp.svg | svg3_line_3 |  | outside_all_resolved_boundaries | Line has no direct label; no resolved subsystem boundary contains it. |
| line | line_03_00003 | data/svg/qps-graph-mvp.svg | svg3_line_4 |  | outside_all_resolved_boundaries | Line has no direct label; no resolved subsystem boundary contains it. |
| line | line_03_00004 | data/svg/qps-graph-mvp.svg | svg3_line_5 |  | outside_all_resolved_boundaries | Line has no direct label; no resolved subsystem boundary contains it. |
| line | line_03_00005 | data/svg/qps-graph-mvp.svg | svg3_line_6 |  | outside_all_resolved_boundaries | Line has no direct label; no resolved subsystem boundary contains it. |
| line | line_03_00006 | data/svg/qps-graph-mvp.svg | svg3_line_7 |  | outside_all_resolved_boundaries | Line has no direct label; no resolved subsystem boundary contains it. |
| line | line_03_00007 | data/svg/qps-graph-mvp.svg | svg3_line_8 |  | outside_all_resolved_boundaries | Line has no direct label; no resolved subsystem boundary contains it. |

## Arrow Coverage Details
| line_id | source_file | source_svg_id | colour_bin | reason |
| --- | --- | --- | --- | --- |
| line_01_mx_1_00001 | data/svg/QCELL_PARASITIC.drawio.svg | sheet1:5 | unknown_black_or_other | No marker-start/marker-end or draw.io endArrow/startArrow evidence on this line. |
| line_01_mx_4_00003 | data/svg/QCELL_PARASITIC.drawio.svg | sheet4:14 | unknown_black_or_other | No marker-start/marker-end or draw.io endArrow/startArrow evidence on this line. |
| line_01_mx_4_00004 | data/svg/QCELL_PARASITIC.drawio.svg | sheet4:36 | olive_S_line | No marker-start/marker-end or draw.io endArrow/startArrow evidence on this line. |
| line_01_mx_4_00005 | data/svg/QCELL_PARASITIC.drawio.svg | sheet4:37 | olive_S_line | No marker-start/marker-end or draw.io endArrow/startArrow evidence on this line. |
| line_01_mx_4_00006 | data/svg/QCELL_PARASITIC.drawio.svg | sheet4:38 | olive_S_line | No marker-start/marker-end or draw.io endArrow/startArrow evidence on this line. |
| line_01_mx_4_00007 | data/svg/QCELL_PARASITIC.drawio.svg | sheet4:39 | olive_S_line | No marker-start/marker-end or draw.io endArrow/startArrow evidence on this line. |
| line_03_00001 | data/svg/qps-graph-mvp.svg | svg3_line_2 | blue_A | No marker-start/marker-end or draw.io endArrow/startArrow evidence on this line. |
| line_03_00002 | data/svg/qps-graph-mvp.svg | svg3_line_3 | blue_A | No marker-start/marker-end or draw.io endArrow/startArrow evidence on this line. |
| line_03_00003 | data/svg/qps-graph-mvp.svg | svg3_line_4 | blue_A | No marker-start/marker-end or draw.io endArrow/startArrow evidence on this line. |
| line_03_00004 | data/svg/qps-graph-mvp.svg | svg3_line_5 | blue_A | No marker-start/marker-end or draw.io endArrow/startArrow evidence on this line. |
| line_03_00005 | data/svg/qps-graph-mvp.svg | svg3_line_6 | blue_A | No marker-start/marker-end or draw.io endArrow/startArrow evidence on this line. |
| line_03_00006 | data/svg/qps-graph-mvp.svg | svg3_line_7 | blue_A | No marker-start/marker-end or draw.io endArrow/startArrow evidence on this line. |
| line_03_00007 | data/svg/qps-graph-mvp.svg | svg3_line_8 | blue_A | No marker-start/marker-end or draw.io endArrow/startArrow evidence on this line. |

## Unresolved tags / labels
| tag_id | source_file | text | reason |
| --- | --- | --- | --- |
| tag_01_mx_2_00007 | data/svg/QCELL_PARASITIC.drawio.svg | Hierarchy group | Draw.io label does not match tag/subsystem regex. |
| tag_01_mx_4_00020 | data/svg/QCELL_PARASITIC.drawio.svg | Teaching Flow Layer | Draw.io label does not match tag/subsystem regex. |
| tag_01_mx_4_00026 | data/svg/QCELL_PARASITIC.drawio.svg | [Endpoint guide: layer-separated canonical form — Sheet 4 is v0.8.1 input] | Draw.io label does not match tag/subsystem regex. |

## Unresolved boundaries
| boundary_id | source_file | subsystem | reason |
| --- | --- | --- | --- |
| boundary_01_mx_2_00001 | data/svg/QCELL_PARASITIC.drawio.svg | Unknown | Boundary label is not one of QM/Jumper/QVB/QINFRA. |
| boundary_01_mx_4_00004 | data/svg/QCELL_PARASITIC.drawio.svg | Unknown | Boundary label is not one of QM/Jumper/QVB/QINFRA. |
| boundary_02_00001 | data/svg/pressure_diagnostic_v0_6_2.svg | Unknown | Boundary/scope label not directly associated. |
| boundary_02_00002 | data/svg/pressure_diagnostic_v0_6_2.svg | Unknown | Boundary/scope label not directly associated. |
| boundary_04_00001 | data/svg/temperature_analysis_v0_6_2.svg | Unknown | Boundary/scope label not directly associated. |
| boundary_04_00002 | data/svg/temperature_analysis_v0_6_2.svg | Unknown | Boundary/scope label not directly associated. |
