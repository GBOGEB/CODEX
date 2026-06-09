# W003 Semantic Layer Validation

## Actual input files found
| path | kind | size_bytes |
| --- | --- | --- |
| No required real input files found | n/a | 0 |

## SVG load status
| path | status | error |
| --- | --- | --- |
| data/svg/PFD-PID MINERVA QCELL-LB.svg | missing |  |
| data/svg/PFD-PID MINERVA RFCELL seen by ACR.svg | missing |  |

## Colour bins detected
| colour_bin | path_line_count |
| --- | --- |
| none | 0 |

## Arrow counts per colour
| colour_bin | arrow_count |
| --- | --- |
| none | 0 |

## Tag counts
| tag_class | count |
| --- | --- |
| none | 0 |

## Subsystem counts
| subsystem | count |
| --- | --- |
| none | 0 |

## Boundary counts
- Boundaries detected: 0

## Unresolved counts
- Unresolved arrows: 0
- Unresolved colours: 0
- Unresolved tags: 0

## Confidence notes
- Colour/process mappings are bin-level hypotheses from SVG stroke colour only.
- Arrow direction is only inferred for SVG marker evidence with available endpoints; geometric arrow-head candidates remain unresolved.
- Subsystem assignment requires visible text evidence or a conservative nearest-label association.

## Known gaps
- PPTX inputs are inventoried for traceability but not parsed in this W003 preparation step.
- Valve/equipment symbol classification remains conservative until symbol templates are supplied.
- If the real SVG files are absent, generated models intentionally contain no inferred process semantics.

## Semantic layers
| layer_id | label | count |
| --- | --- | --- |
| full_drawing | full drawing | 0 |
| colour_process_lines | colour/process lines | 0 |
| blue_A | A / A′ 4.5 K line | 0 |
| cyan_B_2K | B / B′ 2 K line | 0 |
| green_W_coupler | W coupler line | 0 |
| olive_S_line | S line | 0 |
| grey_V_vent | V vent line | 0 |
| red_orange_D_E | D/E manifold lines | 0 |
| unknown_black_or_other | unknown/black/structure | 0 |
| instruments_only | instruments only | 0 |
| valves_only | valves only | 0 |
| equipment_only | equipment only | 0 |
| boundaries_only | boundaries only | 0 |
| vacuum_barrier | vacuum barrier | 0 |
| qm_section | QM section | 0 |
| jumper_section | Jumper section | 0 |
| qvb_section | QVB section | 0 |
| qinfra_interface_section | QINFRA/interface section | 0 |
| arrows_flow_direction | arrows / flow direction only | 0 |
| unresolved_items | unresolved items | 0 |
