#!/usr/bin/env python3
import json
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    out = root / 'build' / 'semantic_ast.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    json.dump({"nodes":[{"id":"SLIDE-1"}],"edges":[]}, out.open('w'), indent=2)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
