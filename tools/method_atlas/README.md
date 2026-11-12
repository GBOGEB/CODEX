# Method Atlas v3

`build_method_atlas.py` builds `docs/method_atlas/` (`method_atlas.json`, `index.html`
and `method_atlas.mmd`) from `method_atlas_seed.yaml` and the tracked files of every
repository the seed declares. CODEX is the host. ABACUS and HUB are read from sibling
checkouts (`../ABACUS` and `../mc-integration`, or `--repo ID=PATH`).

| Command | Where | What it checks |
|---|---|---|
| `python tools/method_atlas/build_method_atlas.py --write` | local | Regenerates the three outputs |
| `python tools/method_atlas/build_method_atlas.py --check` | local only | Exits 1 when a rebuild would change the outputs; writes nothing |
| `python tools/method_atlas/build_method_atlas.py --verify-projection` | CI (`ci.yml`, step `method_atlas`) | Exits 1 when `docs/method_atlas/` was hand-edited |

## Why `--check` is local-only

The atlas records each sibling's HEAD SHA, tree OID and dirty-file count, and the host's
tracked-file count. A single-repo CI checkout has no siblings, and the host count changes
with every commit, so `--check` would report drift on every CI run. The committed atlas is a
snapshot of the workstation federation at the time of the last `--write`.

`--verify-projection` needs no sibling and no git history. It checks that
`method_atlas.json` still matches its own `digest`, and that `index.html` and
`method_atlas.mmd` re-render byte-exact from that JSON and the seed. A hand edit to any of
the three files fails the CI step. To change the atlas, edit the seed, the template or the
builder and run `--write` locally with the siblings present. A template change, or a seed
change to the spine or lanes, also fails the step until `--write` is run. Other seed changes
are caught only by a local `--check`.
