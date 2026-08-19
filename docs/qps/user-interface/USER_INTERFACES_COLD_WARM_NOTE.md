# USER Interfaces — Cold and Warm Piping Descriptive Note

> **Governance status:** SSOT derivative, supplementary, descriptive, and user-facing. The CONTRACT remains the authoritative single source of truth (SSOT). This note is intended to be fixed/locked scientific configuration once reviewed, with ADR traceability.

## 1. Purpose

This note describes the USER interfaces between the Cryogenic Users / QCELLs and the QPLANT. It consolidates the cold and warm piping interface hierarchy, terminal-point philosophy, contract-relevant figures and tables, route length basis, tap-off logic, and internal surface-area calculations.

The USER side is represented by the QCELLs, connected through the QDB, QVB and QM jumper interfaces. The QPLANT side is represented by the QRB / Cold Box Station, which provides or receives helium process services.

## 2. Interface Hierarchy and Terminal Points

Each interface Terminal Point has two functional sides:

| Terminal Point Side | Role                 | System       | Description                                            |
| ------------------- | -------------------- | ------------ | ------------------------------------------------------ |
| TP1                 | Requestor of service | USER / QCELL | QCELL interface via QDB, QVB, QM and jumper connection |
| TP2                 | Provider of service  | QPLANT / QRB | QPLANT interface via QRB / Cold Box Station            |

The TP defines the mechanical, process, operational, commissioning and responsibility boundary between the USER and the QPLANT.

## 3. Contract Figures and Tables Applicable to USER Interfaces

| Contract item                                 | Applicability                                      | Interface relevance                                                             |
| --------------------------------------------- | -------------------------------------------------- | ------------------------------------------------------------------------------- |
| Figure 1 — Overall layout of Cryogenic System | QPS, QPLANT, QRB, QDB, QVB, QCELL relationship     | Shows how QPLANT connects to QDB and the 30 QCELLs                              |
| Figure 2 — Buildings related to QPS           | Compressor room, storage area, cold box room, LTU  | Shows physical routing context for QRB, QLM and warm lines                      |
| Figure 3 — Single QCELL representation        | A, B, D, E and W line connections                  | Shows functional cold and warm process connections to one QCELL                 |
| Table 1 — Helium process lines                | Defines A, B, D, E, U, W, S, G10, G20, HP, LP, VLP | Defines line names, functions and whether they form part of the cryogenic cycle |
| Figure 10 — QLM at QRB–QLM connection         | Cold interface geometry                            | Gives indicative cold header sizes: A ~30 mm, B ~150 mm, D ~50 mm, E ~50 mm     |
| Section 4.5.2 — Warm Piping System            | WPS interface definition                           | Defines warm headers U, W and S and their user-side interface sizes             |

## 4. Cold USER Interfaces

| Line | Type | Function        | Indicative size |
| ---- | ---- | --------------- | --------------- |
| A    | Cold | SHe supply line | ~30 mm          |
| B    | Cold | VLP return line | ~150 mm         |
| D    | Cold | TS supply line  | ~50 mm          |
| E    | Cold | TS return line  | ~50 mm          |

The cold interface shall maintain continuity of the process pipes, thermal shield, multilayer insulation and vacuum jacket across the QRB–QLM connection.

## 5. Warm USER Interfaces

| Line | Type | Function                                                        | User-side interface |
| ---- | ---- | --------------------------------------------------------------- | ------------------- |
| U    | Warm | Warm GHe supply for purge, conditioning and auxiliary operation | DN25, CF40          |
| W    | Warm | Warm GHe recovery return from Cryogenic Users                   | DN40, CF63          |
| S    | Warm | Safety recovery return from relief / abnormal discharge paths   | DN150, CF160        |

## 6. Length and Tap-Off Basis

| Parameter                          |   Value |
| ---------------------------------- | ------: |
| Total process line length per line | 151.5 m |
| Number of primary process pipes    |       7 |
| Cold pipes                         |       4 |
| Warm pipes                         |       3 |
| Final QCELL tap-off region         |  91.5 m |
| First tap offset                   |   1.5 m |
| Regular QCELL spacing              |   3.0 m |
| Number of QCELL taps               |      30 |

Tap-off logic:

* First QCELL tap starts at 1.5 m.
* Subsequent taps repeat every 3.0 m.
* For 30 QCELLs: final tap position = 1.5 + 29 × 3.0 = 88.5 m.
* Remaining allowance in the 91.5 m region = 3.0 m.

## 7. Internal Surface Area Calculation

Formula:

`A = π × Di × L`

| Line | Type                 | Diameter used |  Length | Internal surface area |
| ---- | -------------------- | ------------: | ------: | --------------------: |
| A    | Cold SHe supply      |         30 mm | 151.5 m |              14.28 m² |
| B    | Cold VLP return      |        150 mm | 151.5 m |              71.39 m² |
| D    | Cold TS supply       |         50 mm | 151.5 m |              23.80 m² |
| E    | Cold TS return       |         50 mm | 151.5 m |              23.80 m² |
| U    | Warm supply          |         25 mm | 151.5 m |              11.90 m² |
| W    | Warm recovery        |         40 mm | 151.5 m |              19.04 m² |
| S    | Warm safety recovery |        150 mm | 151.5 m |              71.39 m² |

Total internal surface area for all seven lines: **235.60 m²**

## 8. Structured Data Sources

The numerical line data used by this note are also maintained as reusable structured artefacts for future calculation pipelines:

* [`data/user_interface_lines.yaml`](data/user_interface_lines.yaml)
* [`data/user_interface_lines.json`](data/user_interface_lines.json)

The data files preserve line identifiers, line family, functions, diameters, lengths, calculated internal surface areas, source basis, and SSOT-derivative status.
