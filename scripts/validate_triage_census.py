#!/usr/bin/env python3
from pathlib import Path
import sys,yaml
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'triage'/'census'/'CODEX.census.yaml'
REQ={'identity','locations','architecture','contracts','execution','pipeline','outward_products','automation','integration','governance'}
def main():
 d=yaml.safe_load(P.read_text(encoding='utf-8'))
 assert REQ <= set(d), f'missing {sorted(REQ-set(d))}'
 assert d['identity']['role']=='KEB_SEMANTIC_CONTROL'
 assert 'may not promote engineering facts' in d['governance']['promotion_rules']
 assert 'SHA256' in d['governance']['hashes']
 assert d['automation']['mcp'], 'KEB MCP census must not be empty'
 for b in ['Federation_Bridge','DOW_Bridge','Analysis_Return_Bridge','Reentry_Bridge']:
  assert b in d['integration']['bridges'], f'missing bridge {b}'
 print('TRIAGE census PASS:',d['identity']['repo']); return 0
if __name__=='__main__': sys.exit(main())
