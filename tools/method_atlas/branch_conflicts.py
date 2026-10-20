"""Branch radar and merge-conflict helper for local checkouts (read-only).

    python tools/method_atlas/branch_conflicts.py radar [--path REPO ...] [--days 14] [--base origin/main] [--fetch]
    python tools/method_atlas/branch_conflicts.py audit --path REPO --branch BRANCH [--base origin/main]

radar   For each checkout (default: the Method Atlas seed repos), lists recently
        committed local branches, whether each merges cleanly with the base
        (`git merge-tree --write-tree`, nothing is checked out or written to the
        repo), any rebase in progress, and classifies every conflicting file with
        the seed's conflict playbook. Writes a page of PowerShell commands tailored
        to each repo/branch/file (default artifacts/method_atlas/branches.html).
audit   For a branch rebased locally but not pushed: proves file by file that the
        rebased branch keeps everything the remote branch had, except where the
        base (main) has a newer version. Exit 0 LOSSLESS, 2 REVIEW (hand-combined files), 1 LOSS (a branch change is gone).

Branch state changes minute to minute, so this report is never part of the
canonical atlas or its --check.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
import time
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SEED = ROOT / "tools/method_atlas/method_atlas_seed.yaml"
OUT = ROOT / "artifacts/method_atlas/branches.html"


def git(repo: Path, *args: str, check: bool = True) -> str:
    proc = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    if check and proc.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {proc.stderr.strip()}")
    return proc.stdout


def rev(repo: Path, ref: str) -> str | None:
    out = git(repo, "rev-parse", "-q", "--verify", f"{ref}^{{commit}}", check=False).strip()
    return out or None


def blob(repo: Path, ref: str, path: str) -> str | None:
    out = git(repo, "rev-parse", "-q", "--verify", f"{ref}:{path}", check=False).strip()
    return out or None


def count(repo: Path, rng: str) -> int:
    return int(git(repo, "rev-list", "--count", rng).strip() or 0)


# ---------------------------------------------------------------- playbook

def load_playbook(seed_path: Path = SEED) -> dict:
    return yaml.safe_load(seed_path.read_text(encoding="utf-8"))["conflicts"]


def classify(path: str, playbook: dict) -> dict:
    for cls in playbook["classes"]:
        if any(re.search(p, path) for p in cls["match"]):
            return cls
    return playbook["classes"][-1]


def fill(template: str, **values: str) -> str:
    """Replace {name} placeholders by value; other braces (e.g. @{1}) are left alone."""
    for k, v in values.items():
        template = template.replace("{" + k + "}", v)
    return template


# ---------------------------------------------------------------- analysis

def merge_conflicts(repo: Path, base: str, branch: str) -> list[str]:
    proc = subprocess.run(["git", "-C", str(repo), "merge-tree", "--write-tree", "--name-only", "--no-messages",
                           base, branch], capture_output=True, text=True, encoding="utf-8", errors="replace")
    if proc.returncode == 0:
        return []
    lines = [l for l in proc.stdout.splitlines()[1:] if l.strip()]
    return sorted(set(lines))


def rebase_state(repo: Path, playbook: dict, base: str) -> dict | None:
    gd = Path(git(repo, "rev-parse", "--absolute-git-dir").strip())
    rm = gd / "rebase-merge"
    if not rm.is_dir():
        return None
    read = lambda name: (rm / name).read_text(encoding="utf-8").strip() if (rm / name).exists() else ""
    stopped = read("stopped-sha")
    todo = [l for l in read("git-rebase-todo").splitlines() if l and not l.startswith("#")]
    files = sorted(p for p in git(repo, "diff", "--name-only", "--diff-filter=U").splitlines() if p)
    return {"branch": read("head-name").replace("refs/heads/", ""), "onto": read("onto")[:12],
            "stopped": stopped[:12], "stopped_subject": git(repo, "log", "-1", "--format=%s", stopped, check=False).strip() if stopped else "",
            "done": len(read("done").splitlines()), "todo": len(todo),
            "conflicts": [{"file": f, "class": classify(f, playbook)["id"]} for f in files]}


def audit(repo: Path, branch: str, base: str) -> dict:
    """Does local <branch> keep everything origin/<branch> had (except where base is newer)?"""
    remote = f"origin/{branch}"
    if not rev(repo, remote):
        return {"status": "NO_REMOTE", "files": []}
    mb = git(repo, "merge-base", base, remote).strip()
    files = sorted(p for p in git(repo, "diff", "--name-only", mb, remote).splitlines() if p)
    out = []
    for f in files:
        r, l, b, m = blob(repo, remote, f), blob(repo, branch, f), blob(repo, base, f), blob(repo, mb, f)
        if r == l:
            kind = "SAME"
        elif l == b and git(repo, "log", "-1", "--format=%h", f"{mb}..{base}", "--", f).strip():
            kind = "BASE_NEWER"  # main changed it later; main's version wins
        elif l == m:
            kind = "LOST"  # the branch's change to this file is gone
        else:
            kind = "COMBINED"  # differs from both sides: a hand-resolved or merged result to review
        out.append({"file": f, "result": kind})
    lost = [x["file"] for x in out if x["result"] == "LOST"]
    combined = [x["file"] for x in out if x["result"] == "COMBINED"]
    status = "LOSS" if lost else "REVIEW" if combined else "LOSSLESS"
    return {"status": status, "remote": remote, "merge_base": mb[:12], "files": out,
            "lost": lost, "combined": combined, "differs": lost + combined,
            "counts": {k: sum(x["result"] == k for x in out) for k in ("SAME", "BASE_NEWER", "COMBINED", "LOST")}}


def scan_repo(repo: Path, base: str, days: int, playbook: dict, fetch: bool) -> dict:
    if fetch:
        git(repo, "fetch", "-q", "origin", check=False)
    base_sha = rev(repo, base)
    info = {"path": str(repo), "base": base, "base_sha": (base_sha or "")[:12],
            "origin": git(repo, "remote", "get-url", "origin", check=False).strip(),
            "rebase": rebase_state(repo, playbook, base) if base_sha else None, "branches": []}
    if not base_sha:
        info["error"] = f"base {base} not found (fetch first)"
        return info
    cutoff = time.time() - days * 86400
    refs = git(repo, "for-each-ref", "--format=%(refname:short)%09%(committerdate:unix)%09%(objectname)", "refs/heads").splitlines()
    for line in refs:
        name, ts, sha = line.split("\t")
        if int(ts) < cutoff:
            continue
        up = rev(repo, f"origin/{name}")
        tracked_cfg = git(repo, "config", "--get", f"branch.{name}.merge", check=False).strip()
        b = {"name": name, "sha": sha[:12], "age_days": round((time.time() - int(ts)) / 86400, 1),
             "ahead_base": count(repo, f"{base}..{name}"), "behind_base": count(repo, f"{name}..{base}"),
             "upstream": bool(up)}
        if up:
            b["ahead_upstream"] = count(repo, f"origin/{name}..{name}")
            b["behind_upstream"] = count(repo, f"{name}..origin/{name}")
            b["remote_conflicts"] = merge_conflicts(repo, base, f"origin/{name}") if up != sha else None
        conflicts = merge_conflicts(repo, base, name)
        b["conflicts"] = [{"file": f, "class": classify(f, playbook)["id"]} for f in conflicts]
        if base.split("/", 1)[-1] == name:
            state = "BASE_LOCAL_AHEAD" if b["ahead_base"] else "BASE_LOCAL"
            b["stray_commits"] = git(repo, "log", "--format=%h %s", f"{base}..{name}").splitlines()[:10]
        elif b["ahead_base"] == 0:
            state = "MERGED_OR_EMPTY"
        elif conflicts:
            state = "CONFLICT"
        elif up and up != sha and b["behind_upstream"] > 0:
            state = "DIVERGED_NOT_PUSHED"  # rebased (or otherwise rewritten) locally
            b["audit"] = audit(repo, name, base)
        elif up and up != sha:
            state = "AHEAD_NOT_PUSHED"
        elif not up and tracked_cfg:
            state = "NO_TRACKING_REF"  # has an upstream, but this clone does not fetch that branch
        elif not up:
            state = "LOCAL_ONLY"
        else:
            state = "CLEAN"
        b["state"] = state
        info["branches"].append(b)
    order = ["CONFLICT", "DIVERGED_NOT_PUSHED", "BASE_LOCAL_AHEAD", "AHEAD_NOT_PUSHED", "NO_TRACKING_REF", "LOCAL_ONLY", "CLEAN", "MERGED_OR_EMPTY", "BASE_LOCAL"]
    info["branches"].sort(key=lambda x: (order.index(x["state"]), x["age_days"]))
    return info


# ---------------------------------------------------------------- report

def commands_for(repo: dict, branch: dict | None, playbook: dict) -> list[dict]:
    """Ordered PowerShell command blocks tailored to one branch (or the in-progress rebase)."""
    by_id = {c["id"]: c for c in playbook["classes"]}
    recipes = {r["id"]: r for r in playbook["recipes"]}
    vals = {"repo": repo["path"], "base": repo["base"], "atlas": str(ROOT), "branch": (branch or {}).get("name", "<branch>")}
    blocks = []
    if branch and branch["state"] == "CONFLICT":
        blocks.append({"title": "Rebase onto the current base (drops commits already upstream)",
                       "lines": [fill(c, **vals) for c in recipes["already_merged"]["commands"]]})
    if branch and branch["state"] == "BASE_LOCAL_AHEAD":
        blocks.append({"title": "Move stray commits off the local base branch (switch away from it first)",
                       "lines": [f"git -C '{vals['repo']}' branch <feature-branch> {branch['name']}   # or: git branch -f <existing-branch> {branch['name']}",
                                 f"git -C '{vals['repo']}' branch -f {branch['name']} {vals['base']}",
                                 f"git -C '{vals['repo']}' push -u origin <feature-branch>"]})
    if branch and branch["state"] == "NO_TRACKING_REF":
        blocks.append({"title": "Fetch this branch's remote ref (the clone only fetches the base)",
                       "lines": [f"git -C '{vals['repo']}' fetch origin {branch['name']}:refs/remotes/origin/{branch['name']}",
                                 f"git -C '{vals['repo']}' status -sb"]})
    if branch and branch["state"] in ("DIVERGED_NOT_PUSHED", "AHEAD_NOT_PUSHED"):
        blocks.append({"title": recipes["verify_then_publish"]["label"],
                       "lines": [fill(c, **vals) for c in recipes["verify_then_publish"]["commands"]]})
    files = (branch or {}).get("conflicts") if branch else (repo.get("rebase") or {}).get("conflicts", [])
    for item in files or []:
        cls = by_id[item["class"]]
        v = dict(vals, file=item["file"], stem=Path(item["file"]).stem)
        blocks.append({"title": f"{item['file']} ({cls['label']}: {cls['resolution']})", "why": cls["why"],
                       "lines": [fill(c, **v) for c in cls["commands"]]})
    return blocks


PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Branch Radar</title><style>
:root{--bg:#f6f7f9;--panel:#fff;--ink:#17202a;--muted:#5d6b7a;--line:#d9dee5;--ok:#1f8a4c;--warn:#a86b00;--bad:#b8322a;--code:#f0f2f5}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0f141a;--panel:#161d25;--ink:#e6edf3;--muted:#94a3b3;--line:#2a3542;--ok:#4cc38a;--warn:#e0a63a;--bad:#f0756a;--code:#0b1016}}
:root[data-theme="dark"]{--bg:#0f141a;--panel:#161d25;--ink:#e6edf3;--muted:#94a3b3;--line:#2a3542;--ok:#4cc38a;--warn:#e0a63a;--bad:#f0756a;--code:#0b1016}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.45 system-ui,"Segoe UI",Roboto,sans-serif}
main{max-width:1200px;margin:0 auto;padding:16px}h1{font-size:22px;margin:0 0 4px}h2{font-size:17px;margin:22px 0 6px}h3{font-size:14px;margin:12px 0 4px}
.sub{color:var(--muted);font-size:13px}.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:12px;margin:10px 0}
.badge{display:inline-block;padding:1px 7px;border-radius:5px;font-size:11px;font-weight:600;border:1px solid currentColor}
.CONFLICT{color:var(--bad)}.DIVERGED_NOT_PUSHED,.AHEAD_NOT_PUSHED,.REVIEW,.BASE_LOCAL_AHEAD,.NO_TRACKING_REF{color:var(--warn)}.LOSS{color:var(--bad)}.CLEAN,.MERGED_OR_EMPTY,.LOSSLESS{color:var(--ok)}.LOCAL_ONLY{color:var(--muted)}
table{border-collapse:collapse;width:100%;font-size:13px}th,td{text-align:left;padding:5px 7px;border-bottom:1px solid var(--line);vertical-align:top}
.wrap{overflow-x:auto}pre{position:relative;background:var(--code);border:1px solid var(--line);border-radius:8px;padding:10px 12px;overflow-x:auto;font:12px/1.5 ui-monospace,Consolas,monospace;margin:6px 0}
pre button{position:absolute;top:6px;right:6px;font:11px system-ui;border:1px solid var(--line);background:var(--panel);color:var(--ink);border-radius:5px;padding:2px 7px;cursor:pointer}
code{font-family:ui-monospace,Consolas,monospace;font-size:12px;overflow-wrap:anywhere}details{margin:6px 0}summary{cursor:pointer}
</style></head><body><main>
<h1>Branch Radar</h1><div class="sub">Read-only scan of local branches against the base. Generated {generated} by <code>tools/method_atlas/branch_conflicts.py</code>; re-run it after every fetch, rebase or push. Commands are PowerShell; review before running.</div>
<div class="card sub"><b>ours / theirs:</b> {note}</div>
{body}
</main><script>
document.querySelectorAll('pre').forEach(p=>{const b=document.createElement('button');b.type='button';b.textContent='Copy';b.onclick=async()=>{try{await navigator.clipboard.writeText(p.querySelector('code').innerText);b.textContent='Copied'}catch(e){b.textContent='Select + Ctrl+C'}setTimeout(()=>b.textContent='Copy',1500)};p.appendChild(b)});
</script></body></html>
"""


def _pre(lines: list[str]) -> str:
    return f"<pre><code>{html.escape(chr(10).join(lines))}</code></pre>"


def render(report: dict, playbook: dict) -> str:
    e = html.escape
    parts = []
    for repo in report["repos"]:
        parts.append(f"<h2>{e(repo['path'])}</h2><div class='sub'>origin {e(repo['origin'])} · base <code>{e(repo['base'])}</code> @ {e(repo['base_sha'])}</div>")
        if repo.get("error"):
            parts.append(f"<div class='card CONFLICT'>{e(repo['error'])}</div>")
            continue
        rb = repo.get("rebase")
        if rb:
            parts.append(f"<div class='card'><h3><span class='badge CONFLICT'>REBASE IN PROGRESS</span> {e(rb['branch'])}</h3>"
                         f"<div class='sub'>stopped at <code>{e(rb['stopped'])}</code> {e(rb['stopped_subject'])} · {rb['done']} done, {rb['todo']} to go · onto {e(rb['onto'])}</div>"
                         + ("".join(f"<h3>{e(b['title'])}</h3><div class='sub'>{e(b.get('why', ''))}</div>{_pre(b['lines'])}"
                                    for b in commands_for(repo, None, playbook)) or "<p class='sub'>No conflicted files: continue the rebase.</p>")
                         + _pre([fill(c, repo=repo["path"]) for c in next(r for r in playbook["recipes"] if r["id"] == "stuck_prompt")["commands"]])
                         + "</div>")
        rows = "".join(
            f"<tr><td><code>{e(b['name'])}</code></td><td><span class='badge {b['state']}'>{b['state']}</span></td>"
            f"<td>{b['ahead_base']} / {b['behind_base']}</td><td>{'yes' if b['upstream'] else 'no'}"
            f"{'' if not b['upstream'] else ' (' + str(b.get('ahead_upstream', 0)) + ' / ' + str(b.get('behind_upstream', 0)) + ')'}</td>"
            f"<td>{len(b['conflicts'])}</td><td>{'' if b.get('remote_conflicts') is None else len(b['remote_conflicts'])}</td><td>{b['age_days']} d</td></tr>"
            for b in repo["branches"])
        parts.append("<div class='wrap card'><table><thead><tr><th>Branch</th><th>State</th><th>Ahead / behind base</th><th>Upstream (ahead / behind)</th>"
                     f"<th>Local conflicts</th><th>Remote (PR) conflicts</th><th>Last commit</th></tr></thead><tbody>{rows}</tbody></table></div>")
        for b in repo["branches"]:
            if b["state"] not in ("CONFLICT", "DIVERGED_NOT_PUSHED", "AHEAD_NOT_PUSHED", "BASE_LOCAL_AHEAD", "NO_TRACKING_REF"):
                continue
            body = f"<div class='card'><h3><code>{e(b['name'])}</code> <span class='badge {b['state']}'>{b['state']}</span></h3>"
            if b.get("remote_conflicts"):
                body += f"<div class='sub'>The PR branch on GitHub conflicts with the base in {len(b['remote_conflicts'])} file(s): " + ", ".join(f"<code>{e(f)}</code>" for f in b["remote_conflicts"][:12]) + "</div>"
            a = b.get("audit")
            if a:
                body += (f"<div class='sub'>Nothing-lost audit vs <code>{e(a.get('remote', ''))}</code>: <span class='badge {a['status']}'>{a['status']}</span> "
                         + " · ".join(f"{k} {v}" for k, v in a.get("counts", {}).items()) + "</div>")
                for key, label in (("lost", "LOST: the branch's change is gone"), ("combined", "COMBINED: hand-resolved or merged, review")):
                    if a.get(key):
                        body += f"<details><summary>{label} ({len(a[key])})</summary>" + "".join(f"<div><code>{e(f)}</code></div>" for f in a[key]) + "</details>"
            if b.get("stray_commits"):
                body += ("<div class='sub'>Local base branch has commits that are not on the remote base. If they belong to a feature branch, move them there:</div>"
                         + "".join(f"<div><code>{e(c)}</code></div>" for c in b["stray_commits"]))
            for blk in commands_for(repo, b, playbook):
                body += f"<h3>{e(blk['title'])}</h3>" + (f"<div class='sub'>{e(blk['why'])}</div>" if blk.get("why") else "") + _pre(blk["lines"])
            parts.append(body + "</div>")
    return (PAGE.replace("{generated}", e(report["generated"])).replace("{note}", e(playbook["ours_theirs_note"]))
            .replace("{body}", "".join(parts)))


def default_paths() -> list[Path]:
    seed = yaml.safe_load(SEED.read_text(encoding="utf-8"))
    return [(ROOT / r["path"]).resolve() for r in seed["repos"]]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd")
    r = sub.add_parser("radar")
    r.add_argument("--path", action="append", type=Path)
    r.add_argument("--days", type=int, default=14)
    r.add_argument("--base", default="origin/main")
    r.add_argument("--fetch", action="store_true", help="git fetch origin first (network)")
    r.add_argument("--out", type=Path, default=OUT)
    a = sub.add_parser("audit")
    a.add_argument("--path", type=Path, required=True)
    a.add_argument("--branch", required=True)
    a.add_argument("--base", default="origin/main")
    args = ap.parse_args(argv)
    playbook = load_playbook()
    if args.cmd == "audit":
        result = audit(args.path, args.branch, args.base)
        print(json.dumps({k: v for k, v in result.items() if k != "files"}, indent=1))
        return {"LOSSLESS": 0, "REVIEW": 2}.get(result["status"], 1)
    args.cmd = "radar"
    paths = getattr(args, "path", None) or default_paths()
    report = {"generated": time.strftime("%Y-%m-%d %H:%M:%S"),
              "repos": [scan_repo(p.resolve(), getattr(args, "base", "origin/main"), getattr(args, "days", 14), playbook,
                                  getattr(args, "fetch", False)) for p in paths]}
    out = getattr(args, "out", OUT)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render(report, playbook))
    with open(out.with_suffix(".json"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(report, indent=1) + "\n")
    summary = {p["path"]: {s: sum(b["state"] == s for b in p["branches"]) for s in
                           ("CONFLICT", "DIVERGED_NOT_PUSHED", "AHEAD_NOT_PUSHED", "BASE_LOCAL_AHEAD", "NO_TRACKING_REF", "LOCAL_ONLY", "CLEAN", "MERGED_OR_EMPTY")}
               | {"rebase_in_progress": bool(p.get("rebase"))} for p in report["repos"]}
    print(json.dumps({"out": str(out), "repos": summary}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
