# CODE PURPLE handover verification

This handover is version-controlled reference material. It is not a native telemetry producer or merge authorization.

From this directory run:

```sh
python -m unittest -v test_temporal_matrix.py
python -m py_compile temporal_matrix.py test_temporal_matrix.py
python -m json.tool STATE.json > /dev/null
python -m json.tool MANIFEST.json > /dev/null
```

The reference suite has 18 tests. Required CI, compatible measurement scope, source SHA, upstream owner and independent reviewer evidence must each be verified on a current commit before acceptance.

The N-vector reference does not replace ABACUS #1962, gg_MATH or the native CODEX recovery owner. Historical Ruff 11-to-2 remains an earlier revision; the matched four-file 11-to-0 comparison is the later verified observation from ABACUS run 38590675476.

The earlier recovery ZIP manifest named a missing DROPIN_DELTA.md and did not enumerate the new live receipt. This Git tree instead carries an explicit path inventory in MANIFEST.json. The separately referenced HANDOVER_V2.zip has not been copied or independently compared file-for-file in this migration.
