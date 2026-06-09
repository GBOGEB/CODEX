#!/usr/bin/env python3
"""Acquire P&ID source archives and build conservative SVG semantic models."""
from __future__ import annotations

import argparse, json, math, re, shutil, urllib.error, urllib.request, zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_DIR = ROOT / "Input/source_archives"
DATA_DIRS = {".svg": ROOT / "data/svg", ".pdf": ROOT / "data/pdf", ".ppt": ROOT / "data/ppt", ".pptx": ROOT / "data/ppt"}
MODEL_DIR, LINES_DIR, REPORTS_DIR = ROOT / "data/model", ROOT / "data/model/lines", ROOT / "reports"
VIEWER_DIR, PUBLISH_DIR = ROOT / "viewer", ROOT / "publish"
SOURCES = [
    ("Inkscape_full.zip", "https://github.com/GBOGEB/github_documentorganisatiesysteem_GBOGEB/raw/master/Inkscape_full.zip"),
    ("PFD-PID MINERVA QCELL-LB.zip", "https://github.com/GBOGEB/github_documentorganisatiesysteem_GBOGEB/raw/master/PFD-PID%20MINERVA%20QCELL-LB.zip"),
]
SUBSYSTEMS = ["QM", "Jumper", "QVB", "QINFRA", "Unknown"]
BIN_FILES = {
    "blue_A": "blue_A.json", "cyan_B_2K": "cyan_B_2K.json", "green_W_coupler": "green_W_coupler.json",
    "grey_V_vent": "grey_V_vent.json", "olive_S_line": "olive_S_line.json", "red_orange_D_E": "red_orange_D_E.json",
    "black_structure_unknown": "unknown_black_or_other.json", "unknown_black_or_other": "unknown_black_or_other.json",
}
NS = re.compile(r"^\{.*\}"); NUM = re.compile(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?")
STYLE = re.compile(r"\s*;\s*"); TRANS = re.compile(r"translate\(([-+]?\d*\.?\d+)(?:[,\s]+([-+]?\d*\.?\d+))?")
TAG = re.compile(r"\b(?:[A-Z]{1,8}[-_ ]?)?\d{2,}[A-Z0-9_.-]*\b|\b(?:QM|QVB|QINFRA|JUMPER|RFCELL|QCELL|ACR)\b", re.I)
VALVE = re.compile(r"\b(?:V|HV|CV|XV|PV|SV|MOV|EV)[-_ ]?\d+", re.I)
INSTR = re.compile(r"\b(?:TT|TE|PT|PI|PIC|FT|FI|FIC|LT|LI|LIT|TS|PS|LS|PDT|AIT)[-_ ]?\d+", re.I)
EQUIP = re.compile(r"\b(?:HX|PUMP|COMP|DEWAR|VESSEL|TANK|CELL|QVB|QM|JUMPER|RFCELL|QCELL)\b", re.I)


def rel(p: Path) -> str:
    try: return str(p.relative_to(ROOT))
    except ValueError: return str(p)

def strip(t: str) -> str: return NS.sub("", t)

def style(s: str | None) -> dict[str, str]:
    out = {}
    for part in STYLE.split((s or "").strip()):
        if ":" in part:
            k, v = part.split(":", 1); out[k.strip().lower()] = v.strip()
    return out

def attr(e: ET.Element, name: str) -> str | None: return e.attrib.get(name) or style(e.attrib.get("style")).get(name)

def colour(v: str | None) -> str:
    if not v: return "none"
    v = v.strip().lower(); names = {"black":"#000000","white":"#ffffff","blue":"#0000ff","cyan":"#00ffff","aqua":"#00ffff","green":"#008000","grey":"#808080","gray":"#808080","olive":"#808000","red":"#ff0000","orange":"#ffa500","none":"none"}
    if v in names: return names[v]
    if v.startswith("#"):
        return "#" + "".join(c*2 for c in v[1:]) if len(v) == 4 else v[:7]
    m = re.match(r"rgba?\(([^)]+)\)", v)
    if m:
        vals = [float(x.strip().rstrip("%")) for x in m.group(1).split(",")[:3]]
        if "%" in m.group(1): vals = [x*2.55 for x in vals]
        return "#" + "".join(f"{max(0,min(255,round(x))):02x}" for x in vals)
    return v

def rgb(c: str):
    return (int(c[1:3],16), int(c[3:5],16), int(c[5:7],16)) if re.match(r"^#[0-9a-f]{6}$", c) else None

def bin_colour(c: str):
    r = rgb(colour(c))
    if not r: return "unknown_black_or_other", "unknown/other", .2
    red, green, blue = r
    if red < 45 and green < 45 and blue < 45: return "black_structure_unknown", "structure/unknown", .55
    if blue > 120 and red < 120 and green < 170: return "blue_A", "A / A′", .78
    if blue > 130 and green > 130 and red < 120: return "cyan_B_2K", "B / B′", .78
    if green > 100 and red < 120 and blue < 130: return "green_W_coupler", "W", .72
    if abs(red-green) < 25 and abs(green-blue) < 25 and 70 <= red <= 210: return "grey_V_vent", "V", .68
    if red > 80 and green > 80 and blue < 100 and abs(red-green) < 80: return "olive_S_line", "S", .68
    if red > 150 and green < 180 and blue < 130: return "red_orange_D_E", "D/E", .72
    return "unknown_black_or_other", "unknown/other", .35

def nums(v: str | None): return [float(x) for x in NUM.findall(v or "")]

def points(e: ET.Element):
    t = strip(e.tag)
    if t == "line" and all(k in e.attrib for k in ("x1","y1","x2","y2")): return [(float(e.attrib["x1"]),float(e.attrib["y1"])),(float(e.attrib["x2"]),float(e.attrib["y2"]))]
    if t in {"polyline","polygon"}: n = nums(e.attrib.get("points")); return list(zip(n[0::2], n[1::2]))
    if t == "path": n = nums(e.attrib.get("d")); return list(zip(n[0::2], n[1::2]))
    if t == "rect":
        x,y,w,h = map(float, [e.attrib.get("x",0), e.attrib.get("y",0), e.attrib.get("width",0), e.attrib.get("height",0)]); return [(x,y),(x+w,y),(x+w,y+h),(x,y+h)]
    if t in {"circle","ellipse"}:
        cx,cy = float(e.attrib.get("cx",0)), float(e.attrib.get("cy",0)); rx=float(e.attrib.get("r", e.attrib.get("rx",0))); ry=float(e.attrib.get("r", e.attrib.get("ry",0))); return [(cx-rx,cy-ry),(cx+rx,cy+ry)]
    return []

def bbox(ps):
    if not ps: return None
    xs=[p[0] for p in ps]; ys=[p[1] for p in ps]; return {"x_min":min(xs),"y_min":min(ys),"x_max":max(xs),"y_max":max(ys)}

def mid(box): return ((box["x_min"]+box["x_max"])/2, (box["y_min"]+box["y_max"])/2) if box else None

def dist(a,b): return math.hypot(a[0]-b[0], a[1]-b[1])

def subsystem(text: str):
    u=text.upper()
    if "QINFRA" in u or "INTERFACE" in u: return "QINFRA"
    if "JUMPER" in u: return "Jumper"
    if "QVB" in u or "VACUUM" in u: return "QVB"
    if "QM" in u: return "QM"
    return "Unknown"

def tag_class(text: str):
    classes=[]
    if INSTR.search(text): classes.append("instrument")
    if VALVE.search(text): classes.append("valve")
    if EQUIP.search(text): classes.append("equipment")
    if not classes and TAG.search(text): classes.append("tag")
    return (classes[0] if classes else "annotation_or_label"), classes

def locate_local_archive(name: str):
    candidates = [ARCHIVE_DIR / name, ROOT / name, ROOT / "Input" / name]
    candidates.extend(p for p in ROOT.rglob(name) if ".git" not in p.parts and p.is_file())
    for candidate in candidates:
        if candidate.exists() and candidate.stat().st_size:
            return candidate
    return None

def acquire():
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True); out=[]
    for name, url in SOURCES:
        target = ARCHIVE_DIR/name; rec={"archive":name,"url":url,"path":rel(target),"source_status":"configured"}
        local = locate_local_archive(name)
        if local and local != target:
            if target.exists() and target.read_bytes() != local.read_bytes():
                rec.update(status="local_conflict", local_path=rel(local), error="archive exists with different content; not renamed silently")
            else:
                shutil.copy2(local, target); rec.update(status="copied_from_local", local_path=rel(local), size_bytes=target.stat().st_size)
            out.append(rec); continue
        if target.exists() and target.stat().st_size:
            rec.update(status="present", size_bytes=target.stat().st_size); out.append(rec); continue
        try:
            with urllib.request.urlopen(url, timeout=60) as r, target.open("wb") as f: shutil.copyfileobj(r, f)
            rec.update(status="downloaded", size_bytes=target.stat().st_size)
        except (OSError, urllib.error.URLError, TimeoutError) as exc:
            if target.exists() and not target.stat().st_size: target.unlink()
            rec.update(status="download_failed", error=str(exc))
        out.append(rec)
    return out

def extract_archives():
    for d in DATA_DIRS.values(): d.mkdir(parents=True, exist_ok=True)
    rows=[]
    for zp in sorted(ARCHIVE_DIR.glob("*.zip")):
        try: z = zipfile.ZipFile(zp)
        except zipfile.BadZipFile as exc: rows.append({"archive":rel(zp),"status":"bad_zip","error":str(exc)}); continue
        with z:
            for m in z.infolist():
                ext=Path(m.filename).suffix.lower()
                if m.is_dir() or ext not in DATA_DIRS: continue
                dst = DATA_DIRS[ext]/Path(m.filename).name; data=z.read(m); rec={"archive":rel(zp),"member":m.filename,"destination":rel(dst)}
                if dst.exists() and dst.read_bytes()!=data: rec.update(status="conflict_skipped", reason="existing different file; not renamed silently")
                elif dst.exists(): rec.update(status="already_present", size_bytes=dst.stat().st_size)
                else:
                    dst.write_bytes(data)
                    rec.update(status="extracted", size_bytes=dst.stat().st_size)
                rows.append(rec)
    return rows

def inventory():
    for d in DATA_DIRS.values(): d.mkdir(parents=True, exist_ok=True)
    return {
      "svg":[{"path":rel(p),"size_bytes":p.stat().st_size,"kind":"svg"} for p in sorted((ROOT/"data/svg").glob("*.svg"))],
      "pdf":[{"path":rel(p),"size_bytes":p.stat().st_size,"kind":"pdf"} for p in sorted((ROOT/"data/pdf").glob("*.pdf"))],
      "ppt":[{"path":rel(p),"size_bytes":p.stat().st_size,"kind":p.suffix[1:].lower()} for pat in ("*.ppt","*.pptx") for p in sorted((ROOT/"data/ppt").glob(pat))],
    }

def parse_svg(path: Path, idx: int):
    try: root=ET.parse(path).getroot()
    except ET.ParseError as exc: return {"path":rel(path),"status":"load_error","error":str(exc),"lines":[],"arrows":[],"tags":[],"boundaries":[]}
    lines=[]; arrows=[]; tags=[]; boundaries=[]
    for n,e in enumerate(root.iter()):
        t=strip(e.tag); eid=e.attrib.get("id") or f"svg{idx}_{t}_{n}"; st=colour(attr(e,"stroke")); fl=colour(attr(e,"fill")); ps=points(e); box=bbox(ps); sy=style(e.attrib.get("style"))
        if t in {"path","line","polyline"} and st not in {"none","#ffffff"} and ps:
            bid, proc, conf=bin_colour(st); lid=f"line_{idx:02d}_{len(lines)+1:05d}"; unres=None if bid not in {"unknown_black_or_other","black_structure_unknown"} else "Colour maps to black/unknown/structure pending validation."
            lines.append({"line_id":lid,"source_file":rel(path),"source_svg_id":eid,"source_colour":st,"colour_bin":bid,"process":proc,"geometry":{"points_sample":ps[:20],"bbox":box},"subsystem":"Unknown","confidence":conf,"evidence":[f"stroke={st}",f"element={t}"],"unresolved_reason":unres})
            mend=e.attrib.get("marker-end") or sy.get("marker-end"); mstart=e.attrib.get("marker-start") or sy.get("marker-start")
            if mend or mstart:
                tip=ps[-1] if mend else ps[0]; body=ps[0] if mend else ps[-1]
                arrows.append({"arrow_id":f"arrow_{idx:02d}_{len(arrows)+1:05d}","source_file":rel(path),"source_svg_id":eid,"source_colour":st,"arrow_body_geometry":{"coordinate":body},"arrow_tip_geometry":{"coordinate":tip},"direction_vector":[tip[0]-body[0],tip[1]-body[1]],"associated_line_id":lid,"associated_subsystem":"Unknown","confidence":.84,"evidence":["SVG marker-start/marker-end evidence",f"marker={mend or mstart}"],"unresolved_reason":None})
        if t == "path" and ps and fl not in {"none","#ffffff"} and len(ps)>=3:
            b=bbox(ps[:4])
            if b and b["x_max"]-b["x_min"] <= 40 and b["y_max"]-b["y_min"] <= 40:
                arrows.append({"arrow_id":f"arrow_{idx:02d}_{len(arrows)+1:05d}","source_file":rel(path),"source_svg_id":eid,"source_colour":fl,"arrow_body_geometry":None,"arrow_tip_geometry":{"coordinate":ps[0]},"direction_vector":None,"associated_line_id":None,"associated_subsystem":"Unknown","confidence":.38,"evidence":["Small filled path resembles possible arrow head","No connected body line proven"],"unresolved_reason":"Possible arrow head is not confidently associated with a body line; direction not inferred."})
        if t == "text":
            text="".join(e.itertext()).strip()
            if text:
                m=TRANS.search(e.attrib.get("transform","")); x=float(e.attrib.get("x", m.group(1) if m else 0) or 0); y=float(e.attrib.get("y", m.group(2) if m and m.group(2) else 0) or 0); cls, classes=tag_class(text)
                tags.append({"tag_id":f"tag_{idx:02d}_{len(tags)+1:05d}","source_file":rel(path),"source_svg_id":eid,"text":text,"detected_tokens":TAG.findall(text),"coordinate":[x,y],"semantic_class":cls,"semantic_classes":classes,"subsystem":subsystem(text),"confidence":.82 if TAG.search(text) else .45,"evidence":["SVG text element"],"unresolved_reason":None if TAG.search(text) else "Text could not be classified as a tag by conservative regex."})
        if t in {"rect","polygon","polyline","path"} and box and ((e.attrib.get("stroke-dasharray") or sy.get("stroke-dasharray")) or t=="rect") and box["x_max"]-box["x_min"]>100 and box["y_max"]-box["y_min"]>80:
            boundaries.append({"boundary_id":f"boundary_{idx:02d}_{len(boundaries)+1:05d}","source_file":rel(path),"source_svg_id":eid,"bbox":box,"stroke":st,"subsystem":"Unknown","confidence":.5,"evidence":["large enclosing geometry"],"unresolved_reason":"Boundary/scope label not directly associated."})
    sub_tags=[x for x in tags if x["subsystem"]!="Unknown"]
    for item in lines+boundaries:
        b=item.get("geometry",{}).get("bbox") or item.get("bbox"); c=mid(b)
        if c and sub_tags:
            near=min(sub_tags, key=lambda tg: dist(c, tg["coordinate"]))
            if dist(c, near["coordinate"]) < 450: item["subsystem"]=near["subsystem"]; item["evidence"].append("nearest subsystem text: "+near["text"])
    lmap={x["line_id"]:x for x in lines}
    for a in arrows:
        if a.get("associated_line_id") in lmap: a["associated_subsystem"]=lmap[a["associated_line_id"]]["subsystem"]
    return {"path":rel(path),"status":"loaded","lines":lines,"arrows":arrows,"tags":tags,"boundaries":boundaries}

def write_json(p: Path, data): p.parent.mkdir(parents=True, exist_ok=True); p.write_text(json.dumps(data, indent=2, ensure_ascii=False)+"\n")
def table(rows, heads): return "| "+" | ".join(heads)+" |\n| "+" | ".join(["---"]*len(heads))+" |\n"+"\n".join("| "+" | ".join(map(str,r))+" |" for r in rows)

def build(acq=True):
    acquisitions=acquire() if acq else []; extractions=extract_archives(); inv=inventory(); results=[parse_svg(ROOT/x["path"], i) for i,x in enumerate(inv["svg"],1)]
    lines=[y for r in results for y in r["lines"]]; arrows=[y for r in results for y in r["arrows"]]; tags=[y for r in results for y in r["tags"]]; bounds=[y for r in results for y in r["boundaries"]]
    for x in lines: x["viewer_layer_ids"]=["process_lines",x["colour_bin"],"subsystem_"+x["subsystem"].lower()]
    for x in arrows: x["colour_bin"]=bin_colour(x.get("source_colour"))[0]; x["viewer_layer_ids"]=["arrows",x["colour_bin"],"subsystem_"+x["associated_subsystem"].lower()]
    for x in tags: x["viewer_layer_ids"]=[x["semantic_class"]+"s","subsystem_"+x["subsystem"].lower()]
    for x in bounds: x["viewer_layer_ids"]=["boundaries","subsystem_"+x["subsystem"].lower()]
    cc=Counter(x["colour_bin"] for x in lines); ac=Counter(x["colour_bin"] for x in arrows); tc=Counter(x["semantic_class"] for x in tags); sc=Counter([*(x["subsystem"] for x in lines+tags+bounds), *(x["associated_subsystem"] for x in arrows)])
    for s in SUBSYSTEMS: sc.setdefault(s,0)
    ua=[x for x in arrows if x.get("unresolved_reason") or not x.get("associated_line_id") or not x.get("direction_vector")]; uc=[x for x in lines if x.get("unresolved_reason")]; ut=[x for x in tags if x.get("unresolved_reason")]; ub=[x for x in bounds if x.get("unresolved_reason")]
    run={"schema_version":"0.2","generated_at":datetime.now(timezone.utc).isoformat(),"source_archives":acquisitions,"extraction_results":extractions,"inputs_found":[*inv["svg"],*inv["pdf"],*inv["ppt"]],"svg_load_status":[{"path":r["path"],"status":r["status"],"error":r.get("error")} for r in results],"completion_status":"complete_nonzero" if lines and tags else "incomplete_no_nonzero_semantic_counts"}
    layers=layers_model(cc,tc,len(lines),len(arrows),len(bounds),len(ua)+len(uc)+len(ut)+len(ub),sc)
    write_json(MODEL_DIR/"line_model.json", {**run,"summary":{"line_count":len(lines),"colour_counts":dict(cc)},"lines":lines})
    write_json(MODEL_DIR/"arrow_direction_model.json", {**run,"summary":{"arrow_count":len(arrows),"arrow_colour_counts":dict(ac),"unresolved_arrow_count":len(ua)},"arrows":arrows})
    write_json(MODEL_DIR/"semantic_layer_model.json", {**run,"layers":layers})
    write_json(MODEL_DIR/"subsystem_model.json", {**run,"subsystems":[{"subsystem":s,"item_count":sc.get(s,0)} for s in SUBSYSTEMS]})
    write_json(MODEL_DIR/"tag_layer_register.json", {**run,"summary":{"tag_count":len(tags),"tag_counts":dict(tc),"unresolved_tag_count":len(ut)},"tags":tags,"boundaries":bounds})
    for bid,fn in BIN_FILES.items():
        if bid=="black_structure_unknown": continue
        bl=[x for x in lines if x["colour_bin"]==bid or (bid=="unknown_black_or_other" and x["colour_bin"]=="black_structure_unknown")]
        write_json(LINES_DIR/fn,{**run,"colour_bin":bid,"line_count":len(bl),"lines":bl})
    write_reports(run,inv,cc,ac,tc,sc,lines,arrows,tags,bounds,ua,uc,ut,ub,layers); write_html()
    return {"inventory":inv,"colour_counts":dict(cc),"subsystem_counts":dict(sc),"arrow_counts":dict(ac),"unresolved_counts":{"arrows":len(ua),"colours":len(uc),"tags":len(ut),"boundaries":len(ub),"objects":len(ua)+len(uc)+len(ut)+len(ub)},"completion_status":run["completion_status"]}

def layers_model(cc,tc,lc,ac,bc,uc,sc):
    rows=[("process_lines","process lines",lc),("blue_A","BLUE → A / A′",cc.get("blue_A",0)),("cyan_B_2K","CYAN → B / B′",cc.get("cyan_B_2K",0)),("green_W_coupler","GREEN → W",cc.get("green_W_coupler",0)),("grey_V_vent","GREY → V",cc.get("grey_V_vent",0)),("olive_S_line","OLIVE → S",cc.get("olive_S_line",0)),("red_orange_D_E","RED / ORANGE → D/E",cc.get("red_orange_D_E",0)),("unknown_black_or_other","BLACK/unknown → structure/unknown",cc.get("black_structure_unknown",0)+cc.get("unknown_black_or_other",0)),("instruments","instruments",tc.get("instrument",0)),("valves","valves",tc.get("valve",0)),("equipment","equipment",tc.get("equipment",0)),("boundaries","boundaries",bc),("arrows","arrows",ac),("unresolved_objects","unresolved objects",uc)]
    rows += [("subsystem_"+s.lower(),s,sc.get(s,0)) for s in SUBSYSTEMS[:-1]]
    return [{"layer_id":a,"label":b,"item_count":c} for a,b,c in rows]

def write_reports(run,inv,cc,ac,tc,sc,lines,arrows,tags,bounds,ua,uc,ut,ub,layers):
    arch=[[x.get("archive"),x.get("url"),x.get("status"),x.get("size_bytes",""),x.get("error","")] for x in run["source_archives"]] or [["not attempted","","n/a","",""]]
    ext=[[x.get("archive"),x.get("member",""),x.get("destination",""),x.get("status"),x.get("reason",x.get("error",""))] for x in run["extraction_results"]] or [["none","","","no extracted files",""]]
    inputs=[[x["path"],x["kind"],x["size_bytes"]] for x in run["inputs_found"]] or [["No extracted source files available","n/a",0]]
    common=f"""## Source archive acquisition\n{table(arch,['archive','url','status','size_bytes','error'])}\n\n## Files extracted from archives\n{table(ext[:80],['archive','member','destination','status','note'])}\n\n## Actual source files found\n{table(inputs,['path','kind','size_bytes'])}\n\n## Source file counts\n- SVG files found: {len(inv['svg'])}\n- PDF files found: {len(inv['pdf'])}\n- PPT/PPTX files found: {len(inv['ppt'])}\n\n## SVG load status\n{table([[x['path'],x['status'],x.get('error') or ''] for x in run['svg_load_status']] or [['none','not_loaded','']], ['path','status','error'])}\n\n## Colour bins detected\n{table([[k,v] for k,v in sorted(cc.items())] or [['none',0]], ['colour_bin','process_line_count'])}\n\n## Object counts\n- Process lines: {len(lines)}\n- Tags: {len(tags)}\n- Valves: {tc.get('valve',0)}\n- Instruments: {tc.get('instrument',0)}\n- Equipment: {tc.get('equipment',0)}\n- Arrows: {len(arrows)}\n- Boundaries: {len(bounds)}\n\n## Arrow counts per colour\n{table([[k,v] for k,v in sorted(ac.items())] or [['none',0]], ['colour_bin','arrow_count'])}\n\n## Tag counts\n{table([[k,v] for k,v in sorted(tc.items())] or [['none',0]], ['tag_class','count'])}\n\n## Subsystem counts\n{table([[s,sc.get(s,0)] for s in SUBSYSTEMS], ['subsystem','object_count'])}\n\n## Unresolved counts\n- Unresolved arrows: {len(ua)}\n- Unresolved colours: {len(uc)}\n- Unresolved tags: {len(ut)}\n- Unresolved boundaries: {len(ub)}\n- Unresolved objects: {len(ua)+len(uc)+len(ut)+len(ub)}\n\n## Completion status\n- {run['completion_status']}\n- Complete semantic extraction is not reported unless actual non-zero line and tag counts exist.\n\n## Confidence notes\n- Colour/process mappings use BLUE/CYAN/GREEN/GREY/OLIVE/RED-ORANGE/BLACK evidence.\n- Direction vectors are recorded only for explicit SVG marker evidence with body/tip geometry.\n- Subsystem bins are QM, Jumper, QVB, QINFRA, and Unknown.\n"""
    (REPORTS_DIR/"W002_colour_line_validation.md").write_text("# W002 Colour Line Validation\n\n"+common+"\n## Unresolved colours\n"+table([[x['line_id'],x['source_file'],x['source_colour'],x['unresolved_reason']] for x in uc[:80]] or [['none','','','']], ['line_id','source_file','colour','reason'])+"\n")
    (REPORTS_DIR/"W003_semantic_layer_validation.md").write_text("# W003 Semantic Layer Validation\n\n"+common+"\n## Semantic layers\n"+table([[x['layer_id'],x['label'],x['item_count']] for x in layers], ['layer_id','label','count'])+"\n")
    (REPORTS_DIR/"W003_arrow_direction_validation.md").write_text("# W003 Arrow Direction Validation\n\n"+common+"\n## Unresolved arrows\n"+table([[x['arrow_id'],x['source_file'],x.get('source_colour'),x.get('associated_line_id') or '',x.get('unresolved_reason') or ''] for x in ua[:100]] or [['none','','','','']], ['arrow_id','source_file','colour','associated_line_id','reason'])+"\n")

def write_html():
    html='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>ABACUS P&amp;ID Semantic Viewer</title><style>@page{size:A3 landscape;margin:8mm}body{margin:0;font-family:system-ui,sans-serif;background:#111;color:#eee}.app{display:grid;grid-template-columns:330px 1fr 320px;min-height:100vh}aside{background:#14213d;padding:1rem;overflow:auto}main{background:#f7f7f7;color:#111;overflow:auto;position:relative}.toggle{display:block;margin:.25rem 0;padding:.25rem;border-bottom:1px solid #ffffff22}#canvas{position:relative;min-height:80vh;padding:1rem}#svgHost svg{max-width:100%;height:auto;background:white}.overlay{position:absolute;left:1rem;top:1rem;pointer-events:none}.meta{white-space:pre-wrap;font-family:ui-monospace,monospace;font-size:12px}.badge{border:1px solid currentColor;border-radius:999px;padding:.1rem .4rem}.line-label{background:white;color:#111;stroke:white;stroke-width:3px;paint-order:stroke;font-size:11px}@media print{body{background:white;color:black}.app{display:block}aside{display:none}}</style></head><body><div class="app"><aside><h1>P&amp;ID Viewer</h1><p>Loads original SVG and model-derived semantic toggles.</p><input id="search" placeholder="Search by tag" style="width:100%"><h2>Toggles</h2><div id="toggles"></div></aside><main><div id="canvas"><div id="svgHost"></div><svg id="overlay" class="overlay"></svg></div></main><aside><h2>Metadata</h2><div id="meta" class="meta">Click an overlay item.</div><h2>Unresolved objects</h2><div id="unresolved"></div></aside></div><script>
const U={line:'../data/model/line_model.json',arrows:'../data/model/arrow_direction_model.json',layers:'../data/model/semantic_layer_model.json',tags:'../data/model/tag_layer_register.json'};let M={lines:[],arrows:[],tags:[],boundaries:[],layers:[],unresolved:{}};const active=new Set();
Promise.all(Object.values(U).map(u=>fetch(u).then(r=>r.json()))).then(([line,ar,l,t])=>{M.lines=line.lines||[];M.arrows=ar.arrows||[];M.layers=l.layers||[];M.tags=t.tags||[];M.boundaries=t.boundaries||[];M.unresolved={arrows:M.arrows.filter(x=>x.unresolved_reason||!x.associated_line_id||!x.direction_vector),colours:M.lines.filter(x=>x.unresolved_reason),tags:M.tags.filter(x=>x.unresolved_reason),boundaries:M.boundaries.filter(x=>x.unresolved_reason)};buildToggles();loadSvg((line.inputs_found||[]).find(x=>x.kind==='svg')?.path||'../data/svg/PFD-PID MINERVA QCELL-LB.svg');render()}).catch(e=>meta.textContent='Model load failed: '+e.message);
function buildToggles(){toggles.innerHTML='';for(const l of M.layers){active.add(l.layer_id);let lab=document.createElement('label');lab.className='toggle';lab.innerHTML=`<input type="checkbox" checked data-layer="${l.layer_id}"> ${l.label} <span class="badge">${l.item_count}</span>`;toggles.appendChild(lab)}}
toggles.onchange=e=>{if(e.target.dataset.layer){e.target.checked?active.add(e.target.dataset.layer):active.delete(e.target.dataset.layer);render()}};search.oninput=render;
function loadSvg(src){fetch(src).then(r=>r.ok?r.text():Promise.reject(Error(r.status))).then(x=>{svgHost.innerHTML=x;size();render()}).catch(e=>svgHost.innerHTML=`<div style="padding:2rem;background:white;border:2px dashed #999">SVG input unavailable: ${src}<br>${e.message}</div>`)};onresize=()=>{size();render()};
function size(){let s=document.querySelector('#svgHost svg');if(s){let b=s.getBoundingClientRect();overlay.setAttribute('width',b.width);overlay.setAttribute('height',b.height)}}function show(x){meta.textContent=JSON.stringify(x,null,2)}function vis(x){let ids=x.viewer_layer_ids||[];return ids.some(i=>active.has(i))||(active.has('unresolved_objects')&&x.unresolved_reason)}function box(x){return x.bbox||x.geometry?.bbox}
function render(){overlay.innerHTML='';let q=search.value.toLowerCase();for(const x of M.lines)if(vis(x))rect(x,x.source_colour||'black','4 2');for(const x of M.boundaries)if(vis(x))rect(x,'#7b2cbf','8 4');for(const x of M.arrows)if(vis(x))arrow(x);for(const x of M.tags)if((!q||x.text.toLowerCase().includes(q))&&vis(x))text(x);unres()}function rect(x,c,d){let b=box(x);if(!b)return;let r=document.createElementNS('http://www.w3.org/2000/svg','rect');r.setAttribute('x',b.x_min);r.setAttribute('y',b.y_min);r.setAttribute('width',Math.max(2,b.x_max-b.x_min));r.setAttribute('height',Math.max(2,b.y_max-b.y_min));r.setAttribute('fill','none');r.setAttribute('stroke',c);r.setAttribute('stroke-width','2');r.setAttribute('stroke-dasharray',d);r.style.pointerEvents='all';r.onclick=()=>show(x);overlay.appendChild(r)}function arrow(x){let p=x.arrow_tip_geometry?.coordinate,s=x.arrow_body_geometry?.coordinate;if(!p)return;let g=document.createElementNS('http://www.w3.org/2000/svg','g'),c=x.confidence>=.7?'#d00000':'#ffba08',o=document.createElementNS('http://www.w3.org/2000/svg','circle');o.setAttribute('cx',p[0]);o.setAttribute('cy',p[1]);o.setAttribute('r',5);o.setAttribute('fill',c);g.appendChild(o);if(s){let l=document.createElementNS('http://www.w3.org/2000/svg','line');l.setAttribute('x1',s[0]);l.setAttribute('y1',s[1]);l.setAttribute('x2',p[0]);l.setAttribute('y2',p[1]);l.setAttribute('stroke',c);l.setAttribute('stroke-width',2);g.appendChild(l)}g.style.pointerEvents='all';g.onclick=()=>show(x);overlay.appendChild(g)}function text(x){let e=document.createElementNS('http://www.w3.org/2000/svg','text');e.setAttribute('x',x.coordinate[0]);e.setAttribute('y',x.coordinate[1]);e.setAttribute('class','line-label');e.textContent=x.text.slice(0,28);e.style.pointerEvents='all';e.onclick=()=>show(x);overlay.appendChild(e)}function unres(){unresolved.innerHTML='';for(const[k,items]of Object.entries(M.unresolved)){let h=document.createElement('h3');h.textContent=`${k} (${items.length})`;unresolved.appendChild(h);for(const it of items.slice(0,40)){let b=document.createElement('button');b.textContent=it.arrow_id||it.line_id||it.tag_id||it.boundary_id||'unresolved';b.onclick=()=>show(it);unresolved.appendChild(b);unresolved.appendChild(document.createElement('br'))}}}
</script></body></html>'''
    VIEWER_DIR.mkdir(parents=True, exist_ok=True); PUBLISH_DIR.mkdir(parents=True, exist_ok=True)
    (VIEWER_DIR/"index.html").write_text(html); (PUBLISH_DIR/"colour_line_collage.html").write_text(html.replace("P&amp;ID Semantic Viewer","Colour Line Collage"))

def main(argv=None):
    p=argparse.ArgumentParser(); p.add_argument("command", nargs="?", default="all", choices=["all","extract"]); a=p.parse_args(argv); print(json.dumps(build(a.command=="all"), indent=2, ensure_ascii=False)); return 0
if __name__ == "__main__": raise SystemExit(main())
