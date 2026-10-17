"""Reproducible standalone dashboard and source-derived Mermaid/SVG topologies."""
from __future__ import annotations
from collections import defaultdict
import html
import json
from pathlib import Path
from xml.etree import ElementTree as ET
from .graph import canonical_bytes, sha256

HERE = Path(__file__).resolve().parent


def dashboard(payload: dict) -> str:
    raw=HERE.joinpath('templates/dashboard.html').read_text(encoding='utf-8')
    # JS-owned literal: protect script context and embedded hostile source labels.
    encoded=canonical_bytes(payload).decode('ascii').replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    return raw.replace('__PAYLOAD__',encoded)


def mermaid_sipoc(graph: dict) -> str:
    lines=['flowchart LR','    %% Source-bound SIPOC: separate N1 and N7 process graphs']
    ids={n['id'] for n in graph['nodes'] if n['kind']=='SIPOC_INSTANCE'}
    for n in graph['nodes']:
        if n['id'] not in ids:continue
        safe=(n.get('legacy_id') or n['id'].split(':')[-1])+' | '+n['title'].replace('"',"'")[:93]
        lines.append('    '+_mmd_id(n['id'])+'["'+safe+'"]')
    for e in graph['edges']:
        if e['kind']=='SIPOC_DEPENDENCY':lines.append('    '+_mmd_id(e['from'])+' --> '+_mmd_id(e['to']))
    return '\n'.join(lines)+'\n'


def mermaid_federation(graph: dict) -> str:
    eligible={n['id'] for n in graph['nodes'] if n['kind'] in {'REPOSITORY','CONTRACT','GATE'}}
    edges=[e for e in graph['edges'] if e['from'] in eligible and e['to'] in eligible]
    lines=['flowchart TD','    %% Solid = observed, dotted = declared']
    for n in graph['nodes']:
        if n['id'] not in eligible:continue
        lines.append('    '+_mmd_id(n['id'])+'["'+n['title'].replace('"',"'")[:72]+'"]')
    for e in edges:
        arrow=' -.-> ' if e['binding']=='DECLARED' else ' --> '
        lines.append('    '+_mmd_id(e['from'])+arrow+_mmd_id(e['to']))
    return '\n'.join(lines)+'\n'


def mermaid_golden(graph: dict) -> str:
    eg=[e for e in graph['edges'] if e['layer']=='GOLDEN_THREAD']
    ids={e[k] for e in eg for k in ('from','to')}
    lines=['flowchart LR','    %% Receipt-bound and observed source evidence are not formal root closure']
    for n in graph['nodes']:
        if n['id'] in ids:lines.append('    '+_mmd_id(n['id'])+'["'+n['title'].replace('"',"'")[:88]+'"]')
    for e in eg:
        lines.append('    '+_mmd_id(e['from'])+(' -.-> ' if e['binding']=='DECLARED' else ' --> ')+_mmd_id(e['to']))
    return '\n'.join(lines)+'\n'


def mermaid_bd(graph: dict) -> str:
    rows=[n for n in graph['nodes'] if n['kind']=='BD_ITEM']
    lines=['flowchart LR','    %% State is recorded CPQ lifecycle, not accepted causal root closure']
    for n in rows:lines.append('    '+_mmd_id(n['id'])+'["'+n['title']+'"]')
    for e in graph['edges']:
        if e['from'].startswith('cpq:') and e['to'].startswith('cpq:'):
            arrow=' -.-> ' if e['kind']=='REVERSE_PRESSURE' else ' --> '
            lines.append('    '+_mmd_id(e['from'])+arrow+_mmd_id(e['to']))
    return '\n'.join(lines)+'\n'


def _mmd_id(value: str) -> str:
    return 'n'+''.join(c if c.isalnum() else '_' for c in value)


def static_svg(graph: dict, layer: str) -> str:
    nodes=[n for n in graph['nodes'] if n['layer']==layer]
    ids={n['id'] for n in nodes}
    edges=[e for e in graph['edges'] if e['from'] in ids and e['to'] in ids and e['layer']==layer]
    if not nodes:return ''
    NS='http://www.w3.org/2000/svg'
    ET.register_namespace('',NS)
    svg=ET.Element('{'+NS+'}svg',{'viewBox':'0 0 1440 850','role':'img','aria-label':layer+' source topology'})
    ET.SubElement(svg,'{'+NS+'}rect',{'width':'1440','height':'850','fill':'#10192a'})
    for i,n in enumerate(nodes):
        x=100+(i%8)*178;y=85+(i//8)*135
        color={'SIPOC':'#73befa','GOLDEN_THREAD':'#f0c781','FEDERATION':'#5be3d7','BD':'#f190b5'}.get(layer,'#b7c5e3')
        rect=ET.SubElement(svg,'{'+NS+'}rect',{'x':str(x),'y':str(y),'width':'150','height':'74','rx':'10','fill':'#1f3046','stroke':color,'stroke-width':'2'})
        label=ET.SubElement(svg,'{'+NS+'}text',{'x':str(x+8),'y':str(y+26),'fill':'#e7edf6','font-size':'12','font-family':'monospace'})
        label.text=n['id'][:24]
        p=ET.SubElement(svg,'{'+NS+'}text',{'x':str(x+8),'y':str(y+49),'fill':'#b2c4d6','font-size':'10','font-family':'monospace'})
        p.text=n['evidence']
    footer=ET.SubElement(svg,'{'+NS+'}text',{'x':'60','y':'830','fill':'#9baec5','font-size':'14','font-family':'monospace'})
    footer.text=f'{layer} | {len(nodes)} nodes | {len(edges)} within-layer edges | source-bound local projection only'
    return ET.tostring(svg,encoding='unicode',xml_declaration=False)