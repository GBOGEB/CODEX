# W003 Arrow Direction Validation

## Actual input files found

- `data/svg/PFD-PID MINERVA QCELL-LB.svg` — missing; size=None
- `data/svg/PFD-PID MINERVA RFCELL seen by ACR.svg` — missing; size=None
- `data/ppt/PFD-PID of RFCELL - MASTER.pptx` — missing; size=None
- `data/ppt/PID MINERVA CryoCell (QCELL-LB).pptx` — missing; size=None
- `data/ppt/QSYS (and RFCELL) instrumentation location for LB and LBI.pptx` — missing; size=None

## Inkscape bridge

- Bridge manifest: `data/model/inkscape_bridge_manifest.json`
- Inkscape defaults/fabric are inventoried from an operator-supplied source tree or zip when provided; parser execution keeps SVG XML as source.

## SVG load status

- No SVG inputs loaded.

## Counts

- Colour bins detected: 0
- Path/line counts per colour: {"blue_A": 0, "cyan_B_2K": 0, "green_W_coupler": 0, "grey_V_vent": 0, "olive_S_line": 0, "red_orange_D_E": 0, "unknown_black_or_other": 0}
- Arrow counts per colour: {}
- Tag counts: 0 total; 0 unresolved
- Subsystem counts: 0 populated subsystem bin(s)
- Boundary counts: 0
- Unresolved arrows: 0
- Unresolved colours: 0
- Unresolved tags: 0

## Confidence notes

- Semantic correctness is not claimed without colour/process, arrow geometry, tag text, or boundary/scope evidence.
- Uncertain arrow association is marked unresolved rather than inferred.

## Known gaps

- Expected SVG source files are not present in `data/svg/`; generated models are empty preparation artifacts.
